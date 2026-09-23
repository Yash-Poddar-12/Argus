"""Human-Machine Operational Twin document (contracts/schemas/twin/operational-twin.json is generated from here)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.domain.environment.schemas import Level, TwinEnvironment
from app.domain.tasks.schemas import Priority, TaskStatus, TaskTarget, TaskType
from app.domain.telemetry.schemas import OperatingMode
from app.schemas.common import GeoPoint


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


class TwinSiteContext(BaseModel):
    zone_id: str | None = None
    zone_type: str | None = None
    active_machines: int = 0
    nearby_workers: int | None = Field(None, description="Filled from the IoT hazard mesh; null until then")
    congestion: Level | None = Field(None, description="Filled from site operational intelligence; null until then")


class TwinState(BaseModel):
    operator: TwinOperatorState
    machine: TwinMachineState | None = None
    task: TwinTaskState | None = None
    environment: TwinEnvironment | None = None
    site: TwinSiteContext | None = None


class TwinIntelligence(BaseModel):
    """Slots filled by other capabilities' events. Nullable: the twin is valid without them."""

    safety: dict | None = Field(None, description="From safety.event.raised")
    risk: dict | None = Field(None, description="From prediction.risk.updated (evidence only)")
    eta: dict | None = Field(None, description="From prediction.task_time.updated")
    anomaly: dict | None = Field(None, description="From operator.anomaly.detected")
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
