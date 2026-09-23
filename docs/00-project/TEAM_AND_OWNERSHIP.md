# Team & Ownership

> **Fill this in at kickoff.** It's the only place that maps people to modules. After kickoff, changes need a team agreement recorded in a PR.

## 1. Roster

| Person | GitHub handle | Primary IDE / agent | Modules owned | Slots held | Time zone / hours |
|--------|---------------|---------------------|---------------|------------|-------------------|
| A | `@handle-a` | e.g. Claude CLI | | | |
| B | `@handle-b` | e.g. Antigravity | | | |
| C | `@handle-c` | e.g. Codex CLI | | | |
| D | `@handle-d` | | | | |
| E | `@handle-e` | | | | |

**Integration lead:** Person A by default. They own M00/M01, run the gates, and merge `develop` → `main`.

## 2. Recommended allocations

Pick the row for your team size. Each person's modules are chosen so they **share as few paths as possible**, and each person has something to do in every phase.

### Team of 3

| Person | Phase 0–1 (base) | Phase 2 | Phase 3 | Phase 4 |
|--------|------------------|---------|---------|---------|
| A | M00-WP1/WP2/WP5, M01-WP1/WP3 | M01 hardening, contracts steward | M05 | M09 |
| B | M00-WP4, M01-WP4 | M02 (+ copilot/training slots) | M07 | M11 (UI + demo) |
| C | M00-WP3, M01-WP2/WP5 | M04, M06 | M08 | M10 (optional) |

### Team of 4

| Person | Phase 0–1 | Phase 2 | Phase 3 | Phase 4 |
|--------|-----------|---------|---------|---------|
| A | M00-WP1/WP2/WP5, M01-WP1/WP3 | contracts steward, M03 backend support | M05 | M09 |
| B | M00-WP4, M01-WP4 | M02 | M07 (+ copilot slot) | demo polish |
| C | M00-WP3 | M03, M04 | M05 slot in admin | M11 |
| D | M01-WP2/WP5 | M06 | M08 | M10 (optional) |

### Team of 5

| Person | Phase 0–1 | Phase 2 | Phase 3 | Phase 4 |
|--------|-----------|---------|---------|---------|
| A | M00-WP1/WP2, M01-WP1/WP3 | contracts steward, integration | M05 | M09 |
| B | M00-WP4 | M02 | M07 | demo polish |
| C | M00-WP3, M01-WP4 | M03 | site-intel + scenarios slots | M09 UI |
| D | M01-WP2 | M04 | M05 edge/hazard inputs, M06 support | M11 |
| E | M00-WP5, M01-WP5 | M06 | M08 | M10, M11 |

These tables follow master §55. If they differ, this file wins because it reflects the actual team.

## 3. Module ownership (fill in)

| Module | Owner | Backup reviewer | Slots delegated to |
|--------|-------|-----------------|--------------------|
| M00 Foundation | | | — |
| M01 Operational Twin | | | — |
| M02 Operator Experience | | | copilot → ?, training → ? |
| M03 Supervisor/Admin Console | | | site-intel → ?, scenarios → ?, training-admin → ?, analytics → ? |
| M04 IoT Hazard Mesh | | | — |
| M05 Site Intelligence | | | — |
| M06 Operator ML | | | — |
| M07 Copilot | | | — |
| M08 Training | | | — |
| M09 Counterfactual | | | — |
| M10 Federated | | | — |
| M11 Analytics & Eval | | | — |

**Backup reviewer** reviews that module's PRs and can pick it up if the owner is unavailable.

## 4. CODEOWNERS

When handles are known, uncomment and fill in `.github/CODEOWNERS`. Paths come from `docs/01-architecture/REPO_STRUCTURE.md` §2. Turn on "Require review from Code Owners" on `develop` in GitHub branch protection.

## 5. Communication

| Need | Channel |
|------|---------|
| Status | Your module's `STATUS.md` (async, in Git) |
| Blocker on another module | Your STATUS.md → Blockers **and** ping the owner |
| Breaking contract change | `.github/ISSUE_TEMPLATE/contract_change.md` issue + ping consumers |
| Architecture decision | ADR PR |
| Gate | Short call or async checklist (`docs/04-workflow/INTEGRATION_CHECKPOINTS.md`) |
