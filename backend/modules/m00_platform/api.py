"""M00 REST API: auth + master data CRUD (contracts/openapi/m00-platform.yaml)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.audit import audit
from backend.core.auth import Principal, Role, current_principal, issue_token, require_permission, verify_password
from backend.core.errors import Conflict, NotFound, Unauthorized
from backend.core.events import EventBus
from backend.core.runtime import get_bus, get_session
from backend.modules.m00_platform.models import Machine, Operator, Site, User, UserSiteScope, Zone
from backend.modules.m00_platform.public import (
    CertificationStatus,
    ExperienceLevel,
    GeoPoint,
    MachineDTO,
    MachineType,
    OperatorDTO,
    SiteDTO,
    Status,
    ZoneDTO,
    ZoneType,
)

SOURCE = "m00_platform"
router = APIRouter()


class Page[T](BaseModel):
    items: list[T]
    total: int
    limit: int
    offset: int


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


async def load_principal(session: AsyncSession, user: User) -> Principal:
    sites = (await session.scalars(select(UserSiteScope.site_id).where(UserSiteScope.user_id == user.user_id))).all()
    return Principal(user_id=user.user_id, username=user.username, role=user.role, operator_id=user.operator_id,
                     site_ids=sorted(sites))


@router.post("/auth/login", response_model=TokenResponse, tags=["auth"])
async def login(body: LoginRequest, session: AsyncSession = Depends(get_session)):
    user = await session.scalar(select(User).where(User.username == body.username))
    if user is None or user.status != "ACTIVE" or not verify_password(body.password, user.password_hash):
        raise Unauthorized("Invalid username or password")
    principal = await load_principal(session, user)
    token, ttl = issue_token(principal)
    return TokenResponse(access_token=token, expires_in=ttl, principal=principal)


@router.get("/auth/me", response_model=MeResponse, tags=["auth"])
async def me(principal: Principal = Depends(current_principal)):
    return MeResponse(principal=principal, permissions=sorted(principal.permissions))


# ---------------- helpers ----------------

async def _paginate(session: AsyncSession, stmt, model, dto, limit: int, offset: int) -> dict:
    total = await session.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = (await session.scalars(stmt.limit(limit).offset(offset))).all()
    return {"items": [dto.model_validate(r) for r in rows], "total": total or 0, "limit": limit, "offset": offset}


def _scope(stmt, column, principal: Principal, site_id: str | None):
    if site_id:
        principal.ensure_site(site_id)
        return stmt.where(column == site_id)
    return stmt.where(column.in_(principal.site_ids))


async def _emit(bus: EventBus, event_type: str, dto: BaseModel, site_id: str, changed: list[str] | None = None):
    payload = dto.model_dump(mode="json")
    if changed is not None:
        payload["changed_fields"] = changed
    await bus.publish(event_type, payload, source_id=SOURCE, site_id=site_id)


def _apply(row, patch: BaseModel) -> list[str]:
    changed = []
    for key, value in patch.model_dump(exclude_unset=True, mode="json").items():
        if getattr(row, key) != value:
            setattr(row, key, value)
            changed.append(key)
    return changed


# ---------------- sites ----------------

class SiteCreate(BaseModel):
    site_id: str = Field(pattern=r"^[A-Z0-9_]{2,32}$")
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


@router.get("/sites", response_model=Page[SiteDTO], tags=["sites"])
async def list_sites(limit: int = Query(50, le=500), offset: int = 0,
                     p: Principal = Depends(require_permission("sites:read")),
                     session: AsyncSession = Depends(get_session)):
    stmt = select(Site).where(Site.site_id.in_(p.site_ids)).order_by(Site.site_id)
    return await _paginate(session, stmt, Site, SiteDTO, limit, offset)


@router.post("/sites", response_model=SiteDTO, status_code=201, tags=["sites"])
async def create_site(body: SiteCreate, p: Principal = Depends(require_permission("sites:write")),
                      session: AsyncSession = Depends(get_session), bus: EventBus = Depends(get_bus)):
    if await session.get(Site, body.site_id):
        raise Conflict(f"Site '{body.site_id}' already exists")
    row = Site(**body.model_dump(mode="json"))
    session.add(row)
    session.add(UserSiteScope(user_id=p.user_id, site_id=body.site_id))  # creator gets scope (effective on next login)
    audit(session, p, "create", "site", body.site_id, body.site_id)
    await session.commit()
    dto = SiteDTO.model_validate(row)
    await _emit(bus, "platform.site.created", dto, dto.site_id)
    return dto


@router.get("/sites/{site_id}", response_model=SiteDTO, tags=["sites"])
async def get_site(site_id: str, p: Principal = Depends(require_permission("sites:read")),
                   session: AsyncSession = Depends(get_session)):
    p.ensure_site(site_id)
    row = await session.get(Site, site_id)
    if row is None:
        raise NotFound("site", site_id)
    return SiteDTO.model_validate(row)


@router.patch("/sites/{site_id}", response_model=SiteDTO, tags=["sites"])
async def update_site(site_id: str, body: SiteUpdate, p: Principal = Depends(require_permission("sites:write")),
                      session: AsyncSession = Depends(get_session), bus: EventBus = Depends(get_bus)):
    p.ensure_site(site_id)
    row = await session.get(Site, site_id)
    if row is None:
        raise NotFound("site", site_id)
    changed = _apply(row, body)
    audit(session, p, "update", "site", site_id, site_id, {"changed": changed})
    await session.commit()
    dto = SiteDTO.model_validate(row)
    if changed:
        await _emit(bus, "platform.site.updated", dto, site_id, changed)
    return dto


# ---------------- zones ----------------

class ZoneCreate(BaseModel):
    zone_id: str = Field(pattern=r"^[A-Z0-9_]{2,32}$")
    name: str
    zone_type: ZoneType
    geometry: dict = Field(description="GeoJSON Polygon, coordinates [lon, lat]")


class ZoneUpdate(BaseModel):
    name: str | None = None
    zone_type: ZoneType | None = None
    geometry: dict | None = None
    status: Status | None = None


def _check_polygon(geometry: dict) -> None:
    from backend.core.errors import AppError

    ring = (geometry.get("coordinates") or [[]])[0] if geometry.get("type") == "Polygon" else None
    if not ring or len(ring) < 4 or ring[0] != ring[-1]:
        raise AppError(422, "VALIDATION_ERROR", "geometry must be a closed GeoJSON Polygon (>= 4 positions)")


@router.get("/sites/{site_id}/zones", response_model=list[ZoneDTO], tags=["zones"])
async def list_zones(site_id: str, p: Principal = Depends(require_permission("sites:read")),
                     session: AsyncSession = Depends(get_session)):
    p.ensure_site(site_id)
    rows = (await session.scalars(select(Zone).where(Zone.site_id == site_id).order_by(Zone.zone_id))).all()
    return [ZoneDTO.model_validate(r) for r in rows]


@router.post("/sites/{site_id}/zones", response_model=ZoneDTO, status_code=201, tags=["zones"])
async def create_zone(site_id: str, body: ZoneCreate, p: Principal = Depends(require_permission("zones:write")),
                      session: AsyncSession = Depends(get_session), bus: EventBus = Depends(get_bus)):
    p.ensure_site(site_id)
    if await session.get(Site, site_id) is None:
        raise NotFound("site", site_id)
    if await session.get(Zone, body.zone_id):
        raise Conflict(f"Zone '{body.zone_id}' already exists")
    _check_polygon(body.geometry)
    row = Zone(site_id=site_id, **body.model_dump(mode="json"))
    session.add(row)
    audit(session, p, "create", "zone", body.zone_id, site_id)
    await session.commit()
    dto = ZoneDTO.model_validate(row)
    await _emit(bus, "platform.zone.updated", dto, site_id, ["created"])
    return dto


@router.patch("/sites/{site_id}/zones/{zone_id}", response_model=ZoneDTO, tags=["zones"])
async def update_zone(site_id: str, zone_id: str, body: ZoneUpdate,
                      p: Principal = Depends(require_permission("zones:write")),
                      session: AsyncSession = Depends(get_session), bus: EventBus = Depends(get_bus)):
    p.ensure_site(site_id)
    row = await session.get(Zone, zone_id)
    if row is None or row.site_id != site_id:
        raise NotFound("zone", zone_id)
    if body.geometry is not None:
        _check_polygon(body.geometry)
    changed = _apply(row, body)
    audit(session, p, "update", "zone", zone_id, site_id, {"changed": changed})
    await session.commit()
    dto = ZoneDTO.model_validate(row)
    if changed:
        await _emit(bus, "platform.zone.updated", dto, site_id, changed)
    return dto


# ---------------- operators ----------------

class OperatorCreate(BaseModel):
    operator_id: str = Field(pattern=r"^[A-Z0-9_]{2,32}$")
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


@router.get("/operators", response_model=Page[OperatorDTO], tags=["operators"])
async def list_operators(site_id: str | None = None, limit: int = Query(50, le=500), offset: int = 0,
                         p: Principal = Depends(require_permission("operators:write")),
                         session: AsyncSession = Depends(get_session)):
    stmt = _scope(select(Operator), Operator.site_id, p, site_id).order_by(Operator.operator_id)
    return await _paginate(session, stmt, Operator, OperatorDTO, limit, offset)


@router.post("/operators", response_model=OperatorDTO, status_code=201, tags=["operators"])
async def create_operator(body: OperatorCreate, p: Principal = Depends(require_permission("operators:write")),
                          session: AsyncSession = Depends(get_session), bus: EventBus = Depends(get_bus)):
    p.ensure_site(body.site_id)
    if await session.get(Operator, body.operator_id):
        raise Conflict(f"Operator '{body.operator_id}' already exists")
    row = Operator(**body.model_dump())
    session.add(row)
    audit(session, p, "create", "operator", body.operator_id, body.site_id)
    await session.commit()
    dto = OperatorDTO.model_validate(row)
    await _emit(bus, "platform.operator.created", dto, dto.site_id)
    return dto


@router.get("/operators/{operator_id}", response_model=OperatorDTO, tags=["operators"])
async def get_operator(operator_id: str, p: Principal = Depends(require_permission("operators:read")),
                       session: AsyncSession = Depends(get_session)):
    row = await session.get(Operator, operator_id)
    if row is None:
        raise NotFound("operator", operator_id)
    p.ensure_operator(operator_id, row.site_id)
    return OperatorDTO.model_validate(row)


@router.patch("/operators/{operator_id}", response_model=OperatorDTO, tags=["operators"])
async def update_operator(operator_id: str, body: OperatorUpdate,
                          p: Principal = Depends(require_permission("operators:write")),
                          session: AsyncSession = Depends(get_session), bus: EventBus = Depends(get_bus)):
    row = await session.get(Operator, operator_id)
    if row is None:
        raise NotFound("operator", operator_id)
    p.ensure_site(row.site_id)
    if body.site_id:
        p.ensure_site(body.site_id)
    changed = _apply(row, body)
    audit(session, p, "update", "operator", operator_id, row.site_id, {"changed": changed})
    await session.commit()
    dto = OperatorDTO.model_validate(row)
    if changed:
        await _emit(bus, "platform.operator.updated", dto, dto.site_id, changed)
    return dto


# ---------------- machines ----------------

class MachineCreate(BaseModel):
    machine_id: str = Field(pattern=r"^[A-Z0-9_]{2,32}$")
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


@router.get("/machines", response_model=Page[MachineDTO], tags=["machines"])
async def list_machines(site_id: str | None = None, machine_type: MachineType | None = None,
                        limit: int = Query(50, le=500), offset: int = 0,
                        p: Principal = Depends(require_permission("machines:read")),
                        session: AsyncSession = Depends(get_session)):
    stmt = _scope(select(Machine), Machine.site_id, p, site_id).order_by(Machine.machine_id)
    if machine_type:
        stmt = stmt.where(Machine.machine_type == machine_type)
    return await _paginate(session, stmt, Machine, MachineDTO, limit, offset)


@router.post("/machines", response_model=MachineDTO, status_code=201, tags=["machines"])
async def create_machine(body: MachineCreate, p: Principal = Depends(require_permission("machines:write")),
                         session: AsyncSession = Depends(get_session), bus: EventBus = Depends(get_bus)):
    p.ensure_site(body.site_id)
    if await session.get(Machine, body.machine_id):
        raise Conflict(f"Machine '{body.machine_id}' already exists")
    if await session.scalar(select(Machine).where(Machine.serial_number == body.serial_number)):
        raise Conflict(f"Serial number '{body.serial_number}' already registered")
    row = Machine(**body.model_dump())
    session.add(row)
    audit(session, p, "create", "machine", body.machine_id, body.site_id)
    await session.commit()
    dto = MachineDTO.model_validate(row)
    await _emit(bus, "platform.machine.created", dto, dto.site_id)
    return dto


@router.get("/machines/{machine_id}", response_model=MachineDTO, tags=["machines"])
async def get_machine(machine_id: str, p: Principal = Depends(require_permission("machines:read")),
                      session: AsyncSession = Depends(get_session)):
    row = await session.get(Machine, machine_id)
    if row is None:
        raise NotFound("machine", machine_id)
    p.ensure_site(row.site_id)
    return MachineDTO.model_validate(row)


@router.patch("/machines/{machine_id}", response_model=MachineDTO, tags=["machines"])
async def update_machine(machine_id: str, body: MachineUpdate,
                         p: Principal = Depends(require_permission("machines:write")),
                         session: AsyncSession = Depends(get_session), bus: EventBus = Depends(get_bus)):
    row = await session.get(Machine, machine_id)
    if row is None:
        raise NotFound("machine", machine_id)
    p.ensure_site(row.site_id)
    if body.site_id:
        p.ensure_site(body.site_id)
    changed = _apply(row, body)
    audit(session, p, "update", "machine", machine_id, row.site_id, {"changed": changed})
    await session.commit()
    dto = MachineDTO.model_validate(row)
    if changed:
        await _emit(bus, "platform.machine.updated", dto, dto.site_id, changed)
    return dto


__all__ = ["router", "Role"]
