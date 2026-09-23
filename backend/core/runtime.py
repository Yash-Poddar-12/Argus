"""Shared runtime services (M00): DB, event bus, state store, WS gateway.

Endpoints use the FastAPI dependencies below. Event handlers and background jobs use
``get_runtime()``. Modules never construct their own engines, buses or Redis clients.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import Settings
from backend.core.db import Database
from backend.core.events import EventBus, InMemoryEventBus, RedisStreamsEventBus
from backend.core.state import InMemoryStateStore, RedisStateStore, StateStore
from backend.core.ws import WebSocketGateway


@dataclass
class Runtime:
    settings: Settings
    db: Database
    bus: EventBus
    state: StateStore
    ws: WebSocketGateway
    modules: list[str] = field(default_factory=list)
    redis: object | None = None

    async def close(self) -> None:
        await self.bus.stop()
        await self.db.dispose()
        if self.redis is not None:
            await self.redis.aclose()


_current: Runtime | None = None


def build_runtime(settings: Settings, redis=None) -> Runtime:
    if redis is None and settings.redis_url:
        import redis.asyncio as aioredis

        redis = aioredis.from_url(settings.redis_url)
    if settings.event_bus == "redis":
        if redis is None:
            raise RuntimeError("event_bus=redis requires REDIS_URL")
        bus: EventBus = RedisStreamsEventBus(redis, validate=settings.validate_events)
    else:
        bus = InMemoryEventBus(validate=settings.validate_events)
    state: StateStore = RedisStateStore(redis) if redis is not None else InMemoryStateStore()
    return Runtime(settings=settings, db=Database(settings.database_url), bus=bus, state=state,
                   ws=WebSocketGateway(), redis=redis)


def set_runtime(rt: Runtime | None) -> None:
    global _current
    _current = rt


def get_runtime() -> Runtime:
    if _current is None:
        raise RuntimeError("Runtime not initialised (app not started)")
    return _current


# ---- FastAPI dependencies ----

async def get_session() -> AsyncIterator[AsyncSession]:
    async with get_runtime().db.sessionmaker() as session:
        yield session


def get_bus() -> EventBus:
    return get_runtime().bus


def get_state() -> StateStore:
    return get_runtime().state


def get_ws() -> WebSocketGateway:
    return get_runtime().ws
