"""Environment capability wiring (see app/registry.py)."""

from __future__ import annotations

from app.core.contracts import event_documents
from app.domain.environment.events import EVENT_PAYLOADS

PERMISSIONS = {"SUPERVISOR_ADMIN": ["conditions:write"]}


def contract_documents() -> dict[str, dict]:
    return event_documents("environment", EVENT_PAYLOADS)
