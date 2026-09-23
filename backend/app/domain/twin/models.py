"""Twin read models: intelligence slots (filled by other capabilities' events) and snapshots."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, UTCDateTime, new_id, utcnow


class TwinIntelligence(Base):
    """M01's read model of intelligence slots filled by other modules' events (rebuild source)."""

    __tablename__ = "twin_intelligence"

    operator_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    slot: Mapped[str] = mapped_column(String(32), primary_key=True)  # safety | risk | eta | anomaly
    value: Mapped[dict] = mapped_column(JSON)
    source_event_id: Mapped[str] = mapped_column(String(64))
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, onupdate=utcnow)


class TwinSnapshot(Base):
    __tablename__ = "twin_snapshots"

    snapshot_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    operator_id: Mapped[str] = mapped_column(String(32), index=True)
    machine_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    task_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    site_id: Mapped[str] = mapped_column(String(32))
    reason: Mapped[str] = mapped_column(String(32))
    taken_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, index=True)
    twin: Mapped[dict] = mapped_column(JSON)
