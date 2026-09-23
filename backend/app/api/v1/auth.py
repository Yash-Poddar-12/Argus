"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import Principal, current_principal, get_session
from app.domain.platform import service
from app.domain.platform.schemas import LoginRequest, MeResponse, TokenResponse

router = APIRouter(tags=["auth"])


@router.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest, session: AsyncSession = Depends(get_session)):
    return await service.login(session, body.username, body.password)


@router.get("/auth/me", response_model=MeResponse)
async def me(principal: Principal = Depends(current_principal)):
    return MeResponse(principal=principal, permissions=sorted(principal.permissions))
