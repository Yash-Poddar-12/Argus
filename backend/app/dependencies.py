"""FastAPI dependencies shared by all API routers."""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import StateStore
from app.core.events import EventBus
from app.core.runtime import get_runtime
from app.core.security import Principal, current_principal, require_permission
from app.core.websocket import WebSocketGateway


async def get_session() -> AsyncIterator[AsyncSession]:
    async with get_runtime().db.sessionmaker() as session:
        yield session


def get_bus() -> EventBus:
    return get_runtime().bus


def get_state() -> StateStore:
    return get_runtime().state


def get_ws() -> WebSocketGateway:
    return get_runtime().ws


__all__ = ["Principal", "current_principal", "get_bus", "get_session", "get_state", "get_ws", "require_permission"]
