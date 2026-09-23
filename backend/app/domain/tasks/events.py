"""Event payloads produced by the task domain. JSON Schemas are GENERATED into contracts/events/tasks/."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.domain.tasks.schemas import AssignmentStatus, TaskDTO, TaskStatus


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
}
