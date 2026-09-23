"""Environment conditions history (Timescale hypertable on Postgres). Single writer: domain/environment."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, UTCDateTime, new_id, utcnow


class EnvironmentEvent(Base):
    __tablename__ = "environment_events"

    event_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    ts: Mapped[datetime] = mapped_column(UTCDateTime, primary_key=True, default=utcnow)
    site_id: Mapped[str] = mapped_column(String(32), index=True)
    zone_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    conditions: Mapped[dict] = mapped_column(JSON)  # weather, temperature_c, rain_mm_h, visibility, soil
    source: Mapped[str] = mapped_column(String(32), default="MANUAL")
