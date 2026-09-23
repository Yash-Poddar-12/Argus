# M01 — Operational Twin (core domain) · STATUS

> **Only the module owner (and their agent) edits this file.** Update it in the same commit as your code, **before every push**.
> Shortcut: `python scripts/status.py log --module M01 --action PUSH --msg "..." [--wp M01-WP1=DONE] [--state IN_PROGRESS]`
> States: `NOT_STARTED` · `IN_PROGRESS` · `MOCKED` (contract + mock shipped) · `BLOCKED` · `IN_REVIEW` · `DONE`
> Spec: [SPEC.md](SPEC.md)

<!-- status:summary (parsed by scripts/status.py; keep the table shape) -->
| Field | Value |
|-------|-------|
| Module | M01 |
| Owner | @unassigned |
| Phase | 1 |
| State | NOT_STARTED |
| Current focus | — |
| Contract version | — |
| Last updated | 2026-09-23 · @team · status file created |
<!-- /status:summary -->

## Work packages

| WP | Title | State | Branch / PR | Notes |
|----|-------|-------|-------------|-------|
| M01-WP0 | Contracts v1 draft: twin schema, m01 OpenAPI, m01 events, tool schemas, `public.py` with mocks | NOT_STARTED | — | |
| M01-WP1 | Task / Assignment / TaskSession / pre-check / machine-confirm domain + APIs + events | NOT_STARTED | — | |
| M01-WP2 | Simulator core + scenarios S1, S6 + plugin interface | NOT_STARTED | — | |
| M01-WP3 | Telemetry ingestion + context fusion + Redis twin projection + snapshots | NOT_STARTED | — | |
| M01-WP4 | Twin query API + WS pushes + tool implementations | NOT_STARTED | — | |
| M01-WP5 | Environment/weather adapter (mock-first) + conditions API | NOT_STARTED | — | |
| M01-WP6 | G1 vertical-slice end-to-end test + seed tasks | NOT_STARTED | — | |

## Using mocks for

| Dependency | Mock source | Switch to real when |
|------------|-------------|---------------------|
| M00 auth/master data (if WP2/WP3 not merged) | `backend/modules/m00_platform/public.py` mocks | M00-WP3 LIVE |
| M04 safety slot / M06 intelligence slots | publish example events from `contracts/events/m04|m06/examples` | G2 |

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
