"""Deterministic simulator: reproducibility, scenario effects, scenario discovery."""

from datetime import UTC, datetime

from app.iot.simulator.engine import Simulation
from app.iot.simulator.scenario import discover

START = datetime(2026, 9, 23, 2, 30, tzinfo=UTC)


def test_simulator_is_deterministic():
    def run(seed):
        sim = Simulation(seed=seed, start=START, scenario=discover()["S1"]())
        return list(sim.run(900))

    a, b, c = run(42), run(42), run(7)
    assert a == b
    assert a != c
    assert {k for k, _ in a} == {"telemetry", "conditions"}


def test_s6_rain_slows_excavator_cycles():
    def cycles_between(scenario_id, t0, t1):
        sim = Simulation(seed=42, start=START, machines=["EXC001"], scenario=discover()[scenario_id](), emit_every_s=60)
        pts = {int((datetime.fromisoformat(p["ts"].replace("Z", "+00:00")) - START).total_seconds()): p["load_cycles"]
               for k, p in sim.run(t1) if k == "telemetry"}
        return pts[t1] - pts[t0]

    normal = cycles_between("S1", 600, 3600)
    wet = cycles_between("S6", 600, 3600)
    assert wet < normal * 0.9, (normal, wet)


def test_scenarios_discovered_from_scenarios_package():
    found = discover()
    assert {"S1", "S6"} <= set(found)


def test_cli_lists_scenarios(capsys):
    from app.iot.simulator.cli import main

    assert main(["--list"]) == 0
    assert "S6" in capsys.readouterr().out
