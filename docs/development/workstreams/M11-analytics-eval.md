# M11 — Analytics & Evaluation

| Field | Value |
|-------|-------|
| Phase | 4 (metric definitions and harness can start any time; read-only) |
| Type | Research/eval (`ml/evaluation/`) + small backend module (+ admin analytics slot) |
| Depends on (contracts) | read-only on all events and APIs |
| Consumed by | M03, the research report, the demo |
| Gate | G4 (evaluation report) |

## Objective

Measure whether the system works and whether contextual intelligence beats machine-only baselines: system, safety, model, training, and operational metrics, plus the research questions RQ1–RQ6 (master §72–§74).

## Scope

- Metric definitions (master §74): safety (precision/recall/F1, false alert rate, alert latency, critical miss rate), anomaly, task prediction (MAE/RMSE/MAPE/R², interval coverage), training (completion, scores, pre/post change, recurrence), system (p50/p95 latency, throughput, event loss, recovery time, offline continuity, WS delivery latency)
- Eval harness: runs seeded simulator scenarios end to end and collects metrics
- Research experiments:
  - RQ1 anomaly: contextual vs machine-only
  - RQ2 task-time: contextual fusion vs machine-only
  - RQ3 attribution: false attribution to operators with vs without the WHY? engine
  - RQ4 training: observed behavior change after recommendations
  - RQ5 edge-first: alert latency and availability under network interruption
  - RQ6 interaction graph: bottleneck detection quality
- KPI API + admin analytics slot
- Final evaluation report (`analytics/reports/`)

## Out of scope

Writing to other modules' tables; model training (M06). M11 only reads and computes.

## Where the code lives

`ml/evaluation/` (model/research evaluation), `backend/app/domain/operations/` (KPIs), `docs/research/` (write-ups), `frontend/src/features/operations/` (analytics view).

Folders are created only when real code lands. Ownership rules and the full map: `docs/architecture/REPOSITORY_STRUCTURE.md`.

## Work package plan

| WP | Title | Est. |
|----|-------|------|
| M11-WP0 | Metric definitions doc + KPI contract + mocks | 1 d |
| M11-WP1 | System metrics collection (latency, WS delivery, event loss) | 1–2 d |
| M11-WP2 | Eval harness over seeded scenarios | 2 d |
| M11-WP3 | RQ1/RQ2 model comparisons (with M06 baselines) | 2 d |
| M11-WP4 | RQ3/RQ5/RQ6 experiments | 2 d |
| M11-WP5 | RQ4 training impact analysis (observed association) | 1 d |
| M11-WP6 | KPI API + analytics slot (if held) | 1–2 d |
| M11-WP7 | Evaluation report | 1–2 d |

## Acceptance criteria

- [ ] One command reproduces all headline numbers from seeds
- [ ] Every claim in the report states its data source (simulated vs real) and method, and avoids causal language without a causal design
- [ ] Baseline vs proposed comparison tables for RQ1 and RQ2 at minimum

## Known constraints

Results on simulated data must be labeled as such.

---

# Status

> **Only the workstream owner (and their agent) edits this file.** Update it in the same commit as your code, **before every push**.
> Shortcut: `python scripts/status.py log --module M11 --action PUSH --msg "..." [--wp M11-WP1=DONE] [--state IN_PROGRESS]`
> States: `NOT_STARTED` · `IN_PROGRESS` · `MOCKED` (contract + mock shipped) · `BLOCKED` · `IN_REVIEW` · `DONE`

<!-- status:summary (parsed by scripts/status.py; keep the table shape) -->
| Field | Value |
|-------|-------|
| Module | M11 |
| Owner | @unassigned |
| Phase | 4 |
| State | NOT_STARTED |
| Current focus | — |
| Contract version | — |
| Last updated | 2026-09-23 · @team · status file created |
<!-- /status:summary -->

## Work packages

| WP | Title | State | Branch / PR | Notes |
|----|-------|-------|-------------|-------|
| M11-WP0 | Metric definitions doc + KPI contract + mocks | NOT_STARTED | — | |
| M11-WP1 | System metrics collection (latency, WS delivery, event loss) | NOT_STARTED | — | |
| M11-WP2 | Eval harness over seeded scenarios | NOT_STARTED | — | |
| M11-WP3 | RQ1/RQ2 model comparisons (with M06 baselines) | NOT_STARTED | — | |
| M11-WP4 | RQ3/RQ5/RQ6 experiments | NOT_STARTED | — | |
| M11-WP5 | RQ4 training impact analysis (observed association) | NOT_STARTED | — | |
| M11-WP6 | KPI API + analytics slot (if held) | NOT_STARTED | — | |
| M11-WP7 | Evaluation report | NOT_STARTED | — | |

## Using mocks for

| Dependency | Mock source | Switch to real when |
|------------|-------------|---------------------|
| All event streams | simulator + contract examples | each producer LIVE |

## Blockers

- none

## Contract changes (pending / recent)

- none

## Open questions

- none

## Update log

<!-- newest first · one line per push: date · @handle · ACTION · branch · summary -->
<!-- log:insert -->
- 2026-09-23 · @team · INIT · docs scaffold · Status file created from SPEC work packages
