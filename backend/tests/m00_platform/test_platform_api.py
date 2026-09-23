from backend.tests.conftest import login


def test_ops_endpoints(client):
    assert client.get("/health").json() == {"status": "ok"}
    ready = client.get("/ready")
    assert ready.status_code == 200 and ready.json()["checks"] == {"db": True, "state": True, "bus": True}
    version = client.get("/version").json()
    assert {"name": "m00_platform", "id": "M00"} in version["modules"]
    client.get("/health")
    assert "http_requests_total" in client.get("/metrics").text


def test_request_id_propagates(client):
    r = client.get("/health", headers={"x-request-id": "abc-123"})
    assert r.headers["x-request-id"] == "abc-123"


def test_login_and_me(client):
    bad = client.post("/api/v1/auth/login", json={"username": "sup001", "password": "nope"})
    assert bad.status_code == 401 and bad.json()["error"]["code"] == "UNAUTHORIZED"
    headers = login(client, "sup001")
    me = client.get("/api/v1/auth/me", headers=headers).json()
    assert me["principal"]["role"] == "SUPERVISOR_ADMIN" and me["principal"]["site_ids"] == ["SITE_A"]
    assert "operators:write" in me["permissions"]
    assert client.get("/api/v1/auth/me").status_code == 401


def test_operator_self_scope(client, op1):
    assert client.get("/api/v1/operators/OP1001", headers=op1).status_code == 200
    other = client.get("/api/v1/operators/OP1002", headers=op1)
    assert other.status_code == 403 and other.json()["error"]["code"] == "FORBIDDEN"
    assert client.post("/api/v1/operators", headers=op1, json={"operator_id": "OP9", "name": "x",
                                                                "site_id": "SITE_A"}).status_code == 403


def test_crud_emits_contract_valid_events(client, sup, runtime):
    runtime.bus.published.clear()
    r = client.post("/api/v1/operators", headers=sup, json={"operator_id": "OP2001", "name": "New Op", "site_id": "SITE_A"})
    assert r.status_code == 201, r.text
    assert client.post("/api/v1/operators", headers=sup,
                       json={"operator_id": "OP2001", "name": "dup", "site_id": "SITE_A"}).status_code == 409
    r = client.patch("/api/v1/operators/OP2001", headers=sup, json={"experience_level": "SENIOR"})
    assert r.json()["experience_level"] == "SENIOR"
    r = client.post("/api/v1/machines", headers=sup, json={"machine_id": "LDR001", "site_id": "SITE_A",
                    "machine_type": "LOADER", "model": "CAT 950", "serial_number": "CAT0950L0001"})
    assert r.status_code == 201, r.text
    r = client.post("/api/v1/sites/SITE_A/zones", headers=sup, json={
        "zone_id": "ZONE_C", "name": "C", "zone_type": "HAZARD",
        "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]}})
    assert r.status_code == 201, r.text
    types = [e.event_type for e in runtime.bus.published]
    assert types == ["platform.operator.created", "platform.operator.updated", "platform.machine.created",
                     "platform.zone.updated"]
    assert runtime.bus.published[1].payload["changed_fields"] == ["experience_level"]


def test_invalid_zone_geometry(client, sup):
    r = client.post("/api/v1/sites/SITE_A/zones", headers=sup, json={
        "zone_id": "ZONE_X", "name": "x", "zone_type": "HAZARD", "geometry": {"type": "Point", "coordinates": [0, 0]}})
    assert r.status_code == 422 and r.json()["error"]["code"] == "VALIDATION_ERROR"


def test_site_scope_enforced(client, sup):
    assert client.get("/api/v1/sites/SITE_Z", headers=sup).status_code == 403
    r = client.post("/api/v1/operators", headers=sup, json={"operator_id": "OP3", "name": "x", "site_id": "SITE_Z"})
    assert r.status_code == 403


def test_list_pagination_and_filters(client, sup, op1):
    page = client.get("/api/v1/machines?limit=2&offset=1", headers=sup).json()
    assert page["total"] == 4 and page["limit"] == 2 and len(page["items"]) == 2
    dumpers = client.get("/api/v1/machines?machine_type=DUMPER", headers=op1).json()
    assert [m["machine_id"] for m in dumpers["items"]] == ["DMP001", "DMP002"]
    zones = client.get("/api/v1/sites/SITE_A/zones", headers=sup).json()
    assert {z["zone_id"] for z in zones} >= {"ZONE_A", "ZONE_DISPOSAL"}


def test_audit_log_written(client, sup, runtime):
    client.patch("/api/v1/machines/EXC001", headers=sup, json={"status": "MAINTENANCE"})

    async def _count():
        from sqlalchemy import func, select

        from backend.core.audit import AuditLog

        async with runtime.db.sessionmaker() as s:
            return await s.scalar(select(func.count()).select_from(AuditLog).where(AuditLog.resource_id == "EXC001"))

    assert client.portal.call(_count) == 1
