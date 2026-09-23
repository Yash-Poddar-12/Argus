"""WebSocket gateway (M00).

Channels: ``operators/{operator_id}``, ``machines/{machine_id}``, ``sites/{site_id}``.
Endpoint: ``/ws/{kind}/{id}?token=<jwt>``. Message shape:
``{"type": "SAFETY_ALERT", "version": "1.0", "timestamp": "...", "data": {...}}``.

Producers call ``ws.publish(channel, type, data)``; message types are owned by the producing
module (docs/02-contracts/API_CATALOG.md). Fan-out is in-process; add Redis pub/sub when
running more than one backend replica.
"""

from __future__ import annotations

import asyncio
import contextlib
from collections import defaultdict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.database import utcnow
from app.core.exceptions import AppError
from app.core.logging import get_logger
from app.core.security import Principal, decode_token

log = get_logger(__name__)
KINDS = {"operators", "machines", "sites"}


class WebSocketGateway:
    def __init__(self) -> None:
        self._conns: dict[str, set[WebSocket]] = defaultdict(set)
        self.sent: list[tuple[str, dict]] = []  # recent messages, for tests/inspection
        self._lock = asyncio.Lock()
        self.site_of: dict[str, str] = {}  # entity channel -> site_id (for supervisor scope), filled by producers

    async def connect(self, channel: str, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._conns[channel].add(ws)

    async def disconnect(self, channel: str, ws: WebSocket) -> None:
        async with self._lock:
            self._conns[channel].discard(ws)

    async def publish(self, channel: str, type_: str, data: dict, version: str = "1.0") -> None:
        msg = {"type": type_, "version": version, "timestamp": utcnow().isoformat().replace("+00:00", "Z"),
               "channel": channel, "data": data}
        self.sent.append((channel, msg))
        if len(self.sent) > 1000:
            del self.sent[:500]
        for ws in list(self._conns.get(channel, ())):
            try:
                await ws.send_json(msg)
            except Exception:
                await self.disconnect(channel, ws)

    def connections(self, channel: str) -> int:
        return len(self._conns.get(channel, ()))


def authorize_channel(p: Principal, kind: str, entity_id: str, site_of: dict[str, str]) -> bool:
    if kind not in KINDS:
        return False
    if kind == "sites":
        return p.role == "SUPERVISOR_ADMIN" and entity_id in p.site_ids
    if kind == "operators" and p.role == "OPERATOR":
        return p.operator_id == entity_id
    site = site_of.get(f"{kind}/{entity_id}")
    return site is None or site in p.site_ids


def build_ws_router(gateway: WebSocketGateway) -> APIRouter:
    router = APIRouter()

    @router.websocket("/ws/{kind}/{entity_id}")
    async def ws_endpoint(ws: WebSocket, kind: str, entity_id: str, token: str | None = None):
        try:
            principal = decode_token(token or "")
        except AppError:
            await ws.close(code=4401)
            return
        if not authorize_channel(principal, kind, entity_id, gateway.site_of):
            await ws.close(code=4403)
            return
        channel = f"{kind}/{entity_id}"
        await gateway.connect(channel, ws)
        try:
            while True:
                text = await ws.receive_text()  # clients may send pings; ignore content
                if text == "ping":
                    await ws.send_json({"type": "PONG"})
        except WebSocketDisconnect:
            pass
        finally:
            with contextlib.suppress(Exception):
                await gateway.disconnect(channel, ws)

    return router
