"""Telemetry capability wiring (see app/registry.py)."""

from __future__ import annotations

from app.core.contracts import event_documents
from app.domain.telemetry import ingest
from app.domain.telemetry.events import EVENT_PAYLOADS

PERMISSIONS = {"SUPERVISOR_ADMIN": ["telemetry:ingest"]}
WS_MESSAGE_TYPES = ["MACHINE_STATE_UPDATE"]


async def startup(runtime) -> None:
    ingest.reset_cache()


def contract_documents() -> dict[str, dict]:
    return event_documents("telemetry", EVENT_PAYLOADS)
