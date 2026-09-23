"""Machine telemetry shapes."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

OperatingMode = Literal["DIGGING", "SWINGING", "DUMPING", "LOADING", "HAULING", "RETURNING", "TRAVELLING", "IDLE", "OFF"]


class TelemetryPoint(BaseModel):
    machine_id: str
    ts: datetime
    engine_hours: float = Field(ge=0)
    fuel_pct: float = Field(ge=0, le=100)
    fuel_rate_lph: float = Field(ge=0)
    load_cycles: int = Field(ge=0, description="Cumulative load-cycle counter")
    idle_seconds: float = Field(ge=0, description="Cumulative idle seconds counter")
    speed_kmh: float = Field(ge=0)
    rpm: float = Field(ge=0)
    temperature_c: float
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    operating_mode: OperatingMode
    seatbelt: bool

    @field_validator("ts")
    @classmethod
    def _utc(cls, v: datetime) -> datetime:
        return v.replace(tzinfo=UTC) if v.tzinfo is None else v.astimezone(UTC)


class TelemetryBatch(BaseModel):
    items: list[TelemetryPoint] = Field(min_length=1, max_length=5000)


class IngestResult(BaseModel):
    received: int
    accepted: int
    duplicates: int
