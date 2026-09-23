"""API router: auto-includes every ``app/api/v1/<area>.py`` that defines ``router``.

Add an endpoint file for a new capability without editing this file (avoids a merge hotspot).
Routers stay thin: validate input, check permission/scope, call a domain service, shape the response.
"""

from __future__ import annotations

import importlib
import pkgutil

from fastapi import APIRouter

import app.api.v1 as v1_pkg

API_PREFIX = "/api/v1"


def build_api_router() -> APIRouter:
    api = APIRouter(prefix=API_PREFIX)
    for info in sorted(pkgutil.iter_modules(v1_pkg.__path__), key=lambda i: i.name):
        if info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{v1_pkg.__name__}.{info.name}")
        router = getattr(module, "router", None)
        if router is not None:
            api.include_router(router)
    return api
