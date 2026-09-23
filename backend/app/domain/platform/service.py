"""Platform domain services: authentication, master-data CRUD and read accessors.

Other domains read master data only through the ``get_*`` / ``list_zones`` accessors below
(they never query platform tables themselves).
"""

from __future__ import annotations

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import audit
from app.core.exceptions import AppError, Conflict, NotFound, Unauthorized
from app.core.runtime import get_runtime
from app.core.security import Principal, issue_token, verify_password
from app.domain.platform.models import Machine, Operator, Site, User, UserSiteScope, Zone
from app.domain.platform.schemas import (
    MachineCreate,
    MachineDTO,
    MachineUpdate,
    OperatorCreate,
    OperatorDTO,
    OperatorUpdate,
    SiteCreate,
    SiteDTO,
    SiteUpdate,
    TokenResponse,
    ZoneCreate,
    ZoneDTO,
    ZoneUpdate,
)

SOURCE = "platform"

# ---------------- read accessors for other domains ----------------


async def get_operator(operator_id: str) -> OperatorDTO | None:
    async with get_runtime().db.sessionmaker() as s:
        row = await s.get(Operator, operator_id)
        return OperatorDTO.model_validate(row) if row else None


async def get_machine(machine_id: str) -> MachineDTO | None:
    async with get_runtime().db.sessionmaker() as s:
        row = await s.get(Machine, machine_id)
        return MachineDTO.model_validate(row) if row else None


async def get_site(site_id: str) -> SiteDTO | None:
    async with get_runtime().db.sessionmaker() as s:
        row = await s.get(Site, site_id)
        return SiteDTO.model_validate(row) if row else None


async def list_zones(site_id: str) -> list[ZoneDTO]:
    async with get_runtime().db.sessionmaker() as s:
        rows = (await s.scalars(select(Zone).where(Zone.site_id == site_id).order_by(Zone.zone_id))).all()
        return [ZoneDTO.model_validate(r) for r in rows]


# ---------------- auth ----------------


async def load_principal(session: AsyncSession, user: User) -> Principal:
    sites = (await session.scalars(select(UserSiteScope.site_id).where(UserSiteScope.user_id == user.user_id))).all()
    return Principal(user_id=user.user_id, username=user.username, role=user.role, operator_id=user.operator_id,
                     site_ids=sorted(sites))


async def login(session: AsyncSession, username: str, password: str) -> TokenResponse:
    user = await session.scalar(select(User).where(User.username == username))
    if user is None or user.status != "ACTIVE" or not verify_password(password, user.password_hash):
        raise Unauthorized("Invalid username or password")
    principal = await load_principal(session, user)
    token, ttl = issue_token(principal)
    return TokenResponse(access_token=token, expires_in=ttl, principal=principal)


# ---------------- helpers ----------------


async def _paginate(session: AsyncSession, stmt, dto, limit: int, offset: int) -> dict:
    total = await session.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = (await session.scalars(stmt.limit(limit).offset(offset))).all()
    return {"items": [dto.model_validate(r) for r in rows], "total": total or 0, "limit": limit, "offset": offset}


def _scope(stmt, column, principal: Principal, site_id: str | None):
    if site_id:
        principal.ensure_site(site_id)
        return stmt.where(column == site_id)
    return stmt.where(column.in_(principal.site_ids))


async def _emit(event_type: str, dto: BaseModel, site_id: str, changed: list[str] | None = None) -> None:
    payload = dto.model_dump(mode="json")
    if changed is not None:
        payload["changed_fields"] = changed
    await get_runtime().bus.publish(event_type, payload, source_id=SOURCE, site_id=site_id)


def _apply(row, patch: BaseModel) -> list[str]:
    changed = []
    for key, value in patch.model_dump(exclude_unset=True, mode="json").items():
        if getattr(row, key) != value:
            setattr(row, key, value)
            changed.append(key)
    return changed


def _check_polygon(geometry: dict) -> None:
    ring = (geometry.get("coordinates") or [[]])[0] if geometry.get("type") == "Polygon" else None
    if not ring or len(ring) < 4 or ring[0] != ring[-1]:
        raise AppError(422, "VALIDATION_ERROR", "geometry must be a closed GeoJSON Polygon (>= 4 positions)")


# ---------------- sites ----------------


async def list_sites(s: AsyncSession, p: Principal, limit: int, offset: int) -> dict:
    stmt = select(Site).where(Site.site_id.in_(p.site_ids)).order_by(Site.site_id)
    return await _paginate(s, stmt, SiteDTO, limit, offset)


async def create_site(s: AsyncSession, p: Principal, body: SiteCreate) -> SiteDTO:
    if await s.get(Site, body.site_id):
        raise Conflict(f"Site '{body.site_id}' already exists")
    row = Site(**body.model_dump(mode="json"))
    s.add(row)
    s.add(UserSiteScope(user_id=p.user_id, site_id=body.site_id))  # creator gets scope (effective on next login)
    audit(s, p, "create", "site", body.site_id, body.site_id)
    await s.commit()
    dto = SiteDTO.model_validate(row)
    await _emit("platform.site.created", dto, dto.site_id)
    return dto


async def read_site(s: AsyncSession, p: Principal, site_id: str) -> SiteDTO:
    p.ensure_site(site_id)
    row = await s.get(Site, site_id)
    if row is None:
        raise NotFound("site", site_id)
    return SiteDTO.model_validate(row)


async def update_site(s: AsyncSession, p: Principal, site_id: str, body: SiteUpdate) -> SiteDTO:
    p.ensure_site(site_id)
    row = await s.get(Site, site_id)
    if row is None:
        raise NotFound("site", site_id)
    changed = _apply(row, body)
    audit(s, p, "update", "site", site_id, site_id, {"changed": changed})
    await s.commit()
    dto = SiteDTO.model_validate(row)
    if changed:
        await _emit("platform.site.updated", dto, site_id, changed)
    return dto


# ---------------- zones ----------------


async def zones_for(s: AsyncSession, p: Principal, site_id: str) -> list[ZoneDTO]:
    p.ensure_site(site_id)
    rows = (await s.scalars(select(Zone).where(Zone.site_id == site_id).order_by(Zone.zone_id))).all()
    return [ZoneDTO.model_validate(r) for r in rows]


async def create_zone(s: AsyncSession, p: Principal, site_id: str, body: ZoneCreate) -> ZoneDTO:
    p.ensure_site(site_id)
    if await s.get(Site, site_id) is None:
        raise NotFound("site", site_id)
    if await s.get(Zone, body.zone_id):
        raise Conflict(f"Zone '{body.zone_id}' already exists")
    _check_polygon(body.geometry)
    row = Zone(site_id=site_id, **body.model_dump(mode="json"))
    s.add(row)
    audit(s, p, "create", "zone", body.zone_id, site_id)
    await s.commit()
    dto = ZoneDTO.model_validate(row)
    await _emit("platform.zone.updated", dto, site_id, ["created"])
    return dto


async def update_zone(s: AsyncSession, p: Principal, site_id: str, zone_id: str, body: ZoneUpdate) -> ZoneDTO:
    p.ensure_site(site_id)
    row = await s.get(Zone, zone_id)
    if row is None or row.site_id != site_id:
        raise NotFound("zone", zone_id)
    if body.geometry is not None:
        _check_polygon(body.geometry)
    changed = _apply(row, body)
    audit(s, p, "update", "zone", zone_id, site_id, {"changed": changed})
    await s.commit()
    dto = ZoneDTO.model_validate(row)
    if changed:
        await _emit("platform.zone.updated", dto, site_id, changed)
    return dto


# ---------------- operators ----------------


async def list_operators(s: AsyncSession, p: Principal, site_id: str | None, limit: int, offset: int) -> dict:
    stmt = _scope(select(Operator), Operator.site_id, p, site_id).order_by(Operator.operator_id)
    return await _paginate(s, stmt, OperatorDTO, limit, offset)


async def create_operator(s: AsyncSession, p: Principal, body: OperatorCreate) -> OperatorDTO:
    p.ensure_site(body.site_id)
    if await s.get(Operator, body.operator_id):
        raise Conflict(f"Operator '{body.operator_id}' already exists")
    row = Operator(**body.model_dump())
    s.add(row)
    audit(s, p, "create", "operator", body.operator_id, body.site_id)
    await s.commit()
    dto = OperatorDTO.model_validate(row)
    await _emit("platform.operator.created", dto, dto.site_id)
    return dto


async def read_operator(s: AsyncSession, p: Principal, operator_id: str) -> OperatorDTO:
    row = await s.get(Operator, operator_id)
    if row is None:
        raise NotFound("operator", operator_id)
    p.ensure_operator(operator_id, row.site_id)
    return OperatorDTO.model_validate(row)


async def update_operator(s: AsyncSession, p: Principal, operator_id: str, body: OperatorUpdate) -> OperatorDTO:
    row = await s.get(Operator, operator_id)
    if row is None:
        raise NotFound("operator", operator_id)
    p.ensure_site(row.site_id)
    if body.site_id:
        p.ensure_site(body.site_id)
    changed = _apply(row, body)
    audit(s, p, "update", "operator", operator_id, row.site_id, {"changed": changed})
    await s.commit()
    dto = OperatorDTO.model_validate(row)
    if changed:
        await _emit("platform.operator.updated", dto, dto.site_id, changed)
    return dto


# ---------------- machines ----------------


async def list_machines(s: AsyncSession, p: Principal, site_id: str | None, machine_type: str | None,
                        limit: int, offset: int) -> dict:
    stmt = _scope(select(Machine), Machine.site_id, p, site_id).order_by(Machine.machine_id)
    if machine_type:
        stmt = stmt.where(Machine.machine_type == machine_type)
    return await _paginate(s, stmt, MachineDTO, limit, offset)


async def create_machine(s: AsyncSession, p: Principal, body: MachineCreate) -> MachineDTO:
    p.ensure_site(body.site_id)
    if await s.get(Machine, body.machine_id):
        raise Conflict(f"Machine '{body.machine_id}' already exists")
    if await s.scalar(select(Machine).where(Machine.serial_number == body.serial_number)):
        raise Conflict(f"Serial number '{body.serial_number}' already registered")
    row = Machine(**body.model_dump())
    s.add(row)
    audit(s, p, "create", "machine", body.machine_id, body.site_id)
    await s.commit()
    dto = MachineDTO.model_validate(row)
    await _emit("platform.machine.created", dto, dto.site_id)
    return dto


async def read_machine(s: AsyncSession, p: Principal, machine_id: str) -> MachineDTO:
    row = await s.get(Machine, machine_id)
    if row is None:
        raise NotFound("machine", machine_id)
    p.ensure_site(row.site_id)
    return MachineDTO.model_validate(row)


async def update_machine(s: AsyncSession, p: Principal, machine_id: str, body: MachineUpdate) -> MachineDTO:
    row = await s.get(Machine, machine_id)
    if row is None:
        raise NotFound("machine", machine_id)
    p.ensure_site(row.site_id)
    if body.site_id:
        p.ensure_site(body.site_id)
    changed = _apply(row, body)
    audit(s, p, "update", "machine", machine_id, row.site_id, {"changed": changed})
    await s.commit()
    dto = MachineDTO.model_validate(row)
    if changed:
        await _emit("platform.machine.updated", dto, dto.site_id, changed)
    return dto
