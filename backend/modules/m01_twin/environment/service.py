"""Environment adapter (M01-WP5), mock-first.

Conditions arrive through ``set_conditions`` from the simulator (scenario S6), a supervisor, or a
future real provider. A provider is anything with ``async def fetch(site) -> EnvironmentConditions | None``;
set ``M01_WEATHER_PROVIDER`` when one exists (none is wired yet, by design: demo data must be deterministic).
"""

from __future__ import annotations

from typing import Protocol

from backend.core.db import utcnow
from backend.core.runtime import get_runtime
from backend.modules.m01_twin.models import EnvironmentEvent
from backend.modules.m01_twin.public import EnvironmentConditions, SiteConditions, TwinEnvironment
from backend.modules.m01_twin.twin import fusion
from backend.modules.m01_twin.twin.service import SOURCE, twin_service


class WeatherProvider(Protocol):
    async def fetch(self, site_id: str, lat: float, lon: float) -> EnvironmentConditions | None: ...


async def set_conditions(site_id: str, conditions: EnvironmentConditions, zone_id: str | None = None,
                         source: str = "MANUAL") -> dict:
    rt = get_runtime()
    now = utcnow()
    async with rt.db.sessionmaker() as s:
        s.add(EnvironmentEvent(site_id=site_id, zone_id=zone_id, ts=now, conditions=conditions.model_dump(), source=source))
        await s.commit()
    env = {**conditions.model_dump(), "zone_id": zone_id, "as_of": fusion.iso(now)}
    await rt.state.set_json(f"twin:env:{site_id}" + (f":{zone_id}" if zone_id else ""), env)
    await rt.bus.publish("environment.conditions.updated",
                         {**conditions.model_dump(), "site_id": site_id, "zone_id": zone_id, "source": source,
                          "as_of": fusion.iso(now)}, source_id=SOURCE, site_id=site_id)
    svc = twin_service()
    for op in await svc.operators_in_site(site_id):
        await svc.refresh(op, "environment")
    return env


async def site_conditions(site_id: str, zone_ids: list[str]) -> SiteConditions:
    svc = twin_service()
    site_env = await svc.environment(site_id, None)
    zones = {}
    for zid in zone_ids:
        env = await svc.environment(site_id, zid)
        if env and env.get("zone_id") == zid:
            zones[zid] = TwinEnvironment.model_validate(env)
    worst = site_env
    for z in zones.values():
        if fusion.environmental_difficulty(z.model_dump()) == "HIGH":
            worst = z.model_dump()
    return SiteConditions(site_id=site_id, site=TwinEnvironment.model_validate(site_env) if site_env else None, zones=zones,
                          environmental_difficulty=fusion.environmental_difficulty(worst))
