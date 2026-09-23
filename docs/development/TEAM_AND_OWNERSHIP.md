# Team & Ownership

> **Fill this in at kickoff.** It maps people → ownership areas → workstreams. Paths per area: `docs/architecture/REPOSITORY_STRUCTURE.md` §6. Enforcement: `.github/CODEOWNERS`.

## 1. Roster

| Person | GitHub handle | IDE / agent | Ownership area | Workstreams | Time zone / hours |
|--------|---------------|-------------|----------------|-------------|-------------------|
| A | `@Developer-Devanshhh` | Claude CLI | A · Platform & twin | M00, M01 (built), integration lead | |
| B | `@handle-b` | e.g. Antigravity | B · Operator UX + Copilot | M02, M07 | |
| C | `@handle-c` | e.g. Codex CLI | C · Supervisor + Operations | M03, M05 | |
| D | `@handle-d` | | D · IoT + ML | M04, M06 | |
| E | `@handle-e` | | E · Training + intelligence research | M08, M09, M10, M11 | |

**Integration lead** (default A): runs the gates, reviews shared paths (`contracts/`, `core/`, `components/`, `lib/`), merges `develop` → `main`.

## 2. Areas (from REPOSITORY_STRUCTURE.md §6)

| Area | Owns | Typical work |
|------|------|--------------|
| **A · Platform & twin** | `backend/app/core`, `domain/{platform,tasks,telemetry,environment,twin}`, their `api/v1` files, migrations, seed, `contracts/schemas`, infra, scripts, CI | shared backend, twin, contracts steward |
| **B · Operator UX + Copilot** | `frontend/src/app/operator`, `features/{operator,copilot}`, `backend/app/copilot`, `contracts/tools` | operator screens, Copilot agent + UI |
| **C · Supervisor + Operations** | `frontend/src/app/supervisor`, `features/{supervisor,operations,machines}`, `backend/app/domain/operations` | admin console, site intelligence, KPIs |
| **D · IoT + ML** | `backend/app/iot`, `domain/safety`, `features/safety`, `backend/app/intelligence` (interfaces/adapters), `ml/` | hazard mesh, safety events, models |
| **E · Training + research** | `backend/app/domain/training`, `features/training`, `intelligence/counterfactual`, `ml/evaluation`, `docs/research` | training loop, what-if engine, evaluation |

## 3. Team size

| Team | Merge areas |
|------|-------------|
| 5 | A · B · C · D · E as above |
| 4 | A+E, B, C, D |
| 3 | A+E, B+C (all frontend + Copilot), D |

Shared frontend feature folders (`features/tasks`, `features/auth`) and shared UI (`components/`, `lib/`, `hooks/`) take small PRs reviewed by A and the area that needs the change.

## 4. Workstream ownership (fill in)

| Workstream | Owner | Backup reviewer |
|------------|-------|-----------------|
| M00 Foundation | @Developer-Devanshhh | |
| M01 Operational Twin | @Developer-Devanshhh | |
| M02 Operator Experience | | |
| M03 Supervisor/Admin Console | | |
| M04 IoT Hazard Mesh | | |
| M05 Site Intelligence | | |
| M06 Operator ML | | |
| M07 Copilot | | |
| M08 Training | | |
| M09 Counterfactual | | |
| M10 Federated | | |
| M11 Analytics & Eval | | |

## 5. Communication

| Need | Channel |
|------|---------|
| Status | Your workstream file's Status section (async, in Git) |
| Blocker on another area | Status → Blockers **and** ping the owner |
| Breaking contract change | `.github/ISSUE_TEMPLATE/contract_change.md` issue + ping consumers |
| Architecture decision / new top-level folder | ADR PR (`docs/architecture/decisions/`) |
| Gate | Short call or async checklist (`INTEGRATION_CHECKPOINTS.md`) |
