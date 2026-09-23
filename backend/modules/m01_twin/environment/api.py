"""Site/zone conditions API (M01-WP5)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.core.auth import Principal, current_principal, require_permission
from backend.core.errors import AppError
from backend.modules.m00_platform import public as platform
from backend.modules.m01_twin.environment import service
from backend.modules.m01_twin.public import EnvironmentConditions, SiteConditions, TwinEnvironment

router = APIRouter()


class ConditionsUpdate(BaseModel):
    conditions: EnvironmentConditions
    zone_id: str | None = None
    source: str = "MANUAL"


@router.get("/sites/{site_id}/conditions", response_model=SiteConditions, tags=["environment"])
async def get_conditions(site_id: str, p: Principal = Depends(current_principal)):
    p.ensure_site(site_id)
    zones = [z.zone_id for z in await platform.list_zones(site_id)]
    return await service.site_conditions(site_id, zones)


@router.post("/sites/{site_id}/conditions", response_model=TwinEnvironment, status_code=201, tags=["environment"])
async def post_conditions(site_id: str, body: ConditionsUpdate, p: Principal = Depends(require_permission("conditions:write"))):
    p.ensure_site(site_id)
    if body.zone_id and body.zone_id not in {z.zone_id for z in await platform.list_zones(site_id)}:
        raise AppError(422, "UNKNOWN_ZONE", f"Zone '{body.zone_id}' does not exist in site '{site_id}'")
    return await service.set_conditions(site_id, body.conditions, body.zone_id, body.source)
