# M05 — Site Operational Intelligence

| Field | Value |
|-------|-------|
| Phase | 3 |
| Type | Backend module + simulator scenarios (+ admin slot) |
| Depends on (contracts) | M01, M04 |
| Consumed by | M03, M06 (WHY? site evidence), M07, M09 |
| Gate | G3 (scene 10 bottleneck) |

## Objective

Model the site as a **dynamic machine interaction graph** (nodes: machines, people, zones, resources; edges: loading dependency, material flow, proximity), compute edge statistics, and detect bottlenecks, imbalance, and underutilization. Produce **safety-checked** operational recommendations.

## Why this module exists

It turns individual telemetry into site-level understanding ("E1 waits because D2 queues at a congested disposal zone"). This is the core of USP 5 and the evidence behind "Don't blame the operator" (site-driven delay).

## Scope

- Graph builder from events (M01 telemetry/state/task sessions, M04 proximity/zone): nodes, edges, active flags
- Edge statistics: avg wait, load/unload time, trips/hour, queue time, utilization, interaction efficiency, safety events
- Bottleneck detection + impact estimate (min/hour of non-productive time, affected nodes)
- Fleet balance, machine utilization, material-flow throughput
- Recommendations (dispatch/reallocation insights) with a **safety constraint check** (M04 rules, M06 risk evidence) before they're published (P8)
- Site-evidence feed for the WHY? engine (`site_intel.bottleneck.detected`, `get_site_bottlenecks` tool)
- Simulator scenarios S4 (site bottleneck), dumper shortage, irregular arrivals

## Out of scope

Proximity safety alerts (M04), counterfactual simulation (M09 consumes M05's graph), UI (admin slot, delegable).

## Where the code lives

`backend/app/domain/operations/`, `backend/app/api/v1/operations.py`, `backend/app/iot/simulator/scenarios/site.py`, `contracts/events/operations/`, `frontend/src/features/operations/`.

Folders are created only when real code lands. Ownership rules and the full map: `docs/architecture/REPOSITORY_STRUCTURE.md`.

## Interfaces

Produces the APIs in `API_CATALOG.md` § M05, the `site_intel.*` events, and the tables `interaction_nodes`, `interaction_edges`, `interaction_stats`, `bottlenecks`, `site_recommendations`. Consumes `machine.telemetry.received`, `machine.state.changed`, `task.*`, `hazard.*`, `platform.zone.updated`.

## Work package plan

| WP | Title | Est. |
|----|-------|------|
| M05-WP0 | Contracts + schemas + service + mocks (graph, bottleneck, recommendation examples for the E1/D1/D2 story) | 1 d |
| M05-WP1 | Graph builder (read model from events) | 2 d |
| M05-WP2 | Edge statistics (rolling windows) | 2 d |
| M05-WP3 | Bottleneck detection + impact estimation | 2 d |
| M05-WP4 | Recommendations + safety constraint check | 1–2 d |
| M05-WP5 | WHY? site-evidence feed + `get_site_bottlenecks` tool | 1 d |
| M05-WP6 | Site simulator scenarios (S4, dumper shortage, irregular arrivals) | 1–2 d |
| M05-SLOT | Admin site-intel slot UI (if held) | 2 d |

## Acceptance criteria

- [ ] On S4 (seeded), detects Disposal Zone as the bottleneck with E1 and D2 affected and an impact estimate within ±20% of the simulator's ground truth
- [ ] Stats update incrementally (no full recompute per event) and are reproducible for a given seed
- [ ] No recommendation is published without `safety_check_passed` and its evidence
- [ ] Interaction graph API renders in the admin slot with live updates

## Testing

Unit tests on stat calculations; scenario tests with simulator ground truth; contract tests.

## Future extensions

Queueing-theory models, material-flow optimization, multi-site comparisons, dispatch suggestions over time windows.

## Known constraints

M05 builds its **own read model** from events and doesn't read M01/M04 tables directly (DATA_OWNERSHIP).

## Integration checklist

- [ ] M06 WHY? engine attributes S4 delay to SITE
- [ ] M09 can load the graph as a scenario baseline

---

# Status

> **Only the workstream owner (and their agent) edits this file.** Update it in the same commit as your code, **before every push**.
> Shortcut: `python scripts/status.py log --module M05 --action PUSH --msg "..." [--wp M05-WP1=DONE] [--state IN_PROGRESS]`
> States: `NOT_STARTED` · `IN_PROGRESS` · `MOCKED` (contract + mock shipped) · `BLOCKED` · `IN_REVIEW` · `DONE`

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
| M05-WP0 | Contracts + schemas + service + mocks (graph, bottleneck, recommendation examples for the E1/D1/D2 story) | NOT_STARTED | — | |
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
| M04 hazard events | `contracts/events/<area>/examples` | M04-WP6 LIVE |

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
