"""Platform settings (M00).

Modules define their own settings classes with an env prefix (e.g. ``M07_``) instead of
adding fields here. Values come from the environment or a root ``.env`` file, which
``python scripts/dev.py env`` assembles from ``infra/env/*.env.example``.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["lite", "local", "test", "prod"] = "lite"
    app_version: str = "0.1.0"
    git_sha: str = "dev"

    # lite/test default to SQLite + in-memory bus/state so nothing else is needed to run.
    database_url: str = "sqlite+aiosqlite:///./.data/argus.db"
    db_auto_create: bool = True  # create tables from models (lite/test); use Alembic otherwise
    redis_url: str | None = None  # None -> in-memory state store and bus
    event_bus: Literal["memory", "redis"] = "memory"
    validate_events: bool = False  # validate every published payload against contracts/ (on in tests)

    jwt_secret: str = "dev-only-change-me-dev-only-change-me"
    jwt_ttl_minutes: int = 720
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    log_level: str = "INFO"
    log_json: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
