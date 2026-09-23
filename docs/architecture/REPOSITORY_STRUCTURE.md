# Repository Structure

> **Rule of thumb:** top-level folders are *deployable or independently understandable concerns*. Modularity lives **inside** them (capability packages, feature folders, contracts), not in more top-level folders. Decision record: [`decisions/ADR-0002-production-repository-structure.md`](decisions/ADR-0002-production-repository-structure.md).

## 1. Top level

```text
ARGUS/
├── backend/          FastAPI app (API, domain, copilot, IoT/simulator), migrations, backend tests     → Python package `app`
├── frontend/         Next.js app: operator area (/operator) + supervisor area (/supervisor)          → TypeScript
├── ml/               ML research, training and evaluation (no API routes). See ml/README.md
├── contracts/        Machine-readable interfaces: openapi/, events/, tools/, schemas/  (source of truth)
├── infra/            Infrastructure config used by the stack (Docker service configs; later monitoring/deployment)
├── docs/             product/, architecture/, development/
├── scripts/          Developer tooling: dev.py (task runner), contracts.py, status.py
├── .github/          CI + PR/issue templates (location required by GitHub)
├── docker-compose.yml  full local stack · .env.example · Makefile · pyproject.toml + uv.lock (uv workspace root)
└── AGENTS.md (canonical agent rules) · CLAUDE.md / GEMINI.md (pointers) · README.md · CONTRIBUTING.md · CHANGELOG.md
```

**A new top-level folder is justified only when it is a separately deployable runtime or a separately versioned artifact store**, e.g. `edge/` once the site gateway runs as its own process, or `models/` once trained model artifacts/configs exist. Everything else goes inside an existing top-level folder. Add it via an ADR.

## 2. Backend (`backend/app`)

```text
backend/
├── app/
│   ├── main.py            create_app(): middleware, ops endpoints, wires everything
│   ├── config.py          Settings (env vars)
│   ├── dependencies.py    FastAPI dependencies (session, bus, state, ws, principal, permissions)
│   ├── registry.py        discovers capability wiring (app/domain/*/wiring.py, app/copilot/wiring.py)
│   ├── core/              TECHNICAL infrastructure only. Never imports domain/api/copilot/iot
│   │   ├── database/      Base, UTCDateTime, Database (async engine/sessions)
│   │   ├── events/        EventBus: in-memory + Redis Streams, dedup, contract validation
│   │   ├── cache/         StateStore: in-memory + Redis
│   │   ├── websocket/     WS gateway + channel auth
│   │   ├── security/      JWT auth, passwords, RBAC (Principal, permission registry)
│   │   ├── contracts.py   runtime access to contracts/ (validation, generated-schema helpers)
│   │   ├── runtime.py     Runtime container (db, bus, state, ws)
│   │   ├── logging.py · exceptions.py · audit.py
│   ├── api/
│   │   ├── router.py      auto-includes every api/v1/*.py (no central route list to edit)
│   │   └── v1/            THIN routes per area: auth, platform, tasks, telemetry, environment, twin
│   ├── domain/            BUSINESS capabilities. One package per capability:
│   │   ├── platform/      users, sites, zones, operators, machines (models, schemas, service, wiring)
│   │   ├── tasks/         tasks, assignments, sessions, pre-checks (state_machine, rules, service,
│   │   │                  assignments, lifecycle, reporting, events, wiring)
│   │   ├── telemetry/     ingestion (idempotent), history, events
│   │   ├── environment/   site/zone conditions, weather-provider seam
│   │   └── twin/          Operational Twin: fusion (pure), service (Redis projection), handlers, schemas
│   ├── copilot/           AI agent + tools. tools/registry.py (specs), tools/*_tools.py (call domain services)
│   ├── iot/               device/IoT processing; iot/simulator/ (deterministic simulator, scenarios, CLI)
│   ├── schemas/common.py  the few shapes shared across domains (Page, GeoPoint, DTO base)
│   └── seed/              demo data (python -m app.seed)
├── migrations/            Alembic: env.py + versions/ (linear history)
├── tests/                 core/ platform/ tasks/ twin/ iot/ integration/ + test_architecture.py
├── alembic.ini · pyproject.toml · Dockerfile
```

**Future capability packages** are created when their first real code lands (never as empty folders):
`domain/safety/`, `domain/operations/` (site intelligence, KPIs), `domain/training/` (+ `training/content/`), `intelligence/` (inference interfaces, ML adapters, `counterfactual/`), `copilot/knowledge/` (RAG corpus), more `iot/` adapters.

### Inside a capability package

| File | Holds | Rule |
|------|-------|------|
| `models.py` | SQLAlchemy tables | Only this package writes them. Cross-domain references are plain IDs (no foreign keys) |
| `schemas.py` | Pydantic request/response shapes | Class names are API contract names: don't rename casually |
| `events.py` | Event payload models + `EVENT_PAYLOADS` | Schemas are generated into `contracts/events/<area>/` |
| `service.py` (+ focused modules) | Use cases and read accessors | Other capabilities call these functions; they never query your tables |
| `wiring.py` | `PERMISSIONS`, `EVENT_HANDLERS`, `startup`, `contract_documents()` | Discovered automatically |
| pure modules (`state_machine.py`, `rules.py`, `fusion.py`) | Logic with no I/O | Most unit tests target these |

## 3. Frontend (`frontend/src`)

```text
src/
├── app/                   routes only (thin): login/, operator/<page>/, supervisor/<page>/
│   ├── operator/layout.tsx     RoleGuard(OPERATOR) + operator nav
│   └── supervisor/layout.tsx   RoleGuard(SUPERVISOR_ADMIN) + supervisor nav
├── features/              product features; each owns its views, feature components, strings, mocks
│   ├── auth/ operator/ supervisor/ machines/ tasks/ safety/ operations/ training/ copilot/
├── components/ui/         shared primitives (Button, Card, Badge, Stat, SlotPlaceholder, LanguageSelect)
├── components/layout/     AppShell
├── lib/api/               fetch client + session; generated/ = types from contracts/openapi (never hand-edit)
├── lib/websocket/         useChannel()
├── lib/i18n/              I18nProvider, useT (features own their strings)
├── hooks/                 cross-feature hooks (useSession)
└── app/globals.css        design tokens
```

A page = one route folder in `app/<area>/<page>/page.tsx` that renders a view from `features/<feature>`, plus one line in `features/<area>/nav.ts`.

## 4. Dependency rules (enforced by `backend/tests/test_architecture.py`)

```text
frontend ──HTTP/WS──► backend api/v1 ──► domain services ──► database
                                          │
domain/service ──► intelligence interface ──► ML adapter ──► model        (ml/ never serves routes)
copilot agent ──► copilot tool ──► domain service ──► authoritative data  (tools never touch the DB)
device/simulator ──► iot adapter ──► telemetry/event ──► domain/intelligence
```

| Layer | May import | Must NOT import |
|-------|------------|----------------|
| `app.core` | stdlib, third-party | `app.domain`, `app.api`, `app.copilot`, `app.iot`, `app.registry`, `app.main`, `app.seed` |
| `app.domain` | `app.core`, `app.schemas`, other domains' **services/schemas** | `app.api`, `app.copilot`, `app.iot`, `app.main` |
| `app.api` | `app.dependencies`, `app.core` (exceptions), domain **services/schemas** | domain `models`, `sqlalchemy` (except session typing) |
| `app.copilot` | domain services/schemas, `app.core.exceptions` | `app.core.database`, `sqlalchemy`, domain `models`, `app.api` |
| `app.iot` | domain services/schemas (in-process sinks), `app.core` | `app.api` |
| frontend | backend API + WebSocket only | databases, ML, LLM providers |

Safety-critical decisions stay deterministic (rules + sensor validation in `iot/` / `domain/safety/`); ML is evidence and the LLM never decides safety.

## 5. Where does this belong? (10-second lookup)

| I'm writing… | Put it in |
|--------------|-----------|
| A new REST endpoint | `backend/app/api/v1/<area>.py` → calls `backend/app/domain/<area>/service.py` |
| Business rule / use case | `backend/app/domain/<area>/` |
| DB table | `backend/app/domain/<area>/models.py` + migration in `backend/migrations/versions/` |
| Event another capability consumes | payload model in `domain/<area>/events.py`, handler in the consumer's `wiring.py` |
| Prediction / anomaly / root-cause / what-if logic | `backend/app/intelligence/` (interface + adapter); training code in `ml/` |
| Copilot tool | spec in `backend/app/copilot/tools/registry.py`, implementation calls a domain service |
| Device adapter, proximity math, simulator scenario | `backend/app/iot/` (scenarios: `iot/simulator/scenarios/<theme>.py`) |
| Operator screen | `frontend/src/features/<feature>/` + route under `frontend/src/app/operator/` |
| Supervisor screen | `frontend/src/features/<feature>/` + route under `frontend/src/app/supervisor/` |
| Shared UI primitive | `frontend/src/components/ui/` |
| API/event/tool shape change | code first, then `python scripts/dev.py contracts`; hand-written schemas in `contracts/` |
| Model training / evaluation notebook | `ml/` |
| Docker/service config | `docker-compose.yml`, `infra/docker/` |
| Architecture decision | `docs/architecture/decisions/ADR-NNNN-*.md` |

## 6. Ownership areas (who edits what)

Ownership is by **area**, not by top-level folder. Names/handles: `docs/development/TEAM_AND_OWNERSHIP.md`; enforcement: `.github/CODEOWNERS`.

| Area | Paths |
|------|-------|
| **A · Platform & twin** | `backend/app/{core,main.py,config.py,dependencies.py,registry.py,schemas}/`, `backend/app/domain/{platform,tasks,telemetry,environment,twin}/`, matching `api/v1/*.py`, `backend/migrations/`, `backend/app/seed/`, `contracts/schemas/`, `infra/`, `docker-compose.yml`, `scripts/`, `.github/` |
| **B · Operator UX + Copilot** | `frontend/src/app/operator/`, `frontend/src/features/{operator,copilot}/`, `backend/app/copilot/`, `contracts/tools/` |
| **C · Supervisor + Operations** | `frontend/src/app/supervisor/`, `frontend/src/features/{supervisor,operations,machines}/`, `backend/app/domain/operations/` |
| **D · IoT + ML** | `backend/app/iot/`, `backend/app/domain/safety/`, `frontend/src/features/safety/`, `ml/`, `backend/app/intelligence/` (interfaces/adapters) |
| **E · Training + Intelligence research** | `backend/app/domain/training/`, `frontend/src/features/training/`, `backend/app/intelligence/counterfactual/`, `ml/evaluation/`, `docs/research/` |
| Shared (deliberate PRs, reviewed by A + the affected area) | `frontend/src/{components,lib,hooks}/`, `frontend/src/features/{auth,tasks}/`, `contracts/`, `docs/architecture/`, `AGENTS.md` |

With 3–4 people, merge areas (e.g. A+E, C+D). Generated files (`contracts/openapi/argus-api.yaml`, generated event/tool schemas, `frontend/src/lib/api/generated/`) are never hand-edited: regenerate with `python scripts/dev.py contracts`.
