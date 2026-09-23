# M00 — Foundation

| Field | Value |
|-------|-------|
| Phase | 0 (base, blocks everything) |
| Type | Platform / infra / shells |
| Depends on | — |
| Consumed by | every module |
| Exit gate | **G0**: clone → one command → frontend + backend + DB + Redis + event bus healthy; CI green |

## Objective

Create the stable technical substrate so every other module plugs in **without editing shared files**: repo skeleton, local infrastructure, backend core with module auto-discovery, auth/RBAC, master data, event bus and WS gateway abstractions, frontend shells with role-guarded area pages, contracts baseline, and CI.

## Why this module exists

Parallel work is only safe if integration points are designed up front. M00 turns the usual hotspots (router, migrations, nav, compose, env, API client) into discovery/slot mechanisms (see `PARALLEL_WORKFLOW.md` §5).

## Scope

- Repo skeleton for the full target tree (`REPOSITORY_STRUCTURE.md`), with `.gitkeep` files and module README stubs
- Docker Compose base: Postgres (+Timescale, +pgvector), Redis, MQTT broker (for M04's simulated devices), backend, frontend apps
- `Makefile` targets: `up`, `down`, `test`, `test M=<module>`, `contracts`, `seed`, `sim`, `lint`
- Backend core: settings loader (merges `.env.example` names), DB session, Alembic multi-branch setup, `EventBus` interface + Redis Streams impl + in-memory impl for tests, WS gateway, structured logging, error envelope, `/health` `/ready` `/version` `/metrics`, **module registry** (auto-discovers `backend/app/domain/*/wiring.py`)
- Auth: JWT login, `OPERATOR` / `SUPERVISOR_ADMIN` roles, permission strings, site scope, `require_permission()` dependency, audit-log helper
- Master data (`backend/app/domain/platform`): users, operators, machines, sites, zones: CRUD APIs + events + seed data (glossary demo IDs)
- Frontend: pnpm workspace, `packages/ui` (tokens, primitives, glove-friendly sizes, light/dark, RTL-safe), `packages/api-client` generation, `apps/operator` and `apps/admin` shells with auth guard, layout, WS client hook, i18n scaffolding, and **role-guarded area pages** for every feature listed in `REPOSITORY_STRUCTURE.md` §1
- Contracts baseline: common schemas (ids, envelope, error, pagination, geo), empty-but-valid OpenAPI file per module, contract validation script, CI
- CI (GitHub Actions): lint, typecheck, tests, contract validation, api-client drift check
- `scripts/status.py` maintenance

## Out of scope

Tasks/assignments/twin (M01), any domain intelligence, final operator/admin UX (M02/M03), ML, IoT behavior, training content.

## Where the code lives

`backend/app/core/`, `backend/app/{main,config,dependencies,registry}.py`, `backend/app/domain/platform/`, `backend/app/api/v1/{auth,platform}.py`, `backend/app/seed/platform.py`, `backend/migrations/` (env), `frontend/src/{app/layout.tsx,app/login,components,lib,hooks}/`, `frontend/src/features/auth/`, `contracts/schemas/common/`, `contracts/events/platform/`, `scripts/`, `infra/`, `docker-compose.yml`, `.github/`.

Folders are created only when real code lands. Ownership rules and the full map: `docs/architecture/REPOSITORY_STRUCTURE.md`.

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

**Capability wiring contract** (as built: `backend/app/domain/<area>/wiring.py` + routes in `backend/app/api/v1/<area>.py`):

```python
router: APIRouter | None
event_handlers: list[tuple[str, Callable]]    # (event_type pattern, handler)
ws_channels: list[str]                        # message types this module may push
async def startup(app) -> None: ...           # optional
```

## Work package plan

| WP | Title | Paths | Depends on | Est. |
|----|-------|-------|------------|------|
| M00-WP1 | Repo skeleton, compose base, Makefile, CI | `infra/`, `.github/`, root | — | 1–2 d |
| M00-WP2 | Backend core: settings, DB, Alembic branches, EventBus, WS gateway, logging, health, registry | `backend/app/core/` | WP1 | 2–3 d |
| M00-WP3 | Auth, RBAC, site scope, master data CRUD + events + seed | `backend/app/domain/platform/` | WP2 (can stub core) | 2 d |
| M00-WP4 | Frontend workspace, UI kit, API client gen, both app shells with role-guarded area pages, i18n scaffold, WS hook | `frontend/` | WP5 (OpenAPI skeleton) | 2–3 d |
| M00-WP5 | Contracts baseline: common schemas, envelope, per-module OpenAPI skeletons, validation script | `contracts/` | — | 1 d |

WP1 and WP5 can start in parallel on day 1. WP2, WP3, and WP4 overlap using stubs.

## Acceptance criteria

- [ ] Fresh clone → `python scripts/dev.py up` → all containers healthy on Windows, macOS, and Linux (Docker Desktop)
- [ ] `GET /health`, `/ready`, `/version` return 200; `/metrics` exposes Prometheus text
- [ ] Adding `backend/app/api/v1/<area>.py` + `backend/app/domain/<area>/wiring.py` makes routes and permissions appear, **with zero edits to core**
- [ ] Two modules can each add an Alembic migration on their own branch; `alembic upgrade heads` applies both
- [ ] Login as `OP1001` (OPERATOR) and `SUP001` (SUPERVISOR_ADMIN); permission checks and site scope are enforced
- [ ] CRUD for operators/machines/sites/zones works and emits `platform.*` events
- [ ] Both apps render the shell and every role-guarded area pages placeholder; nav comes from slot manifests
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

- [ ] All teammates ran `python scripts/dev.py up` successfully on their machine
- [ ] Every module folder, slot, compose file, and env file stub exists
- [ ] `develop` and `main` branch protections on; CODEOWNERS filled in
- [ ] Tag `g0` on `main`

---

# Status

> **Only the workstream owner (and their agent) edits this file.** Update it in the same commit as your code, **before every push**.
> Shortcut: `python scripts/status.py log --module M00 --action PUSH --msg "..." [--wp M00-WP1=DONE] [--state IN_PROGRESS]`
> States: `NOT_STARTED` · `IN_PROGRESS` · `MOCKED` (contract + mock shipped) · `BLOCKED` · `IN_REVIEW` · `DONE`

<!-- status:summary (parsed by scripts/status.py; keep the table shape) -->
| Field | Value |
|-------|-------|
| Module | M00 |
| Owner | @Developer-Devanshhh |
| Phase | 0 |
| State | IN_REVIEW |
| Current focus | G0 verification (Docker stack) |
| Contract version | m00-platform 1.0.0 (generated) · events v1 |
| Last updated | 2026-09-23 · @Developer-Devanshhh · Repository restructure (ADR-0002): backend/app package, one  |
<!-- /status:summary -->

## Work packages

| WP | Title | State | Branch / PR | Notes |
|----|-------|-------|-------------|-------|
| M00-WP1 | Repo skeleton, compose base, Makefile, CI | IN_REVIEW | — | |
| M00-WP2 | Backend core: settings, DB, Alembic branches, EventBus, WS gateway, logging, health, registry | IN_REVIEW | — | |
| M00-WP3 | Auth, RBAC, site scope, master data CRUD + events + seed | IN_REVIEW | — | |
| M00-WP4 | Frontend workspace, UI kit, API client gen, both app shells with role-guarded area pages, i18n scaffold, WS hook | IN_REVIEW | — | |
| M00-WP5 | Contracts baseline: common schemas, envelope, per-module OpenAPI skeletons, validation script | IN_REVIEW | — | |

## Using mocks for

| Dependency | Mock source | Switch to real when |
|------------|-------------|---------------------|
| — | — | — |

## Blockers

- none

## Verification notes

- Verified locally (Windows, no Docker): 17 backend tests (auth/RBAC/site scope, CRUD + contract-validated events, in-memory + Redis Streams bus (fakeredis), module auto-discovery, WS auth, Alembic heads == models, contracts check + OpenAPI drift), lite-mode server smoke test, `next build` of both apps, typecheck of all packages.
- **Not yet verified:** `python scripts/dev.py up` (Docker Compose stack: Timescale image, Redis, MQTT, containers). Needs a teammate with Docker for the G0 checklist.
- G0 items still open: every teammate runs the stack; branch protection + CODEOWNERS; ADR-0001 → ACCEPTED.

## Contract changes (pending / recent)

- none

## Open questions

- none

## Update log

<!-- newest first · one line per push: date · @handle · ACTION · branch · summary -->
<!-- log:insert -->
- 2026-09-23 · @Developer-Devanshhh · PUSH · refactor/production-structure · Repository restructure (ADR-0002): backend/app package, one frontend app, contracts by area, linear migrations, architecture tests; API surface unchanged; 53 tests + frontend lint/typecheck/build green
- 2026-09-23 · @Developer-Devanshhh · PUSH · feature/m01-operational-twin · core fixes found while building M01: nested-router path collection (FastAPI 0.14x), RedisStateStore.keys bug, seed_all discovery, generated contract documents in scripts/contracts.py
- 2026-09-23 · @Developer-Devanshhh · PUSH · feature/m00-foundation · M00 implemented: core (config, db, event bus memory+Redis Streams, state, WS gateway, auth/RBAC, registry, errors, logging, health/metrics), m00_platform CRUD+events+seed, Alembic branches, contracts baseline + tooling, frontend workspace + both app shells with slots, dev.py, compose, CI
- 2026-09-23 · @team · INIT · docs scaffold · Status file created from SPEC work packages
