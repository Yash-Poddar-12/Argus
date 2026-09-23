# M03 — Supervisor/Admin Console · STATUS

> **Only the module owner (and their agent) edits this file.** Update it in the same commit as your code, **before every push**.
> Shortcut: `python scripts/status.py log --module M03 --action PUSH --msg "..." [--wp M03-WP1=DONE] [--state IN_PROGRESS]`
> States: `NOT_STARTED` · `IN_PROGRESS` · `MOCKED` (contract + mock shipped) · `BLOCKED` · `IN_REVIEW` · `DONE`
> Spec: [SPEC.md](SPEC.md)

<!-- status:summary (parsed by scripts/status.py; keep the table shape) -->
| Field | Value |
|-------|-------|
| Module | M03 |
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
| M03-WP0 | Mock layer + site WS replay mock (S1–S6) | NOT_STARTED | — | |
| M03-WP1 | CRUD: operators, machines, sites, zones (incl. zone drawing) | NOT_STARTED | — | |
| M03-WP2 | Tasks: create/update, deadlines, targets, assistance | NOT_STARTED | — | |
| M03-WP3 | Assignments with consequence preview | NOT_STARTED | — | |
| M03-WP4 | Site map with togglable layers + live positions | NOT_STARTED | — | |
| M03-WP5 | Safety/hazards view + rule/threshold config + device registry | NOT_STARTED | — | |
| M03-WP6 | Overview + operator support context | NOT_STARTED | — | |
| M03-SLOT-SI | Site-intel slot: interaction graph viz, bottlenecks, utilization, recommendations | NOT_STARTED | — | |
| M03-SLOT-SC | Scenarios slot: build "what if", compare baseline vs scenario, safety check, uncertainty | NOT_STARTED | — | |
| M03-SLOT-TA | Training-admin slot: catalogue, triggers, operator training status, impact | NOT_STARTED | — | |
| M03-SLOT-AN | Analytics slot: KPIs, experiment results | NOT_STARTED | — | |

## Using mocks for

| Dependency | Mock source | Switch to real when |
|------------|-------------|---------------------|
| M01 tasks/assignments/site twin | OpenAPI examples + site WS replay | G1 |
| M04 hazards/rules/devices | `contracts/openapi/m04-safety.yaml` examples | M04-WP6 LIVE |
| M05 / M09 / M08 / M11 slots | their contract examples | each module LIVE |

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
