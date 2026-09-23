"""Test helpers shared across test packages (import from here, never from another test module)."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.iot.simulator.engine import Simulation
from app.iot.simulator.scenario import discover
from app.seed.platform import DEMO_PASSWORD


def login(client: TestClient, username: str, password: str = DEMO_PASSWORD) -> dict[str, str]:
    r = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def token_of(headers: dict[str, str]) -> str:
    return headers["Authorization"].split(" ", 1)[1]


def recv_until(ws, msg_type: str, limit: int = 50) -> dict:
    for _ in range(limit):
        msg = ws.receive_json()
        if msg["type"] == msg_type:
            return msg
    raise AssertionError(f"no {msg_type} within {limit} messages")


def sim_points(seconds: float, machines=("EXC001", "DMP002"), start: datetime | None = None) -> list[dict]:
    sim = Simulation(seed=42, start=start or datetime.now(UTC), machines=list(machines), scenario=discover()["S1"](),
                     emit_every_s=10)
    return [p for kind, p in sim.run(seconds) if kind == "telemetry"]


def all_ok(client, headers, machine="EXC001") -> dict:
    items = client.get(f"/api/v1/machines/{machine}/precheck", headers=headers).json()["items"]
    return {"results": [{"item_id": i["item_id"], "ok": True} for i in items]}
