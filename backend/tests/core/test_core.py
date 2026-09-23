"""Core infrastructure: event bus, discovery, WebSocket gateway, migrations, contracts."""

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.api.v1 as v1_pkg
import app.domain as domain_pkg
from app.core.contracts import ContractError
from app.core.events import Event, InMemoryEventBus, RedisStreamsEventBus
from app.main import create_app
from tests.helpers import login, token_of

ROOT = Path(__file__).resolve().parents[3]  # repo root
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


def test_capability_plugs_in_without_editing_shared_files(tmp_path, settings, monkeypatch):
    """A new capability = one API file in api/v1 + one domain package with wiring.py. No central edits."""
    api_dir, dom_dir = tmp_path / "api", tmp_path / "domain"
    (dom_dir / "zz_demo").mkdir(parents=True)
    api_dir.mkdir()
    (api_dir / "zz_demo.py").write_text(textwrap.dedent("""
        from fastapi import APIRouter
        router = APIRouter()

        @router.get("/demo/ping")
        async def ping():
            return {"pong": True}
    """))
    (dom_dir / "zz_demo" / "__init__.py").write_text("")
    (dom_dir / "zz_demo" / "wiring.py").write_text('PERMISSIONS = {"OPERATOR": ["demo:read"]}' + chr(10))
    monkeypatch.setattr(v1_pkg, "__path__", [*v1_pkg.__path__, str(api_dir)])
    monkeypatch.setattr(domain_pkg, "__path__", [*domain_pkg.__path__, str(dom_dir)])
    app = create_app(settings)
    with TestClient(app) as c:
        assert c.get("/api/v1/demo/ping").json() == {"pong": True}
        assert "zz_demo" in c.get("/version").json()["capabilities"]
    from app.core.security import ROLE_PERMISSIONS

    assert "demo:read" in ROLE_PERMISSIONS["OPERATOR"]
    for mod in ("app.api.v1.zz_demo", "app.domain.zz_demo.wiring", "app.domain.zz_demo"):
        sys.modules.pop(mod, None)


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


def _alembic_cfg(db: Path):
    from alembic.config import Config

    cfg = Config(str(ROOT / "backend" / "alembic.ini"))
    cfg.attributes["database_url"] = f"sqlite+aiosqlite:///{db.as_posix()}"
    return cfg


def test_alembic_single_head_matches_models(tmp_path):
    """Clean database: `upgrade head` creates exactly the tables declared in models."""
    from alembic import command
    from alembic.script import ScriptDirectory
    from sqlalchemy import create_engine, inspect

    from app.core.database import Base
    from app.registry import import_all_models

    cfg = _alembic_cfg(tmp_path / "mig.db")
    assert len(ScriptDirectory.from_config(cfg).get_heads()) == 1
    command.upgrade(cfg, "head")
    import_all_models()
    tables = set(inspect(create_engine(f"sqlite:///{(tmp_path / 'mig.db').as_posix()}")).get_table_names())
    assert tables - {"alembic_version"} == set(Base.metadata.tables)


def test_alembic_upgrades_pre_restructure_database(tmp_path):
    """A database created before the restructure (at both old branch heads) upgrades with only the merge revision."""
    from alembic import command
    from sqlalchemy import create_engine, text

    cfg = _alembic_cfg(tmp_path / "old.db")
    command.upgrade(cfg, "heads")  # same state as before: m00_0001 + 6a49290df5f0
    command.downgrade(cfg, "m00_0001")  # step back through the merge so we're exactly at the two old heads
    command.upgrade(cfg, "6a49290df5f0")
    with create_engine(f"sqlite:///{(tmp_path / 'old.db').as_posix()}").connect() as conn:
        before = {r[0] for r in conn.execute(text("select version_num from alembic_version"))}
    assert before == {"m00_0001", "6a49290df5f0"}
    command.upgrade(cfg, "head")
    with create_engine(f"sqlite:///{(tmp_path / 'old.db').as_posix()}").connect() as conn:
        after = {r[0] for r in conn.execute(text("select version_num from alembic_version"))}
    assert after == {"a1b2c3d4e5f6"}


def test_contracts_valid_and_openapi_in_sync():
    for args in (["check"], ["export", "--check"]):
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "contracts.py"), *args], capture_output=True,
                           text=True, cwd=ROOT)
        assert r.returncode == 0, r.stdout + r.stderr


async def test_redis_state_store_roundtrip():
    import fakeredis

    from app.core.cache import RedisStateStore

    store = RedisStateStore(fakeredis.FakeAsyncRedis())
    await store.set_json("twin:operator:OP1001", {"a": 1, "nested": {"b": [1, 2]}})
    await store.set_json("twin:machine:EXC001", {"mode": "DIGGING"})
    assert await store.get_json("twin:operator:OP1001") == {"a": 1, "nested": {"b": [1, 2]}}
    assert await store.keys("twin:*") == ["twin:machine:EXC001", "twin:operator:OP1001"]
    await store.delete("twin:machine:EXC001")
    assert await store.get_json("twin:machine:EXC001") is None and await store.ping()
