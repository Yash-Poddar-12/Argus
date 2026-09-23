"""Pure logic: task state machine, pre-check rules, fusion, simulator determinism."""

from datetime import UTC, datetime

import pytest

from backend.modules.m01_twin.tasks import domain
from backend.modules.m01_twin.twin import fusion
from simulator.core.engine import Simulation
from simulator.core.scenario import discover

START = datetime(2026, 9, 23, 2, 30, tzinfo=UTC)


def test_lifecycle_transitions():
    s = "PLANNED"
    for action, expected in [("assign", "ASSIGNED"), ("start", "IN_PROGRESS"), ("pause", "PAUSED"),
                             ("resume", "IN_PROGRESS"), ("complete", "COMPLETED")]:
        s = domain.next_status(s, action)
        assert s == expected
    for status, action in [("PLANNED", "start"), ("IN_PROGRESS", "resume"), ("COMPLETED", "pause"),
                           ("IN_PROGRESS", "cancel"), ("CANCELLED", "assign")]:
        with pytest.raises(domain.TransitionError):
            domain.next_status(status, action)
    assert domain.allowed_actions("IN_PROGRESS") == ["complete", "pause"]


def test_precheck_rules():
    items = [{"item_id": "seatbelt", "critical": True}, {"item_id": "cab_clean", "critical": False}]
    ok = domain.evaluate_precheck(items, [{"item_id": "seatbelt", "ok": True}, {"item_id": "cab_clean", "ok": False}])
    assert ok.passed and ok.failed_items == ["cab_clean"]
    bad = domain.evaluate_precheck(items, [{"item_id": "seatbelt", "ok": False}, {"item_id": "cab_clean", "ok": True}])
    assert not bad.passed
    missing = domain.evaluate_precheck(items, [{"item_id": "seatbelt", "ok": True}])
    assert not missing.passed and missing.missing_items == ["cab_clean"]


def _pt(ts, idle, cycles=10, mode="DIGGING"):
    return {"machine_id": "EXC001", "site_id": "SITE_A", "ts": ts, "operating_mode": mode, "fuel_pct": 60.0,
            "fuel_rate_lph": 14, "speed_kmh": 0, "rpm": 1600, "engine_hours": 10, "load_cycles": cycles,
            "idle_seconds": idle, "temperature_c": 85, "seatbelt": True, "lat": 1, "lon": 2}


def test_machine_state_folding_and_out_of_order():
    s1 = fusion.machine_state_from_telemetry(None, _pt("2026-09-23T02:30:00Z", 100))
    s2 = fusion.machine_state_from_telemetry(s1, _pt("2026-09-23T02:30:10Z", 105))
    assert s2["idle_window"] == [0.5] and s2["health"] == "OK"
    late = fusion.machine_state_from_telemetry(s2, _pt("2026-09-23T02:29:00Z", 0))
    assert late is s2  # late point doesn't regress live state
    hot = fusion.machine_state_from_telemetry(s2, {**_pt("2026-09-23T02:30:20Z", 105), "temperature_c": 106})
    assert hot["health"] == "CRITICAL"


def test_environmental_difficulty_and_intel_mapping():
    assert fusion.environmental_difficulty({"soil": "DRY", "visibility": "GOOD"}) == "LOW"
    assert fusion.environmental_difficulty({"soil": "WET", "rain_mm_h": 6.5, "visibility": "MODERATE"}) == "HIGH"
    slot, value = fusion.intelligence_from_event("prediction.task_time.updated",
                                                 {"task_id": "TASK001", "p50": 92, "confidence_level": "HIGH"}, "t")
    assert slot == "eta" and value["p50_duration_min"] == 92 and value["source"] == "M06"
    assert fusion.intelligence_from_event("something.else", {}, "t") is None


def test_simulator_is_deterministic():
    def run(seed):
        sim = Simulation(seed=seed, start=START, scenario=discover()["S1"]())
        return list(sim.run(900))

    a, b, c = run(42), run(42), run(7)
    assert a == b
    assert a != c
    kinds = {k for k, _ in a}
    assert kinds == {"telemetry", "conditions"}


def test_s6_rain_slows_excavator_cycles():
    def cycles_between(scenario_id, t0, t1):
        sim = Simulation(seed=42, start=START, machines=["EXC001"], scenario=discover()[scenario_id](), emit_every_s=60)
        pts = {int((datetime.fromisoformat(p["ts"].replace("Z", "+00:00")) - START).total_seconds()): p["load_cycles"]
               for k, p in sim.run(t1) if k == "telemetry"}
        return pts[t1] - pts[t0]

    normal = cycles_between("S1", 600, 3600)
    wet = cycles_between("S6", 600, 3600)
    assert wet < normal * 0.9, (normal, wet)


def test_scenarios_discovered_from_module_folders():
    found = discover()
    assert {"S1", "S6"} <= set(found)
    assert found["S6"].owner == "M01"
