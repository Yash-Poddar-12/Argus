# M03 — Supervisor/Admin Console

| Field | Value |
|-------|-------|
| Phase | 2 |
| Type | Frontend (`frontend/src/app/supervisor/`) |
| Depends on (contracts) | M00, M01; mocks of M04, M05, M09, M11 |
| Consumed by | supervisors/admins |
| Gate | G2 (assignment + site map), G3/G4 (intel + scenarios slots) |

## Objective

A practical, operational console where every action has a clear consequence for an operator, machine, task, or site safety/productivity (master §7). It supports the operator and is not a competing product.

## Scope

- CRUD: operators, machines, sites, zones (drawing zones on the map)
- Tasks: create/update, deadlines, targets, priority, **additional assistance/resources** (e.g., Dumper D2)
- Assignments: operator + machine + task, with visible consequences ("operator will see this now", predicted ETA)
- **Site map** (MapLibre): machines, operators, workers, hazard/restricted/task zones, routes, proximity alerts, congestion, weather. Layers are togglable; the default shows active machines, active operator/task, critical hazards, current task zones, and major conditions (§69)
- Safety/hazards view: live site hazards, event list with "why", safety rule & threshold configuration, device/tag registry
- Overview: site status at a glance, operator support context (who may need help, framed as support, not blame)
- **Slots** (pre-registered, delegable): `site-intel` (M05), `scenarios` (M09), `training-admin` (M08), `analytics` (M11)

## Out of scope

ML, IoT sensor algorithms, Copilot reasoning, bottleneck computation (M05), scenario simulation (M09). The console **visualizes** these; it doesn't compute them.

## Where the code lives

`frontend/src/app/supervisor/`, `frontend/src/features/supervisor/`, plus the supervisor views in `frontend/src/features/{machines,tasks,safety}/`.

Folders are created only when real code lands. Ownership rules and the full map: `docs/architecture/REPOSITORY_STRUCTURE.md`.

## Inputs

REST: M00 CRUD; M01 tasks/assignments/site twin; M04 hazards, rules, devices, alerts; M05/M09/M08/M11 via slots. WS `/ws/sites/{site_id}`: all site-level message types.

## Outputs

User actions via REST. No events or tables of its own.

## Work package plan

| WP | Title | Depends on | Est. |
|----|-------|------------|------|
| M03-WP0 | Mock layer + site WS replay mock (S1–S6) | M00-WP4 | 1 d |
| M03-WP1 | CRUD: operators, machines, sites, zones (incl. zone drawing) | M00 | 2 d |
| M03-WP2 | Tasks: create/update, deadlines, targets, assistance | M01 | 1–2 d |
| M03-WP3 | Assignments with consequence preview | M01, mock M06 | 1–2 d |
| M03-WP4 | Site map with togglable layers + live positions | M01 site twin, mock M04 | 2–3 d |
| M03-WP5 | Safety/hazards view + rule/threshold config + device registry | mock/real M04 | 2 d |
| M03-WP6 | Overview + operator support context | M01, M04, M06 | 1–2 d |
| M03-SLOT-SI | Site-intel slot: interaction graph viz, bottlenecks, utilization, recommendations | mock/real M05 | 2 d |
| M03-SLOT-SC | Scenarios slot: build "what if", compare baseline vs scenario, safety check, uncertainty | mock/real M09 | 2 d |
| M03-SLOT-TA | Training-admin slot: catalogue, triggers, operator training status, impact | mock/real M08 | 1–2 d |
| M03-SLOT-AN | Analytics slot: KPIs, experiment results | mock/real M11 | 1 d |

## Acceptance criteria

- [ ] Assigning OP1001 → EXC001 → TASK001 shows up in the operator app within 1 s (G1/G2 scene)
- [ ] Map default view isn't cluttered; each layer toggles independently; state persists per user
- [ ] Safety rule changes are versioned and show when they reached the edge (from M04 status)
- [ ] All destructive actions confirm and are audit-logged (via M00 APIs)
- [ ] Recommendations and scenario results are phrased as decision support ("The simulation indicates…")

## Testing

Component tests, Playwright for the assignment flow and map layers, mock-driven tests for each slot.

## Future extensions

Multi-site switcher, reports export, shift planning calendar, dispatch board.

## Known constraints

Keep the console operational and lean (master §3.3). Push back on "second product" scope creep.

## Integration checklist

- [ ] Slot holders recorded in `TEAM_AND_OWNERSHIP.md`
- [ ] Every slot runs against mocks before its backend is LIVE

---

# Status

> **Only the workstream owner (and their agent) edits this file.** Update it in the same commit as your code, **before every push**.
> Shortcut: `python scripts/status.py log --module M03 --action PUSH --msg "..." [--wp M03-WP1=DONE] [--state IN_PROGRESS]`
> States: `NOT_STARTED` · `IN_PROGRESS` · `MOCKED` (contract + mock shipped) · `BLOCKED` · `IN_REVIEW` · `DONE`

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
| M04 hazards/rules/devices | `contracts/openapi/argus-api.yaml` examples | M04-WP6 LIVE |
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
