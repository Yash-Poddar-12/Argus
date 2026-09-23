"""Scenario plugin interface.

Add scenarios as a file in ``app/iot/simulator/scenarios/`` (one file per theme, e.g. baseline.py,
hazard.py, site.py, behavior.py) that defines ``SCENARIOS = [MyScenario, ...]``. Discovery is automatic.

A scenario tweaks the world (machine behaviour, conditions, seatbelt, positions) through
the ``Simulation`` API; it never talks to the backend directly.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.iot.simulator.engine import Simulation


class Scenario:
    id: str = "S0"
    title: str = "base"
    description: str = ""
    owner: str = "twin"

    def configure(self, sim: Simulation) -> None:
        """Called once before the first tick."""

    def on_tick(self, sim: Simulation, t_s: float) -> None:
        """Called every tick with seconds since start."""


def discover() -> dict[str, type[Scenario]]:
    import app.iot.simulator.scenarios as pkg

    found: dict[str, type[Scenario]] = {}
    for mod_info in sorted(pkgutil.iter_modules(pkg.__path__), key=lambda m: m.name):
        mod = importlib.import_module(f"{pkg.__name__}.{mod_info.name}")
        for cls in getattr(mod, "SCENARIOS", []):
            if cls.id in found:
                raise RuntimeError(f"Duplicate scenario id {cls.id} ({cls} vs {found[cls.id]})")
            found[cls.id] = cls
    return found
