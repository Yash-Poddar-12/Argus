"""Task-domain services: shared helpers + task CRUD. All writes to task-domain tables happen in this package."""

from __future__ import annotations

import secrets
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import audit
from app.core.database import utcnow
from app.core.exceptions import AppError, Conflict, Forbidden, InvalidState, NotFound
from app.core.runtime import get_runtime
from app.core.security import Principal
from app.domain.platform import service as platform
from app.domain.tasks import state_machine as sm
from app.domain.tasks.models import Assignment, OperatorEvent, Task
from app.domain.tasks.schemas import TaskCreate, TaskDTO, TaskStatus, TaskUpdate

SOURCE = "tasks"
ACTIVE_SESSION = ("IN_PROGRESS", "PAUSED")


def transition(task: Task, action: str) -> None:
    try:
        task.status = sm.next_status(task.status, action)
    except sm.TransitionError as exc:
        raise InvalidState(str(exc), {"status": exc.status, "action": action,
                                      "allowed": sm.allowed_actions(exc.status)}) from exc


async def get_task_or_404(s: AsyncSession, task_id: str) -> Task:
    task = await s.get(Task, task_id)
    if task is None:
        raise NotFound("task", task_id)
    return task


async def active_assignment(s: AsyncSession, task_id: str) -> Assignment | None:
    return await s.scalar(select(Assignment).where(Assignment.task_id == task_id, Assignment.status == "ACTIVE"))


async def ensure_can_read_task(s: AsyncSession, p: Principal, task: Task) -> None:
    if p.role == "OPERATOR":
        a = await s.scalar(select(Assignment).where(Assignment.task_id == task.task_id,
                                                    Assignment.operator_id == p.operator_id))
        if a is None:
            raise Forbidden("Operators can only see tasks assigned to them")
    else:
        p.ensure_site(task.site_id)


async def emit_task(event_type: str, task: Task, changed: list[str] | None = None) -> None:
    payload = TaskDTO.model_validate(task).model_dump(mode="json")
    if changed is not None:
        payload["changed_fields"] = changed
    await get_runtime().bus.publish(event_type, payload, source_id=SOURCE, site_id=task.site_id)


async def push_task_update(task: Task, action: str, operator_id: str | None, extra: dict | None = None) -> None:
    ws = get_runtime().ws
    data = {"action": action, "task": TaskDTO.model_validate(task).model_dump(mode="json"), **(extra or {})}
    if operator_id:
        await ws.publish(f"operators/{operator_id}", "TASK_UPDATE", data)
    await ws.publish(f"sites/{task.site_id}", "TASK_UPDATE", data)


def _log_operator_event(s: AsyncSession, operator_id: str, event_type: str, details: dict) -> None:
    s.add(OperatorEvent(operator_id=operator_id, event_type=event_type, details=details))


# ---------------- task CRUD ----------------


async def _validate_zone(site_id: str, zone_id: str | None) -> None:
    if zone_id and zone_id not in {z.zone_id for z in await platform.list_zones(site_id)}:
        raise AppError(422, "UNKNOWN_ZONE", f"Zone '{zone_id}' does not exist in site '{site_id}'")


async def create_task(p: Principal, body: TaskCreate) -> Task:
    p.ensure_site(body.site_id)
    if await platform.get_site(body.site_id) is None:
        raise AppError(422, "UNKNOWN_SITE", f"Site '{body.site_id}' does not exist")
    await _validate_zone(body.site_id, body.zone_id)
    async with get_runtime().db.sessionmaker() as s:
        task_id = body.task_id or f"TASK_{utcnow():%y%m%d}_{secrets.token_hex(3).upper()}"
        if await s.get(Task, task_id):
            raise Conflict(f"Task '{task_id}' already exists")
        task = Task(task_id=task_id, created_by=p.user_id, status="PLANNED", **body.model_dump(exclude={"task_id"}))
        s.add(task)
        audit(s, p, "create", "task", task_id, body.site_id)
        await s.commit()
    await emit_task("task.created", task)
    await push_task_update(task, "created", None)
    return task


async def read_task(p: Principal, task_id: str) -> Task:
    async with get_runtime().db.sessionmaker() as s:
        task = await get_task_or_404(s, task_id)
        await ensure_can_read_task(s, p, task)
        return task


async def update_task(p: Principal, task_id: str, body: TaskUpdate) -> Task:
    from app.domain.twin.service import twin_service  # local: twin depends on tasks at import time

    async with get_runtime().db.sessionmaker() as s:
        task = await get_task_or_404(s, task_id)
        p.ensure_site(task.site_id)
        patch = body.model_dump(exclude_unset=True)
        current = await active_assignment(s, task_id)
        affected_operator = current.operator_id if current else None
        if "status" in patch:
            if patch.pop("status") != "CANCELLED":
                raise AppError(422, "VALIDATION_ERROR", "Only status=CANCELLED can be set via PATCH")
            transition(task, "cancel")
            if current:
                current.status = "CANCELLED"
        if "zone_id" in patch:
            await _validate_zone(task.site_id, patch["zone_id"])
        changed = ["status"] if task.status == "CANCELLED" and body.status else []
        for key, value in patch.items():
            if key == "assistance":
                value = [a.model_dump() for a in body.assistance or []]
            elif key == "target":
                value = body.target.model_dump()
            if getattr(task, key) != value:
                setattr(task, key, value)
                changed.append(key)
        if task.planned_end <= task.planned_start:
            raise AppError(422, "VALIDATION_ERROR", "planned_end must be after planned_start")
        audit(s, p, "update", "task", task_id, task.site_id, {"changed": changed})
        await s.commit()
    if changed:
        await emit_task("task.updated", task, changed)
        await push_task_update(task, "updated", affected_operator, {"changed_fields": changed})
        if affected_operator:
            await twin_service().refresh(affected_operator, "task.updated", full=True)
    return task


async def list_site_tasks(p: Principal, site_id: str, status: TaskStatus | None, day: date | None) -> list[Task]:
    from app.domain.tasks.reporting import site_day_bounds

    p.ensure_site(site_id)
    stmt = select(Task).where(Task.site_id == site_id).order_by(Task.planned_start)
    if status:
        stmt = stmt.where(Task.status == status)
    if day:
        start, end = await site_day_bounds(site_id, day)
        stmt = stmt.where(Task.planned_start >= start, Task.planned_start < end)
    async with get_runtime().db.sessionmaker() as s:
        return list((await s.scalars(stmt)).all())
