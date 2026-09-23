# M06 — Operator Intelligence / ML (+ WHY? Engine)

| Field | Value |
|-------|-------|
| Phase | 2 (feature work and notebooks can start on simulator output during Phase 1) |
| Type | ML pipelines (`ml/`) + inference/explanation backend module |
| Depends on (contracts) | M00, M01; mock M04; M05 (site evidence, later) |
| Consumed by | M01 (twin intelligence), M02, M03, M07, M08, M09, M10, M11 |
| Gate | G2 (ETA scene 5), G3 (root cause scene 6, drift scene 7) |

## Objective

Behind stable contracts, provide operator baselines (Personal Operating Fingerprint), the **task-time predictor**, **behavior anomaly** detection, **contextual risk** evidence, **skill estimation**, and the **WHY? Engine** that attributes deviations to OPERATOR / MACHINE / TASK / SITE / ENVIRONMENT / INTERACTION / UNKNOWN with evidence.

## Why this module exists

Predictions and explanations are the "Understand → Predict" part of the product thesis. Putting all ML behind one module's `schemas.py`/`service.py` means frontend and Copilot never depend on model internals (master §26), and models can be swapped (P12).

## Scope

- Feature engineering (master §85): deviations vs personal/machine/site baselines, recent safety/proximity counts, progress rate, familiarity, congestion, environmental difficulty, time since training
- **Behavior profiles** + multi-baseline + **cold-start fallback** (personal → machine → site → task → fleet)
- **M2 task-time:** LightGBM quantile models (P50/P80/P90) + SHAP contributors + confidence level/reason
- **M1 anomaly:** IsolationForest (MVP) over behavior features; severity + contributing signals
- **M3 risk:** gradient-boosted classifier → probability, level, factors. **Evidence only** (never triggers alerts)
- **M4 skill estimation:** hybrid rules + behavior metrics + assessment results (from M08 events)
- **WHY? Engine:** rules + evidence graph combining operator baselines, machine state, task state, environment (M01), and site evidence (M05). Outputs attribution shares + evidence + confidence
- Model registry (versions, metrics, model cards), inference serving via `schemas.py`/`service.py` + REST, inference cache
- Machine-only **baseline models** for research comparison (RQ1, RQ2) handed to M11
- Behavior simulator scenarios (S5 drift, high idle, machine slowdown)
- Tools: `predict_task_duration`, `get_operator_performance`, `explain_operational_deviation`

## Out of scope

Safety decisions (M04), training recommendation logic (M08 consumes skill gaps), federated training (M10), deep temporal models (future extension).

## Where the code lives

`ml/` (features, models, training, evaluation), `backend/app/intelligence/` (inference interfaces + ML adapters), `models/` (artifact registry/configs, once artifacts exist), `backend/app/iot/simulator/scenarios/behavior.py`, `contracts/schemas/ml/`.

Folders are created only when real code lands. Ownership rules and the full map: `docs/architecture/REPOSITORY_STRUCTURE.md`.

## Interfaces

See `TOOL_AND_ML_CONTRACTS.md` Part B (the canonical mock lives there). Produces the `prediction.*` and `operator.*` (anomaly/profile/skill/deviation) events and the tables listed in `DATA_OWNERSHIP.md` § M06. Consumes `machine.telemetry.received`, `task.*`, `operator.task.assigned`, `environment.conditions.updated`, `safety.event.raised`, `hazard.*`, `site_intel.*`, `training.completed`.

**When predictions run:** on `operator.task.assigned` (initial ETA), periodically during `IN_PROGRESS` (e.g., every 60 s or every N cycles), and on significant context change (environment, bottleneck).

## Work package plan

| WP | Title | Est. |
|----|-------|------|
| M06-WP0 | Contracts + schemas + service + mocks for all 5 interfaces (shipped first, unblocks M01/M02/M07/M09) | 1 d |
| M06-WP1 | Dataset generation from simulator + feature pipeline | 2 d |
| M06-WP2 | Behavior profiles, multi-baseline, cold start | 2 d |
| M06-WP3 | Task-time predictor (quantile LightGBM) + SHAP + confidence | 2–3 d |
| M06-WP4 | Anomaly model (IsolationForest) + severity + signals | 1–2 d |
| M06-WP5 | Risk model (evidence only) | 1–2 d |
| M06-WP6 | WHY? Engine (rules + evidence graph, root-cause categories) | 2–3 d |
| M06-WP7 | Skill estimation (hybrid) | 1–2 d |
| M06-WP8 | Model registry, model cards, serving, cache, event emission | 1–2 d |
| M06-WP9 | Behavior scenarios (S5 etc.) + machine-only baselines for M11 | 1–2 d |

## Acceptance criteria

- [ ] Every output conforms to `contracts/ml/*` and carries `model_version`, `confidence_level`, `contributors`, `fallback_level`
- [ ] On S6 (wet soil, no operator deviation), the WHY? engine attributes most of the delay to ENVIRONMENT; on S4 to SITE; on S5 to OPERATOR
- [ ] Task-time: MAE and P80 coverage reported on a held-out seeded dataset, plus comparison vs the machine-only baseline
- [ ] New operator (no history) → prediction with `fallback_level ≠ PERSONAL` and a LOW/MODERATE confidence reason
- [ ] Inference p95 < 300 ms in-process for task-time and risk
- [ ] Training pipelines reproducible from a seed; artifacts registered with model cards

## Testing

Feature unit tests, model smoke tests (train on a tiny dataset in CI), contract tests on outputs, scenario tests for WHY? attribution.

## Future extensions

Temporal models (LSTM/TFT), Bayesian Knowledge Tracing for skills, learning-to-rank for training (with M08), causal impact models (with M11).

## Known constraints

Simulated data can make models look better than they are. Always report metrics as "on simulated data" and keep a machine-only baseline for honest comparison.

## Integration checklist

- [ ] M01 twin shows real ETA/risk/anomaly
- [ ] M07 tools switched from mock to real
- [ ] M08 receives anomaly/skill events

---

# Status

> **Only the workstream owner (and their agent) edits this file.** Update it in the same commit as your code, **before every push**.
> Shortcut: `python scripts/status.py log --module M06 --action PUSH --msg "..." [--wp M06-WP1=DONE] [--state IN_PROGRESS]`
> States: `NOT_STARTED` · `IN_PROGRESS` · `MOCKED` (contract + mock shipped) · `BLOCKED` · `IN_REVIEW` · `DONE`

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
| M06-WP0 | Contracts + schemas + service + mocks for all 5 interfaces (shipped first, unblocks M01/M02/M07/M09) | NOT_STARTED | — | |
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
| M04 safety events | `contracts/events/<area>/examples` | M04-WP6 LIVE |
| M05 site evidence | `contracts/events/<area>/examples` | M05-WP5 LIVE |

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
