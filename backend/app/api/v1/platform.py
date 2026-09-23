"""Master data endpoints: sites, zones, operators, machines (thin: logic in app/domain/platform/service.py)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import Principal, get_session, require_permission
from app.domain.platform import service
from app.domain.platform.schemas import (
    MachineCreate,
    MachineDTO,
    MachineType,
    MachineUpdate,
    OperatorCreate,
    OperatorDTO,
    OperatorUpdate,
    SiteCreate,
    SiteDTO,
    SiteUpdate,
    ZoneCreate,
    ZoneDTO,
    ZoneUpdate,
)
from app.schemas.common import Page

router = APIRouter()

# ---------------- sites ----------------


@router.get("/sites", response_model=Page[SiteDTO], tags=["sites"])
async def list_sites(limit: int = Query(50, le=500), offset: int = 0,
                     p: Principal = Depends(require_permission("sites:read")),
                     session: AsyncSession = Depends(get_session)):
    return await service.list_sites(session, p, limit, offset)


@router.post("/sites", response_model=SiteDTO, status_code=201, tags=["sites"])
async def create_site(body: SiteCreate, p: Principal = Depends(require_permission("sites:write")),
                      session: AsyncSession = Depends(get_session)):
    return await service.create_site(session, p, body)


@router.get("/sites/{site_id}", response_model=SiteDTO, tags=["sites"])
async def get_site(site_id: str, p: Principal = Depends(require_permission("sites:read")),
                   session: AsyncSession = Depends(get_session)):
    return await service.read_site(session, p, site_id)


@router.patch("/sites/{site_id}", response_model=SiteDTO, tags=["sites"])
async def update_site(site_id: str, body: SiteUpdate, p: Principal = Depends(require_permission("sites:write")),
                      session: AsyncSession = Depends(get_session)):
    return await service.update_site(session, p, site_id, body)


# ---------------- zones ----------------


@router.get("/sites/{site_id}/zones", response_model=list[ZoneDTO], tags=["zones"])
async def list_zones(site_id: str, p: Principal = Depends(require_permission("sites:read")),
                     session: AsyncSession = Depends(get_session)):
    return await service.zones_for(session, p, site_id)


@router.post("/sites/{site_id}/zones", response_model=ZoneDTO, status_code=201, tags=["zones"])
async def create_zone(site_id: str, body: ZoneCreate, p: Principal = Depends(require_permission("zones:write")),
                      session: AsyncSession = Depends(get_session)):
    return await service.create_zone(session, p, site_id, body)


@router.patch("/sites/{site_id}/zones/{zone_id}", response_model=ZoneDTO, tags=["zones"])
async def update_zone(site_id: str, zone_id: str, body: ZoneUpdate,
                      p: Principal = Depends(require_permission("zones:write")),
                      session: AsyncSession = Depends(get_session)):
    return await service.update_zone(session, p, site_id, zone_id, body)


# ---------------- operators ----------------


@router.get("/operators", response_model=Page[OperatorDTO], tags=["operators"])
async def list_operators(site_id: str | None = None, limit: int = Query(50, le=500), offset: int = 0,
                         p: Principal = Depends(require_permission("operators:write")),
                         session: AsyncSession = Depends(get_session)):
    return await service.list_operators(session, p, site_id, limit, offset)


@router.post("/operators", response_model=OperatorDTO, status_code=201, tags=["operators"])
async def create_operator(body: OperatorCreate, p: Principal = Depends(require_permission("operators:write")),
                          session: AsyncSession = Depends(get_session)):
    return await service.create_operator(session, p, body)


@router.get("/operators/{operator_id}", response_model=OperatorDTO, tags=["operators"])
async def get_operator(operator_id: str, p: Principal = Depends(require_permission("operators:read")),
                       session: AsyncSession = Depends(get_session)):
    return await service.read_operator(session, p, operator_id)


@router.patch("/operators/{operator_id}", response_model=OperatorDTO, tags=["operators"])
async def update_operator(operator_id: str, body: OperatorUpdate,
                          p: Principal = Depends(require_permission("operators:write")),
                          session: AsyncSession = Depends(get_session)):
    return await service.update_operator(session, p, operator_id, body)


# ---------------- machines ----------------


@router.get("/machines", response_model=Page[MachineDTO], tags=["machines"])
async def list_machines(site_id: str | None = None, machine_type: MachineType | None = None,
                        limit: int = Query(50, le=500), offset: int = 0,
                        p: Principal = Depends(require_permission("machines:read")),
                        session: AsyncSession = Depends(get_session)):
    return await service.list_machines(session, p, site_id, machine_type, limit, offset)


@router.post("/machines", response_model=MachineDTO, status_code=201, tags=["machines"])
async def create_machine(body: MachineCreate, p: Principal = Depends(require_permission("machines:write")),
                         session: AsyncSession = Depends(get_session)):
    return await service.create_machine(session, p, body)


@router.get("/machines/{machine_id}", response_model=MachineDTO, tags=["machines"])
async def get_machine(machine_id: str, p: Principal = Depends(require_permission("machines:read")),
                      session: AsyncSession = Depends(get_session)):
    return await service.read_machine(session, p, machine_id)


@router.patch("/machines/{machine_id}", response_model=MachineDTO, tags=["machines"])
async def update_machine(machine_id: str, body: MachineUpdate,
                         p: Principal = Depends(require_permission("machines:write")),
                         session: AsyncSession = Depends(get_session)):
    return await service.update_machine(session, p, machine_id, body)
