"""M00 public facade: the only file other modules may import from m00_platform.

DTOs mirror contracts/openapi/m00-platform.yaml. Accessors read master data for other
modules (e.g. M01 validates an assignment's operator/machine and resolves their site).
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from backend.core.runtime import get_runtime

ExperienceLevel = Literal["JUNIOR", "INTERMEDIATE", "SENIOR"]
CertificationStatus = Literal["VALID", "EXPIRING", "EXPIRED"]
MachineType = Literal["EXCAVATOR", "DUMPER", "LOADER", "DOZER", "OTHER"]
ZoneType = Literal["TASK", "HAZARD", "RESTRICTED", "DISPOSAL", "SOFT_GROUND", "OTHER"]
Status = Literal["ACTIVE", "INACTIVE", "MAINTENANCE", "RETIRED"]


class _DTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class GeoPoint(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)


class SiteDTO(_DTO):
    site_id: str
    name: str
    location: GeoPoint | None = None
    timezone: str = "UTC"
    configuration: dict = {}
    status: Status = "ACTIVE"
    created_at: datetime | None = None


class ZoneDTO(_DTO):
    zone_id: str
    site_id: str
    name: str
    zone_type: ZoneType
    geometry: dict
    status: Status = "ACTIVE"


class OperatorDTO(_DTO):
    operator_id: str
    name: str
    site_id: str
    experience_level: ExperienceLevel = "JUNIOR"
    certification_status: CertificationStatus = "VALID"
    preferred_language: str = "en"
    status: Status = "ACTIVE"
    created_at: datetime | None = None


class MachineDTO(_DTO):
    machine_id: str
    site_id: str
    machine_type: MachineType
    model: str
    serial_number: str
    engine_hours: float = 0.0
    status: Status = "ACTIVE"
    created_at: datetime | None = None


async def get_operator(operator_id: str) -> OperatorDTO | None:
    from backend.modules.m00_platform.models import Operator

    async with get_runtime().db.sessionmaker() as s:
        row = await s.get(Operator, operator_id)
        return OperatorDTO.model_validate(row) if row else None


async def get_machine(machine_id: str) -> MachineDTO | None:
    from backend.modules.m00_platform.models import Machine

    async with get_runtime().db.sessionmaker() as s:
        row = await s.get(Machine, machine_id)
        return MachineDTO.model_validate(row) if row else None


async def get_site(site_id: str) -> SiteDTO | None:
    from backend.modules.m00_platform.models import Site

    async with get_runtime().db.sessionmaker() as s:
        row = await s.get(Site, site_id)
        return SiteDTO.model_validate(row) if row else None


async def list_zones(site_id: str) -> list[ZoneDTO]:
    from sqlalchemy import select

    from backend.modules.m00_platform.models import Zone

    async with get_runtime().db.sessionmaker() as s:
        rows = (await s.scalars(select(Zone).where(Zone.site_id == site_id).order_by(Zone.zone_id))).all()
        return [ZoneDTO.model_validate(r) for r in rows]
