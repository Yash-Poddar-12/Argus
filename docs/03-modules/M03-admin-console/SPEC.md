# M03 — Supervisor/Admin Console

| Field | Value |
|-------|-------|
| Phase | 2 |
| Type | Frontend (`frontend/apps/admin`) |
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

## Owned paths

`frontend/apps/admin/**` except delegated slot folders.

## Inputs

REST: M00 CRUD; M01 tasks/assignments/site twin; M04 hazards, rules, devices, alerts; M05/M09/M08/M11 via slots. WS `/ws/sites/{site_id}`: all site-level message types.

## Outputs

User actions via REST. No events or tables of its own.

## Work packages

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
