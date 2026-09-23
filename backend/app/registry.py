"""Discovery of capability wiring (replaces a hand-edited central registry).

Any capability package can plug into the app by adding a ``wiring.py``. Searched locations:
``app/domain/<area>/wiring.py`` and top-level components ``app/<component>/wiring.py`` (e.g. copilot, iot).
A ``wiring.py`` may define:

    PERMISSIONS: dict[str, list[str]]           role -> permission strings this capability introduces
    EVENT_HANDLERS: list[tuple[str, handler]]   (event_type glob, async handler(event))
    WS_MESSAGE_TYPES: list[str]                 WebSocket message types this capability pushes (docs only)
    async def startup(runtime) / shutdown(runtime)
    def contract_documents() -> dict[str, dict] JSON Schemas generated from models (scripts/contracts.py export)

HTTP routes are NOT registered here: they live in ``app/api/v1/*.py`` (auto-included by app/api/router.py).
Set ``DISABLED_CAPABILITIES=twin,...`` to skip capabilities.
"""

from __future__ import annotations

import importlib
import os
import pkgutil
from dataclasses import dataclass
from types import ModuleType

import app as app_pkg
import app.domain as domain_pkg
from app.core.security import register_permissions

TOP_LEVEL_COMPONENTS = ("copilot", "iot")


@dataclass
class Capability:
    name: str
    wiring: ModuleType


def _try_import(name: str) -> ModuleType | None:
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError as exc:
        if exc.name == name:
            return None
        raise


def import_all_models() -> None:
    """Populate Base.metadata with every domain's tables (Alembic, create_all, tests)."""
    import app.core.audit  # noqa: F401  (audit_log table)

    for info in pkgutil.iter_modules(domain_pkg.__path__):
        if info.ispkg:
            _try_import(f"{domain_pkg.__name__}.{info.name}.models")


def discover() -> list[Capability]:
    disabled = {c.strip() for c in os.environ.get("DISABLED_CAPABILITIES", "").split(",") if c.strip()}
    import_all_models()
    found: list[Capability] = []
    candidates = [(i.name, f"{domain_pkg.__name__}.{i.name}.wiring")
                  for i in sorted(pkgutil.iter_modules(domain_pkg.__path__), key=lambda i: i.name) if i.ispkg]
    candidates += [(c, f"{app_pkg.__name__}.{c}.wiring") for c in TOP_LEVEL_COMPONENTS]
    for name, module_name in candidates:
        if name in disabled:
            continue
        wiring = _try_import(module_name)
        if wiring is None:
            continue
        register_permissions(getattr(wiring, "PERMISSIONS", {}))
        found.append(Capability(name, wiring))
    return found
