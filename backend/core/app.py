"""Application factory (M00). Run: ``uvicorn backend.core.app:create_app --factory``."""

from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Histogram, generate_latest

import backend.core.audit  # noqa: F401  (registers audit_log table)
from backend.core.config import Settings, get_settings
from backend.core.db import new_id
from backend.core.errors import install_error_handlers
from backend.core.logging import configure_logging, get_logger, request_id_var
from backend.core.registry import discover
from backend.core.runtime import Runtime, build_runtime, set_runtime
from backend.core.ws import build_ws_router

log = get_logger(__name__)
API_PREFIX = "/api/v1"


def route_paths(router, prefix: str = "") -> set[str]:
    """All paths of a router, including nested include_router() children (any FastAPI version)."""
    paths: set[str] = set()
    for r in router.routes:
        if hasattr(r, "path"):
            paths.add(prefix + r.path)
        elif hasattr(r, "original_router"):  # FastAPI >= 0.140 wraps included routers
            ctx = getattr(r, "include_context", None)
            paths |= route_paths(r.original_router, prefix + (getattr(ctx, "prefix", "") or ""))
    return paths


def create_app(settings: Settings | None = None, runtime: Runtime | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level, settings.log_json)
    rt = runtime or build_runtime(settings)
    modules = discover()
    rt.modules = [m.name for m in modules]

    metrics = CollectorRegistry()
    req_count = Counter("http_requests_total", "HTTP requests", ["method", "route", "status"], registry=metrics)
    req_latency = Histogram("http_request_seconds", "HTTP latency", ["method", "route"], registry=metrics)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        set_runtime(rt)
        if settings.db_auto_create:
            await rt.db.create_all()
        for m in modules:
            for pattern, handler in getattr(m.module, "event_handlers", []):
                rt.bus.subscribe(pattern, handler, group=m.name)
        for m in modules:
            if hasattr(m.module, "startup"):
                await m.module.startup(rt)
        await rt.bus.start()
        log.info("started", extra={"app_module": ",".join(rt.modules)})
        yield
        for m in reversed(modules):
            if hasattr(m.module, "shutdown"):
                await m.module.shutdown(rt)
        await rt.close()
        set_runtime(None)

    app = FastAPI(title="Argus Platform API", version=settings.app_version, lifespan=lifespan)
    app.state.runtime = rt
    app.state.module_paths = {}
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
        from fastapi.responses import JSONResponse

        return JSONResponse({"status": "ready" if ok else "not_ready", "checks": checks}, status_code=200 if ok else 503)

    @app.get("/version", tags=["ops"])
    async def version():
        return {"version": settings.app_version, "git_sha": settings.git_sha, "env": settings.app_env,
                "modules": [{"name": m.name, "id": m.module_id} for m in modules]}

    @app.get("/metrics", tags=["ops"], response_class=PlainTextResponse)
    async def metrics_endpoint():
        return PlainTextResponse(generate_latest(metrics).decode(), media_type=CONTENT_TYPE_LATEST)

    for m in modules:
        if m.router is None:
            continue
        app.include_router(m.router, prefix=API_PREFIX)
        app.state.module_paths[m.name] = route_paths(m.router, API_PREFIX)

    app.include_router(build_ws_router(rt.ws))
    return app
