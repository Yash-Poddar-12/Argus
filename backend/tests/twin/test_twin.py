"""Twin behaviour: intelligence slots from other modules, rebuildability, environment, site twin, tools."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from functools import partial

import pytest

from app.copilot.tools import TOOL_SPECS, call_tool
from app.core.contracts import CONTRACTS, validate_json
from app.domain.twin.service import twin_service
from tests.helpers import all_ok, login, recv_until, sim_points, token_of

TWIN_SCHEMA = CONTRACTS / "schemas" / "twin" / "operational-twin.json"


@pytest.fixture
def running(client):
    """OP1001 on EXC001 working TASK001 with 5 minutes of telemetry."""
    sup, op = login(client, "sup001"), login(client, "op1001")
    client.post("/api/v1/tasks/TASK001/assign", headers=sup, json={"operator_id": "OP1001", "machine_id": "EXC001"})
    client.post("/api/v1/operators/OP1001/machine/confirm", headers=op, json={"machine_id": "EXC001"})
    client.post("/api/v1/machines/EXC001/precheck", headers=op, json=all_ok(client, op))
    r = client.post("/api/v1/tasks/TASK001/start", headers=op)
    start = datetime.fromisoformat(r.json()["session"]["actual_start"].replace("Z", "+00:00"))
    client.post("/api/v1/telemetry", headers=sup, json={"items": sim_points(300, start=start + timedelta(seconds=1))})
    return sup, op


def test_intelligence_slots_filled_by_other_modules(client, runtime, running, monkeypatch):
    sup, op = running
    monkeypatch.setattr(runtime.bus, "_validate", False)  # stand-in producers: M04/M06 contracts don't exist yet
    with client.websocket_connect(f"/ws/operators/OP1001?token={token_of(op)}") as ws:
        eta = {"operator_id": "OP1001", "task_id": "TASK001", "p50": 92, "p80": 104, "p90": 111,
               "confidence_level": "HIGH", "contributors": [{"feature": "wet_soil", "contribution": 7}],
               "model_version": "mock-0.1"}
        client.portal.call(partial(runtime.bus.publish, "prediction.task_time.updated", eta, source_id="m06_ml_mock"))
        msg = recv_until(ws, "TASK_ETA_UPDATED")
        assert msg["data"]["eta"]["p50_duration_min"] == 92
    client.portal.call(partial(runtime.bus.publish, "safety.event.raised",
                               {"operator_id": "OP1001", "severity": "HIGH", "event_type": "SEATBELT_UNFASTENED",
                                "safety_event_id": "se-1"}, source_id="m04_mock"))
    twin = client.get("/api/v1/operators/OP1001/twin", headers=op).json()
    validate_json(TWIN_SCHEMA, twin)
    assert twin["intelligence"]["eta"]["source"] == "M06" and twin["intelligence"]["eta"]["p80_duration_min"] == 104
    assert twin["intelligence"]["safety"] == {**twin["intelligence"]["safety"], "level": "HIGH", "source": "M04"}
    assert twin["state"]["operator"]["machine_familiarity"] == "LOW"


def test_twin_rebuilds_after_cache_flush(client, runtime, running, monkeypatch):
    sup, op = running
    monkeypatch.setattr(runtime.bus, "_validate", False)  # stand-in M06 producer
    client.portal.call(partial(runtime.bus.publish, "prediction.risk.updated",
                               {"operator_id": "OP1001", "risk_level": "LOW", "risk_probability": 0.08, "model_version": "m"},
                               source_id="m06_ml_mock"))
    before = client.get("/api/v1/operators/OP1001/twin", headers=op).json()
    client.portal.call(twin_service().flush_cache)
    assert client.portal.call(runtime.state.keys, "twin:*") == []
    after = client.get("/api/v1/operators/OP1001/twin", headers=op).json()

    def stable(t):
        t = json.loads(json.dumps(t))
        t.pop("as_of"), t.pop("freshness")
        t["state"]["site"].pop("active_machines")  # live-only count: recovers with the next telemetry
        t["intelligence"].pop("productivity")      # needs a window of recent readings
        return t

    assert stable(after) == stable(before)
    assert after["intelligence"]["risk"]["probability"] == 0.08


def test_environment_conditions_flow_into_twin(client, runtime, running):
    sup, op = running
    wet = {"weather": "RAIN", "temperature_c": 27, "rain_mm_h": 6.5, "visibility": "MODERATE", "soil": "WET"}
    assert client.post("/api/v1/sites/SITE_A/conditions", headers=op, json={"conditions": wet}).status_code == 403
    assert client.post("/api/v1/sites/SITE_A/conditions", headers=sup,
                       json={"conditions": wet, "zone_id": "ZONE_A"}).status_code == 201
    conditions = client.get("/api/v1/sites/SITE_A/conditions", headers=op).json()
    assert conditions["zones"]["ZONE_A"]["soil"] == "WET" and conditions["environmental_difficulty"] == "HIGH"
    twin = client.get("/api/v1/operators/OP1001/twin", headers=op).json()
    assert twin["state"]["environment"]["zone_id"] == "ZONE_A"
    assert twin["intelligence"]["environmental_difficulty"] == "HIGH"
    assert any(e.event_type == "environment.conditions.updated" for e in runtime.bus.published)


def test_site_twin_and_machine_endpoints(client, running):
    sup, op = running
    site = client.get("/api/v1/sites/SITE_A/twin", headers=sup).json()
    assert [t["operator_id"] for t in site["operators"]] == ["OP1001"]
    assert {m["machine_id"] for m in site["machines"]} == {"EXC001", "DMP002"}
    assert client.get("/api/v1/sites/SITE_A/twin", headers=op).status_code == 403
    state = client.get("/api/v1/machines/DMP002/state", headers=op).json()
    assert state["machine_type"] == "DUMPER" and state["operating_mode"]
    history = client.get("/api/v1/machines/EXC001/telemetry?limit=5", headers=op).json()
    assert len(history) == 5 and history[0]["ts"] < history[-1]["ts"]


def test_supervisor_site_ws_receives_machine_updates(client, runtime, running):
    sup, _ = running
    with client.websocket_connect(f"/ws/sites/SITE_A?token={token_of(sup)}") as ws:
        start = datetime.now(UTC) + timedelta(hours=1)
        client.post("/api/v1/telemetry", headers=sup, json={"items": sim_points(20, ("DMP001",), start=start)})
        assert recv_until(ws, "MACHINE_STATE_UPDATE")["data"]["machine_id"] == "DMP001"


@pytest.mark.parametrize("tool,args", [
    ("get_current_machine_state", {"machine_id": "EXC001"}),
    ("get_current_task", {"operator_id": "OP1001"}),
    ("get_task_progress", {"task_id": "TASK001"}),
    ("get_machine_health", {"machine_id": "EXC001"}),
    ("get_weather", {"site_id": "SITE_A"}),
    ("get_site_conditions", {"site_id": "SITE_A"}),
])
def test_copilot_tools_match_contracts(client, running, tool, args):
    sup, _ = running
    client.post("/api/v1/sites/SITE_A/conditions", headers=sup, json={"conditions": {"soil": "WET"}})
    out = client.portal.call(call_tool, tool, args)
    validate_json(CONTRACTS / "tools" / f"{tool}.json", {"input": args, "output": out})
    assert set(TOOL_SPECS) == {p.stem for p in (CONTRACTS / "tools").glob("*.json") if not p.name.startswith("_")}


def test_twin_on_redis_state_store(settings):
    """Same flow with the Redis state store (docker/prod path) instead of the in-memory one."""
    import fakeredis
    from fastapi.testclient import TestClient

    from app.core.cache import RedisStateStore
    from app.core.runtime import build_runtime
    from app.main import create_app
    from app.seed import seed_all

    rt = build_runtime(settings, redis=fakeredis.FakeAsyncRedis())
    assert isinstance(rt.state, RedisStateStore)
    with TestClient(create_app(settings, runtime=rt)) as client:
        client.portal.call(seed_all, rt.db)
        sup, op = login(client, "sup001"), login(client, "op1001")
        client.post("/api/v1/tasks/TASK001/assign", headers=sup, json={"operator_id": "OP1001", "machine_id": "EXC001"})
        client.post("/api/v1/operators/OP1001/machine/confirm", headers=op, json={"machine_id": "EXC001"})
        client.post("/api/v1/machines/EXC001/precheck", headers=op, json=all_ok(client, op))
        r = client.post("/api/v1/tasks/TASK001/start", headers=op)
        start = datetime.fromisoformat(r.json()["session"]["actual_start"].replace("Z", "+00:00"))
        client.post("/api/v1/telemetry", headers=sup, json={"items": sim_points(120, start=start + timedelta(seconds=1))})
        twin = client.get("/api/v1/operators/OP1001/twin", headers=op).json()
        validate_json(TWIN_SCHEMA, twin)
        assert twin["state"]["task"]["cycles_done"] is not None
        assert "twin:operator:OP1001" in client.portal.call(rt.state.keys, "twin:operator:*")
