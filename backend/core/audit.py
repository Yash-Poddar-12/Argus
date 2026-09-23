"""Audit log helper (M00). Any module may record admin writes through ``audit()``."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.auth import Principal
from backend.core.db import Base, UTCDateTime, new_id, utcnow


class AuditLog(Base):
    __tablename__ = "audit_log"

    audit_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, index=True)
    actor_id: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(64))
    resource: Mapped[str] = mapped_column(String(64))
    resource_id: Mapped[str] = mapped_column(String(64))
    site_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)


def audit(session: AsyncSession, actor: Principal, action: str, resource: str, resource_id: str,
          site_id: str | None = None, details: dict | None = None) -> None:
    """Add an audit row to the caller's session (committed with the caller's transaction)."""
    session.add(AuditLog(actor_id=actor.user_id, action=action, resource=resource, resource_id=resource_id,
                         site_id=site_id, details=details))
