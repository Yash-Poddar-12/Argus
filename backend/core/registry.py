"""Module auto-discovery (M00).

Every folder ``backend/modules/<name>/`` with a ``module.py`` is loaded automatically.
A module never edits core to plug in. ``module.py`` may define:

    MODULE_ID = "M04"                        # required
    router: APIRouter | None                 # mounted under /api/v1
    event_handlers: list[tuple[str, handler]]  # (event_type glob, async handler(event))
    ws_message_types: list[str]              # WS message types this module pushes
    permissions: dict[str, list[str]]        # role -> extra permissions
    async def startup(runtime) -> None       # optional
    async def shutdown(runtime) -> None      # optional

``models.py`` (if present) is imported first so its tables join the shared metadata.
Set ``DISABLED_MODULES=m09_scenarios,...`` to skip modules.
"""

from __future__ import annotations

import importlib
import os
import pkgutil
from dataclasses import dataclass, field
from types import ModuleType

from fastapi import APIRouter

import backend.modules as modules_pkg
from backend.core.auth import register_permissions
from backend.core.logging import get_logger

log = get_logger(__name__)


@dataclass
class LoadedModule:
    name: str
    module_id: str
    module: ModuleType
    router: APIRouter | None = None
    ws_message_types: list[str] = field(default_factory=list)


def discover() -> list[LoadedModule]:
    disabled = {m.strip() for m in os.environ.get("DISABLED_MODULES", "").split(",") if m.strip()}
    loaded: list[LoadedModule] = []
    for info in sorted(pkgutil.iter_modules(modules_pkg.__path__), key=lambda i: i.name):
        if not info.ispkg or info.name.startswith("_") or info.name in disabled:
            continue
        base = f"{modules_pkg.__name__}.{info.name}"
        try:
            importlib.import_module(f"{base}.models")
        except ModuleNotFoundError as exc:
            if exc.name != f"{base}.models":
                raise
        try:
            mod = importlib.import_module(f"{base}.module")
        except ModuleNotFoundError as exc:
            if exc.name == f"{base}.module":
                continue
            raise
        module_id = getattr(mod, "MODULE_ID", None)
        if not module_id:
            raise RuntimeError(f"{base}.module must define MODULE_ID")
        register_permissions(getattr(mod, "permissions", {}))
        loaded.append(LoadedModule(info.name, module_id, mod, getattr(mod, "router", None),
                                   list(getattr(mod, "ws_message_types", []))))
    return loaded


def import_all_models() -> None:
    """Populate Base.metadata with every module's tables (Alembic, tests)."""
    for info in pkgutil.iter_modules(modules_pkg.__path__):
        if info.ispkg and not info.name.startswith("_"):
            try:
                importlib.import_module(f"{modules_pkg.__name__}.{info.name}.models")
            except ModuleNotFoundError as exc:
                if exc.name != f"{modules_pkg.__name__}.{info.name}.models":
                    raise
