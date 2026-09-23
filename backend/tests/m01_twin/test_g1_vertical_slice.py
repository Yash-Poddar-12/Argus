"""Gate G1 vertical slice through the real API + WebSocket (master §94):

Admin assigns OP1001 -> EXC001 -> TASK001 -> operator sees it -> simulator telemetry -> twin updates -> operator sees state.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta

from backend.core.contracts import CONTRACTS, validate_json
from backend.tests.conftest import login, token_of
from simulator.core.engine import Simulation
from simulator.core.scenario import discover

TWIN_SCHEMA = CONTRACTS / "schemas" / "twin" / "operational-twin.json"


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


def test_g1_vertical_slice(client, runtime, monkeypatch):
    sup, op = login(client, "sup001"), login(client, "op1001")
    runtime.bus.published.clear()
    assert client.get("/api/v1/operators/OP1001/tasks/today", headers=op).json() == []

    with client.websocket_connect(f"/ws/operators/OP1001?token={token_of(op)}") as ws:
        # 1. supervisor assigns -> operator gets TASK_UPDATE immediately
        t0 = time.perf_counter()
        r = client.post("/api/v1/assignments", headers=sup,
                        json={"task_id": "TASK001", "operator_id": "OP1001", "machine_id": "EXC001"})
        assert r.status_code == 201, r.text
        msg = recv_until(ws, "TASK_UPDATE")
        assert time.perf_counter() - t0 < 1.0
        assert msg["data"]["action"] == "assigned" and msg["data"]["task"]["status"] == "ASSIGNED"

        # 2. operator sees the task in today's list
        today = client.get("/api/v1/operators/OP1001/tasks/today", headers=op).json()
        assert [t["task"]["task_id"] for t in today] == ["TASK001"]
        assert today[0]["allowed_actions"] == ["start"]

        # 3. guarded start: machine confirm -> pre-check -> start
        r = client.post("/api/v1/tasks/TASK001/start", headers=op)
        assert r.status_code == 409 and r.json()["error"]["details"]["step"] == "machine_confirm"
        assert client.post("/api/v1/operators/OP1001/machine/confirm", headers=op,
                           json={"machine_id": "EXC001"}).status_code == 200
        assert client.post("/api/v1/tasks/TASK001/start", headers=op).json()["error"]["details"]["step"] == "precheck"
        bad = all_ok(client, op)
        bad["results"][0]["ok"] = False  # a critical item fails
        assert client.post("/api/v1/machines/EXC001/precheck", headers=op, json=bad).json()["passed"] is False
        assert client.post("/api/v1/tasks/TASK001/start", headers=op).status_code == 409
        assert client.post("/api/v1/machines/EXC001/precheck", headers=op, json=all_ok(client, op)).json()["passed"]
        r = client.post("/api/v1/tasks/TASK001/start", headers=op)
        assert r.status_code == 200, r.text
        assert r.json()["task"]["status"] == "IN_PROGRESS"

        # 4. simulator telemetry (as the supervisor/service account) -> twin updates -> operator WS
        session_start = datetime.fromisoformat(r.json()["session"]["actual_start"].replace("Z", "+00:00"))
        points = sim_points(600, start=session_start + timedelta(seconds=1))
        t0 = time.perf_counter()
        r = client.post("/api/v1/telemetry", headers=sup, json={"items": points})
        assert r.status_code == 202 and r.json()["accepted"] == len(points)
        twin_msg = recv_until(ws, "TWIN_UPDATE", limit=500)
        assert time.perf_counter() - t0 < 2.0
    twin = client.get("/api/v1/operators/OP1001/twin", headers=op).json()
    validate_json(TWIN_SCHEMA, twin)
    assert twin_msg["data"]["operator_id"] == "OP1001"
    assert twin["machine_id"] == "EXC001" and twin["task_id"] == "TASK001"
    assert twin["state"]["machine"]["operating_mode"] and twin["state"]["machine"]["load_cycles"] >= 1000
    assert twin["state"]["task"]["status"] == "IN_PROGRESS" and twin["state"]["task"]["cycles_done"] > 0
    assert twin["state"]["task"]["progress_pct"] > 0
    assert twin["state"]["environment"] is None and twin["intelligence"]["eta"] is None  # valid without M04/M06

    # 5. replaying the same batch is idempotent
    r = client.post("/api/v1/telemetry", headers=sup, json={"items": points[:5]})
    assert r.json() == {"received": 5, "accepted": 0, "duplicates": 5}

    # 6. pause/resume/complete + illegal transition + summary
    assert client.post("/api/v1/tasks/TASK001/resume", headers=op).status_code == 409
    assert client.post("/api/v1/tasks/TASK001/pause", headers=op).json()["session"]["status"] == "PAUSED"
    assert client.post("/api/v1/tasks/TASK001/resume", headers=op).json()["task"]["status"] == "IN_PROGRESS"
    from backend.modules.m01_twin.tasks import service as task_service

    last_ts = datetime.fromisoformat(points[-1]["ts"].replace("Z", "+00:00"))
    monkeypatch.setattr(task_service, "utcnow", lambda: last_ts + timedelta(seconds=5))  # complete after last reading
    done = client.post("/api/v1/tasks/TASK001/complete", headers=op)
    assert done.json()["task"]["status"] == "COMPLETED"
    summary = client.get("/api/v1/tasks/TASK001/summary", headers=op).json()
    assert summary["cycles_done"] > 0 and summary["fuel_used_pct"] > 0 and summary["finished_by_deadline"] is not None

    types = [e.event_type for e in runtime.bus.published]
    for expected in ["operator.task.assigned", "session.machine.confirmed", "session.precheck.completed", "task.started",
                     "machine.telemetry.received", "machine.state.changed", "twin.updated", "task.paused", "task.resumed",
                     "task.completed"]:
        assert expected in types, expected


def test_permissions_and_scoping(client):
    sup, op1, op2 = login(client, "sup001"), login(client, "op1001"), login(client, "op1002")
    body = {"operator_id": "OP1001", "machine_id": "EXC001"}
    assert client.post("/api/v1/tasks/TASK001/assign", headers=op1, json=body).status_code == 403
    assert client.post("/api/v1/tasks/TASK001/assign", headers=sup, json=body).status_code == 201
    dup = client.post("/api/v1/tasks/TASK001/assign", headers=sup, json={**body, "machine_id": "EXC002"})
    assert dup.status_code == 409
    assert client.post("/api/v1/tasks/TASK001/assign", headers=sup,
                       json={"operator_id": "OP1002", "machine_id": "EXC002", "replace": True}).status_code == 201
    assert client.get("/api/v1/tasks/TASK001", headers=op2).status_code == 200
    assert client.get("/api/v1/tasks/TASK002", headers=op2).status_code == 403
    assert client.get("/api/v1/operators/OP1001/twin", headers=op2).status_code == 403
    assert client.post("/api/v1/tasks/TASK001/start", headers=sup).status_code == 403
    assert client.post("/api/v1/operators/OP1002/machine/confirm", headers=op1,
                       json={"machine_id": "EXC002"}).status_code == 403
    assert client.post("/api/v1/telemetry", headers=op1, json={"items": sim_points(10, ("EXC001",))}).status_code == 403


def test_task_crud_and_validation(client, runtime):
    sup = login(client, "sup001")
    base = {"site_id": "SITE_A", "zone_id": "ZONE_A", "title": "Grade access road", "task_type": "GRADING",
            "target": {"unit": "minutes", "value": 60}, "planned_start": "2026-09-24T03:00:00Z",
            "planned_end": "2026-09-24T04:00:00Z"}
    r = client.post("/api/v1/tasks", headers=sup, json=base)
    assert r.status_code == 201 and r.json()["status"] == "PLANNED" and r.json()["task_id"].startswith("TASK_")
    tid = r.json()["task_id"]
    assert client.post("/api/v1/tasks", headers=sup, json={**base, "planned_end": "2026-09-24T02:00:00Z"}).status_code == 422
    assert client.post("/api/v1/tasks", headers=sup, json={**base, "zone_id": "NOPE"}).status_code == 422
    assert client.post("/api/v1/tasks", headers=sup, json={**base, "planned_start": "2026-09-24T03:00:00"}).status_code == 422
    r = client.patch(f"/api/v1/tasks/{tid}", headers=sup, json={"planned_end": "2026-09-24T05:00:00Z", "priority": "HIGH"})
    assert r.status_code == 200 and r.json()["priority"] == "HIGH"
    upd = [e for e in runtime.bus.published if e.event_type == "task.updated"][-1]
    assert sorted(upd.payload["changed_fields"]) == ["planned_end", "priority"]
    assert client.patch(f"/api/v1/tasks/{tid}", headers=sup, json={"status": "COMPLETED"}).status_code == 422
    assert client.patch(f"/api/v1/tasks/{tid}", headers=sup, json={"status": "CANCELLED"}).json()["status"] == "CANCELLED"
    listed = client.get("/api/v1/sites/SITE_A/tasks?status=CANCELLED", headers=sup).json()
    assert [t["task_id"] for t in listed] == [tid]


def test_assignment_update_and_cancel(client):
    sup, op = login(client, "sup001"), login(client, "op1001")
    a = client.post("/api/v1/tasks/TASK002/assign", headers=sup, json={"operator_id": "OP1001", "machine_id": "EXC001"}).json()
    r = client.patch(f"/api/v1/assignments/{a['assignment_id']}", headers=sup, json={"machine_id": "EXC002"})
    assert r.json()["machine_id"] == "EXC002"
    r = client.patch(f"/api/v1/assignments/{a['assignment_id']}", headers=sup, json={"status": "CANCELLED"})
    assert r.json()["status"] == "CANCELLED"
    assert client.get("/api/v1/tasks/TASK002", headers=sup).json()["status"] == "PLANNED"
    assert client.get("/api/v1/operators/OP1001/tasks/today", headers=op).json() == []
