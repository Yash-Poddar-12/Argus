# Parallel Workflow

> How 3–5 people (and their agents in Claude Code, Codex CLI, Antigravity, …) build ARGUS in parallel without stepping on each other.
> Code structure: `docs/architecture/REPOSITORY_STRUCTURE.md`. Why: `docs/architecture/decisions/ADR-0002-production-repository-structure.md`.

## 1. Two separate ideas: workstreams vs code structure

| Concept | What it is | Where it lives |
|---------|------------|----------------|
| **Workstream (M00–M11)** | A unit of *planning and delivery*: scope, work packages, acceptance, status | `docs/development/workstreams/MXX-*.md` |
| **Capability / feature** | A unit of *code*: a backend domain package or a frontend feature folder | `backend/app/domain/<area>/`, `frontend/src/features/<feature>/`, … |

A workstream usually touches one or two capability packages plus a frontend feature. **Workstream numbers never appear as folder names.**

| Workstream | Code it mainly touches |
|------------|------------------------|
| M00 Foundation | `backend/app/core`, `domain/platform`, tooling, infra, frontend shell/`lib`/`components` |
| M01 Operational Twin | `domain/{tasks,telemetry,environment,twin}`, `copilot/tools`, `iot/simulator` |
| M02 Operator Experience | `frontend/src/app/operator`, `features/operator` + operator views in other features |
| M03 Supervisor/Admin | `frontend/src/app/supervisor`, `features/supervisor` + supervisor views |
| M04 IoT Hazard Mesh | `backend/app/iot`, `domain/safety`, `features/safety` (`edge/` only once deployable) |
| M05 Site Intelligence | `domain/operations`, `features/operations` |
| M06 Operator ML | `ml/`, `backend/app/intelligence` |
| M07 Copilot | `backend/app/copilot`, `features/copilot` |
| M08 Training | `domain/training`, `features/training` |
| M09 Counterfactual | `backend/app/intelligence/counterfactual`, scenarios view |
| M10 Federated | `ml/federated` |
| M11 Analytics & Eval | `ml/evaluation`, KPIs in `domain/operations`, `docs/research` |

## 2. Phases and gates

Only **M00** and **M01** are prerequisites (both built). Everything after gate G1 runs in parallel against contracts and mocks. Gate checklists: `INTEGRATION_CHECKPOINTS.md`.

| Phase | Workstreams | Gate |
|-------|-------------|------|
| 0 | M00 | G0: one command runs the stack; CI green |
| 1 | M01 | G1: assign → operator sees task → telemetry → twin → operator sees state; contracts v1 frozen |
| 2 | M02, M03, M04, M06 | G2: demo scenes 1–5 |
| 3 | M05, M07, M08 | G3: demo scenes 6–10 |
| 4 | M09, M10, M11 | G4: scenes 11–12 + evaluation |

Phases are "start no earlier than" hints. With mocks, any workstream can start once G1 passes.

## 3. Rules that keep parallel work conflict-free

1. **Stay in your ownership area** (`REPOSITORY_STRUCTURE.md` §6). Shared paths change through small, reviewed PRs.
2. **Talk through contracts.** Other capabilities are used through their `service.py`/`schemas.py` (in-process) or REST/events. Never import another capability's `models`.
3. **Contract first, mock second, real third.** When you start a capability, publish its schemas/events (and a mock or fixture from the examples) before the real logic, so consumers aren't blocked.
4. **No central registration files.** New endpoints: a new `api/v1/<area>.py` (auto-included). New capability wiring: `domain/<area>/wiring.py` (auto-discovered). New simulator scenarios: `iot/simulator/scenarios/<theme>.py`. New page: a route folder + one nav line.
5. **Generated files are regenerated, never merged by hand:** `python scripts/dev.py contracts`. Lockfiles: take `develop`'s version and re-run `uv lock` / `pnpm install`.
6. **Migrations are linear.** If two branches both add a revision, the second to merge rebases and re-parents its revision (`alembic merge` only as a last resort).
7. **Status on every push and pull** (`SYNC_PROTOCOL.md`): one writer per status file, so status never conflicts.
8. **Safety logic is deterministic; the Copilot is grounded.** Reviewers reject changes that violate either.

## 4. Remaining hotspots and how they're handled

| Hotspot | Handling |
|---------|----------|
| `contracts/openapi/argus-api.yaml` | Generated. On conflict: accept either side, run `python scripts/dev.py contracts`, commit |
| `frontend/src/features/{operator,supervisor}/nav.ts` | One line per page. Keep the list sorted by page order |
| `backend/app/seed/__init__.py` (`SEEDERS`) | One line per seeder, append-only |
| `backend/app/schemas/common.py`, `frontend/src/components/ui/` | Shared: small PRs reviewed by area A + the requester |
| `pyproject.toml`/`uv.lock`, `frontend/package.json`/`pnpm-lock.yaml` | Declare deps in the PR that needs them; regenerate lockfiles on conflict |

## 5. Refining boundaries

| Change | Who decides | How |
|--------|-------------|-----|
| Add/split work packages | Workstream owner | Edit your workstream file |
| New capability package | Area owner | Create it with real code + wiring; update `REPOSITORY_STRUCTURE.md` §2 |
| Move a responsibility between areas | Both owners | Short ADR + update ownership table + CODEOWNERS |
| New top-level folder or runtime | Team | ADR (see ADR-0002 "When is a new top-level directory justified?") |
| Product intent | Team | Master plan + its change log §115 |
