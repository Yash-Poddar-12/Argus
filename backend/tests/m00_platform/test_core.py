"""Core infrastructure: event bus, discovery, WebSocket gateway, migrations, contracts."""

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.modules as modules_pkg
from backend.core.app import create_app
from backend.core.contracts import ContractError
from backend.core.events import Event, InMemoryEventBus, RedisStreamsEventBus
from backend.tests.conftest import login, token_of

ROOT = Path(__file__).resolve().parents[3]
OP_PAYLOAD = {"operator_id": "OP1001", "name": "R", "site_id": "SITE_A", "experience_level": "SENIOR",
              "certification_status": "VALID", "status": "ACTIVE"}


async def test_inmemory_bus_patterns_and_dedup():
    bus = InMemoryEventBus(validate=True)
    seen: list[str] = []

    async def handler(e: Event):
        seen.append(e.event_type)

    bus.subscribe("platform.operator.*", handler, group="m01_twin")
    event = await bus.publish("platform.operator.created", OP_PAYLOAD, source_id="t", site_id="SITE_A")
    await bus.publish_event(event)  # replay of the same event_id is ignored
    await bus.publish("platform.site.created", {"site_id": "SITE_A", "name": "A", "status": "ACTIVE"}, source_id="t")
    assert seen == ["platform.operator.created"]


async def test_bus_rejects_contract_violations():
    bus = InMemoryEventBus(validate=True)
    with pytest.raises(ContractError):
        await bus.publish("platform.operator.created", {"operator_id": "OP1001"}, source_id="t")
    with pytest.raises(ContractError):
        await bus.publish("no.such.event", {}, source_id="t")


async def test_handler_failure_is_isolated():
    bus = InMemoryEventBus()
    ok: list[str] = []

    async def boom(_):
        raise RuntimeError("x")

    async def fine(e):
        ok.append(e.event_id)

    bus.subscribe("a.b", boom, group="g1")
    bus.subscribe("a.b", fine, group="g2")
    await bus.publish("a.b", {}, source_id="t")
    assert len(ok) == 1


async def test_redis_streams_bus_with_consumer_groups():
    import fakeredis

    redis = fakeredis.FakeAsyncRedis()
    bus = RedisStreamsEventBus(redis, validate=True)
    got: dict[str, list[str]] = {"m01_twin": [], "m06_ml": []}

    def make(group):
        async def h(e: Event):
            got[group].append(e.event_id)
        return h

    bus.subscribe("platform.*", make("m01_twin"), group="m01_twin")
    bus.subscribe("platform.operator.created", make("m06_ml"), group="m06_ml")
    event = await bus.publish("platform.operator.created", OP_PAYLOAD, source_id="t")
    await bus.publish_event(event)  # edge-style replay
    await bus.drain()
    assert got == {"m01_twin": [event.event_id], "m06_ml": [event.event_id]}
    assert await bus.ping()


def test_module_auto_discovery_without_core_edits(tmp_path, settings, monkeypatch):
    pkg = tmp_path / "mzz_demo"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    (pkg / "module.py").write_text(textwrap.dedent("""
        from fastapi import APIRouter
        MODULE_ID = "MZZ"
        router = APIRouter()
        permissions = {"OPERATOR": ["demo:read"]}

        @router.get("/demo/ping")
        async def ping():
            return {"pong": True}
    """))
    monkeypatch.setattr(modules_pkg, "__path__", [*modules_pkg.__path__, str(tmp_path)])
    app = create_app(settings)
    with TestClient(app) as c:
        assert c.get("/api/v1/demo/ping").json() == {"pong": True}
        assert {"name": "mzz_demo", "id": "MZZ"} in c.get("/version").json()["modules"]
    sys.modules.pop("backend.modules.mzz_demo.module", None)
    sys.modules.pop("backend.modules.mzz_demo", None)


def test_websocket_channels_and_auth(client, runtime):
    op = login(client, "op1001")
    with client.websocket_connect(f"/ws/operators/OP1001?token={token_of(op)}") as ws:
        client.portal.call(runtime.ws.publish, "operators/OP1001", "TASK_UPDATE", {"task_id": "TASK001"})
        msg = ws.receive_json()
        assert msg["type"] == "TASK_UPDATE" and msg["data"] == {"task_id": "TASK001"}
    from starlette.websockets import WebSocketDisconnect

    with pytest.raises(WebSocketDisconnect) as denied:
        with client.websocket_connect(f"/ws/operators/OP1002?token={token_of(op)}") as ws:
            ws.receive_json()
    assert denied.value.code == 4403
    with pytest.raises(WebSocketDisconnect) as unauth:
        with client.websocket_connect("/ws/sites/SITE_A?token=bad") as ws:
            ws.receive_json()
    assert unauth.value.code == 4401


def test_alembic_heads_match_models(tmp_path):
    """Every table declared in models has a migration, across all module branches."""
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import create_engine, inspect

    import backend.core.audit  # noqa: F401
    from backend.core.db import Base
    from backend.core.registry import import_all_models

    db = tmp_path / "mig.db"
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.attributes["database_url"] = f"sqlite+aiosqlite:///{db.as_posix()}"
    command.upgrade(cfg, "heads")
    import_all_models()
    tables = set(inspect(create_engine(f"sqlite:///{db.as_posix()}")).get_table_names()) - {"alembic_version"}
    assert tables == set(Base.metadata.tables)


def test_contracts_valid_and_openapi_in_sync():
    for args in (["check"], ["export", "--check"]):
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "contracts.py"), *args], capture_output=True,
                           text=True, cwd=ROOT)
        assert r.returncode == 0, r.stdout + r.stderr
