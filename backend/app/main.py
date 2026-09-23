"""Application factory. Run: ``uvicorn app.main:create_app --factory`` (from the repo root after ``uv sync``)."""

from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Histogram, generate_latest

from app.api.router import API_PREFIX, build_api_router
from app.config import Settings, get_settings
from app.core.database import new_id
from app.core.exceptions import install_error_handlers
from app.core.logging import configure_logging, get_logger, request_id_var
from app.core.runtime import Runtime, build_runtime, set_runtime
from app.core.websocket import build_ws_router
from app.registry import discover

log = get_logger(__name__)

__all__ = ["API_PREFIX", "create_app"]


def create_app(settings: Settings | None = None, runtime: Runtime | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level, settings.log_json)
    rt = runtime or build_runtime(settings)
    capabilities = discover()
    rt.capabilities = [c.name for c in capabilities]

    metrics = CollectorRegistry()
    req_count = Counter("http_requests_total", "HTTP requests", ["method", "route", "status"], registry=metrics)
    req_latency = Histogram("http_request_seconds", "HTTP latency", ["method", "route"], registry=metrics)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        set_runtime(rt)
        if settings.db_auto_create:
            await rt.db.create_all()
        for c in capabilities:
            for pattern, handler in getattr(c.wiring, "EVENT_HANDLERS", []):
                rt.bus.subscribe(pattern, handler, group=c.name)
        for c in capabilities:
            if hasattr(c.wiring, "startup"):
                await c.wiring.startup(rt)
        await rt.bus.start()
        log.info("started", extra={"app_module": ",".join(rt.capabilities)})
        yield
        for c in reversed(capabilities):
            if hasattr(c.wiring, "shutdown"):
                await c.wiring.shutdown(rt)
        await rt.close()
        set_runtime(None)

    app = FastAPI(title="ARGUS Platform API", version=settings.app_version, lifespan=lifespan)
    app.state.runtime = rt
    install_error_handlers(app)
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True,
                       allow_methods=["*"], allow_headers=["*"])

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        rid = request.headers.get("x-request-id") or new_id()
        token = request_id_var.set(rid)
        start = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(token)
        route = getattr(request.scope.get("route"), "path", "unmatched")
        req_count.labels(request.method, route, response.status_code).inc()
        req_latency.labels(request.method, route).observe(time.perf_counter() - start)
        response.headers["x-request-id"] = rid
        return response

    @app.get("/health", tags=["ops"])
    async def health():
        return {"status": "ok"}

    @app.get("/ready", tags=["ops"])
    async def ready():
        checks = {"db": await rt.db.ping(), "state": await rt.state.ping(), "bus": await rt.bus.ping()}
        ok = all(checks.values())
        return JSONResponse({"status": "ready" if ok else "not_ready", "checks": checks}, status_code=200 if ok else 503)

    @app.get("/version", tags=["ops"])
    async def version():
        return {"version": settings.app_version, "git_sha": settings.git_sha, "env": settings.app_env,
                "capabilities": rt.capabilities}

    @app.get("/metrics", tags=["ops"], response_class=PlainTextResponse)
    async def metrics_endpoint():
        return PlainTextResponse(generate_latest(metrics).decode(), media_type=CONTENT_TYPE_LATEST)

    app.include_router(build_api_router())
    app.include_router(build_ws_router(rt.ws))
    return app
