"""Twin query API + telemetry ingestion endpoint (M01-WP3/WP4)."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import select

from backend.core.auth import Principal, current_principal, require_permission
from backend.core.db import utcnow
from backend.core.errors import NotFound
from backend.core.runtime import get_runtime
from backend.modules.m00_platform import public as platform
from backend.modules.m01_twin.models import Assignment, MachineTelemetry, TaskSession
from backend.modules.m01_twin.public import OperationalTwin, SiteTwin, TelemetryPoint, TwinMachineState
from backend.modules.m01_twin.twin.service import telemetry_row_to_point, twin_service
from backend.modules.m01_twin.twin.telemetry import ingest

router = APIRouter()


class TelemetryBatch(BaseModel):
    items: list[TelemetryPoint] = Field(min_length=1, max_length=5000)


class IngestResult(BaseModel):
    received: int
    accepted: int
    duplicates: int


async def machine_view(machine_id: str) -> TwinMachineState:
    machine = await platform.get_machine(machine_id)
    if machine is None:
        raise NotFound("machine", machine_id)
    state = await twin_service().machine_state(machine_id) or {}
    live = {k: v for k, v in state.items() if k not in ("idle_window", "site_id", "machine_id", "ts")}
    return TwinMachineState(machine_id=machine_id, machine_type=machine.machine_type, model=machine.model,
                            telemetry_at=state.get("ts"), **live)


@router.post("/telemetry", response_model=IngestResult, status_code=202, tags=["telemetry"])
async def post_telemetry(body: TelemetryBatch, p: Principal = Depends(require_permission("telemetry:ingest"))):
    for machine_id in {i.machine_id for i in body.items}:
        machine = await platform.get_machine(machine_id)
        if machine is not None:
            p.ensure_site(machine.site_id)
    accepted = await ingest(body.items)
    return IngestResult(received=len(body.items), accepted=accepted, duplicates=len(body.items) - accepted)


@router.get("/operators/{operator_id}/twin", response_model=OperationalTwin, tags=["twin"])
async def get_operator_twin(operator_id: str, p: Principal = Depends(current_principal)):
    operator = await platform.get_operator(operator_id)
    if operator is None:
        raise NotFound("operator", operator_id)
    p.ensure_operator(operator_id, operator.site_id)
    return await twin_service().get_twin(operator_id)


@router.get("/sites/{site_id}/twin", response_model=SiteTwin, tags=["twin"])
async def get_site_twin(site_id: str, p: Principal = Depends(require_permission("twin:read"))):
    p.ensure_site(site_id)
    rt = get_runtime()
    async with rt.db.sessionmaker() as s:
        ops = set((await s.scalars(select(Assignment.operator_id).where(Assignment.site_id == site_id,
                                                                         Assignment.status == "ACTIVE"))).all())
        ops |= set((await s.scalars(select(TaskSession.operator_id).where(TaskSession.site_id == site_id,
                                                                           TaskSession.status.in_(("IN_PROGRESS", "PAUSED")))
                                    )).all())
        machine_ids = set((await s.scalars(select(MachineTelemetry.machine_id).where(MachineTelemetry.site_id == site_id)
                                           .distinct())).all())
    ops |= set(await twin_service().operators_in_site(site_id))
    twins = [t for op in sorted(ops) if (t := await twin_service().get_twin(op))]
    machines = [await machine_view(m) for m in sorted(machine_ids)]
    return SiteTwin(site_id=site_id, as_of=utcnow(), operators=twins, machines=machines)


@router.get("/machines/{machine_id}/state", response_model=TwinMachineState, tags=["twin"])
async def get_machine_state(machine_id: str, p: Principal = Depends(current_principal)):
    view = await machine_view(machine_id)
    machine = await platform.get_machine(machine_id)
    p.ensure_site(machine.site_id)
    return view


@router.get("/machines/{machine_id}/telemetry", response_model=list[TelemetryPoint], tags=["telemetry"])
async def get_machine_telemetry(machine_id: str, since: datetime | None = Query(None, alias="from"),
                                until: datetime | None = Query(None, alias="to"), limit: int = Query(500, le=5000),
                                p: Principal = Depends(current_principal)):
    machine = await platform.get_machine(machine_id)
    if machine is None:
        raise NotFound("machine", machine_id)
    p.ensure_site(machine.site_id)
    stmt = select(MachineTelemetry).where(MachineTelemetry.machine_id == machine_id)
    if since:
        stmt = stmt.where(MachineTelemetry.ts >= since)
    if until:
        stmt = stmt.where(MachineTelemetry.ts <= until)
    async with get_runtime().db.sessionmaker() as s:
        rows = (await s.scalars(stmt.order_by(MachineTelemetry.ts.desc()).limit(limit))).all()
    return [TelemetryPoint.model_validate(telemetry_row_to_point(r)) for r in reversed(rows)]
