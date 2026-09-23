"""Copilot tool registry: tool specs (input/output models) and dispatch.

Principle (P5): every operational fact the Copilot states comes from a tool result.
Dependency direction: copilot agent -> tool -> domain service -> authoritative data.
Tools never query the database or raw telemetry directly; they call domain services.
Contracts: contracts/tools/<name>.json are GENERATED from TOOL_SPECS (scripts/contracts.py export).
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.core.exceptions import NotFound
from app.domain.environment.schemas import EnvironmentConditions, SiteConditions
from app.domain.tasks.schemas import TaskStatus, TaskTarget
from app.domain.twin.schemas import TwinMachineState, TwinTaskState

# ---------------- tool I/O models ----------------


class MachineIdInput(BaseModel):
    machine_id: str


class OperatorIdInput(BaseModel):
    operator_id: str


class TaskIdInput(BaseModel):
    task_id: str


class SiteIdInput(BaseModel):
    site_id: str


class SiteZoneInput(BaseModel):
    site_id: str
    zone_id: str | None = None


class TaskProgressOutput(BaseModel):
    task_id: str
    status: TaskStatus
    progress_pct: float | None = None
    cycles_done: int | None = None
    target: TaskTarget
    active_minutes: float | None = None
    planned_end: datetime


class MachineHealthOutput(BaseModel):
    machine_id: str
    health: Literal["OK", "WARNING", "CRITICAL", "UNKNOWN"]
    temperature_c: float | None = None
    fuel_pct: float | None = None
    engine_hours: float | None = None
    telemetry_at: datetime | None = None
    reasons: list[str]


class CurrentTaskOutput(BaseModel):
    operator_id: str
    task: TwinTaskState | None = None


# owner = capability whose service provides the authoritative data
TOOL_SPECS: dict[str, dict] = {
    "get_current_machine_state": {"input": MachineIdInput, "output": TwinMachineState, "owner": "twin",
                                  "description": "Live state of a machine from the operational twin."},
    "get_current_task": {"input": OperatorIdInput, "output": CurrentTaskOutput, "owner": "twin",
                         "description": "The operator's current (in-progress, paused or next assigned) task."},
    "get_task_progress": {"input": TaskIdInput, "output": TaskProgressOutput, "owner": "tasks",
                          "description": "Progress of a task: cycles done vs target, active time."},
    "get_machine_health": {"input": MachineIdInput, "output": MachineHealthOutput, "owner": "twin",
                           "description": "Machine health from telemetry (temperature, fuel) with reasons."},
    "get_weather": {"input": SiteIdInput, "output": EnvironmentConditions, "owner": "environment",
                    "description": "Current site-level weather/environment conditions."},
    "get_site_conditions": {"input": SiteZoneInput, "output": SiteConditions, "owner": "environment",
                            "description": "Site and zone conditions plus derived environmental difficulty."},
}


async def call_tool(name: str, arguments: dict) -> dict:
    """Validate input, run the tool, validate output. Returns a JSON-ready dict."""
    from app.copilot.tools.twin_tools import IMPLEMENTATIONS

    spec = TOOL_SPECS.get(name)
    if spec is None:
        raise NotFound("tool", name)
    args = spec["input"].model_validate(arguments).model_dump()
    output = await IMPLEMENTATIONS[name](args)
    return spec["output"].model_validate(output).model_dump(mode="json")
