"""Tool implementations backed by the twin, tasks and environment domain services."""

from __future__ import annotations

from app.copilot.tools.registry import CurrentTaskOutput, MachineHealthOutput, TaskProgressOutput
from app.core.exceptions import AppError, NotFound
from app.domain.environment.schemas import EnvironmentConditions
from app.domain.environment.service import site_conditions
from app.domain.platform import service as platform
from app.domain.tasks.reporting import task_progress
from app.domain.twin import service as twin


async def _machine_state(machine_id: str) -> dict:
    return (await twin.machine_view(machine_id)).model_dump(mode="json")


async def _current_task(operator_id: str) -> dict:
    doc = await twin.twin_service().get_twin(operator_id)
    if doc is None:
        raise NotFound("operator", operator_id)
    return CurrentTaskOutput(operator_id=operator_id, task=doc["state"]["task"]).model_dump(mode="json")


async def _task_progress(task_id: str) -> dict:
    return TaskProgressOutput(**await task_progress(task_id)).model_dump(mode="json")


async def _machine_health(machine_id: str) -> dict:
    if await platform.get_machine(machine_id) is None:
        raise NotFound("machine", machine_id)
    state = await twin.twin_service().machine_state(machine_id)
    if not state:
        return MachineHealthOutput(machine_id=machine_id, health="UNKNOWN", reasons=["No telemetry received yet"]).model_dump(
            mode="json")
    reasons = []
    if state["temperature_c"] >= 95:
        reasons.append(f"Engine temperature {state['temperature_c']:.0f}°C (warning at 95°C, critical at 105°C)")
    if state["fuel_pct"] <= 15:
        reasons.append(f"Fuel at {state['fuel_pct']:.0f}% (warning at 15%, critical at 5%)")
    return MachineHealthOutput(machine_id=machine_id, health=state["health"], temperature_c=state["temperature_c"],
                               fuel_pct=state["fuel_pct"], engine_hours=state["engine_hours"], telemetry_at=state["ts"],
                               reasons=reasons or ["All monitored values within normal range"]).model_dump(mode="json")


async def _weather(site_id: str) -> dict:
    env = await twin.twin_service().environment(site_id, None)
    if env is None:
        raise AppError(404, "NO_CONDITIONS", f"No conditions recorded for site '{site_id}' yet")
    return EnvironmentConditions.model_validate(env).model_dump(mode="json")


async def _site_conditions(site_id: str, zone_id: str | None = None) -> dict:
    zones = [zone_id] if zone_id else [z.zone_id for z in await platform.list_zones(site_id)]
    return (await site_conditions(site_id, zones)).model_dump(mode="json")


IMPLEMENTATIONS = {
    "get_current_machine_state": lambda a: _machine_state(a["machine_id"]),
    "get_current_task": lambda a: _current_task(a["operator_id"]),
    "get_task_progress": lambda a: _task_progress(a["task_id"]),
    "get_machine_health": lambda a: _machine_health(a["machine_id"]),
    "get_weather": lambda a: _weather(a["site_id"]),
    "get_site_conditions": lambda a: _site_conditions(a["site_id"], a.get("zone_id")),
}
