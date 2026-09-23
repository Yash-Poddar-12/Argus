"""M01 public facade: the only file other modules may import from m01_twin.

* DTOs and event payload models (their JSON Schemas are GENERATED into contracts/ by
  ``scripts/contracts.py export``, so code and contract can't drift).
* Twin accessors, telemetry ingestion and the pure fusion helpers (M09 builds modified twins with them).
* Copilot tool implementations (schemas in contracts/tools/, see TOOL_SPECS).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.modules.m00_platform.public import GeoPoint

TaskType = Literal["EXCAVATION", "TRENCHING", "LOADING", "HAULING", "GRADING", "BACKFILLING", "OTHER"]
TaskStatus = Literal["PLANNED", "ASSIGNED", "IN_PROGRESS", "PAUSED", "COMPLETED", "CANCELLED"]
Priority = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
SessionStatus = Literal["IN_PROGRESS", "PAUSED", "COMPLETED"]
AssignmentStatus = Literal["ACTIVE", "CANCELLED", "COMPLETED"]
OperatingMode = Literal["DIGGING", "SWINGING", "DUMPING", "LOADING", "HAULING", "RETURNING", "TRAVELLING", "IDLE", "OFF"]
Level = Literal["LOW", "MEDIUM", "HIGH"]


class _DTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------------- tasks ----------------

class TaskTarget(BaseModel):
    unit: Literal["cycles", "m3", "tonnes", "minutes"]
    value: float = Field(gt=0)


class AssistanceItem(BaseModel):
    kind: Literal["MACHINE", "PERSON", "RESOURCE", "NOTE"]
    resource_id: str | None = None
    note: str | None = None


class TaskDTO(_DTO):
    task_id: str
    site_id: str
    zone_id: str | None = None
    title: str
    task_type: TaskType
    priority: Priority
    target: TaskTarget
    planned_start: datetime
    planned_end: datetime
    assistance: list[AssistanceItem] = []
    status: TaskStatus
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AssignmentDTO(_DTO):
    assignment_id: str
    task_id: str
    operator_id: str
    machine_id: str
    site_id: str
    assigned_by: str
    status: AssignmentStatus
    created_at: datetime | None = None


class SessionDTO(_DTO):
    session_id: str
    task_id: str
    assignment_id: str
    operator_id: str
    machine_id: str
    status: SessionStatus
    actual_start: datetime
    actual_end: datetime | None = None
    paused_at: datetime | None = None
    pause_duration_s: float = 0.0
    start_load_cycles: int | None = None


class PrecheckItem(BaseModel):
    item_id: str
    label: str
    critical: bool = False


class PrecheckTemplateDTO(_DTO):
    template_id: str
    machine_type: str
    version: int
    items: list[PrecheckItem]


class PrecheckAnswer(BaseModel):
    item_id: str
    ok: bool
    note: str | None = None


class PrecheckResultDTO(_DTO):
    precheck_id: str
    machine_id: str
    operator_id: str
    template_id: str
    passed: bool
    failed_items: list[str]
    results: list[PrecheckAnswer]
    submitted_at: datetime


# ---------------- telemetry / environment ----------------

class TelemetryPoint(BaseModel):
    machine_id: str
    ts: datetime
    engine_hours: float = Field(ge=0)
    fuel_pct: float = Field(ge=0, le=100)
    fuel_rate_lph: float = Field(ge=0)
    load_cycles: int = Field(ge=0, description="Cumulative load-cycle counter")
    idle_seconds: float = Field(ge=0, description="Cumulative idle seconds counter")
    speed_kmh: float = Field(ge=0)
    rpm: float = Field(ge=0)
    temperature_c: float
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    operating_mode: OperatingMode
    seatbelt: bool

    @field_validator("ts")
    @classmethod
    def _utc(cls, v: datetime) -> datetime:
        return v.replace(tzinfo=UTC) if v.tzinfo is None else v.astimezone(UTC)


class EnvironmentConditions(BaseModel):
    weather: Literal["CLEAR", "CLOUDY", "RAIN", "STORM", "FOG"] = "CLEAR"
    temperature_c: float = 30.0
    rain_mm_h: float = Field(0.0, ge=0)
    visibility: Literal["GOOD", "MODERATE", "POOR"] = "GOOD"
    soil: Literal["DRY", "WET", "MUD", "ROCKY"] = "DRY"


# ---------------- twin ----------------

class TwinOperatorState(BaseModel):
    name: str
    status: str
    experience_level: str
    certification_status: str
    preferred_language: str = "en"
    machine_familiarity: Level | None = None


class TwinMachineState(BaseModel):
    machine_id: str
    machine_type: str
    model: str
    telemetry_at: datetime | None = None
    operating_mode: OperatingMode | None = None
    fuel_pct: float | None = None
    fuel_rate_lph: float | None = None
    speed_kmh: float | None = None
    rpm: float | None = None
    engine_hours: float | None = None
    load_cycles: int | None = None
    idle_seconds: float | None = None
    temperature_c: float | None = None
    seatbelt: bool | None = None
    location: GeoPoint | None = None
    health: Literal["OK", "WARNING", "CRITICAL"] | None = None


class TwinTaskState(BaseModel):
    task_id: str
    title: str
    task_type: TaskType
    status: TaskStatus
    zone_id: str | None = None
    priority: Priority
    target: TaskTarget
    cycles_done: int | None = None
    progress_pct: float | None = None
    planned_start: datetime
    planned_end: datetime
    session_id: str | None = None
    actual_start: datetime | None = None


class TwinEnvironment(EnvironmentConditions):
    zone_id: str | None = None
    as_of: datetime | None = None


class TwinSiteContext(BaseModel):
    zone_id: str | None = None
    zone_type: str | None = None
    active_machines: int = 0
    nearby_workers: int | None = Field(None, description="Filled from M04 hazard mesh; null until then")
    congestion: Level | None = Field(None, description="Filled from M05 site intelligence; null until then")


class TwinState(BaseModel):
    operator: TwinOperatorState
    machine: TwinMachineState | None = None
    task: TwinTaskState | None = None
    environment: TwinEnvironment | None = None
    site: TwinSiteContext | None = None


class TwinIntelligence(BaseModel):
    """Slots filled by other modules' events. Nullable: the twin is valid without M04/M06."""

    safety: dict | None = Field(None, description="From M04 safety.event.raised")
    risk: dict | None = Field(None, description="From M06 prediction.risk.updated (evidence only)")
    eta: dict | None = Field(None, description="From M06 prediction.task_time.updated")
    anomaly: dict | None = Field(None, description="From M06 operator.anomaly.detected")
    productivity: dict | None = None
    environmental_difficulty: Level | None = None


class TwinFreshness(BaseModel):
    telemetry_age_s: float | None = None
    environment_age_s: float | None = None


class OperationalTwin(BaseModel):
    """Human-Machine Operational Twin: state layer + intelligence layer (master §4)."""

    operator_id: str
    machine_id: str | None = None
    task_id: str | None = None
    site_id: str
    as_of: datetime
    state: TwinState
    intelligence: TwinIntelligence
    freshness: TwinFreshness


class SiteTwin(BaseModel):
    site_id: str
    as_of: datetime
    operators: list[OperationalTwin]
    machines: list[TwinMachineState]


class SiteConditions(BaseModel):
    site_id: str
    site: TwinEnvironment | None = None
    zones: dict[str, TwinEnvironment] = {}
    environmental_difficulty: Level | None = None


# ---------------- event payloads (schemas generated into contracts/events/m01/) ----------------

class TaskEventPayload(TaskDTO):
    changed_fields: list[str] | None = None


class TaskAssignedPayload(BaseModel):
    assignment_id: str
    task_id: str
    operator_id: str
    machine_id: str
    site_id: str
    assigned_by: str
    planned_start: datetime
    planned_end: datetime


class AssignmentUpdatedPayload(BaseModel):
    assignment_id: str
    task_id: str
    operator_id: str
    machine_id: str
    status: AssignmentStatus
    changed_fields: list[str]


class MachineConfirmedPayload(BaseModel):
    operator_id: str
    machine_id: str
    machine_type: str
    confirmed_at: datetime


class PrecheckCompletedPayload(BaseModel):
    precheck_id: str
    operator_id: str
    machine_id: str
    passed: bool
    failed_items: list[str]
    submitted_at: datetime


class TaskLifecyclePayload(BaseModel):
    session_id: str
    task_id: str
    operator_id: str
    machine_id: str
    status: TaskStatus
    at: datetime
    pause_duration_s: float = 0.0
    cycles_done: int | None = None


class MachineStateChangedPayload(BaseModel):
    machine_id: str
    site_id: str
    from_mode: OperatingMode | None = None
    to_mode: OperatingMode
    at: datetime


class TelemetryReceivedPayload(TelemetryPoint):
    site_id: str


class EnvironmentUpdatedPayload(EnvironmentConditions):
    site_id: str
    zone_id: str | None = None
    source: str = "MANUAL"
    as_of: datetime


class TwinUpdatedPayload(BaseModel):
    operator_id: str
    machine_id: str | None = None
    task_id: str | None = None
    reason: str
    changed: list[str] = Field(description="Top-level twin sections that changed, e.g. state.machine")


EVENT_PAYLOADS: dict[str, type[BaseModel]] = {
    "task.created": TaskEventPayload,
    "task.updated": TaskEventPayload,
    "operator.task.assigned": TaskAssignedPayload,
    "assignment.updated": AssignmentUpdatedPayload,
    "session.machine.confirmed": MachineConfirmedPayload,
    "session.precheck.completed": PrecheckCompletedPayload,
    "task.started": TaskLifecyclePayload,
    "task.paused": TaskLifecyclePayload,
    "task.resumed": TaskLifecyclePayload,
    "task.completed": TaskLifecyclePayload,
    "machine.telemetry.received": TelemetryReceivedPayload,
    "machine.state.changed": MachineStateChangedPayload,
    "environment.conditions.updated": EnvironmentUpdatedPayload,
    "twin.updated": TwinUpdatedPayload,
}


# ---------------- Copilot tools (schemas generated into contracts/tools/) ----------------

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


TOOL_SPECS: dict[str, dict] = {
    "get_current_machine_state": {"input": MachineIdInput, "output": TwinMachineState,
                                  "description": "Live state of a machine from the operational twin."},
    "get_current_task": {"input": OperatorIdInput, "output": CurrentTaskOutput,
                         "description": "The operator's current (in-progress, paused or next assigned) task."},
    "get_task_progress": {"input": TaskIdInput, "output": TaskProgressOutput,
                          "description": "Progress of a task: cycles done vs target, active time."},
    "get_machine_health": {"input": MachineIdInput, "output": MachineHealthOutput,
                           "description": "Machine health from telemetry (temperature, fuel) with reasons."},
    "get_weather": {"input": SiteIdInput, "output": EnvironmentConditions,
                    "description": "Current site-level weather/environment conditions."},
    "get_site_conditions": {"input": SiteZoneInput, "output": SiteConditions,
                            "description": "Site and zone conditions plus derived environmental difficulty."},
}


# ---------------- facade functions (lazy imports keep this module import-light) ----------------

async def get_operator_twin(operator_id: str) -> OperationalTwin | None:
    from backend.modules.m01_twin.twin.service import twin_service

    doc = await twin_service().get_twin(operator_id)
    return OperationalTwin.model_validate(doc) if doc else None


async def ingest_telemetry(points: list[TelemetryPoint]) -> int:
    """In-process ingestion (simulator embedded mode, edge forwarder in the same process)."""
    from backend.modules.m01_twin.twin.telemetry import ingest

    return await ingest(points)


async def call_tool(name: str, arguments: dict) -> dict:
    """Execute one of TOOL_SPECS; returns output as JSON-ready dict (validated against the spec)."""
    from backend.modules.m01_twin.api.tools import run_tool

    return await run_tool(name, arguments)


def fuse_twin(**kwargs) -> dict:
    """Pure fusion (no I/O) for counterfactual twins (M09). See twin/fusion.py build_twin()."""
    from backend.modules.m01_twin.twin.fusion import build_twin

    return build_twin(**kwargs)
