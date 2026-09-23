# M08 — Training (closed-loop) · STATUS

> **Only the module owner (and their agent) edits this file.** Update it in the same commit as your code, **before every push**.
> Shortcut: `python scripts/status.py log --module M08 --action PUSH --msg "..." [--wp M08-WP1=DONE] [--state IN_PROGRESS]`
> States: `NOT_STARTED` · `IN_PROGRESS` · `MOCKED` (contract + mock shipped) · `BLOCKED` · `IN_REVIEW` · `DONE`
> Spec: [SPEC.md](SPEC.md)

<!-- status:summary (parsed by scripts/status.py; keep the table shape) -->
| Field | Value |
|-------|-------|
| Module | M08 |
| Owner | @unassigned |
| Phase | 3 |
| State | NOT_STARTED |
| Current focus | — |
| Contract version | — |
| Last updated | 2026-09-23 · @team · status file created |
<!-- /status:summary -->

## Work packages

| WP | Title | State | Branch / PR | Notes |
|----|-------|-------|-------------|-------|
| M08-WP0 | Contracts + `public.py` + mocks (recommendation with reason, impact example) | NOT_STARTED | — | |
| M08-WP1 | Catalogue + content format + 6 seed micro-modules (en; hi/ta titles) | NOT_STARTED | — | |
| M08-WP2 | Sessions + assessments | NOT_STARTED | — | |
| M08-WP3 | Trigger engine (event-driven rules, windows) | NOT_STARTED | — | |
| M08-WP4 | Recommendation engine + reasons + priority | NOT_STARTED | — | |
| M08-WP5 | Impact measurement (before/after, observed association) | NOT_STARTED | — | |
| M08-SLOT-T | Operator training slot UI (if held) | NOT_STARTED | — | |
| M08-SLOT-TA | Admin training-admin slot UI (if held) | NOT_STARTED | — | |

## Using mocks for

| Dependency | Mock source | Switch to real when |
|------------|-------------|---------------------|
| M06 anomaly/skill/deviation | `contracts/events/m06/examples` | M06-WP4/WP6/WP7 LIVE |
| M04 safety events | `contracts/events/m04/examples` | M04-WP6 LIVE |

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
