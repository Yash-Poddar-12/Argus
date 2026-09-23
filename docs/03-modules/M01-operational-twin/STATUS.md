# M01 — Operational Twin (core domain) · STATUS

> **Only the module owner (and their agent) edits this file.** Update it in the same commit as your code, **before every push**.
> Shortcut: `python scripts/status.py log --module M01 --action PUSH --msg "..." [--wp M01-WP1=DONE] [--state IN_PROGRESS]`
> States: `NOT_STARTED` · `IN_PROGRESS` · `MOCKED` (contract + mock shipped) · `BLOCKED` · `IN_REVIEW` · `DONE`
> Spec: [SPEC.md](SPEC.md)

<!-- status:summary (parsed by scripts/status.py; keep the table shape) -->
| Field | Value |
|-------|-------|
| Module | M01 |
| Owner | @Developer-Devanshhh |
| Phase | 1 |
| State | IN_REVIEW |
| Current focus | G1 gate: UI slice via M02/M03 + Docker verification |
| Contract version | m01-twin 1.0.0 (generated) · events v1 · tools v1 · twin schema v1 |
| Last updated | 2026-09-23 · @Developer-Devanshhh · M01 implemented: tasks/assignments/sessions/pre-checks + lif |
<!-- /status:summary -->

## Work packages

| WP | Title | State | Branch / PR | Notes |
|----|-------|-------|-------------|-------|
| M01-WP0 | Contracts v1 draft: twin schema, m01 OpenAPI, m01 events, tool schemas, `public.py` with mocks | IN_REVIEW | — | |
| M01-WP1 | Task / Assignment / TaskSession / pre-check / machine-confirm domain + APIs + events | IN_REVIEW | — | |
| M01-WP2 | Simulator core + scenarios S1, S6 + plugin interface | IN_REVIEW | — | |
| M01-WP3 | Telemetry ingestion + context fusion + Redis twin projection + snapshots | IN_REVIEW | — | |
| M01-WP4 | Twin query API + WS pushes + tool implementations | IN_REVIEW | — | |
| M01-WP5 | Environment/weather adapter (mock-first) + conditions API | IN_REVIEW | — | |
| M01-WP6 | G1 vertical-slice end-to-end test + seed tasks | IN_REVIEW | — | |

## Using mocks for

| Dependency | Mock source | Switch to real when |
|------------|-------------|---------------------|
| M00 auth/master data | none needed: real M00 (stacked branch) | — |
| M04 safety slot / M06 intelligence slots | tests publish stand-in events (validation off) | M04/M06 publish their event contracts (WP0) |

## Blockers

- none

## Contract changes (pending / recent)

- none

## Open questions

- Service account for telemetry ingestion (simulator/edge currently use a supervisor login): add a `SERVICE` role in M00?
- Should `twin.updated` throttling (10 s) be configurable per consumer need (M05/M09)?

## Verification notes

- 24 M01 tests (state machine, pre-check rules, fusion, simulator determinism + S6 effect, G1 vertical slice over HTTP + WS, permissions, task CRUD, assignment update/cancel, intelligence slots, rebuild-after-flush equality, environment, site twin, 6 tools vs contracts, Redis state store path). Full suite: 41 passed.
- Live check: lite server + `simulator.core.cli --scenario S6 --demo-g1` over real HTTP (assign → confirm → pre-check → start → 543 telemetry points → twin shows progress + WET/HIGH difficulty).
- Not verified: Postgres/Timescale migrations (hypertables), Redis Streams consumer loop under Docker.

## Update log

<!-- newest first · one line per push: date · @handle · ACTION · branch · summary -->
<!-- log:insert -->
- 2026-09-23 · @Developer-Devanshhh · PUSH · feature/m01-operational-twin · M01 implemented: tasks/assignments/sessions/pre-checks + lifecycle, telemetry ingestion, context fusion + Redis twin (full/light refresh, intelligence slots, snapshots), twin/site/machine APIs + WS, environment adapter, 6 Copilot tools, generated contracts, deterministic simulator (S1, S6, --demo-g1)
- 2026-09-23 · @team · INIT · docs scaffold · Status file created from SPEC work packages
