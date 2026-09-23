"""Tasks capability wiring (see app/registry.py)."""

from __future__ import annotations

from app.core.contracts import event_documents
from app.domain.tasks.events import EVENT_PAYLOADS

PERMISSIONS = {
    "OPERATOR": ["tasks:execute"],
    "SUPERVISOR_ADMIN": ["tasks:read", "tasks:write", "tasks:assign"],
}
WS_MESSAGE_TYPES = ["TASK_UPDATE"]


def contract_documents() -> dict[str, dict]:
    return event_documents("tasks", EVENT_PAYLOADS)
