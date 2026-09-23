"""Shared test fixtures. Tests are grouped by capability: core/, platform/, tasks/, twin/, iot/, integration/.

Every test app runs with SQLite + in-memory bus/state and ``validate_events=True``: any event a
module publishes that doesn't match its contract fails the request (producer conformance).
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.seed import seed_all
from tests.helpers import login


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
        c.portal.call(seed_all, app.state.runtime.db)
        yield c


@pytest.fixture
def runtime(app, client):
    return app.state.runtime


@pytest.fixture
def sup(client) -> dict[str, str]:
    return login(client, "sup001")


@pytest.fixture
def op1(client) -> dict[str, str]:
    return login(client, "op1001")
