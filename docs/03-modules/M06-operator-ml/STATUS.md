# M06 — Operator Intelligence / ML (+ WHY? Engine) · STATUS

> **Only the module owner (and their agent) edits this file.** Update it in the same commit as your code, **before every push**.
> Shortcut: `python scripts/status.py log --module M06 --action PUSH --msg "..." [--wp M06-WP1=DONE] [--state IN_PROGRESS]`
> States: `NOT_STARTED` · `IN_PROGRESS` · `MOCKED` (contract + mock shipped) · `BLOCKED` · `IN_REVIEW` · `DONE`
> Spec: [SPEC.md](SPEC.md)

<!-- status:summary (parsed by scripts/status.py; keep the table shape) -->
| Field | Value |
|-------|-------|
| Module | M06 |
| Owner | @unassigned |
| Phase | 2 |
| State | NOT_STARTED |
| Current focus | — |
| Contract version | — |
| Last updated | 2026-09-23 · @team · status file created |
<!-- /status:summary -->

## Work packages

| WP | Title | State | Branch / PR | Notes |
|----|-------|-------|-------------|-------|
| M06-WP0 | Contracts + `public.py` + mocks for all 5 interfaces (shipped first, unblocks M01/M02/M07/M09) | NOT_STARTED | — | |
| M06-WP1 | Dataset generation from simulator + feature pipeline | NOT_STARTED | — | |
| M06-WP2 | Behavior profiles, multi-baseline, cold start | NOT_STARTED | — | |
| M06-WP3 | Task-time predictor (quantile LightGBM) + SHAP + confidence | NOT_STARTED | — | |
| M06-WP4 | Anomaly model (IsolationForest) + severity + signals | NOT_STARTED | — | |
| M06-WP5 | Risk model (evidence only) | NOT_STARTED | — | |
| M06-WP6 | WHY? Engine (rules + evidence graph, root-cause categories) | NOT_STARTED | — | |
| M06-WP7 | Skill estimation (hybrid) | NOT_STARTED | — | |
| M06-WP8 | Model registry, model cards, serving, cache, event emission | NOT_STARTED | — | |
| M06-WP9 | Behavior scenarios (S5 etc.) + machine-only baselines for M11 | NOT_STARTED | — | |

## Using mocks for

| Dependency | Mock source | Switch to real when |
|------------|-------------|---------------------|
| M01 telemetry/task/env events | simulator datasets | G1 |
| M04 safety events | `contracts/events/m04/examples` | M04-WP6 LIVE |
| M05 site evidence | `contracts/events/m05/examples` | M05-WP5 LIVE |

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
