# M02 — Operator Experience · STATUS

> **Only the module owner (and their agent) edits this file.** Update it in the same commit as your code, **before every push**.
> Shortcut: `python scripts/status.py log --module M02 --action PUSH --msg "..." [--wp M02-WP1=DONE] [--state IN_PROGRESS]`
> States: `NOT_STARTED` · `IN_PROGRESS` · `MOCKED` (contract + mock shipped) · `BLOCKED` · `IN_REVIEW` · `DONE`
> Spec: [SPEC.md](SPEC.md)

<!-- status:summary (parsed by scripts/status.py; keep the table shape) -->
| Field | Value |
|-------|-------|
| Module | M02 |
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
| M02-WP0 | Mock layer + WS replay mock + fixture scenarios S1–S6 | NOT_STARTED | — | |
| M02-WP1 | Login → machine confirm → pre-op checklist | NOT_STARTED | — | |
| M02-WP2 | My Day + shift briefing + "What changed?" | NOT_STARTED | — | |
| M02-WP3 | My Tasks + live operation (lifecycle, progress, ETA + WHY? drawer) | NOT_STARTED | — | |
| M02-WP4 | My Machine (live state, alerts, map) | NOT_STARTED | — | |
| M02-WP5 | My Safety + CRITICAL alert overlay + ack + "why this alert" | NOT_STARTED | — | |
| M02-WP6 | My Performance (non-punitive trends, baselines, deviation explanations) | NOT_STARTED | — | |
| M02-WP7 | Notification center + priority tiers + coaching tips | NOT_STARTED | — | |
| M02-WP8 | i18n (en/hi/ta UI strings), accessibility + glove/sunlight pass | NOT_STARTED | — | |
| M02-SLOT-C | Copilot slot UI (text + push-to-talk, tool trace "sources", language picker) | NOT_STARTED | — | |
| M02-SLOT-T | Training slot UI (recommendations with reasons, micro-learning player, assessment, impact) | NOT_STARTED | — | |

## Using mocks for

| Dependency | Mock source | Switch to real when |
|------------|-------------|---------------------|
| M01 tasks/twin | `contracts/openapi/m01-twin.yaml` examples + WS replay | G1 |
| M04 safety | `contracts/events/m04/examples` + WS replay S2/S3 | M04-WP6 LIVE |
| M06 ETA/performance/WHY? | `contracts/ml/examples` | M06-WP3/WP6 LIVE |
| M07 copilot (slot) | `contracts/openapi/m07-copilot.yaml` examples | M07-WP1 LIVE |
| M08 training (slot) | `contracts/openapi/m08-training.yaml` examples | M08-WP4 LIVE |

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
