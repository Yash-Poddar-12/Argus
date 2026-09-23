"""Shared test fixtures (M00). Module tests live in backend/tests/<module>/.

Every test app runs with SQLite + in-memory bus/state and ``validate_events=True``: any event a
module publishes that doesn't match its contract fails the request (producer conformance).
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.core.app import create_app
from backend.core.config import Settings
from backend.modules.m00_platform.seed import DEMO_PASSWORD, seed_platform


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(app_env="test", database_url=f"sqlite+aiosqlite:///{tmp_path.as_posix()}/test.db",
                    validate_events=True, log_json=False, log_level="WARNING")


@pytest.fixture
def app(settings):
    return create_app(settings)


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        rt = app.state.runtime

        async def _seed():
            async with rt.db.sessionmaker() as s:
                await seed_platform(s)

        c.portal.call(_seed)
        yield c


@pytest.fixture
def runtime(app, client):
    return app.state.runtime


def login(client: TestClient, username: str, password: str = DEMO_PASSWORD) -> dict[str, str]:
    r = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def sup(client) -> dict[str, str]:
    return login(client, "sup001")


@pytest.fixture
def op1(client) -> dict[str, str]:
    return login(client, "op1001")


def token_of(headers: dict[str, str]) -> str:
    return headers["Authorization"].split(" ", 1)[1]
