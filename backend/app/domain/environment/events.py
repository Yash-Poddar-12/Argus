"""Event payloads produced by the environment domain. Schemas GENERATED into contracts/events/environment/."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.domain.environment.schemas import EnvironmentConditions


class EnvironmentUpdatedPayload(EnvironmentConditions):
    site_id: str
    zone_id: str | None = None
    source: str = "MANUAL"
    as_of: datetime


EVENT_PAYLOADS: dict[str, type[BaseModel]] = {"environment.conditions.updated": EnvironmentUpdatedPayload}
