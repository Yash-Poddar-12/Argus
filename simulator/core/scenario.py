"""Scenario plugin interface (M01 core; scenarios are owned per module).

Any module adds scenarios under ``simulator/scenarios/<module>/`` in a file that defines
``SCENARIOS = [MyScenario, ...]``. Discovery is automatic, so no core file is edited.

A scenario tweaks the world (machine behaviour, conditions, seatbelt, positions) through
the ``Simulation`` API; it never talks to the backend directly.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simulator.core.engine import Simulation


class Scenario:
    id: str = "S0"
    title: str = "base"
    description: str = ""
    owner: str = "M01"

    def configure(self, sim: Simulation) -> None:
        """Called once before the first tick."""

    def on_tick(self, sim: Simulation, t_s: float) -> None:
        """Called every tick with seconds since start."""


def discover() -> dict[str, type[Scenario]]:
    import simulator.scenarios as pkg

    found: dict[str, type[Scenario]] = {}
    for group in pkgutil.iter_modules(pkg.__path__):
        if not group.ispkg:
            continue
        sub = importlib.import_module(f"{pkg.__name__}.{group.name}")
        for mod_info in pkgutil.iter_modules(sub.__path__):
            mod = importlib.import_module(f"{sub.__name__}.{mod_info.name}")
            for cls in getattr(mod, "SCENARIOS", []):
                if cls.id in found:
                    raise RuntimeError(f"Duplicate scenario id {cls.id} ({cls} vs {found[cls.id]})")
                found[cls.id] = cls
    return found
