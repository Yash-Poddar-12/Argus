"""Event payloads produced by telemetry ingestion. JSON Schemas are GENERATED into contracts/events/telemetry/."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.domain.telemetry.schemas import OperatingMode, TelemetryPoint


class TelemetryReceivedPayload(TelemetryPoint):
    site_id: str


class MachineStateChangedPayload(BaseModel):
    machine_id: str
    site_id: str
    from_mode: OperatingMode | None = None
    to_mode: OperatingMode
    at: datetime


EVENT_PAYLOADS: dict[str, type[BaseModel]] = {
    "machine.telemetry.received": TelemetryReceivedPayload,
    "machine.state.changed": MachineStateChangedPayload,
}
