"""Task-domain DTOs (request/response shapes; mirrored in contracts/openapi/argus-api.yaml)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import AwareDatetime, BaseModel, Field, model_validator

from app.schemas.common import DTO

TaskType = Literal["EXCAVATION", "TRENCHING", "LOADING", "HAULING", "GRADING", "BACKFILLING", "OTHER"]
TaskStatus = Literal["PLANNED", "ASSIGNED", "IN_PROGRESS", "PAUSED", "COMPLETED", "CANCELLED"]
Priority = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
SessionStatus = Literal["IN_PROGRESS", "PAUSED", "COMPLETED"]
AssignmentStatus = Literal["ACTIVE", "CANCELLED", "COMPLETED"]


class TaskTarget(BaseModel):
    unit: Literal["cycles", "m3", "tonnes", "minutes"]
    value: float = Field(gt=0)


class AssistanceItem(BaseModel):
    kind: Literal["MACHINE", "PERSON", "RESOURCE", "NOTE"]
    resource_id: str | None = None
    note: str | None = None


class TaskDTO(DTO):
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


class AssignmentDTO(DTO):
    assignment_id: str
    task_id: str
    operator_id: str
    machine_id: str
    site_id: str
    assigned_by: str
    status: AssignmentStatus
    created_at: datetime | None = None


class SessionDTO(DTO):
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


class PrecheckTemplateDTO(DTO):
    template_id: str
    machine_type: str
    version: int
    items: list[PrecheckItem]


class PrecheckAnswer(BaseModel):
    item_id: str
    ok: bool
    note: str | None = None


class PrecheckResultDTO(DTO):
    precheck_id: str
    machine_id: str
    operator_id: str
    template_id: str
    passed: bool
    failed_items: list[str]
    results: list[PrecheckAnswer]
    submitted_at: datetime


class TodayTask(BaseModel):
    task: TaskDTO
    assignment: AssignmentDTO
    session: SessionDTO | None = None
    allowed_actions: list[str]


class TaskSummary(BaseModel):
    task: TaskDTO
    session: SessionDTO | None = None
    planned_duration_min: float
    active_duration_min: float | None = None
    pause_duration_min: float | None = None
    cycles_done: int | None = None
    fuel_used_pct: float | None = None
    idle_min: float | None = None
    finished_by_deadline: bool | None = None


# ---------------- requests ----------------


class TaskCreate(BaseModel):
    task_id: str | None = Field(None, pattern=r"^[A-Z0-9_]{2,32}$", description="Optional; generated if omitted")
    site_id: str
    zone_id: str | None = None
    title: str = Field(min_length=1, max_length=160)
    task_type: TaskType
    priority: Priority = "MEDIUM"
    target: TaskTarget
    planned_start: AwareDatetime
    planned_end: AwareDatetime
    assistance: list[AssistanceItem] = []

    @model_validator(mode="after")
    def _window(self):
        if self.planned_end <= self.planned_start:
            raise ValueError("planned_end must be after planned_start")
        return self


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=160)
    zone_id: str | None = None
    priority: Priority | None = None
    target: TaskTarget | None = None
    planned_start: AwareDatetime | None = None
    planned_end: AwareDatetime | None = Field(None, description="The task deadline")
    assistance: list[AssistanceItem] | None = None
    status: TaskStatus | None = Field(None, description="Only CANCELLED is accepted here; lifecycle uses the action endpoints")


class AssignRequest(BaseModel):
    operator_id: str
    machine_id: str
    replace: bool = Field(False, description="Cancel the current active assignment and reassign")


class AssignmentCreate(AssignRequest):
    task_id: str


class AssignmentUpdate(BaseModel):
    status: str | None = Field(None, pattern="^CANCELLED$")
    machine_id: str | None = None


class ConfirmMachineRequest(BaseModel):
    machine_id: str


class ConfirmMachineResponse(BaseModel):
    operator_id: str
    machine_id: str
    confirmed_at: datetime


class PrecheckSubmit(BaseModel):
    results: list[PrecheckAnswer]


class TaskActionResponse(BaseModel):
    task: TaskDTO
    session: SessionDTO
