"""Event handlers: other modules' outputs fill the twin's intelligence layer (M01 stores, never computes)."""

from __future__ import annotations

from backend.core.events import Event
from backend.core.runtime import get_runtime
from backend.modules.m01_twin.twin.fusion import intelligence_from_event
from backend.modules.m01_twin.twin.service import twin_service


async def on_intelligence_event(event: Event) -> None:
    operator_id = event.payload.get("operator_id")
    mapped = intelligence_from_event(event.event_type, event.payload, event.timestamp)
    if not operator_id or mapped is None:
        return
    slot, value = mapped
    svc = twin_service()
    await svc.set_intelligence(operator_id, slot, value, event.event_id)
    doc = await svc.refresh(operator_id, f"intelligence.{slot}")
    if slot == "eta" and doc:
        rt = get_runtime()
        data = {"task_id": value.get("task_id"), "operator_id": operator_id, "eta": value}
        await rt.ws.publish(f"operators/{operator_id}", "TASK_ETA_UPDATED", data)
        await rt.ws.publish(f"sites/{doc['site_id']}", "TASK_ETA_UPDATED", data)


async def on_master_data_changed(event: Event) -> None:
    """Operator/machine master data changed: rebuild affected cached twins."""
    svc = twin_service()
    rt = get_runtime()
    if event.event_type.startswith("platform.operator."):
        op = event.payload["operator_id"]
        if await rt.state.get_json(f"twin:ctx:{op}"):
            await svc.refresh(op, "master_data", full=True)
    elif event.event_type.startswith("platform.machine."):
        op = await svc.operator_on_machine(event.payload["machine_id"])
        if op:
            await svc.refresh(op, "master_data", full=True)


EVENT_HANDLERS = [
    ("safety.event.raised", on_intelligence_event),
    ("prediction.task_time.updated", on_intelligence_event),
    ("prediction.risk.updated", on_intelligence_event),
    ("operator.anomaly.detected", on_intelligence_event),
    ("platform.operator.updated", on_master_data_changed),
    ("platform.machine.updated", on_master_data_changed),
]
