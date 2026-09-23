"""Task / assignment / session / pre-check use cases (M01-WP1). All writes to M01 tables happen here."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import Principal
from backend.core.db import new_id, utcnow
from backend.core.errors import AppError, Conflict, Forbidden, InvalidState, NotFound
from backend.core.runtime import get_runtime
from backend.modules.m00_platform import public as platform
from backend.modules.m01_twin.models import (
    Assignment,
    MachineConfirmation,
    MachineTelemetry,
    OperatorEvent,
    PrecheckResult,
    PrecheckTemplate,
    Task,
    TaskSession,
)
from backend.modules.m01_twin.public import AssignmentDTO, SessionDTO, TaskDTO
from backend.modules.m01_twin.tasks import domain
from backend.modules.m01_twin.twin.fusion import iso
from backend.modules.m01_twin.twin.service import SOURCE, twin_service

ACTIVE_SESSION = ("IN_PROGRESS", "PAUSED")


def transition(task: Task, action: str) -> None:
    try:
        task.status = domain.next_status(task.status, action)
    except domain.TransitionError as exc:
        raise InvalidState(str(exc), {"status": exc.status, "action": action,
                                      "allowed": domain.allowed_actions(exc.status)}) from exc


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


# ---------------- assignment ----------------

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


# ---------------- operator day ----------------

async def site_day_bounds(site_id: str, day: date | None) -> tuple[datetime, datetime]:
    site = await platform.get_site(site_id)
    tz = ZoneInfo(site.timezone if site else "UTC")
    day = day or datetime.now(tz).date()
    start = datetime.combine(day, time.min, tzinfo=tz)
    return start, start + timedelta(days=1)


async def tasks_today(operator_id: str, day: date | None) -> list[dict]:
    operator = await platform.get_operator(operator_id)
    if operator is None:
        raise NotFound("operator", operator_id)
    start, end = await site_day_bounds(operator.site_id, day)
    async with get_runtime().db.sessionmaker() as s:
        rows = (await s.execute(
            select(Task, Assignment).join(Assignment, Assignment.task_id == Task.task_id)
            .where(Assignment.operator_id == operator_id, Assignment.status.in_(("ACTIVE", "COMPLETED")))
            .order_by(Task.planned_start))).all()
        out = []
        for task, a in rows:
            in_day = start <= task.planned_start < end or task.status in ACTIVE_SESSION
            if not in_day:
                continue
            session = await s.scalar(select(TaskSession).where(TaskSession.task_id == task.task_id,
                                                               TaskSession.operator_id == operator_id)
                                     .order_by(TaskSession.actual_start.desc()).limit(1))
            out.append({"task": TaskDTO.model_validate(task), "assignment": AssignmentDTO.model_validate(a),
                        "session": SessionDTO.model_validate(session) if session else None,
                        "allowed_actions": [x for x in domain.allowed_actions(task.status)
                                            if x in ("start", "pause", "resume", "complete")]})
        return out


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


# ---------------- pre-check ----------------

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
        if conf is None or not domain.is_recent(conf.confirmed_at, utcnow(), domain.CONFIRMATION_VALID_FOR):
            raise InvalidState("Confirm the machine before the pre-operation check", {"machine_id": machine_id})
        outcome = domain.evaluate_precheck(tpl.items, results)
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


# ---------------- lifecycle ----------------

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
        if conf is None or conf.machine_id != a.machine_id or not domain.is_recent(conf.confirmed_at, now,
                                                                                   domain.CONFIRMATION_VALID_FOR):
            raise InvalidState("Confirm the assigned machine first", {"machine_id": a.machine_id, "step": "machine_confirm"})
        pre = await s.scalar(select(PrecheckResult).where(PrecheckResult.operator_id == op,
                                                          PrecheckResult.machine_id == a.machine_id)
                             .order_by(PrecheckResult.submitted_at.desc()).limit(1))
        if pre is None or not domain.is_recent(pre.submitted_at, now, domain.PRECHECK_VALID_FOR):
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


async def summary(task_id: str) -> dict:
    async with get_runtime().db.sessionmaker() as s:
        task = await get_task_or_404(s, task_id)
        sess = await s.scalar(select(TaskSession).where(TaskSession.task_id == task_id)
                              .order_by(TaskSession.actual_start.desc()).limit(1))
        out = {"task": TaskDTO.model_validate(task), "session": SessionDTO.model_validate(sess) if sess else None,
               "planned_duration_min": round((task.planned_end - task.planned_start).total_seconds() / 60, 1),
               "active_duration_min": None, "pause_duration_min": None, "cycles_done": None, "fuel_used_pct": None,
               "idle_min": None, "finished_by_deadline": None}
        if sess is None:
            return out
        end = sess.actual_end or utcnow()
        out["active_duration_min"] = round(domain.active_seconds(sess.actual_start, end, sess.pause_duration_s,
                                                                 sess.paused_at) / 60, 1)
        out["pause_duration_min"] = round(sess.pause_duration_s / 60, 1)
        q = select(MachineTelemetry).where(MachineTelemetry.machine_id == sess.machine_id,
                                           MachineTelemetry.ts >= sess.actual_start, MachineTelemetry.ts <= end)
        first = await s.scalar(q.order_by(MachineTelemetry.ts.asc()).limit(1))
        last = await s.scalar(q.order_by(MachineTelemetry.ts.desc()).limit(1))
        if first and last:
            base = sess.start_load_cycles if sess.start_load_cycles is not None else first.load_cycles
            out["cycles_done"] = max(0, last.load_cycles - base)
            out["fuel_used_pct"] = round(max(0.0, first.fuel_pct - last.fuel_pct), 2)
            out["idle_min"] = round(max(0.0, last.idle_seconds - first.idle_seconds) / 60, 1)
        if sess.actual_end:
            out["finished_by_deadline"] = sess.actual_end <= task.planned_end
        return out
