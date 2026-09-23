"""Task-domain tables (single writer: domain/tasks). Cross-domain references are plain IDs."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, UTCDateTime, new_id, utcnow


class Task(Base):
    __tablename__ = "tasks"

    task_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    site_id: Mapped[str] = mapped_column(String(32), index=True)
    zone_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    title: Mapped[str] = mapped_column(String(160))
    task_type: Mapped[str] = mapped_column(String(32))
    priority: Mapped[str] = mapped_column(String(16), default="MEDIUM")
    target: Mapped[dict] = mapped_column(JSON)  # {"unit": "cycles", "value": 50}
    planned_start: Mapped[datetime] = mapped_column(UTCDateTime)
    planned_end: Mapped[datetime] = mapped_column(UTCDateTime)
    assistance: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(16), default="PLANNED", index=True)
    created_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, onupdate=utcnow)


class Assignment(Base):
    __tablename__ = "assignments"

    assignment_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.task_id"), index=True)
    operator_id: Mapped[str] = mapped_column(String(32), index=True)
    machine_id: Mapped[str] = mapped_column(String(32), index=True)
    site_id: Mapped[str] = mapped_column(String(32))
    assigned_by: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16), default="ACTIVE")  # ACTIVE | CANCELLED | COMPLETED
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, onupdate=utcnow)


class TaskSession(Base):
    __tablename__ = "task_sessions"

    session_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.task_id"), index=True)
    assignment_id: Mapped[str] = mapped_column(ForeignKey("assignments.assignment_id"))
    operator_id: Mapped[str] = mapped_column(String(32), index=True)
    machine_id: Mapped[str] = mapped_column(String(32), index=True)
    site_id: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16))  # IN_PROGRESS | PAUSED | COMPLETED
    actual_start: Mapped[datetime] = mapped_column(UTCDateTime)
    actual_end: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    paused_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    pause_duration_s: Mapped[float] = mapped_column(Float, default=0.0)
    start_load_cycles: Mapped[int | None] = mapped_column(Integer, nullable=True)
    precheck_id: Mapped[str | None] = mapped_column(String(36), nullable=True)


class MachineConfirmation(Base):
    __tablename__ = "machine_confirmations"

    confirmation_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    operator_id: Mapped[str] = mapped_column(String(32), index=True)
    machine_id: Mapped[str] = mapped_column(String(32))
    confirmed_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)


class PrecheckTemplate(Base):
    __tablename__ = "precheck_templates"

    template_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    machine_type: Mapped[str] = mapped_column(String(32), unique=True)
    items: Mapped[list] = mapped_column(JSON)  # [{"item_id", "label", "critical"}]
    version: Mapped[int] = mapped_column(Integer, default=1)


class PrecheckResult(Base):
    __tablename__ = "precheck_results"

    precheck_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    machine_id: Mapped[str] = mapped_column(String(32), index=True)
    operator_id: Mapped[str] = mapped_column(String(32), index=True)
    template_id: Mapped[str] = mapped_column(String(32))
    results: Mapped[list] = mapped_column(JSON)  # [{"item_id", "ok", "note"}]
    passed: Mapped[bool] = mapped_column(Boolean)
    failed_items: Mapped[list] = mapped_column(JSON, default=list)
    submitted_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)


class OperatorEvent(Base):
    __tablename__ = "operator_events"

    event_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    ts: Mapped[datetime] = mapped_column(UTCDateTime, primary_key=True, default=utcnow)
    operator_id: Mapped[str] = mapped_column(String(32), index=True)
    event_type: Mapped[str] = mapped_column(String(64))
    details: Mapped[dict] = mapped_column(JSON, default=dict)
