"""Baseline scenarios: S1 normal operation, S6 environmental delay (master §84)."""

from __future__ import annotations

from app.iot.simulator.scenario import Scenario

CLEAR = {"weather": "CLEAR", "temperature_c": 31.0, "rain_mm_h": 0.0, "visibility": "GOOD", "soil": "DRY"}


class S1Normal(Scenario):
    id = "S1"
    title = "Normal operation"
    description = "Seatbelt on, normal speed, no proximity, normal idle."

    def configure(self, sim):
        sim.set_conditions(CLEAR)


class S6EnvironmentalDelay(Scenario):
    id = "S6"
    title = "Environmental delay"
    description = ("Rain starts after 5 minutes and Zone A becomes wet: excavator cycle time rises ~30% with no "
                   "change in operator behaviour (ground truth for the WHY? engine: ENVIRONMENT).")
    RAIN_AT_S = 300.0
    CYCLE_FACTOR = 1.3

    def configure(self, sim):
        sim.set_conditions(CLEAR)
        self._raining = False

    def on_tick(self, sim, t_s):
        if not self._raining and t_s >= self.RAIN_AT_S:
            self._raining = True
            sim.set_conditions({"weather": "RAIN", "temperature_c": 27.0, "rain_mm_h": 6.5, "visibility": "MODERATE",
                                "soil": "WET"})
            sim.set_conditions({"weather": "RAIN", "temperature_c": 27.0, "rain_mm_h": 6.5, "visibility": "MODERATE",
                                "soil": "WET"}, zone_id="ZONE_A")
            for m in sim.machines.values():
                if m.machine_type == "EXCAVATOR":
                    m.cycle_factor = self.CYCLE_FACTOR


SCENARIOS = [S1Normal, S6EnvironmentalDelay]
