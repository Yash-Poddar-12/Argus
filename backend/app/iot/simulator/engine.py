"""Deterministic machine/site simulator.

Same ``seed`` + ``start`` + scenario => byte-identical telemetry on every machine and OS.
Per-machine randomness uses ``random.Random(seed ^ crc32(machine_id))`` (never Python's salted hash).
"""

from __future__ import annotations

import math
import random
import zlib
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from app.iot.simulator.scenario import Scenario

# SITE_A zone centres (lon, lat), matching app/seed/platform.py
ZONE_CENTRES = {"ZONE_A": (77.5946, 12.9716), "ZONE_B": (77.5962, 12.9716), "ZONE_DISPOSAL": (77.5980, 12.9730)}

EXCAVATOR_PHASES = [("DIGGING", 18.0), ("SWINGING", 12.0), ("DUMPING", 8.0), ("SWINGING", 12.0)]  # ~50 s cycle
DUMPER_PHASES = [("LOADING", 60.0), ("HAULING", 120.0), ("DUMPING", 30.0), ("RETURNING", 100.0)]  # ~5 min cycle
FUEL_LPH = {"DIGGING": 18, "SWINGING": 14, "DUMPING": 12, "LOADING": 6, "HAULING": 22, "RETURNING": 16, "IDLE": 4,
            "TRAVELLING": 12, "OFF": 0}
RPM = {"DIGGING": 1800, "SWINGING": 1600, "DUMPING": 1500, "LOADING": 1000, "HAULING": 1900, "RETURNING": 1700,
       "IDLE": 900, "TRAVELLING": 1500, "OFF": 0}
TEMP_TARGET = {"IDLE": 80.0, "OFF": 35.0}
TANK_L = {"EXCAVATOR": 400.0, "DUMPER": 600.0}


@dataclass
class MachineSim:
    machine_id: str
    machine_type: str  # EXCAVATOR | DUMPER
    rng: random.Random
    engine_hours: float
    load_cycles: int
    fuel_pct: float = 80.0
    idle_seconds: float = 5000.0
    temperature_c: float = 70.0
    zone: str = "ZONE_A"
    seatbelt: bool = True
    cycle_factor: float = 1.0          # >1 slows cycles (wet soil, drift)
    idle_probability: float = 0.08     # chance of a wait between cycles
    idle_range_s: tuple[float, float] = (20.0, 90.0)
    phase_index: int = 0
    phase_left: float = 0.0
    mode: str = "IDLE"
    speed_kmh: float = 0.0
    lat: float = 0.0
    lon: float = 0.0
    extra: dict = field(default_factory=dict)

    def phases(self):
        return EXCAVATOR_PHASES if self.machine_type == "EXCAVATOR" else DUMPER_PHASES


DEFAULT_MACHINES = {
    "EXC001": ("EXCAVATOR", 4210.5, "ZONE_A"),
    "EXC002": ("EXCAVATOR", 2875.0, "ZONE_B"),
    "DMP001": ("DUMPER", 6120.0, "ZONE_A"),
    "DMP002": ("DUMPER", 5980.0, "ZONE_A"),
}


class Simulation:
    def __init__(self, *, seed: int = 42, start: datetime | None = None, machines: list[str] | None = None,
                 scenario: Scenario | None = None, site_id: str = "SITE_A", tick_s: float = 1.0, emit_every_s: float = 5.0):
        self.seed = seed
        self.start = (start or datetime.now(UTC)).replace(microsecond=0)
        self.site_id = site_id
        self.tick_s = tick_s
        self.emit_every_s = emit_every_s
        self.scenario = scenario or Scenario()
        self.machines: dict[str, MachineSim] = {}
        self.pending_conditions: list[dict] = []
        for machine_id in machines or ["EXC001", "DMP001", "DMP002"]:
            mtype, hours, zone = DEFAULT_MACHINES.get(machine_id, ("EXCAVATOR", 1000.0, "ZONE_A"))
            rng = random.Random(seed ^ zlib.crc32(machine_id.encode()))
            m = MachineSim(machine_id=machine_id, machine_type=mtype, rng=rng, engine_hours=hours,
                           load_cycles=1000 + zlib.crc32(machine_id.encode()) % 500, zone=zone)
            m.lon, m.lat = ZONE_CENTRES[zone]
            self._enter_phase(m, 0)
            self.machines[machine_id] = m
        self.scenario.configure(self)

    # ---- scenario API ----
    def set_conditions(self, conditions: dict, zone_id: str | None = None) -> None:
        self.pending_conditions.append({"zone_id": zone_id, "conditions": conditions})

    def machine(self, machine_id: str) -> MachineSim:
        return self.machines[machine_id]

    # ---- mechanics ----
    def _enter_phase(self, m: MachineSim, index: int) -> None:
        name, base = m.phases()[index]
        m.phase_index, m.mode = index, name
        m.phase_left = base * m.cycle_factor * m.rng.uniform(0.9, 1.1)

    def _advance(self, m: MachineSim, dt: float) -> None:
        m.phase_left -= dt
        if m.mode == "IDLE":
            m.idle_seconds += dt
        if m.phase_left > 0:
            return
        if m.mode == "IDLE":
            self._enter_phase(m, 0)
            return
        if m.mode == "DUMPING":
            m.load_cycles += 1
        nxt = (m.phase_index + 1) % len(m.phases())
        if nxt == 0 and m.rng.random() < m.idle_probability:
            m.mode, m.phase_left, m.phase_index = "IDLE", m.rng.uniform(*m.idle_range_s), 0
            return
        self._enter_phase(m, nxt)

    def _physics(self, m: MachineSim, dt: float, t: float) -> None:
        tank = TANK_L[m.machine_type]
        m.fuel_pct = max(0.0, m.fuel_pct - FUEL_LPH[m.mode] * dt / 3600.0 / tank * 100.0)
        m.engine_hours += dt / 3600.0 if m.mode != "OFF" else 0.0
        target = TEMP_TARGET.get(m.mode, 92.0 if m.mode in ("DIGGING", "HAULING") else 88.0)
        m.temperature_c += (target - m.temperature_c) * min(1.0, dt / 120.0) + m.rng.gauss(0, 0.05)
        if m.machine_type == "DUMPER":
            (lon_a, lat_a), (lon_d, lat_d) = ZONE_CENTRES["ZONE_A"], ZONE_CENTRES["ZONE_DISPOSAL"]
            base = dict(DUMPER_PHASES)
            if m.mode in ("HAULING", "RETURNING"):
                total = base[m.mode] * m.cycle_factor
                frac = max(0.0, min(1.0, 1.0 - m.phase_left / total))
                frac = frac if m.mode == "HAULING" else 1.0 - frac
                m.lon, m.lat = lon_a + (lon_d - lon_a) * frac, lat_a + (lat_d - lat_a) * frac
                m.speed_kmh = 25.0 + m.rng.uniform(-3, 3) if m.mode == "HAULING" else 30.0 + m.rng.uniform(-3, 3)
            else:
                m.speed_kmh = 0.0
                m.lon, m.lat = (lon_d, lat_d) if m.mode == "DUMPING" else (lon_a, lat_a)
        else:
            cx, cy = ZONE_CENTRES[m.zone]
            m.lon = cx + 0.00005 * math.sin(t / 300.0)
            m.lat = cy + 0.00005 * math.cos(t / 300.0)
            m.speed_kmh = 0.0

    def point(self, m: MachineSim, ts: datetime) -> dict:
        return {
            "machine_id": m.machine_id, "ts": ts.isoformat().replace("+00:00", "Z"),
            "engine_hours": round(m.engine_hours, 3), "fuel_pct": round(m.fuel_pct, 3),
            "fuel_rate_lph": float(FUEL_LPH[m.mode]), "load_cycles": m.load_cycles,
            "idle_seconds": round(m.idle_seconds, 1), "speed_kmh": round(m.speed_kmh, 2),
            "rpm": float(RPM[m.mode]) + round(m.rng.uniform(-20, 20), 1) * (m.mode != "OFF"),
            "temperature_c": round(m.temperature_c, 2), "lat": round(m.lat, 7), "lon": round(m.lon, 7),
            "operating_mode": m.mode, "seatbelt": m.seatbelt,
        }

    def run(self, duration_s: float) -> Iterator[tuple[str, dict]]:
        """Yields ("conditions", {...}) and ("telemetry", point) in time order."""
        steps = int(duration_s / self.tick_s)
        next_emit = 0.0
        for i in range(steps + 1):
            t = i * self.tick_s
            ts = self.start + timedelta(seconds=t)
            self.scenario.on_tick(self, t)
            while self.pending_conditions:
                c = self.pending_conditions.pop(0)
                yield "conditions", {**c, "ts": ts.isoformat().replace("+00:00", "Z")}
            if i > 0:
                for m in self.machines.values():
                    self._advance(m, self.tick_s)
                    self._physics(m, self.tick_s, t)
            if t + 1e-9 >= next_emit:
                for m in self.machines.values():
                    yield "telemetry", self.point(m, ts)
                next_emit += self.emit_every_s
