"""Telemetry time series (Timescale hypertables on Postgres; PK includes ts). Single writer: domain/telemetry."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, UTCDateTime


class MachineTelemetry(Base):
    __tablename__ = "machine_telemetry"

    machine_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    ts: Mapped[datetime] = mapped_column(UTCDateTime, primary_key=True)
    site_id: Mapped[str] = mapped_column(String(32))
    engine_hours: Mapped[float] = mapped_column(Float)
    fuel_pct: Mapped[float] = mapped_column(Float)
    fuel_rate_lph: Mapped[float] = mapped_column(Float)
    load_cycles: Mapped[int] = mapped_column(Integer)
    idle_seconds: Mapped[float] = mapped_column(Float)
    speed_kmh: Mapped[float] = mapped_column(Float)
    rpm: Mapped[float] = mapped_column(Float)
    temperature_c: Mapped[float] = mapped_column(Float)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    operating_mode: Mapped[str] = mapped_column(String(16))
    seatbelt: Mapped[bool] = mapped_column(Boolean)


class MachineStateChange(Base):
    __tablename__ = "machine_state_changes"

    machine_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    ts: Mapped[datetime] = mapped_column(UTCDateTime, primary_key=True)
    from_mode: Mapped[str | None] = mapped_column(String(16), nullable=True)
    to_mode: Mapped[str] = mapped_column(String(16))
