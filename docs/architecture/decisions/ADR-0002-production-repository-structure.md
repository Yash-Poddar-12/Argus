# ADR-0002: Production repository structure (capabilities, not phase folders)

| Field | Value |
|-------|-------|
| Status | **ACCEPTED** |
| Date | 2026-09-23 |
| Author | @Developer-Devanshhh |
| Affected | whole repository (no API, event or database schema changes) |
| Supersedes | the per-module layout of docs/architecture/REPOSITORY_STRUCTURE.md (pre-restructure) |

## Context

The first layout mirrored the delivery plan: every workstream (M00–M11) had its own backend package (`backend/modules/m00_platform`, `m01_twin`, …), migration branch, test folder, contract folders (`contracts/events/m00`, `openapi/m04-safety.yaml`), frontend slot, and doc folder. There were also top-level folders per concept: `simulator/`, `edge/`, `ml/`, `knowledge/`, `content/`, `analytics/`.

It was technically valid but, measured on the real code, it had these problems:

- **17 top-level entries**, five of them (`edge/`, `ml/`, `knowledge/`, `content/`, `analytics/`) containing only `.gitkeep`: structure without substance.
- **Phase numbers used as code boundaries.** "Where does proximity code go?" required knowing that proximity belongs to "M04", and M01 alone mixed five capabilities (tasks, telemetry, environment, twin, simulator) in one package with a `public.py` facade.
- **Duplicated concepts:** two frontend apps with duplicated shells/login, two workspace packages, per-module OpenAPI files (seven of them empty skeletons), per-module compose/env files, and 24 SPEC/STATUS files.
- Hard for humans and AI agents to answer "what am I allowed to modify?" without reading a long ownership table.

## Decision

1. **Top level = deployable or independently understandable concern:** `backend/`, `frontend/`, `ml/`, `contracts/`, `infra/`, `docs/`, `scripts/`, `.github/`, plus root config (`docker-compose.yml`, `.env.example`, `Makefile`, `pyproject.toml` workspace, agent files).
2. **Modularity lives inside:** `backend/app/{core, api/v1, domain/<capability>, copilot, iot, seed, schemas}` and `frontend/src/{app, features/<feature>, components, lib, hooks}`. Capabilities plug in through `domain/<area>/wiring.py` (auto-discovered) and `api/v1/<area>.py` (auto-included), so no central file is edited to add one.
3. **M00–M11 remain workstreams** (planning + status in `docs/development/workstreams/`), never folder names. A test forbids phase-numbered folders.
4. **Layering is enforced by tests** (`backend/tests/test_architecture.py`): core ↛ business code; routes ↛ queries; Copilot ↛ database; domains read other domains through services (explicit read-only exceptions for the twin read model).
5. **Contracts are organized by type and business area:** one generated `contracts/openapi/argus-api.yaml`, `contracts/events/<area>/`, `contracts/tools/`, `contracts/schemas/`.
6. **Migrations are linear.** The two historical branches (`m00_platform`, `m01_twin`) are kept byte-for-byte and joined by merge revision `a1b2c3d4e5f6`. Pre-restructure databases upgrade with only that no-op merge (tested).
7. **One frontend app** with `/operator/*` and `/supervisor/*` areas guarded by role, replacing two apps.

### Placement decisions for previously separate folders

| Former folder | Content found | Decision |
|---------------|---------------|----------|
| `simulator/` | working deterministic simulator (engine, scenarios, sinks, CLI) importing backend services | → `backend/app/iot/simulator/` (same process, same dependencies). Still independently invokable: `python -m app.iot.simulator` / `argus-sim` |
| `edge/` | empty | **Not retained.** IoT processing lives in `backend/app/iot/` as a library until a gateway must run as its own deployable process (edge-first safety, P10). At that point create top-level `edge/` with its own Dockerfile + compose service, reusing `app.iot` logic |
| `ml/` | empty | Kept as the ML area with `ml/README.md` defining the layout and the backend interface boundary; subfolders appear with real code |
| `knowledge/` | empty | Will live in `backend/app/copilot/knowledge/` (RAG corpus is Copilot data) |
| `content/training/` | empty | Will live in `backend/app/domain/training/content/` |
| `analytics/` | empty | Split by responsibility when built: KPIs → `backend/app/domain/operations/`, model/research evaluation → `ml/evaluation/`, write-ups → `docs/research/`, views → `frontend/src/features/operations/` |
| `models/` (target tree) | no artifacts yet | Not created. Created when trained artifacts/configs exist (registry + configs, large binaries outside git) |
| `tests/` (top level) | no cross-service tests yet | Not created. Backend integration tests are in `backend/tests/integration/`. Top-level `tests/e2e/` appears with the first browser/end-to-end suite |
| `infra/{compose,env,mosquitto}` | base compose, base env, broker config | → root `docker-compose.yml`, root `.env.example`, `infra/docker/mosquitto/` |

## When is a new top-level directory justified?

Only for a **separately deployable runtime** (own process/image, e.g. `edge/`) or a **separately versioned artifact store** (e.g. `models/`, top-level `tests/e2e/`). Record it in an ADR and add it to the allow-list in `test_top_level_layout_is_intentional`.

## How parallel development is preserved

- **Ownership by area** (`REPOSITORY_STRUCTURE.md` §6): 5 areas map to 3–5 people; each area is a small set of capability packages and feature folders.
- **No shared registration files:** routers, wiring, simulator scenarios and nav items are discovered or one-line additions.
- **Generated artifacts** (OpenAPI, event/tool schemas, frontend API types) are regenerated rather than merged; CI fails on drift.
- **Status tracking** stays one-writer-per-file (workstream file per owner, sync log per person).

## Consequences

- Positive: 8 meaningful top-level folders instead of 17; one backend package `app`; one frontend app; single OpenAPI; linear migrations; architecture rules executable in CI; API surface verified identical (45 operations, same schema names).
- Changed: frontend URLs moved under `/operator/*` and `/supervisor/*` (one app, one port: 3000); `/version` reports `capabilities` instead of `modules`; event envelope `source_id` values are capability names (`tasks`, `telemetry`, …) instead of `m01_twin`.
- Negative / risks: the Docker path (Timescale image, Redis Streams consumer loop) is still unverified on a machine with Docker; per-area CODEOWNERS must be filled in before enforcement.
