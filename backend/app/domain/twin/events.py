"""Event payloads produced by the twin. Schemas GENERATED into contracts/events/twin/."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TwinUpdatedPayload(BaseModel):
    operator_id: str
    machine_id: str | None = None
    task_id: str | None = None
    reason: str
    changed: list[str] = Field(description="Top-level twin sections that changed, e.g. state.machine")


EVENT_PAYLOADS: dict[str, type[BaseModel]] = {"twin.updated": TwinUpdatedPayload}
