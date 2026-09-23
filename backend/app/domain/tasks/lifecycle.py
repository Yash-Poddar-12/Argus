"""Operator shift flow: machine confirmation, pre-operation check, and the guarded task lifecycle."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import new_id, utcnow
from app.core.exceptions import AppError, Conflict, Forbidden, InvalidState, NotFound
from app.core.runtime import get_runtime
from app.core.security import Principal
from app.domain.platform import service as platform
from app.domain.tasks import rules
from app.domain.tasks.models import Assignment, MachineConfirmation, PrecheckResult, PrecheckTemplate, Task, TaskSession
from app.domain.tasks.schemas import SessionDTO
from app.domain.tasks.service import (
    ACTIVE_SESSION,
    SOURCE,
    _log_operator_event,
    active_assignment,
    get_task_or_404,
    push_task_update,
    transition,
)
from app.domain.telemetry.models import MachineTelemetry
from app.domain.twin.fusion import iso
from app.domain.twin.service import twin_service


async def confirm_machine(p: Principal, operator_id: str, machine_id: str) -> MachineConfirmation:
    p.ensure_operator(operator_id)
    machine = await platform.get_machine(machine_id)
    if machine is None:
        raise NotFound("machine", machine_id)
    rt = get_runtime()
    async with rt.db.sessionmaker() as s:
        a = await s.scalar(select(Assignment).where(Assignment.operator_id == operator_id, Assignment.machine_id == machine_id,
                                                    Assignment.status == "ACTIVE"))
        if a is None:
            raise InvalidState("This machine is not assigned to you", {"machine_id": machine_id})
        c = MachineConfirmation(operator_id=operator_id, machine_id=machine_id, confirmed_at=utcnow())
        s.add(c)
        _log_operator_event(s, operator_id, "machine.confirmed", {"machine_id": machine_id})
        await s.commit()
    await rt.bus.publish("session.machine.confirmed", {"operator_id": operator_id, "machine_id": machine_id,
                                                       "machine_type": machine.machine_type,
                                                       "confirmed_at": iso(c.confirmed_at)},
                         source_id=SOURCE, site_id=machine.site_id)
    svc = twin_service()
    await svc.set_operator_on_machine(machine_id, operator_id)
    await svc.refresh(operator_id, "machine_confirmed", full=True)
    return c


async def precheck_template(machine_id: str) -> PrecheckTemplate:
    machine = await platform.get_machine(machine_id)
    if machine is None:
        raise NotFound("machine", machine_id)
    async with get_runtime().db.sessionmaker() as s:
        tpl = await s.scalar(select(PrecheckTemplate).where(PrecheckTemplate.machine_type == machine.machine_type))
        if tpl is None:
            tpl = await s.scalar(select(PrecheckTemplate).where(PrecheckTemplate.machine_type == "DEFAULT"))
        if tpl is None:
            raise NotFound("precheck template", machine.machine_type)
        return tpl


async def submit_precheck(p: Principal, machine_id: str, results: list[dict]) -> PrecheckResult:
    if p.role != "OPERATOR" or not p.operator_id:
        raise Forbidden("Only the operator on the machine can submit a pre-operation check")
    tpl = await precheck_template(machine_id)
    rt = get_runtime()
    async with rt.db.sessionmaker() as s:
        conf = await s.scalar(select(MachineConfirmation).where(MachineConfirmation.operator_id == p.operator_id,
                                                                MachineConfirmation.machine_id == machine_id)
                              .order_by(MachineConfirmation.confirmed_at.desc()).limit(1))
        if conf is None or not rules.is_recent(conf.confirmed_at, utcnow(), rules.CONFIRMATION_VALID_FOR):
            raise InvalidState("Confirm the machine before the pre-operation check", {"machine_id": machine_id})
        outcome = rules.evaluate_precheck(tpl.items, results)
        if outcome.missing_items:
            raise AppError(422, "PRECHECK_INCOMPLETE", "Every checklist item needs an answer",
                           {"missing_items": outcome.missing_items})
        r = PrecheckResult(precheck_id=new_id(), machine_id=machine_id, operator_id=p.operator_id,
                           template_id=tpl.template_id, results=results, passed=outcome.passed,
                           failed_items=outcome.failed_items, submitted_at=utcnow())
        s.add(r)
        _log_operator_event(s, p.operator_id, "precheck.completed", {"machine_id": machine_id, "passed": outcome.passed})
        await s.commit()
    machine = await platform.get_machine(machine_id)
    await rt.bus.publish("session.precheck.completed", {
        "precheck_id": r.precheck_id, "operator_id": p.operator_id, "machine_id": machine_id, "passed": r.passed,
        "failed_items": r.failed_items, "submitted_at": iso(r.submitted_at)}, source_id=SOURCE, site_id=machine.site_id)
    return r


async def _operator_session(s: AsyncSession, operator_id: str, task_id: str) -> TaskSession | None:
    return await s.scalar(select(TaskSession).where(TaskSession.task_id == task_id, TaskSession.operator_id == operator_id,
                                                    TaskSession.status.in_(ACTIVE_SESSION)))


async def _lifecycle_event(action: str, task: Task, sess: TaskSession, at: datetime, cycles_done: int | None = None):
    await get_runtime().bus.publish(f"task.{action}", {
        "session_id": sess.session_id, "task_id": task.task_id, "operator_id": sess.operator_id,
        "machine_id": sess.machine_id, "status": task.status, "at": iso(at), "pause_duration_s": sess.pause_duration_s,
        "cycles_done": cycles_done}, source_id=SOURCE, site_id=task.site_id)


async def _after_lifecycle(task: Task, sess: TaskSession, action: str) -> None:
    await push_task_update(task, action, sess.operator_id, {"session": SessionDTO.model_validate(sess).model_dump(mode="json")})
    svc = twin_service()
    await svc.refresh(sess.operator_id, f"task.{action}", full=True)
    await svc.snapshot(sess.operator_id, f"task.{action}")


async def start(p: Principal, task_id: str) -> tuple[Task, TaskSession]:
    if p.role != "OPERATOR" or not p.operator_id:
        raise Forbidden("Only the assigned operator can start a task")
    op = p.operator_id
    now = utcnow()
    rt = get_runtime()
    async with rt.db.sessionmaker() as s:
        task = await get_task_or_404(s, task_id)
        a = await active_assignment(s, task_id)
        if a is None or a.operator_id != op:
            raise Forbidden("This task is not assigned to you")
        conf = await s.scalar(select(MachineConfirmation).where(MachineConfirmation.operator_id == op)
                              .order_by(MachineConfirmation.confirmed_at.desc()).limit(1))
        if conf is None or conf.machine_id != a.machine_id or not rules.is_recent(conf.confirmed_at, now,
                                                                                   rules.CONFIRMATION_VALID_FOR):
            raise InvalidState("Confirm the assigned machine first", {"machine_id": a.machine_id, "step": "machine_confirm"})
        pre = await s.scalar(select(PrecheckResult).where(PrecheckResult.operator_id == op,
                                                          PrecheckResult.machine_id == a.machine_id)
                             .order_by(PrecheckResult.submitted_at.desc()).limit(1))
        if pre is None or not rules.is_recent(pre.submitted_at, now, rules.PRECHECK_VALID_FOR):
            raise InvalidState("Complete the pre-operation check first", {"machine_id": a.machine_id, "step": "precheck"})
        if not pre.passed:
            raise InvalidState("The last pre-operation check failed; the machine can't be started",
                               {"failed_items": pre.failed_items, "step": "precheck"})
        same_operator_or_machine = (TaskSession.operator_id == op) | (TaskSession.machine_id == a.machine_id)
        busy = await s.scalar(select(TaskSession).where(TaskSession.status.in_(ACTIVE_SESSION), same_operator_or_machine))
        if busy is not None:
            raise Conflict("Finish or pause-complete the other active task first", {"active_task_id": busy.task_id})
        transition(task, "start")
        state = await twin_service().machine_state(a.machine_id)
        sess = TaskSession(session_id=new_id(), task_id=task_id, assignment_id=a.assignment_id, operator_id=op,
                           machine_id=a.machine_id, site_id=task.site_id, status="IN_PROGRESS", actual_start=now,
                           start_load_cycles=state["load_cycles"] if state else None, precheck_id=pre.precheck_id)
        s.add(sess)
        _log_operator_event(s, op, "task.started", {"task_id": task_id})
        await s.commit()
    await twin_service().set_operator_on_machine(sess.machine_id, op)
    await _lifecycle_event("started", task, sess, now)
    await _after_lifecycle(task, sess, "started")
    return task, sess


async def _change(p: Principal, task_id: str, action: str) -> tuple[Task, TaskSession]:
    if p.role != "OPERATOR" or not p.operator_id:
        raise Forbidden(f"Only the operator working the task can {action} it")
    now = utcnow()
    rt = get_runtime()
    cycles_done = None
    async with rt.db.sessionmaker() as s:
        task = await get_task_or_404(s, task_id)
        sess = await _operator_session(s, p.operator_id, task_id)
        if sess is None:
            raise InvalidState(f"No active session for this task to {action}", {"task_status": task.status})
        transition(task, action)
        if action == "pause":
            sess.status, sess.paused_at = "PAUSED", now
        elif action == "resume":
            sess.pause_duration_s += (now - sess.paused_at).total_seconds() if sess.paused_at else 0.0
            sess.status, sess.paused_at = "IN_PROGRESS", None
        elif action == "complete":
            if sess.paused_at:
                sess.pause_duration_s += (now - sess.paused_at).total_seconds()
            sess.status, sess.paused_at, sess.actual_end = "COMPLETED", None, now
            a = await s.get(Assignment, sess.assignment_id)
            a.status = "COMPLETED"
            state = await twin_service().machine_state(sess.machine_id)
            if state and sess.start_load_cycles is not None:
                cycles_done = max(0, state["load_cycles"] - sess.start_load_cycles)
        _log_operator_event(s, p.operator_id, f"task.{action}", {"task_id": task_id})
        await s.commit()
    past = {"pause": "paused", "resume": "resumed", "complete": "completed"}[action]
    await _lifecycle_event(past, task, sess, now, cycles_done)
    await _after_lifecycle(task, sess, past)
    return task, sess


async def pause(p, task_id):
    return await _change(p, task_id, "pause")


async def resume(p, task_id):
    return await _change(p, task_id, "resume")


async def complete(p, task_id):
    return await _change(p, task_id, "complete")


async def ensure_session_baseline(machine_id: str) -> bool:
    """Task started before any telemetry: baseline = first reading at/after the session start."""
    async with get_runtime().db.sessionmaker() as s:
        sess = await s.scalar(select(TaskSession).where(TaskSession.machine_id == machine_id,
                                                        TaskSession.status.in_(ACTIVE_SESSION),
                                                        TaskSession.start_load_cycles.is_(None)))
        if sess is None:
            return False
        first = await s.scalar(select(MachineTelemetry).where(MachineTelemetry.machine_id == machine_id,
                                                              MachineTelemetry.ts >= sess.actual_start)
                               .order_by(MachineTelemetry.ts.asc()).limit(1))
        if first is None:
            return False
        sess.start_load_cycles = first.load_cycles
        await s.commit()
        return True
