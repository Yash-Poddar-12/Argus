"""Live state store (M00): Redis in local/prod, in-memory in lite/test.

Key spaces are owned per module (docs/02-contracts/DATA_OWNERSHIP.md), e.g. ``twin:*`` by M01.
State here must always be rebuildable from the database and events.
"""

from __future__ import annotations

import fnmatch
import json
from typing import Any, Protocol


class StateStore(Protocol):
    async def get_json(self, key: str) -> Any | None: ...

    async def set_json(self, key: str, value: Any, ttl_s: int | None = None) -> None: ...

    async def delete(self, key: str) -> None: ...

    async def keys(self, pattern: str) -> list[str]: ...

    async def ping(self) -> bool: ...


class InMemoryStateStore:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    async def get_json(self, key: str) -> Any | None:
        raw = self._data.get(key)
        return json.loads(raw) if raw is not None else None

    async def set_json(self, key: str, value: Any, ttl_s: int | None = None) -> None:
        self._data[key] = json.dumps(value, default=str)

    async def delete(self, key: str) -> None:
        self._data.pop(key, None)

    async def keys(self, pattern: str) -> list[str]:
        return sorted(k for k in self._data if fnmatch.fnmatchcase(k, pattern))

    async def flush(self) -> None:
        self._data.clear()

    async def ping(self) -> bool:
        return True


class RedisStateStore:
    def __init__(self, redis) -> None:
        self._redis = redis

    async def get_json(self, key: str) -> Any | None:
        raw = await self._redis.get(key)
        return json.loads(raw) if raw is not None else None

    async def set_json(self, key: str, value: Any, ttl_s: int | None = None) -> None:
        await self._redis.set(key, json.dumps(value, default=str), ex=ttl_s)

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)

    async def keys(self, pattern: str) -> list[str]:
        return sorted(k.decode() if isinstance(k, bytes) else k async for k in self._redis.scan_iter(match=pattern))

    async def ping(self) -> bool:
        try:
            return bool(await self._redis.ping())
        except Exception:
            return False
