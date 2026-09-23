# M04 — IoT Hazard Mesh (edge + safety) · STATUS

> **Only the module owner (and their agent) edits this file.** Update it in the same commit as your code, **before every push**.
> Shortcut: `python scripts/status.py log --module M04 --action PUSH --msg "..." [--wp M04-WP1=DONE] [--state IN_PROGRESS]`
> States: `NOT_STARTED` · `IN_PROGRESS` · `MOCKED` (contract + mock shipped) · `BLOCKED` · `IN_REVIEW` · `DONE`
> Spec: [SPEC.md](SPEC.md)

<!-- status:summary (parsed by scripts/status.py; keep the table shape) -->
| Field | Value |
|-------|-------|
| Module | M04 |
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
| M04-WP0 | Contracts + `public.py` + mocks (events, APIs, tools) + example alert fixtures | NOT_STARTED | — | |
| M04-WP1 | Edge skeleton: DeviceAdapter, MQTT sim adapter, local state store | NOT_STARTED | — | |
| M04-WP2 | Proximity engine (distance, closing speed, TTC, radius per machine type) | NOT_STARTED | — | |
| M04-WP3 | Zone logic (geofence, entry/exit, hysteresis) | NOT_STARTED | — | |
| M04-WP4 | Deterministic rules engine + sensor validation + rule versioning | NOT_STARTED | — | |
| M04-WP5 | Local alert path + SQLite buffer + replay + dedupe | NOT_STARTED | — | |
| M04-WP6 | Cloud ingestion, persistence, ack, safety APIs, WS pushes, tools | NOT_STARTED | — | |
| M04-WP7 | Rule/threshold config API + push to edge + device registry | NOT_STARTED | — | |
| M04-WP8 | Hazard simulator scenarios + offline/latency test harness | NOT_STARTED | — | |

## Using mocks for

| Dependency | Mock source | Switch to real when |
|------------|-------------|---------------------|
| M01 telemetry stream | simulator core or `contracts/events/m01/examples` | M01-WP3 LIVE |
| M00 zones | seed zones fixture | M00-WP3 LIVE |

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
