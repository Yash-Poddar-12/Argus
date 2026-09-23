"""M01 Operational Twin module: discovered automatically by backend/core/registry.py."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic.json_schema import models_json_schema

from backend.modules.m01_twin.api.twin_api import router as twin_router
from backend.modules.m01_twin.environment.api import router as environment_router
from backend.modules.m01_twin.public import EVENT_PAYLOADS, TOOL_SPECS, OperationalTwin
from backend.modules.m01_twin.tasks.api import router as tasks_router
from backend.modules.m01_twin.twin import telemetry
from backend.modules.m01_twin.twin.handlers import EVENT_HANDLERS
from backend.modules.m01_twin.twin.service import reset_twin_service

MODULE_ID = "M01"
OPENAPI_FILE = "m01-twin.yaml"
API_VERSION = "1.0.0"

router = APIRouter()
router.include_router(tasks_router)
router.include_router(environment_router)
router.include_router(twin_router)

event_handlers = EVENT_HANDLERS
ws_message_types = ["TASK_UPDATE", "TASK_ETA_UPDATED", "MACHINE_STATE_UPDATE", "TWIN_UPDATE"]
permissions = {
    "OPERATOR": ["tasks:execute"],
    "SUPERVISOR_ADMIN": ["tasks:read", "tasks:write", "tasks:assign", "twin:read", "telemetry:ingest", "conditions:write"],
}


async def startup(runtime) -> None:
    reset_twin_service()
    telemetry.reset_cache()


def contract_documents() -> dict[str, dict]:
    """Machine-readable contracts GENERATED from this module's models (scripts/contracts.py export)."""
    docs: dict[str, dict] = {
        "schemas/twin/operational-twin.json": OperationalTwin.model_json_schema(),
    }
    for event_type, model in EVENT_PAYLOADS.items():
        schema = model.model_json_schema()
        schema["description"] = f"Payload of '{event_type}' (producer M01). " + (schema.get("description") or "")
        docs[f"events/m01/{event_type}.v1.json"] = schema
    for name, spec in TOOL_SPECS.items():
        keys, defs = models_json_schema([(spec["input"], "validation"), (spec["output"], "validation")],
                                        ref_template="#/$defs/{model}")
        docs[f"tools/{name}.json"] = {
            "title": name,
            "description": spec["description"],
            "x-tool": {"name": name, "version": "1.0", "owner": "M01", "permissions": ["OPERATOR:self", "SUPERVISOR_ADMIN:site"],
                       "safety_critical": False, "latency_budget_ms": 500},
            "type": "object",
            "required": ["input", "output"],
            "properties": {"input": keys[(spec["input"], "validation")], "output": keys[(spec["output"], "validation")]},
            **defs,
        }
    return docs
