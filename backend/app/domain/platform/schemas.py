"""Platform (master data + auth) request/response shapes. Mirrored in contracts/openapi/argus-api.yaml."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.core.security import Principal
from app.schemas.common import DTO, GeoPoint

ExperienceLevel = Literal["JUNIOR", "INTERMEDIATE", "SENIOR"]
CertificationStatus = Literal["VALID", "EXPIRING", "EXPIRED"]
MachineType = Literal["EXCAVATOR", "DUMPER", "LOADER", "DOZER", "OTHER"]
ZoneType = Literal["TASK", "HAZARD", "RESTRICTED", "DISPOSAL", "SOFT_GROUND", "OTHER"]
Status = Literal["ACTIVE", "INACTIVE", "MAINTENANCE", "RETIRED"]
BUSINESS_ID = r"^[A-Z0-9_]{2,32}$"

# ---------------- responses ----------------


class SiteDTO(DTO):
    site_id: str
    name: str
    location: GeoPoint | None = None
    timezone: str = "UTC"
    configuration: dict = {}
    status: Status = "ACTIVE"
    created_at: datetime | None = None


class ZoneDTO(DTO):
    zone_id: str
    site_id: str
    name: str
    zone_type: ZoneType
    geometry: dict
    status: Status = "ACTIVE"


class OperatorDTO(DTO):
    operator_id: str
    name: str
    site_id: str
    experience_level: ExperienceLevel = "JUNIOR"
    certification_status: CertificationStatus = "VALID"
    preferred_language: str = "en"
    status: Status = "ACTIVE"
    created_at: datetime | None = None


class MachineDTO(DTO):
    machine_id: str
    site_id: str
    machine_type: MachineType
    model: str
    serial_number: str
    engine_hours: float = 0.0
    status: Status = "ACTIVE"
    created_at: datetime | None = None


# ---------------- auth ----------------


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    principal: Principal


class MeResponse(BaseModel):
    principal: Principal
    permissions: list[str]


# ---------------- requests ----------------


class SiteCreate(BaseModel):
    site_id: str = Field(pattern=BUSINESS_ID)
    name: str
    location: GeoPoint | None = None
    timezone: str = "UTC"
    configuration: dict = {}


class SiteUpdate(BaseModel):
    name: str | None = None
    location: GeoPoint | None = None
    timezone: str | None = None
    configuration: dict | None = None
    status: Status | None = None


class ZoneCreate(BaseModel):
    zone_id: str = Field(pattern=BUSINESS_ID)
    name: str
    zone_type: ZoneType
    geometry: dict = Field(description="GeoJSON Polygon, coordinates [lon, lat]")


class ZoneUpdate(BaseModel):
    name: str | None = None
    zone_type: ZoneType | None = None
    geometry: dict | None = None
    status: Status | None = None


class OperatorCreate(BaseModel):
    operator_id: str = Field(pattern=BUSINESS_ID)
    name: str
    site_id: str
    experience_level: ExperienceLevel = "JUNIOR"
    certification_status: CertificationStatus = "VALID"
    preferred_language: str = "en"


class OperatorUpdate(BaseModel):
    name: str | None = None
    site_id: str | None = None
    experience_level: ExperienceLevel | None = None
    certification_status: CertificationStatus | None = None
    preferred_language: str | None = None
    status: Status | None = None


class MachineCreate(BaseModel):
    machine_id: str = Field(pattern=BUSINESS_ID)
    site_id: str
    machine_type: MachineType
    model: str
    serial_number: str
    engine_hours: float = Field(0.0, ge=0)


class MachineUpdate(BaseModel):
    site_id: str | None = None
    model: str | None = None
    engine_hours: float | None = Field(None, ge=0)
    status: Status | None = None
