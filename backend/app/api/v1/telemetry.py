"""Telemetry ingestion (simulator / edge forwarder) and history (thin routes)."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.core.exceptions import NotFound
from app.dependencies import Principal, current_principal, require_permission
from app.domain.platform import service as platform
from app.domain.telemetry import service
from app.domain.telemetry.ingest import ingest
from app.domain.telemetry.schemas import IngestResult, TelemetryBatch, TelemetryPoint

router = APIRouter(tags=["telemetry"])


@router.post("/telemetry", response_model=IngestResult, status_code=202)
async def post_telemetry(body: TelemetryBatch, p: Principal = Depends(require_permission("telemetry:ingest"))):
    for machine_id in {i.machine_id for i in body.items}:
        machine = await platform.get_machine(machine_id)
        if machine is not None:
            p.ensure_site(machine.site_id)
    accepted = await ingest(body.items)
    return IngestResult(received=len(body.items), accepted=accepted, duplicates=len(body.items) - accepted)


@router.get("/machines/{machine_id}/telemetry", response_model=list[TelemetryPoint])
async def get_machine_telemetry(machine_id: str, since: datetime | None = Query(None, alias="from"),
                                until: datetime | None = Query(None, alias="to"), limit: int = Query(500, le=5000),
                                p: Principal = Depends(current_principal)):
    machine = await platform.get_machine(machine_id)
    if machine is None:
        raise NotFound("machine", machine_id)
    p.ensure_site(machine.site_id)
    return await service.history(machine_id, since, until, limit)
