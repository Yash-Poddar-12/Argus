"""Read-side task queries: an operator's day and post-task summaries."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select

from app.core.database import utcnow
from app.core.exceptions import NotFound
from app.core.runtime import get_runtime
from app.domain.platform import service as platform
from app.domain.tasks import rules
from app.domain.tasks import state_machine as sm
from app.domain.tasks.models import Assignment, Task, TaskSession
from app.domain.tasks.schemas import AssignmentDTO, SessionDTO, TaskDTO
from app.domain.tasks.service import ACTIVE_SESSION, get_task_or_404
from app.domain.telemetry.models import MachineTelemetry


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
                        "allowed_actions": [x for x in sm.allowed_actions(task.status)
                                            if x in ("start", "pause", "resume", "complete")]})
        return out


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
        out["active_duration_min"] = round(rules.active_seconds(sess.actual_start, end, sess.pause_duration_s,
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


async def task_progress(task_id: str) -> dict:
    """Progress of a task: cycles vs target and active minutes (used by the Copilot tool)."""
    from app.domain.twin.service import twin_service

    async with get_runtime().db.sessionmaker() as s:
        task = await s.get(Task, task_id)
        if task is None:
            raise NotFound("task", task_id)
        sess = await s.scalar(select(TaskSession).where(TaskSession.task_id == task_id)
                              .order_by(TaskSession.actual_start.desc()).limit(1))
    cycles = active = None
    if sess:
        state = await twin_service().machine_state(sess.machine_id)
        if state and sess.start_load_cycles is not None:
            cycles = max(0, state["load_cycles"] - sess.start_load_cycles)
        end = sess.actual_end or utcnow()
        active = round(rules.active_seconds(sess.actual_start, end, sess.pause_duration_s, sess.paused_at) / 60, 1)
    return {"task_id": task_id, "status": task.status, "target": task.target, "cycles_done": cycles,
            "progress_pct": rules.cycles_progress(task.target, cycles), "active_minutes": active,
            "planned_end": task.planned_end}
