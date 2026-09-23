"""Telemetry read services (history). Ingestion lives in ingest.py."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from app.core.runtime import get_runtime
from app.domain.telemetry.models import MachineTelemetry
from app.domain.telemetry.schemas import TelemetryPoint
from app.domain.twin.service import telemetry_row_to_point


async def history(machine_id: str, since: datetime | None, until: datetime | None, limit: int) -> list[TelemetryPoint]:
    stmt = select(MachineTelemetry).where(MachineTelemetry.machine_id == machine_id)
    if since:
        stmt = stmt.where(MachineTelemetry.ts >= since)
    if until:
        stmt = stmt.where(MachineTelemetry.ts <= until)
    async with get_runtime().db.sessionmaker() as s:
        rows = (await s.scalars(stmt.order_by(MachineTelemetry.ts.desc()).limit(limit))).all()
    return [TelemetryPoint.model_validate(telemetry_row_to_point(r)) for r in reversed(rows)]
