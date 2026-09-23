# M05 — Site Operational Intelligence · STATUS

> **Only the module owner (and their agent) edits this file.** Update it in the same commit as your code, **before every push**.
> Shortcut: `python scripts/status.py log --module M05 --action PUSH --msg "..." [--wp M05-WP1=DONE] [--state IN_PROGRESS]`
> States: `NOT_STARTED` · `IN_PROGRESS` · `MOCKED` (contract + mock shipped) · `BLOCKED` · `IN_REVIEW` · `DONE`
> Spec: [SPEC.md](SPEC.md)

<!-- status:summary (parsed by scripts/status.py; keep the table shape) -->
| Field | Value |
|-------|-------|
| Module | M05 |
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
| M05-WP0 | Contracts + `public.py` + mocks (graph, bottleneck, recommendation examples for the E1/D1/D2 story) | NOT_STARTED | — | |
| M05-WP1 | Graph builder (read model from events) | NOT_STARTED | — | |
| M05-WP2 | Edge statistics (rolling windows) | NOT_STARTED | — | |
| M05-WP3 | Bottleneck detection + impact estimation | NOT_STARTED | — | |
| M05-WP4 | Recommendations + safety constraint check | NOT_STARTED | — | |
| M05-WP5 | WHY? site-evidence feed + `get_site_bottlenecks` tool | NOT_STARTED | — | |
| M05-WP6 | Site simulator scenarios (S4, dumper shortage, irregular arrivals) | NOT_STARTED | — | |
| M05-SLOT | Admin site-intel slot UI (if held) | NOT_STARTED | — | |

## Using mocks for

| Dependency | Mock source | Switch to real when |
|------------|-------------|---------------------|
| M01 telemetry/task events | simulator S4 output | G1 |
| M04 hazard events | `contracts/events/m04/examples` | M04-WP6 LIVE |

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
