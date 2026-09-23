"""Telemetry ingestion: persist -> fold into machine state -> events -> twin refresh.

Idempotent on (machine_id, ts) so the edge/simulator can replay batches safely.
"""

from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select, tuple_

from app.core.exceptions import AppError
from app.core.runtime import get_runtime
from app.domain.platform import service as platform
from app.domain.tasks.lifecycle import ensure_session_baseline
from app.domain.telemetry.models import MachineStateChange, MachineTelemetry
from app.domain.telemetry.schemas import TelemetryPoint
from app.domain.twin import fusion
from app.domain.twin.service import twin_service

SOURCE = "telemetry"

_machine_site: dict[str, str] = {}


async def _site_of(machine_id: str) -> str:
    if machine_id not in _machine_site:
        machine = await platform.get_machine(machine_id)
        if machine is None:
            raise AppError(422, "UNKNOWN_MACHINE", f"Machine '{machine_id}' is not registered", {"machine_id": machine_id})
        _machine_site[machine_id] = machine.site_id
    return _machine_site[machine_id]


def reset_cache() -> None:
    _machine_site.clear()


async def ingest(points: list[TelemetryPoint]) -> int:
    rt = get_runtime()
    svc = twin_service()
    if not points:
        return 0
    points = sorted(points, key=lambda p: (p.machine_id, p.ts))
    sites = {p.machine_id: await _site_of(p.machine_id) for p in points}

    async with rt.db.sessionmaker() as s:
        keys = [(p.machine_id, p.ts) for p in points]
        existing = set()
        for i in range(0, len(keys), 500):
            chunk = keys[i:i + 500]
            rows = await s.execute(select(MachineTelemetry.machine_id, MachineTelemetry.ts)
                                   .where(tuple_(MachineTelemetry.machine_id, MachineTelemetry.ts).in_(chunk)))
            existing |= {(m, fusion.iso(t)) for m, t in rows}
        fresh = [p for p in points if (p.machine_id, fusion.iso(p.ts)) not in existing]
        if not fresh:
            return 0
        s.add_all(MachineTelemetry(site_id=sites[p.machine_id], **p.model_dump()) for p in fresh)

        mode_changes = []
        touched: dict[str, dict] = {}
        by_machine: dict[str, list[TelemetryPoint]] = defaultdict(list)
        for p in fresh:
            by_machine[p.machine_id].append(p)
        for machine_id, pts in by_machine.items():
            state = touched.get(machine_id) or await svc.machine_state(machine_id)
            for p in pts:
                point = {**p.model_dump(mode="json"), "ts": fusion.iso(p.ts), "site_id": sites[machine_id]}
                prev_mode = (state or {}).get("operating_mode")
                new_state = fusion.machine_state_from_telemetry(state, point)
                if new_state is not state and prev_mode != new_state["operating_mode"]:
                    mode_changes.append((machine_id, prev_mode, new_state["operating_mode"], p.ts))
                    s.add(MachineStateChange(machine_id=machine_id, ts=p.ts, from_mode=prev_mode,
                                             to_mode=new_state["operating_mode"]))
                state = new_state
            touched[machine_id] = state
        await s.commit()

    for p in fresh:
        await rt.bus.publish("machine.telemetry.received", {**p.model_dump(mode="json"), "site_id": sites[p.machine_id]},
                             source_id=SOURCE, site_id=sites[p.machine_id])
    for machine_id, from_mode, to_mode, ts in mode_changes:
        await rt.bus.publish("machine.state.changed", {"machine_id": machine_id, "site_id": sites[machine_id],
                                                       "from_mode": from_mode, "to_mode": to_mode, "at": fusion.iso(ts)},
                             source_id=SOURCE, site_id=sites[machine_id])
    for machine_id, state in touched.items():
        await svc.set_machine_state(machine_id, state)
        public_state = {k: v for k, v in state.items() if k != "idle_window"}
        site_id = sites[machine_id]
        rt.ws.site_of[f"machines/{machine_id}"] = site_id
        await rt.ws.publish(f"machines/{machine_id}", "MACHINE_STATE_UPDATE", public_state)
        await rt.ws.publish(f"sites/{site_id}", "MACHINE_STATE_UPDATE", public_state)
        operator_id = await svc.operator_on_machine(machine_id)
        if operator_id:
            await rt.ws.publish(f"operators/{operator_id}", "MACHINE_STATE_UPDATE", public_state)
            baseline_set = await ensure_session_baseline(machine_id)
            await svc.refresh(operator_id, "telemetry", full=baseline_set)
    return len(fresh)
