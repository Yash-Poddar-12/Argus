"""Site/zone environment conditions."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Level = Literal["LOW", "MEDIUM", "HIGH"]


class EnvironmentConditions(BaseModel):
    weather: Literal["CLEAR", "CLOUDY", "RAIN", "STORM", "FOG"] = "CLEAR"
    temperature_c: float = 30.0
    rain_mm_h: float = Field(0.0, ge=0)
    visibility: Literal["GOOD", "MODERATE", "POOR"] = "GOOD"
    soil: Literal["DRY", "WET", "MUD", "ROCKY"] = "DRY"


class TwinEnvironment(EnvironmentConditions):
    """Conditions as recorded for a site or zone (name kept for API compatibility)."""

    zone_id: str | None = None
    as_of: datetime | None = None


class SiteConditions(BaseModel):
    site_id: str
    site: TwinEnvironment | None = None
    zones: dict[str, TwinEnvironment] = {}
    environmental_difficulty: Level | None = None


class ConditionsUpdate(BaseModel):
    conditions: EnvironmentConditions
    zone_id: str | None = None
    source: str = "MANUAL"
