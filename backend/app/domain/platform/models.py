"""M00 master data tables. Single writer: M00 (docs/02-contracts/DATA_OWNERSHIP.md)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, UTCDateTime, new_id, utcnow


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32))
    operator_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)


class UserSiteScope(Base):
    __tablename__ = "user_site_scopes"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    site_id: Mapped[str] = mapped_column(ForeignKey("sites.site_id", ondelete="CASCADE"), primary_key=True)


class Site(Base):
    __tablename__ = "sites"

    site_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    location: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # {"lat":..,"lon":..}
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    configuration: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(16), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)


class Zone(Base):
    __tablename__ = "zones"

    zone_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    site_id: Mapped[str] = mapped_column(ForeignKey("sites.site_id"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    zone_type: Mapped[str] = mapped_column(String(32))  # TASK | HAZARD | RESTRICTED | DISPOSAL | SOFT_GROUND | OTHER
    geometry: Mapped[dict] = mapped_column(JSON)  # GeoJSON Polygon
    status: Mapped[str] = mapped_column(String(16), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)


class Operator(Base):
    __tablename__ = "operators"

    operator_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    site_id: Mapped[str] = mapped_column(ForeignKey("sites.site_id"), index=True)
    experience_level: Mapped[str] = mapped_column(String(16), default="JUNIOR")  # JUNIOR | INTERMEDIATE | SENIOR
    certification_status: Mapped[str] = mapped_column(String(16), default="VALID")  # VALID | EXPIRING | EXPIRED
    preferred_language: Mapped[str] = mapped_column(String(8), default="en")
    status: Mapped[str] = mapped_column(String(16), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)


class Machine(Base):
    __tablename__ = "machines"

    machine_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    site_id: Mapped[str] = mapped_column(ForeignKey("sites.site_id"), index=True)
    machine_type: Mapped[str] = mapped_column(String(32))  # EXCAVATOR | DUMPER | LOADER | DOZER | OTHER
    model: Mapped[str] = mapped_column(String(64))
    serial_number: Mapped[str] = mapped_column(String(64), unique=True)
    engine_hours: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(16), default="ACTIVE")  # ACTIVE | MAINTENANCE | RETIRED
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
