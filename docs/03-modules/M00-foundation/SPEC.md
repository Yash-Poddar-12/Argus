# M00 — Foundation

| Field | Value |
|-------|-------|
| Phase | 0 (base, blocks everything) |
| Type | Platform / infra / shells |
| Depends on | — |
| Consumed by | every module |
| Exit gate | **G0**: clone → one command → frontend + backend + DB + Redis + event bus healthy; CI green |

## Objective

Create the stable technical substrate so every other module plugs in **without editing shared files**: repo skeleton, local infrastructure, backend core with module auto-discovery, auth/RBAC, master data, event bus and WS gateway abstractions, frontend shells with pre-registered slots, contracts baseline, and CI.

## Why this module exists

Parallel work is only safe if integration points are designed up front. M00 turns the usual hotspots (router, migrations, nav, compose, env, API client) into discovery/slot mechanisms (see `MODULAR_WORKFLOW.md` §5).

## Scope

- Repo skeleton for the full target tree (`REPO_STRUCTURE.md`), with `.gitkeep` files and module README stubs
- Docker Compose base: Postgres (+Timescale, +pgvector), Redis, MQTT broker (for M04's simulated devices), backend, frontend apps
- `Makefile` targets: `up`, `down`, `test`, `test M=<module>`, `contracts`, `seed`, `sim`, `lint`
- Backend core: settings loader (merges `infra/env/*.env.example` names), DB session, Alembic multi-branch setup, `EventBus` interface + Redis Streams impl + in-memory impl for tests, WS gateway, structured logging, error envelope, `/health` `/ready` `/version` `/metrics`, **module registry** (auto-discovers `backend/modules/*/module.py`)
- Auth: JWT login, `OPERATOR` / `SUPERVISOR_ADMIN` roles, permission strings, site scope, `require_permission()` dependency, audit-log helper
- Master data (`m00_platform`): users, operators, machines, sites, zones: CRUD APIs + events + seed data (glossary demo IDs)
- Frontend: pnpm workspace, `packages/ui` (tokens, primitives, glove-friendly sizes, light/dark, RTL-safe), `packages/api-client` generation, `apps/operator` and `apps/admin` shells with auth guard, layout, WS client hook, i18n scaffolding, and **pre-registered slots** for every feature listed in `REPO_STRUCTURE.md` §1
- Contracts baseline: common schemas (ids, envelope, error, pagination, geo), empty-but-valid OpenAPI file per module, contract validation script, CI
- CI (GitHub Actions): lint, typecheck, tests, contract validation, api-client drift check
- `scripts/status.py` maintenance

## Out of scope

Tasks/assignments/twin (M01), any domain intelligence, final operator/admin UX (M02/M03), ML, IoT behavior, training content.

## Owned paths

`backend/core/`, `backend/modules/m00_platform/`, `backend/migrations/m00_platform/`, `backend/tests/m00_platform/`, `frontend/packages/ui/`, app **shells** (layout, nav, guards; the app owner takes over after G0), `infra/compose/base.yml`, `infra/env/base.env.example`, `scripts/`, `.github/`, `contracts/schemas/common/`, `contracts/openapi/m00-platform.yaml`, `contracts/events/m00/`, root docs.

## Interfaces

**Produces:** APIs in `API_CATALOG.md` § M00; events in `EVENT_CATALOG.md` § M00; tables `users`, `roles`, `permissions`, `user_site_scopes`, `operators`, `machines`, `sites`, `zones`, `audit_log`.

**Core interfaces every module uses:**

```python
# backend/core
EventBus.publish(event_type, payload, *, site_id, source_id, correlation_id=None) -> event_id
EventBus.subscribe(event_type_pattern, handler, *, group)       # idempotent on event_id
ws.publish(channel: str, type: str, data: dict)                  # channel e.g. "operators/OP1001"
require_permission("tasks:assign")                               # FastAPI dependency, site-scoped
get_db() / get_redis() / get_settings()
audit(actor, action, resource, details)
```

**Module discovery contract** (`backend/modules/<m>/module.py`):

```python
router: APIRouter | None
event_handlers: list[tuple[str, Callable]]    # (event_type pattern, handler)
ws_channels: list[str]                        # message types this module may push
async def startup(app) -> None: ...           # optional
```

## Work packages

| WP | Title | Paths | Depends on | Est. |
|----|-------|-------|------------|------|
| M00-WP1 | Repo skeleton, compose base, Makefile, CI | `infra/`, `.github/`, root | — | 1–2 d |
| M00-WP2 | Backend core: settings, DB, Alembic branches, EventBus, WS gateway, logging, health, registry | `backend/core/` | WP1 | 2–3 d |
| M00-WP3 | Auth, RBAC, site scope, master data CRUD + events + seed | `backend/modules/m00_platform/` | WP2 (can stub core) | 2 d |
| M00-WP4 | Frontend workspace, UI kit, API client gen, both app shells with pre-registered slots, i18n scaffold, WS hook | `frontend/` | WP5 (OpenAPI skeleton) | 2–3 d |
| M00-WP5 | Contracts baseline: common schemas, envelope, per-module OpenAPI skeletons, validation script | `contracts/` | — | 1 d |

WP1 and WP5 can start in parallel on day 1. WP2, WP3, and WP4 overlap using stubs.

## Acceptance criteria

- [ ] Fresh clone → `make up` → all containers healthy on Windows, macOS, and Linux (Docker Desktop)
- [ ] `GET /health`, `/ready`, `/version` return 200; `/metrics` exposes Prometheus text
- [ ] Dropping a new folder `backend/modules/mzz_demo/module.py` with a router makes its route appear, **with zero edits to core**
- [ ] Two modules can each add an Alembic migration on their own branch; `alembic upgrade heads` applies both
- [ ] Login as `OP1001` (OPERATOR) and `SUP001` (SUPERVISOR_ADMIN); permission checks and site scope are enforced
- [ ] CRUD for operators/machines/sites/zones works and emits `platform.*` events
- [ ] Both apps render the shell and every pre-registered slot placeholder; nav comes from slot manifests
- [ ] `make contracts` validates all contracts and regenerates the API client; CI fails on drift
- [ ] Event published → handler in another module receives it; replaying the same `event_id` doesn't process it twice
- [ ] `python scripts/status.py board` prints all modules

## Testing

Unit tests (settings, permissions, envelope), integration tests (bus round-trip, WS fan-out, auth flow), a smoke test in CI that starts compose.

## Future extensions

OIDC provider, mTLS device identity, Kafka/NATS bus implementation, OpenTelemetry tracing, Helm/k8s deploy.

## Known constraints

Windows teammates: prefer Docker Desktop with the WSL2 backend; keep scripts in Python or Make (no bash-only tooling in the critical path).

## Integration checklist (G0)

- [ ] All teammates ran `make up` successfully on their machine
- [ ] Every module folder, slot, compose file, and env file stub exists
- [ ] `develop` and `main` branch protections on; CODEOWNERS filled in
- [ ] Tag `g0` on `main`
