"""Copilot tool implementations owned by M01 (schemas: contracts/tools/<name>.json, generated from TOOL_SPECS).

M07 calls these through ``m01_twin.public.call_tool``; it only relays what they return (grounding, P5).
"""

from __future__ import annotations

from sqlalchemy import select

from backend.core.db import utcnow
from backend.core.errors import AppError, NotFound
from backend.core.runtime import get_runtime
from backend.modules.m00_platform import public as platform
from backend.modules.m01_twin.environment.service import site_conditions
from backend.modules.m01_twin.models import Task, TaskSession
from backend.modules.m01_twin.public import (
    TOOL_SPECS,
    CurrentTaskOutput,
    EnvironmentConditions,
    MachineHealthOutput,
    TaskProgressOutput,
)
from backend.modules.m01_twin.tasks import domain
from backend.modules.m01_twin.twin.service import twin_service


async def _machine_state(machine_id: str) -> dict:
    from backend.modules.m01_twin.api.twin_api import machine_view

    return (await machine_view(machine_id)).model_dump(mode="json")


async def _current_task(operator_id: str) -> dict:
    twin = await twin_service().get_twin(operator_id)
    if twin is None:
        raise NotFound("operator", operator_id)
    return CurrentTaskOutput(operator_id=operator_id, task=twin["state"]["task"]).model_dump(mode="json")


async def _task_progress(task_id: str) -> dict:
    async with get_runtime().db.sessionmaker() as s:
        task = await s.get(Task, task_id)
        if task is None:
            raise NotFound("task", task_id)
        sess = await s.scalar(select(TaskSession).where(TaskSession.task_id == task_id)
                              .order_by(TaskSession.actual_start.desc()).limit(1))
    cycles = active = None
    if sess:
        state = await twin_service().machine_state(sess.machine_id)
        if state and sess.start_load_cycles is not None:
            cycles = max(0, state["load_cycles"] - sess.start_load_cycles)
        end = sess.actual_end or utcnow()
        active = round(domain.active_seconds(sess.actual_start, end, sess.pause_duration_s, sess.paused_at) / 60, 1)
    return TaskProgressOutput(task_id=task_id, status=task.status, target=task.target, cycles_done=cycles,
                              progress_pct=domain.cycles_progress(task.target, cycles), active_minutes=active,
                              planned_end=task.planned_end).model_dump(mode="json")


async def _machine_health(machine_id: str) -> dict:
    if await platform.get_machine(machine_id) is None:
        raise NotFound("machine", machine_id)
    state = await twin_service().machine_state(machine_id)
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
    env = await twin_service().environment(site_id, None)
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


async def run_tool(name: str, arguments: dict) -> dict:
    spec = TOOL_SPECS.get(name)
    if spec is None:
        raise NotFound("tool", name)
    args = spec["input"].model_validate(arguments).model_dump()
    output = await IMPLEMENTATIONS[name](args)
    return spec["output"].model_validate(output).model_dump(mode="json")
