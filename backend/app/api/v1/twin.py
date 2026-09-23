"""Operational twin endpoints: operator twin, site twin, machine live state (thin routes)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.exceptions import NotFound
from app.dependencies import Principal, current_principal, require_permission
from app.domain.platform import service as platform
from app.domain.twin import service as twin
from app.domain.twin.schemas import OperationalTwin, SiteTwin, TwinMachineState

router = APIRouter(tags=["twin"])


@router.get("/operators/{operator_id}/twin", response_model=OperationalTwin)
async def get_operator_twin(operator_id: str, p: Principal = Depends(current_principal)):
    operator = await platform.get_operator(operator_id)
    if operator is None:
        raise NotFound("operator", operator_id)
    p.ensure_operator(operator_id, operator.site_id)
    return await twin.twin_service().get_twin(operator_id)


@router.get("/sites/{site_id}/twin", response_model=SiteTwin)
async def get_site_twin(site_id: str, p: Principal = Depends(require_permission("twin:read"))):
    p.ensure_site(site_id)
    return await twin.site_twin(site_id)


@router.get("/machines/{machine_id}/state", response_model=TwinMachineState)
async def get_machine_state(machine_id: str, p: Principal = Depends(current_principal)):
    view = await twin.machine_view(machine_id)
    machine = await platform.get_machine(machine_id)
    p.ensure_site(machine.site_id)
    return view
