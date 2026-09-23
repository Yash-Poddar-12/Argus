"""Tasks, assignments, machine confirmation, pre-checks and lifecycle (API_CATALOG.md § M01)."""

from __future__ import annotations

import secrets
from datetime import date, datetime

from fastapi import APIRouter, Depends, Query
from pydantic import AwareDatetime, BaseModel, Field, model_validator
from sqlalchemy import select

from backend.core.audit import audit
from backend.core.auth import Principal, current_principal, require_permission
from backend.core.db import utcnow
from backend.core.errors import AppError, Conflict
from backend.core.runtime import get_runtime
from backend.modules.m00_platform import public as platform
from backend.modules.m01_twin.models import Task
from backend.modules.m01_twin.public import (
    AssignmentDTO,
    AssistanceItem,
    PrecheckAnswer,
    PrecheckResultDTO,
    PrecheckTemplateDTO,
    Priority,
    SessionDTO,
    TaskDTO,
    TaskStatus,
    TaskTarget,
    TaskType,
)
from backend.modules.m01_twin.tasks import service
from backend.modules.m01_twin.twin.service import twin_service

router = APIRouter()


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


class TodayTask(BaseModel):
    task: TaskDTO
    assignment: AssignmentDTO
    session: SessionDTO | None = None
    allowed_actions: list[str]


class TaskActionResponse(BaseModel):
    task: TaskDTO
    session: SessionDTO


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


async def _validate_zone(site_id: str, zone_id: str | None) -> None:
    if zone_id and zone_id not in {z.zone_id for z in await platform.list_zones(site_id)}:
        raise AppError(422, "UNKNOWN_ZONE", f"Zone '{zone_id}' does not exist in site '{site_id}'")


@router.post("/tasks", response_model=TaskDTO, status_code=201, tags=["tasks"])
async def create_task(body: TaskCreate, p: Principal = Depends(require_permission("tasks:write"))):
    p.ensure_site(body.site_id)
    if await platform.get_site(body.site_id) is None:
        raise AppError(422, "UNKNOWN_SITE", f"Site '{body.site_id}' does not exist")
    await _validate_zone(body.site_id, body.zone_id)
    rt = get_runtime()
    async with rt.db.sessionmaker() as s:
        task_id = body.task_id or f"TASK_{utcnow():%y%m%d}_{secrets.token_hex(3).upper()}"
        if await s.get(Task, task_id):
            raise Conflict(f"Task '{task_id}' already exists")
        task = Task(task_id=task_id, created_by=p.user_id, status="PLANNED", **body.model_dump(exclude={"task_id"}))
        s.add(task)
        audit(s, p, "create", "task", task_id, body.site_id)
        await s.commit()
    await service.emit_task("task.created", task)
    await service.push_task_update(task, "created", None)
    return TaskDTO.model_validate(task)


@router.get("/tasks/{task_id}", response_model=TaskDTO, tags=["tasks"])
async def get_task(task_id: str, p: Principal = Depends(current_principal)):
    async with get_runtime().db.sessionmaker() as s:
        task = await service.get_task_or_404(s, task_id)
        await service.ensure_can_read_task(s, p, task)
        return TaskDTO.model_validate(task)


@router.patch("/tasks/{task_id}", response_model=TaskDTO, tags=["tasks"])
async def update_task(task_id: str, body: TaskUpdate, p: Principal = Depends(require_permission("tasks:write"))):
    rt = get_runtime()
    async with rt.db.sessionmaker() as s:
        task = await service.get_task_or_404(s, task_id)
        p.ensure_site(task.site_id)
        patch = body.model_dump(exclude_unset=True)
        current = await service.active_assignment(s, task_id)
        affected_operator = current.operator_id if current else None
        if "status" in patch:
            if patch.pop("status") != "CANCELLED":
                raise AppError(422, "VALIDATION_ERROR", "Only status=CANCELLED can be set via PATCH")
            service.transition(task, "cancel")
            a = await service.active_assignment(s, task_id)
            if a:
                a.status = "CANCELLED"
        if "zone_id" in patch:
            await _validate_zone(task.site_id, patch["zone_id"])
        changed = ["status"] if task.status == "CANCELLED" and body.status else []
        for key, value in patch.items():
            value = value.model_dump() if hasattr(value, "model_dump") else value
            if key == "assistance":
                value = [a.model_dump() if hasattr(a, "model_dump") else a for a in body.assistance or []]
            if key == "target":
                value = body.target.model_dump()
            if getattr(task, key) != value:
                setattr(task, key, value)
                changed.append(key)
        if task.planned_end <= task.planned_start:
            raise AppError(422, "VALIDATION_ERROR", "planned_end must be after planned_start")
        audit(s, p, "update", "task", task_id, task.site_id, {"changed": changed})
        await s.commit()
    if changed:
        await service.emit_task("task.updated", task, changed)
        op = affected_operator
        await service.push_task_update(task, "updated", op, {"changed_fields": changed})
        if op:
            await twin_service().refresh(op, "task.updated", full=True)
    return TaskDTO.model_validate(task)


@router.get("/sites/{site_id}/tasks", response_model=list[TaskDTO], tags=["tasks"])
async def list_site_tasks(site_id: str, status: TaskStatus | None = None, day: date | None = Query(None, alias="date"),
                          p: Principal = Depends(require_permission("tasks:read"))):
    p.ensure_site(site_id)
    stmt = select(Task).where(Task.site_id == site_id).order_by(Task.planned_start)
    if status:
        stmt = stmt.where(Task.status == status)
    if day:
        start, end = await service.site_day_bounds(site_id, day)
        stmt = stmt.where(Task.planned_start >= start, Task.planned_start < end)
    async with get_runtime().db.sessionmaker() as s:
        return [TaskDTO.model_validate(t) for t in (await s.scalars(stmt)).all()]


@router.post("/tasks/{task_id}/assign", response_model=AssignmentDTO, status_code=201, tags=["assignments"])
async def assign_task(task_id: str, body: AssignRequest, p: Principal = Depends(require_permission("tasks:assign"))):
    return AssignmentDTO.model_validate(await service.assign(p, task_id, body.operator_id, body.machine_id, body.replace))


@router.post("/assignments", response_model=AssignmentDTO, status_code=201, tags=["assignments"])
async def create_assignment(body: AssignmentCreate, p: Principal = Depends(require_permission("tasks:assign"))):
    return AssignmentDTO.model_validate(await service.assign(p, body.task_id, body.operator_id, body.machine_id, body.replace))


@router.patch("/assignments/{assignment_id}", response_model=AssignmentDTO, tags=["assignments"])
async def patch_assignment(assignment_id: str, body: AssignmentUpdate,
                           p: Principal = Depends(require_permission("tasks:assign"))):
    return AssignmentDTO.model_validate(await service.update_assignment(p, assignment_id, status=body.status,
                                                                        machine_id=body.machine_id))


@router.get("/operators/{operator_id}/tasks/today", response_model=list[TodayTask], tags=["operator-day"])
async def operator_tasks_today(operator_id: str, day: date | None = Query(None, alias="date"),
                               p: Principal = Depends(current_principal)):
    operator = await platform.get_operator(operator_id)
    p.ensure_operator(operator_id, operator.site_id if operator else None)
    return await service.tasks_today(operator_id, day)


@router.post("/operators/{operator_id}/machine/confirm", response_model=ConfirmMachineResponse, tags=["operator-day"])
async def confirm_machine(operator_id: str, body: ConfirmMachineRequest,
                          p: Principal = Depends(require_permission("tasks:execute"))):
    c = await service.confirm_machine(p, operator_id, body.machine_id)
    return ConfirmMachineResponse(operator_id=c.operator_id, machine_id=c.machine_id, confirmed_at=c.confirmed_at)


@router.get("/machines/{machine_id}/precheck", response_model=PrecheckTemplateDTO, tags=["precheck"])
async def get_precheck(machine_id: str, p: Principal = Depends(current_principal)):
    machine = await platform.get_machine(machine_id)
    p.ensure_site(machine.site_id if machine else None)
    return PrecheckTemplateDTO.model_validate(await service.precheck_template(machine_id))


@router.post("/machines/{machine_id}/precheck", response_model=PrecheckResultDTO, status_code=201, tags=["precheck"])
async def post_precheck(machine_id: str, body: PrecheckSubmit, p: Principal = Depends(require_permission("tasks:execute"))):
    r = await service.submit_precheck(p, machine_id, [a.model_dump() for a in body.results])
    return PrecheckResultDTO.model_validate(r)


def _action(fn):
    async def endpoint(task_id: str, p: Principal = Depends(require_permission("tasks:execute"))):
        task, sess = await fn(p, task_id)
        return TaskActionResponse(task=TaskDTO.model_validate(task), session=SessionDTO.model_validate(sess))
    return endpoint


for _name, _fn in (("start", service.start), ("pause", service.pause), ("resume", service.resume),
                   ("complete", service.complete)):
    router.add_api_route(f"/tasks/{{task_id}}/{_name}", _action(_fn), methods=["POST"], response_model=TaskActionResponse,
                         tags=["task-lifecycle"], name=f"{_name}_task", summary=f"{_name.title()} task")


@router.get("/tasks/{task_id}/summary", response_model=TaskSummary, tags=["task-lifecycle"])
async def task_summary(task_id: str, p: Principal = Depends(current_principal)):
    async with get_runtime().db.sessionmaker() as s:
        task = await service.get_task_or_404(s, task_id)
        await service.ensure_can_read_task(s, p, task)
    return await service.summary(task_id)
