"""Pure context fusion: machine state folding, environmental difficulty, intelligence slot mapping."""

from app.domain.twin import fusion


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
