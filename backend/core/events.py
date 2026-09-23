"""Event fabric abstraction (M00).

``EventBus`` is the only way modules talk asynchronously. Implementations:

* ``InMemoryEventBus``: lite mode and tests. Handlers run inline, in subscription order.
* ``RedisStreamsEventBus``: one stream (``bus:events``) with a consumer group per module.

Both deliver the envelope from ``contracts/schemas/common/event-envelope.json`` and
deduplicate per consumer group on ``event_id`` (edge replay can redeliver events).
Swap for Kafka/NATS later behind the same interface (ADR-0001).
"""

from __future__ import annotations

import asyncio
import contextlib
import fnmatch
import json
from collections import OrderedDict
from collections.abc import Awaitable, Callable
from typing import Any, Protocol

from pydantic import BaseModel, Field

from backend.core.contracts import validate_event_payload
from backend.core.db import new_id, utcnow
from backend.core.logging import get_logger

log = get_logger(__name__)


class Event(BaseModel):
    event_id: str = Field(default_factory=new_id)
    event_type: str
    event_version: str = "1.0"
    timestamp: str = Field(default_factory=lambda: utcnow().isoformat().replace("+00:00", "Z"))
    site_id: str | None = None
    source_id: str
    correlation_id: str | None = None
    payload: dict[str, Any]


Handler = Callable[[Event], Awaitable[None]]


class EventBus(Protocol):
    async def publish(
        self, event_type: str, payload: dict, *, source_id: str, site_id: str | None = None,
        version: str = "1.0", correlation_id: str | None = None,
    ) -> Event: ...

    async def publish_event(self, event: Event) -> Event: ...

    def subscribe(self, pattern: str, handler: Handler, *, group: str) -> None: ...

    async def start(self) -> None: ...

    async def stop(self) -> None: ...

    async def ping(self) -> bool: ...


class _Dedup:
    """Bounded per-group memory of processed event IDs."""

    def __init__(self, size: int = 50_000):
        self._seen: OrderedDict[str, None] = OrderedDict()
        self._size = size

    def first_time(self, event_id: str) -> bool:
        if event_id in self._seen:
            return False
        self._seen[event_id] = None
        if len(self._seen) > self._size:
            self._seen.popitem(last=False)
        return True


class _BaseBus:
    def __init__(self, validate: bool = False):
        self._subs: list[tuple[str, Handler, str]] = []
        self._dedup: dict[str, _Dedup] = {}
        self._validate = validate
        self.published: list[Event] = []  # kept for tests/inspection (bounded)

    def subscribe(self, pattern: str, handler: Handler, *, group: str) -> None:
        self._subs.append((pattern, handler, group))
        self._dedup.setdefault(group, _Dedup())

    async def publish(self, event_type, payload, *, source_id, site_id=None, version="1.0", correlation_id=None):
        event = Event(event_type=event_type, event_version=version, payload=payload, source_id=source_id,
                      site_id=site_id, correlation_id=correlation_id)
        return await self.publish_event(event)

    def _check(self, event: Event) -> None:
        if self._validate:
            validate_event_payload(event.event_type, event.event_version, event.payload)
        self.published.append(event)
        if len(self.published) > 1000:
            del self.published[:500]

    async def _dispatch(self, event: Event, only_group: str | None = None) -> None:
        for pattern, handler, group in self._subs:
            if only_group and group != only_group:
                continue
            if not fnmatch.fnmatchcase(event.event_type, pattern):
                continue
            if not self._dedup[group].first_time(f"{event.event_id}:{id(handler)}"):
                continue
            try:
                await handler(event)
            except Exception:
                log.exception("event handler failed", extra={"event_id": event.event_id, "app_module": group})


class InMemoryEventBus(_BaseBus):
    async def publish_event(self, event: Event) -> Event:
        self._check(event)
        await self._dispatch(event)
        return event

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    async def ping(self) -> bool:
        return True


class RedisStreamsEventBus(_BaseBus):
    STREAM = "bus:events"

    def __init__(self, redis, validate: bool = False, consumer: str = "backend-1", maxlen: int = 100_000):
        super().__init__(validate)
        self._redis = redis
        self._consumer = consumer
        self._maxlen = maxlen
        self._tasks: list[asyncio.Task] = []

    async def publish_event(self, event: Event) -> Event:
        self._check(event)
        await self._redis.xadd(self.STREAM, {"e": event.model_dump_json()}, maxlen=self._maxlen, approximate=True)
        return event

    async def start(self) -> None:
        for group in {g for _, _, g in self._subs}:
            with contextlib.suppress(Exception):  # BUSYGROUP: group exists
                await self._redis.xgroup_create(self.STREAM, group, id="$", mkstream=True)
            self._tasks.append(asyncio.create_task(self._consume(group), name=f"bus:{group}"))

    async def _consume(self, group: str) -> None:
        while True:
            try:
                batches = await self._redis.xreadgroup(group, self._consumer, {self.STREAM: ">"}, count=100, block=1000)
                for _stream, messages in batches or []:
                    for msg_id, fields in messages:
                        raw = fields.get(b"e") or fields.get("e")
                        await self._dispatch(Event.model_validate(json.loads(raw)), only_group=group)
                        await self._redis.xack(self.STREAM, group, msg_id)
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("bus consumer error", extra={"app_module": group})
                await asyncio.sleep(1)

    async def drain(self) -> None:
        """Process everything currently pending (used by tests)."""
        for group in {g for _, _, g in self._subs}:
            with contextlib.suppress(Exception):
                await self._redis.xgroup_create(self.STREAM, group, id="0", mkstream=True)
            batches = await self._redis.xreadgroup(group, self._consumer, {self.STREAM: ">"}, count=1000)
            for _stream, messages in batches or []:
                for msg_id, fields in messages:
                    raw = fields.get(b"e") or fields.get("e")
                    await self._dispatch(Event.model_validate(json.loads(raw)), only_group=group)
                    await self._redis.xack(self.STREAM, group, msg_id)

    async def stop(self) -> None:
        for task in self._tasks:
            task.cancel()
        for task in self._tasks:
            with contextlib.suppress(asyncio.CancelledError):
                await task
        self._tasks.clear()

    async def ping(self) -> bool:
        try:
            return bool(await self._redis.ping())
        except Exception:
            return False
