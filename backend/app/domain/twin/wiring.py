"""Operational twin capability wiring (see app/registry.py)."""

from __future__ import annotations

from app.core.contracts import event_documents
from app.domain.twin.events import EVENT_PAYLOADS
from app.domain.twin.handlers import EVENT_HANDLERS as _HANDLERS
from app.domain.twin.schemas import OperationalTwin
from app.domain.twin.service import reset_twin_service

PERMISSIONS = {"SUPERVISOR_ADMIN": ["twin:read"]}
EVENT_HANDLERS = _HANDLERS
WS_MESSAGE_TYPES = ["TWIN_UPDATE", "TASK_ETA_UPDATED"]


async def startup(runtime) -> None:
    reset_twin_service()


def contract_documents() -> dict[str, dict]:
    return {"schemas/twin/operational-twin.json": OperationalTwin.model_json_schema(),
            **event_documents("twin", EVENT_PAYLOADS)}
