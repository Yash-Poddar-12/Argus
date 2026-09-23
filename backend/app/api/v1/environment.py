"""Site/zone conditions endpoints (thin routes)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.exceptions import AppError
from app.dependencies import Principal, current_principal, require_permission
from app.domain.environment import service
from app.domain.environment.schemas import ConditionsUpdate, SiteConditions, TwinEnvironment
from app.domain.platform import service as platform

router = APIRouter(tags=["environment"])


@router.get("/sites/{site_id}/conditions", response_model=SiteConditions)
async def get_conditions(site_id: str, p: Principal = Depends(current_principal)):
    p.ensure_site(site_id)
    zones = [z.zone_id for z in await platform.list_zones(site_id)]
    return await service.site_conditions(site_id, zones)


@router.post("/sites/{site_id}/conditions", response_model=TwinEnvironment, status_code=201)
async def post_conditions(site_id: str, body: ConditionsUpdate, p: Principal = Depends(require_permission("conditions:write"))):
    p.ensure_site(site_id)
    if body.zone_id and body.zone_id not in {z.zone_id for z in await platform.list_zones(site_id)}:
        raise AppError(422, "UNKNOWN_ZONE", f"Zone '{body.zone_id}' does not exist in site '{site_id}'")
    return await service.set_conditions(site_id, body.conditions, body.zone_id, body.source)
