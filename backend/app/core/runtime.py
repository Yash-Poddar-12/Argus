"""Shared runtime services: DB, event bus, state store, WS gateway.

Built once per process by ``create_app``. Endpoints use app/dependencies.py; services, event handlers
and background jobs call ``get_runtime()``. Nothing else constructs engines, buses or Redis clients.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.config import Settings
from app.core.cache import InMemoryStateStore, RedisStateStore, StateStore
from app.core.database import Database
from app.core.events import EventBus, InMemoryEventBus, RedisStreamsEventBus
from app.core.websocket import WebSocketGateway


@dataclass
class Runtime:
    settings: Settings
    db: Database
    bus: EventBus
    state: StateStore
    ws: WebSocketGateway
    capabilities: list[str] = field(default_factory=list)
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
