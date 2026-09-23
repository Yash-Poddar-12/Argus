"""Assigning operators + machines to tasks."""

from __future__ import annotations

from app.core.database import new_id
from app.core.exceptions import AppError, Conflict, InvalidState, NotFound
from app.core.runtime import get_runtime
from app.core.security import Principal
from app.domain.platform import service as platform
from app.domain.tasks.models import Assignment
from app.domain.tasks.schemas import AssignmentDTO
from app.domain.tasks.service import SOURCE, _log_operator_event, active_assignment, get_task_or_404, push_task_update, transition
from app.domain.twin.fusion import iso
from app.domain.twin.service import twin_service


async def assign(p: Principal, task_id: str, operator_id: str, machine_id: str, replace: bool = False) -> Assignment:
    rt = get_runtime()
    operator = await platform.get_operator(operator_id)
    machine = await platform.get_machine(machine_id)
    if operator is None:
        raise NotFound("operator", operator_id)
    if machine is None:
        raise NotFound("machine", machine_id)
    async with rt.db.sessionmaker() as s:
        task = await get_task_or_404(s, task_id)
        p.ensure_site(task.site_id)
        if operator.site_id != task.site_id or machine.site_id != task.site_id:
            raise AppError(422, "SITE_MISMATCH", "Operator, machine and task must belong to the same site",
                           {"task_site": task.site_id, "operator_site": operator.site_id, "machine_site": machine.site_id})
        if operator.status != "ACTIVE" or machine.status != "ACTIVE":
            raise InvalidState("Operator and machine must both be ACTIVE",
                               {"operator_status": operator.status, "machine_status": machine.status})
        previous = await active_assignment(s, task_id)
        if previous is not None:
            if not replace:
                raise Conflict("Task already has an active assignment; pass replace=true to reassign",
                               {"assignment_id": previous.assignment_id})
            previous.status = "CANCELLED"
        transition(task, "assign")
        a = Assignment(assignment_id=new_id(), task_id=task_id, operator_id=operator_id, machine_id=machine_id,
                       site_id=task.site_id, assigned_by=p.user_id)
        s.add(a)
        _log_operator_event(s, operator_id, "task.assigned", {"task_id": task_id, "machine_id": machine_id})
        await s.commit()
        if previous is not None:
            await rt.bus.publish("assignment.updated", {
                "assignment_id": previous.assignment_id, "task_id": task_id, "operator_id": previous.operator_id,
                "machine_id": previous.machine_id, "status": "CANCELLED", "changed_fields": ["status"]},
                source_id=SOURCE, site_id=task.site_id)
        await rt.bus.publish("operator.task.assigned", {
            "assignment_id": a.assignment_id, "task_id": task_id, "operator_id": operator_id, "machine_id": machine_id,
            "site_id": task.site_id, "assigned_by": p.user_id, "planned_start": iso(task.planned_start),
            "planned_end": iso(task.planned_end)}, source_id=SOURCE, site_id=task.site_id)
        assignment_json = AssignmentDTO.model_validate(a).model_dump(mode="json")
        await push_task_update(task, "assigned", operator_id, {"assignment": assignment_json})
    svc = twin_service()
    await svc.refresh(operator_id, "assignment", full=True)
    if previous is not None and previous.operator_id != operator_id:
        await svc.refresh(previous.operator_id, "assignment", full=True)
    return a


async def update_assignment(p: Principal, assignment_id: str, *, status: str | None, machine_id: str | None) -> Assignment:
    rt = get_runtime()
    async with rt.db.sessionmaker() as s:
        a = await s.get(Assignment, assignment_id)
        if a is None:
            raise NotFound("assignment", assignment_id)
        p.ensure_site(a.site_id)
        task = await get_task_or_404(s, a.task_id)
        if a.status != "ACTIVE" or task.status not in ("ASSIGNED",):
            raise InvalidState("Only an ACTIVE assignment of a not-yet-started task can be changed",
                               {"assignment_status": a.status, "task_status": task.status})
        changed = []
        if machine_id and machine_id != a.machine_id:
            machine = await platform.get_machine(machine_id)
            if machine is None:
                raise NotFound("machine", machine_id)
            if machine.site_id != a.site_id:
                raise AppError(422, "SITE_MISMATCH", "Machine belongs to another site")
            a.machine_id = machine_id
            changed.append("machine_id")
        if status == "CANCELLED":
            a.status = "CANCELLED"
            transition(task, "unassign")
            changed.append("status")
        await s.commit()
        if changed:
            await rt.bus.publish("assignment.updated", {
                "assignment_id": a.assignment_id, "task_id": a.task_id, "operator_id": a.operator_id,
                "machine_id": a.machine_id, "status": a.status, "changed_fields": changed},
                source_id=SOURCE, site_id=a.site_id)
            await push_task_update(task, "assignment_updated", a.operator_id,
                                   {"assignment": AssignmentDTO.model_validate(a).model_dump(mode="json")})
    await twin_service().refresh(a.operator_id, "assignment", full=True)
    return a
