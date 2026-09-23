"""Common error envelope (contracts/schemas/common/error.json)."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger, request_id_var

log = get_logger(__name__)


class AppError(Exception):
    def __init__(self, status: int, code: str, message: str, details: Any = None):
        super().__init__(message)
        self.status, self.code, self.message, self.details = status, code, message, details


class NotFound(AppError):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(404, "NOT_FOUND", f"{resource} '{resource_id}' not found", {"resource": resource, "id": resource_id})


class Conflict(AppError):
    def __init__(self, message: str, details: Any = None):
        super().__init__(409, "CONFLICT", message, details)


class Forbidden(AppError):
    def __init__(self, message: str = "Not allowed"):
        super().__init__(403, "FORBIDDEN", message)


class Unauthorized(AppError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(401, "UNAUTHORIZED", message)


class InvalidState(AppError):
    def __init__(self, message: str, details: Any = None):
        super().__init__(409, "INVALID_STATE", message, details)


def envelope(code: str, message: str, details: Any = None) -> dict:
    return {"error": {"code": code, "message": message, "details": details, "request_id": request_id_var.get()}}


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError):
        return JSONResponse(envelope(exc.code, exc.message, exc.details), status_code=exc.status)

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(_: Request, exc: StarletteHTTPException):
        codes = {401: "UNAUTHORIZED", 403: "FORBIDDEN", 404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}
        code = codes.get(exc.status_code, "HTTP_ERROR")
        return JSONResponse(envelope(code, str(exc.detail)), status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_: Request, exc: RequestValidationError):
        errors = [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()]
        return JSONResponse(envelope("VALIDATION_ERROR", "Request validation failed", errors), status_code=422)

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, exc: Exception):
        log.exception("unhandled error")
        return JSONResponse(envelope("INTERNAL_ERROR", "Internal server error"), status_code=500)
