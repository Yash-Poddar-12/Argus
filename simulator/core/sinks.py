"""Where simulated data goes: the platform API (HTTP), the backend in-process, or JSON lines (datasets)."""

from __future__ import annotations

import json
import sys
from typing import IO

import httpx


class HttpSink:
    """Posts telemetry batches and conditions to the platform API as a supervisor/service account."""

    def __init__(self, api: str, username: str, password: str, site_id: str = "SITE_A", batch: int = 20):
        self.client = httpx.Client(base_url=api.rstrip("/"), timeout=30)
        self.site_id = site_id
        self.batch = batch
        self.buffer: list[dict] = []
        r = self.client.post("/api/v1/auth/login", json={"username": username, "password": password})
        r.raise_for_status()
        self.client.headers["Authorization"] = f"Bearer {r.json()['access_token']}"
        self.sent = 0

    def telemetry(self, point: dict) -> None:
        self.buffer.append(point)
        if len(self.buffer) >= self.batch:
            self.flush()

    def conditions(self, item: dict) -> None:
        self.flush()
        body = {"conditions": item["conditions"], "zone_id": item.get("zone_id"), "source": "SIMULATOR"}
        self.client.post(f"/api/v1/sites/{self.site_id}/conditions", json=body).raise_for_status()

    def flush(self) -> None:
        if self.buffer:
            self.client.post("/api/v1/telemetry", json={"items": self.buffer}).raise_for_status()
            self.sent += len(self.buffer)
            self.buffer = []

    def close(self) -> None:
        self.flush()
        self.client.close()


class JsonlSink:
    def __init__(self, out: IO[str] | None = None):
        self.out = out or sys.stdout

    def telemetry(self, point: dict) -> None:
        self.out.write(json.dumps({"kind": "telemetry", **point}) + "\n")

    def conditions(self, item: dict) -> None:
        self.out.write(json.dumps({"kind": "conditions", **item}) + "\n")

    def flush(self) -> None:
        self.out.flush()

    def close(self) -> None:
        self.flush()


class InProcessSink:
    """Feeds a running backend in the same process (tests, embedded demos). Methods are async."""

    def __init__(self, site_id: str = "SITE_A"):
        self.site_id = site_id
        self.buffer: list[dict] = []

    async def telemetry(self, point: dict) -> None:
        self.buffer.append(point)

    async def conditions(self, item: dict) -> None:
        await self.flush()
        from backend.modules.m01_twin.environment.service import set_conditions
        from backend.modules.m01_twin.public import EnvironmentConditions

        await set_conditions(self.site_id, EnvironmentConditions(**item["conditions"]), item.get("zone_id"), "SIMULATOR")

    async def flush(self) -> None:
        if self.buffer:
            from backend.modules.m01_twin.public import TelemetryPoint, ingest_telemetry

            await ingest_telemetry([TelemetryPoint.model_validate(p) for p in self.buffer])
            self.buffer = []
