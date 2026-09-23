"""Twin service: live twin in the state store, rebuildable from DB + events.

Redis/state key space owned by M01:
  twin:operator:{op}        full OperationalTwin document
  twin:ctx:{op}             cached slow-changing context (operator, machine, task, session, site, familiarity)
  twin:intel:{op}           intelligence slots (also persisted in twin_intelligence)
  twin:machine:{m}          live machine state folded from telemetry
  twin:machine_op:{m}       operator currently on the machine
  twin:env:{site}[:{zone}]  latest environment conditions

"Light" refresh (telemetry, environment, intelligence) reuses twin:ctx; "full" refresh (lifecycle,
assignment, master-data changes, cold cache) re-reads the database.
"""

from __future__ import annotations

import time
from datetime import timedelta

from sqlalchemy import func, select

from backend.core.db import utcnow
from backend.core.logging import get_logger
from backend.core.runtime import get_runtime
from backend.modules.m00_platform import public as platform
from backend.modules.m01_twin.models import (
    Assignment,
    EnvironmentEvent,
    MachineConfirmation,
    MachineTelemetry,
    Task,
    TaskSession,
    TwinIntelligence,
    TwinSnapshot,
)
from backend.modules.m01_twin.tasks.domain import CONFIRMATION_VALID_FOR
from backend.modules.m01_twin.twin import fusion

log = get_logger(__name__)
SOURCE = "m01_twin"
TWIN_EVENT_MIN_INTERVAL_S = 10.0
ACTIVE_MACHINE_WINDOW_S = 300


def telemetry_row_to_point(row: MachineTelemetry) -> dict:
    return {"machine_id": row.machine_id, "site_id": row.site_id, "ts": fusion.iso(row.ts), "engine_hours": row.engine_hours,
            "fuel_pct": row.fuel_pct, "fuel_rate_lph": row.fuel_rate_lph, "load_cycles": row.load_cycles,
            "idle_seconds": row.idle_seconds, "speed_kmh": row.speed_kmh, "rpm": row.rpm, "temperature_c": row.temperature_c,
            "lat": row.lat, "lon": row.lon, "operating_mode": row.operating_mode, "seatbelt": row.seatbelt}


def _task_dict(t: Task) -> dict:
    return {"task_id": t.task_id, "title": t.title, "task_type": t.task_type, "status": t.status, "zone_id": t.zone_id,
            "priority": t.priority, "target": t.target, "planned_start": fusion.iso(t.planned_start),
            "planned_end": fusion.iso(t.planned_end), "site_id": t.site_id}


def _session_dict(s: TaskSession) -> dict:
    return {"session_id": s.session_id, "status": s.status, "actual_start": fusion.iso(s.actual_start),
            "start_load_cycles": s.start_load_cycles, "machine_id": s.machine_id}


class TwinService:
    def __init__(self) -> None:
        self._last_twin_event: dict[str, float] = {}

    @property
    def rt(self):
        return get_runtime()

    # ---------- machine live state ----------

    async def machine_state(self, machine_id: str) -> dict | None:
        state = await self.rt.state.get_json(f"twin:machine:{machine_id}")
        if state is not None:
            return state
        async with self.rt.db.sessionmaker() as s:
            row = await s.scalar(select(MachineTelemetry).where(MachineTelemetry.machine_id == machine_id)
                                 .order_by(MachineTelemetry.ts.desc()).limit(1))
        if row is None:
            return None
        state = fusion.machine_state_from_telemetry(None, telemetry_row_to_point(row))
        await self.rt.state.set_json(f"twin:machine:{machine_id}", state)
        return state

    async def set_machine_state(self, machine_id: str, state: dict) -> None:
        await self.rt.state.set_json(f"twin:machine:{machine_id}", state)

    async def operator_on_machine(self, machine_id: str) -> str | None:
        op = await self.rt.state.get_json(f"twin:machine_op:{machine_id}")
        if op:
            return op
        async with self.rt.db.sessionmaker() as s:
            sess = await s.scalar(select(TaskSession).where(TaskSession.machine_id == machine_id,
                                                            TaskSession.status.in_(("IN_PROGRESS", "PAUSED"))))
            if sess:
                op = sess.operator_id
            else:
                conf = await s.scalar(select(MachineConfirmation).where(MachineConfirmation.machine_id == machine_id)
                                      .order_by(MachineConfirmation.confirmed_at.desc()).limit(1))
                if conf and utcnow() - conf.confirmed_at <= CONFIRMATION_VALID_FOR:
                    op = conf.operator_id
        if op:
            await self.rt.state.set_json(f"twin:machine_op:{machine_id}", op)
        return op

    async def set_operator_on_machine(self, machine_id: str, operator_id: str | None) -> None:
        if operator_id:
            await self.rt.state.set_json(f"twin:machine_op:{machine_id}", operator_id)
        else:
            await self.rt.state.delete(f"twin:machine_op:{machine_id}")

    # ---------- environment ----------

    async def environment(self, site_id: str, zone_id: str | None) -> dict | None:
        keys = [f"twin:env:{site_id}:{zone_id}"] if zone_id else []
        keys.append(f"twin:env:{site_id}")
        for key in keys:
            env = await self.rt.state.get_json(key)
            if env:
                return env
        async with self.rt.db.sessionmaker() as s:
            for zid in ([zone_id] if zone_id else []) + [None]:
                row = await s.scalar(select(EnvironmentEvent).where(
                    EnvironmentEvent.site_id == site_id,
                    EnvironmentEvent.zone_id == zid if zid else EnvironmentEvent.zone_id.is_(None))
                    .order_by(EnvironmentEvent.ts.desc()).limit(1))
                if row:
                    env = {**row.conditions, "zone_id": row.zone_id, "as_of": fusion.iso(row.ts)}
                    await self.rt.state.set_json(f"twin:env:{site_id}" + (f":{zid}" if zid else ""), env)
                    return env
        return None

    # ---------- intelligence ----------

    async def intelligence(self, operator_id: str) -> dict:
        intel = await self.rt.state.get_json(f"twin:intel:{operator_id}")
        if intel is not None:
            return intel
        async with self.rt.db.sessionmaker() as s:
            rows = (await s.scalars(select(TwinIntelligence).where(TwinIntelligence.operator_id == operator_id))).all()
        intel = {r.slot: r.value for r in rows}
        await self.rt.state.set_json(f"twin:intel:{operator_id}", intel)
        return intel

    async def set_intelligence(self, operator_id: str, slot: str, value: dict, source_event_id: str) -> None:
        async with self.rt.db.sessionmaker() as s:
            row = await s.get(TwinIntelligence, (operator_id, slot))
            if row is None:
                s.add(TwinIntelligence(operator_id=operator_id, slot=slot, value=value, source_event_id=source_event_id))
            else:
                row.value, row.source_event_id = value, source_event_id
            await s.commit()
        intel = await self.intelligence(operator_id)
        intel[slot] = value
        await self.rt.state.set_json(f"twin:intel:{operator_id}", intel)

    # ---------- context (slow-changing) ----------

    async def build_context(self, operator_id: str) -> dict | None:
        operator = await platform.get_operator(operator_id)
        if operator is None:
            return None
        now = utcnow()
        async with self.rt.db.sessionmaker() as s:
            session = await s.scalar(select(TaskSession).where(TaskSession.operator_id == operator_id,
                                                               TaskSession.status.in_(("IN_PROGRESS", "PAUSED"))))
            task = assignment = None
            if session:
                task = await s.get(Task, session.task_id)
                machine_id = session.machine_id
            else:
                row = (await s.execute(
                    select(Task, Assignment).join(Assignment, Assignment.task_id == Task.task_id)
                    .where(Assignment.operator_id == operator_id, Assignment.status == "ACTIVE",
                           Task.status.in_(("ASSIGNED", "PLANNED")))
                    .order_by(Task.planned_start).limit(1))).first()
                if row:
                    task, assignment = row
                machine_id = assignment.machine_id if assignment else None
                if machine_id is None:
                    conf = await s.scalar(select(MachineConfirmation).where(MachineConfirmation.operator_id == operator_id)
                                          .order_by(MachineConfirmation.confirmed_at.desc()).limit(1))
                    if conf and now - conf.confirmed_at <= CONFIRMATION_VALID_FOR:
                        machine_id = conf.machine_id
            familiarity = None
            if machine_id:
                n = await s.scalar(select(func.count()).select_from(TaskSession).where(
                    TaskSession.operator_id == operator_id, TaskSession.machine_id == machine_id,
                    TaskSession.status == "COMPLETED"))
                familiarity = fusion.familiarity(n or 0)
        machine = await platform.get_machine(machine_id) if machine_id else None
        zone_type = None
        if task and task.zone_id:
            zone_type = next((z.zone_type for z in await platform.list_zones(operator.site_id) if z.zone_id == task.zone_id),
                             None)
        return {
            "operator": operator.model_dump(mode="json"),
            "machine": machine.model_dump(mode="json") if machine else None,
            "task": _task_dict(task) if task else None,
            "session": _session_dict(session) if session else None,
            "site_ctx": {"zone_id": task.zone_id if task else None, "zone_type": zone_type},
            "familiarity": familiarity,
        }

    async def _active_machines(self, site_id: str) -> int:
        now = utcnow()
        count = 0
        for key in await self.rt.state.keys("twin:machine:*"):
            st = await self.rt.state.get_json(key)
            if st and st.get("site_id") == site_id and st.get("ts"):
                age = (now - fusion.parse_ts(st["ts"])).total_seconds()
                count += age <= ACTIVE_MACHINE_WINDOW_S and st.get("operating_mode") != "OFF"
        return count

    # ---------- twin ----------

    async def get_twin(self, operator_id: str) -> dict | None:
        doc = await self.rt.state.get_json(f"twin:operator:{operator_id}")
        return doc if doc is not None else await self.refresh(operator_id, "rebuild", full=True, publish=False)

    async def refresh(self, operator_id: str, reason: str, *, full: bool = False, publish: bool = True) -> dict | None:
        ctx = None if full else await self.rt.state.get_json(f"twin:ctx:{operator_id}")
        if ctx is None:
            ctx = await self.build_context(operator_id)
            if ctx is None:
                return None
            await self.rt.state.set_json(f"twin:ctx:{operator_id}", ctx)
        operator, machine, task = ctx["operator"], ctx["machine"], ctx["task"]
        site_id = operator["site_id"]
        machine_state = await self.machine_state(machine["machine_id"]) if machine else None
        env = await self.environment(site_id, task.get("zone_id") if task else None)
        site = {**ctx["site_ctx"], "active_machines": await self._active_machines(site_id),
                "nearby_workers": None, "congestion": None}
        doc = fusion.build_twin(now=utcnow(), operator=operator, machine=machine, machine_state=machine_state, task=task,
                                session=ctx["session"], environment=env, site=site,
                                intelligence=await self.intelligence(operator_id), familiarity_level=ctx["familiarity"])
        prev = await self.rt.state.get_json(f"twin:operator:{operator_id}")
        await self.rt.state.set_json(f"twin:operator:{operator_id}", doc)
        ws = self.rt.ws
        ws.site_of[f"operators/{operator_id}"] = site_id
        if machine:
            ws.site_of[f"machines/{machine['machine_id']}"] = site_id
        if publish:
            await ws.publish(f"operators/{operator_id}", "TWIN_UPDATE", doc)
            await ws.publish(f"sites/{site_id}", "TWIN_UPDATE", doc)
            await self._maybe_emit(doc, prev, reason)
        return doc

    async def _maybe_emit(self, doc: dict, prev: dict | None, reason: str) -> None:
        changed = []
        for section in ("machine", "task", "environment", "site", "operator"):
            if (prev or {}).get("state", {}).get(section) != doc["state"].get(section):
                changed.append(f"state.{section}")
        if (prev or {}).get("intelligence") != doc["intelligence"]:
            changed.append("intelligence")
        if not changed:
            return
        now = time.monotonic()
        op = doc["operator_id"]
        telemetry_only = reason == "telemetry"
        if telemetry_only and now - self._last_twin_event.get(op, 0.0) < TWIN_EVENT_MIN_INTERVAL_S:
            return
        self._last_twin_event[op] = now
        await self.rt.bus.publish("twin.updated", {"operator_id": op, "machine_id": doc["machine_id"], "task_id": doc["task_id"],
                                                   "reason": reason, "changed": changed},
                                  source_id=SOURCE, site_id=doc["site_id"])

    async def operators_in_site(self, site_id: str) -> list[str]:
        ops = []
        for key in await self.rt.state.keys("twin:ctx:*"):
            ctx = await self.rt.state.get_json(key)
            if ctx and ctx["operator"]["site_id"] == site_id:
                ops.append(ctx["operator"]["operator_id"])
        return sorted(ops)

    async def snapshot(self, operator_id: str, reason: str) -> None:
        doc = await self.rt.state.get_json(f"twin:operator:{operator_id}")
        if not doc:
            return
        async with self.rt.db.sessionmaker() as s:
            s.add(TwinSnapshot(operator_id=operator_id, machine_id=doc["machine_id"], task_id=doc["task_id"],
                               site_id=doc["site_id"], reason=reason, twin=doc))
            await s.commit()

    async def flush_cache(self) -> None:
        """Drop every M01 key (used to prove rebuildability)."""
        for key in await self.rt.state.keys("twin:*"):
            await self.rt.state.delete(key)


_service: TwinService | None = None


def twin_service() -> TwinService:
    global _service
    if _service is None:
        _service = TwinService()
    return _service


def reset_twin_service() -> None:
    global _service
    _service = None


def stale_after() -> timedelta:
    return timedelta(seconds=ACTIVE_MACHINE_WINDOW_S)
