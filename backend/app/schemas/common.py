"""Schemas shared by several domains (keep this file small: domain-specific schemas live in their domain)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DTO(BaseModel):
    """Base for response models built from ORM rows."""

    model_config = ConfigDict(from_attributes=True)


class GeoPoint(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)


class Page[T](BaseModel):
    items: list[T]
    total: int
    limit: int
    offset: int
