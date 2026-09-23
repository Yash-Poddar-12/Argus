# M01 — Operational Twin (core domain)

| Field | Value |
|-------|-------|
| Phase | 1 (base) |
| Type | Core domain / backend + simulator |
| Depends on | M00 |
| Consumed by | every module |
| Exit gate | **G1**: vertical slice works end to end + **contracts v1 frozen** |

## Objective

Build the shared **operator–machine–task–environment** context: the task/assignment/session domain, telemetry ingestion, a deterministic simulator, context fusion into the **Human-Machine Operational Twin**, and the twin query API + live WebSocket updates.

## Why this module exists

Every intelligence module (safety, ML, copilot, training, site intel, scenarios) reads the same context. If each built its own, we'd have competing sources of truth (master §108 rule 9). M01 is that single source.

## Scope

- **Core domain:** Task, Assignment, TaskSession (start/pause/resume/complete), machine confirmation, pre-op checklist templates + results, task summary
- **Telemetry ingestion:** `POST /telemetry` (batch), persisted to Timescale `machine_telemetry`, emitted as `machine.telemetry.received`
- **Simulator core:** seeded clock, entities from seed data, telemetry generator per machine type, event emitter, CLI `python scripts/dev.py sim --scenario S1 --seed 42 [--speed N] [--demo-g1]`, scenario plugin interface (other modules add scenarios in `backend/app/iot/simulator/scenarios/<theme>.py`)
- **Environment adapter:** weather/soil/visibility per site/zone, mock-first (scripted by the simulator) with a pluggable real provider
- **Twin:** state layer (current operator/machine/task/environment state in Redis) + intelligence-layer **slots** filled by events from other modules (risk from M04/M06, ETA from M06, anomaly from M06, familiarity etc.); snapshots in `twin_snapshots`
- **Twin API + WS:** operator twin, site twin, conditions; push `TASK_UPDATE`, `TASK_ETA_UPDATED`, `MACHINE_STATE_UPDATE`, `TWIN_UPDATE`
- **Tools** (implementation in `schemas.py`/`service.py`): `get_current_machine_state`, `get_current_task`, `get_task_progress`, `get_machine_health`, `get_weather`, `get_site_conditions`

## Out of scope

Safety decisions (M04), predictions (M06). The twin **stores and serves** their outputs but never computes them. Also out: copilot, training recommendations, site optimization.

## Where the code lives

`backend/app/domain/{tasks,telemetry,environment,twin}/`, `backend/app/api/v1/{tasks,telemetry,environment,twin}.py`, `backend/app/copilot/tools/` (twin/task/environment tools), `backend/app/iot/simulator/`, `backend/app/seed/tasks.py`, `contracts/schemas/twin/`, `contracts/events/{tasks,telemetry,environment,twin}/`, `contracts/tools/`.

Folders are created only when real code lands. Ownership rules and the full map: `docs/architecture/REPOSITORY_STRUCTURE.md`.

## Twin shape (v1 draft, finalized in WP0)

```json
{
  "operator_id": "OP1001", "machine_id": "EXC001", "task_id": "TASK001", "site_id": "SITE_A",
  "as_of": "2026-09-23T08:15:00Z",
  "state": {
    "operator": { "status": "ACTIVE", "experience_level": "SENIOR", "machine_familiarity": "HIGH" },
    "machine":  { "operating_mode": "DIGGING", "fuel_pct": 62, "speed": 8.2, "rpm": 1650, "engine_hours": 4210.5,
                  "seatbelt": true, "location": { "lat": 0, "lon": 0 }, "health": "OK" },
    "task":     { "status": "IN_PROGRESS", "progress_pct": 48, "cycles_done": 24, "target_cycles": 50,
                  "planned_end": "2026-09-23T10:30:00Z" },
    "environment": { "weather": "RAIN", "temperature_c": 31, "soil": "WET", "visibility": "GOOD" },
    "site": { "zone_id": "ZONE_A", "nearby_workers": 2, "nearby_machines": 1, "congestion": "MEDIUM" }
  },
  "intelligence": {
    "safety":       { "level": "LOW", "source": "M04", "as_of": "..." },
    "risk":         { "level": "LOW", "probability": 0.08, "source": "M06", "model_version": "..." },
    "eta":          { "p50_completion_at": "...", "confidence_level": "HIGH", "source": "M06" },
    "anomaly":      { "severity": "LOW", "source": "M06" },
    "productivity": { "state": "NORMAL" },
    "environmental_difficulty": "MEDIUM"
  },
  "freshness": { "telemetry_age_s": 2, "environment_age_s": 300 }
}
```

Intelligence fields are **nullable**. The twin is valid without M04/M06, which keeps G1 independent of Phase 2.

## Interfaces

Produces the APIs in `API_CATALOG.md` § M01, the events in `EVENT_CATALOG.md` § M01, the tables in `DATA_OWNERSHIP.md` (tasks, assignments, sessions, prechecks, telemetry, state changes, operator/environment events, twin snapshots), and Redis `twin:*`.

Consumes: `platform.*` (M00), `safety.event.raised` / `hazard.*` (M04) → twin safety slot, `prediction.*` (M06) → twin intelligence slots.

## Work package plan

| WP | Title | Paths | Depends on | Est. |
|----|-------|-------|------------|------|
| M01-WP0 | Contracts v1 draft: twin schema, m01 OpenAPI, m01 events, tool schemas, `schemas.py`/`service.py` with mocks | `contracts/…`, `schemas.py`/`service.py`, `mocks/` | M00-WP5 | 1 d |
| M01-WP1 | Task / Assignment / TaskSession / pre-check / machine-confirm domain + APIs + events | `backend/app/domain/tasks/` | M00-WP2/WP3 | 2–3 d |
| M01-WP2 | Simulator core + scenarios S1, S6 + plugin interface | `backend/app/iot/simulator/`, `backend/app/iot/simulator/scenarios/baseline.py` | WP0 | 2 d |
| M01-WP3 | Telemetry ingestion + context fusion + Redis twin projection + snapshots | `backend/app/domain/twin/` | WP1, WP2 | 2–3 d |
| M01-WP4 | Twin query API + WS pushes + tool implementations | `backend/app/api/v1/twin.py` | WP3 | 1–2 d |
| M01-WP5 | Environment/weather adapter (mock-first) + conditions API | `backend/app/domain/environment/` | WP0 | 1 d |
| M01-WP6 | G1 vertical-slice end-to-end test + seed tasks | `backend/tests/<area>/` | WP1–WP5 | 1 d |

## Acceptance criteria (G1)

- [x] `POST /assignments` for OP1001 → EXC001 → TASK001 emits `operator.task.assigned` and pushes `TASK_UPDATE` to `/ws/operators/OP1001` in < 1 s
- [x] `GET /operators/OP1001/tasks/today` returns TASK001
- [x] Machine confirm → pre-check → start → pause → resume → complete: all transitions validated (illegal transitions rejected) and emitted
- [x] `python scripts/dev.py sim --scenario S1 --seed 42` produces identical telemetry on every run; the twin updates within 2 s of ingestion
- [x] `GET /operators/OP1001/twin` returns a schema-valid twin; intelligence fields null when M04/M06 are absent, filled when mock events are published
- [x] Twin can be rebuilt from DB + events after a Redis flush
- [x] All six tools return schema-valid results
- [ ] Contracts tagged **v1** and frozen

## Testing

State-machine unit tests; fusion unit tests (out-of-order and late telemetry); simulator determinism test; contract tests for APIs, events, and tools; the G1 end-to-end test.

## As built (2026-09-23)

| Topic | Decision |
|-------|----------|
| Layout | `tasks/` (domain.py pure state machine + service + api), `twin/` (fusion.py pure, service, telemetry, handlers), `environment/`, `api/` (twin + telemetry endpoints, Copilot tools) |
| Contracts | OpenAPI, twin schema, all 14 event schemas and 6 tool schemas are **generated from `schemas.py`/`service.py` models** (`scripts/contracts.py export`, drift-checked in CI). Examples in `contracts/**/examples/` |
| Start guards | Active assignment to the caller, machine confirmed ≤ 12 h ago (the assigned one), latest pre-check ≤ 12 h and passed (all items answered, no CRITICAL item failed), no other active session for the operator or machine |
| Cycles / progress | Baseline = machine `load_cycles` at start, or the first reading at/after start if the task started before any telemetry |
| Twin refresh | *Full* (DB) on lifecycle/assignment/master-data changes; *light* (cached context) on telemetry, environment, intelligence. `twin.updated` events are throttled to one per 10 s per operator for telemetry-only changes; WS `TWIN_UPDATE` is not throttled |
| Intelligence slots | Filled from `safety.event.raised`, `prediction.task_time.updated` (→ also WS `TASK_ETA_UPDATED`), `prediction.risk.updated`, `operator.anomaly.detected`; persisted in `twin_intelligence` so the twin rebuilds exactly after a Redis flush |
| Telemetry | Idempotent on `(machine_id, ts)`; out-of-order points are stored but don't regress live state; mode changes → `machine_state_changes` + `machine.state.changed` |
| Environment | Manual/simulator provider via `POST /sites/{id}/conditions`; `WeatherProvider` protocol for a real source later |
| Simulator | `simulator/core` (seeded engine, scenario discovery, HTTP/in-process/JSONL sinks, CLI with `--demo-g1`); scenarios S1 and S6 in `backend/app/iot/simulator/scenarios/baseline.py` |

**Known gaps:** WS payload schemas (`contracts/events/<area>/ws/`) not written yet; telemetry ingestion uses a supervisor token (a dedicated service account/role is future work); Timescale hypertable creation is untested on real Postgres (no Docker on the build machine); the G1 *UI* screens (assignment form, operator task view) belong to M03/M02. The slice is demonstrable through the API and `python scripts/dev.py sim --demo-g1`.

## Future extensions

Richer environment sources (real weather API), twin history/time-travel queries, per-zone site twin, CAN/J1939 ingestion adapter.

## Known constraints

Keep fusion logic in `domain/` (pure) so M09 can reuse it through `schemas.py`/`service.py` to build **modified** twins for counterfactuals.

## Integration checklist

- [ ] M02 and M03 can render real twin/task data (not just mocks)
- [ ] M04, M06, and M05 have consumed a real `machine.telemetry.received` stream
- [ ] Tag `g1` on `main`

---

# Status

> **Only the workstream owner (and their agent) edits this file.** Update it in the same commit as your code, **before every push**.
> Shortcut: `python scripts/status.py log --module M01 --action PUSH --msg "..." [--wp M01-WP1=DONE] [--state IN_PROGRESS]`
> States: `NOT_STARTED` · `IN_PROGRESS` · `MOCKED` (contract + mock shipped) · `BLOCKED` · `IN_REVIEW` · `DONE`

<!-- status:summary (parsed by scripts/status.py; keep the table shape) -->
| Field | Value |
|-------|-------|
| Module | M01 |
| Owner | @Developer-Devanshhh |
| Phase | 1 |
| State | IN_REVIEW |
| Current focus | G1 gate: UI slice via M02/M03 + Docker verification |
| Contract version | m01-twin 1.0.0 (generated) · events v1 · tools v1 · twin schema v1 |
| Last updated | 2026-09-23 · @Developer-Devanshhh · Code moved to backend/app/domain/{tasks,telemetry,environmen |
<!-- /status:summary -->

## Work packages

| WP | Title | State | Branch / PR | Notes |
|----|-------|-------|-------------|-------|
| M01-WP0 | Contracts v1 draft: twin schema, m01 OpenAPI, m01 events, tool schemas, `schemas.py`/`service.py` with mocks | IN_REVIEW | — | |
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
- Live check: lite server + `python -m app.iot.simulator --scenario S6 --demo-g1` over real HTTP (assign → confirm → pre-check → start → 543 telemetry points → twin shows progress + WET/HIGH difficulty).
- Not verified: Postgres/Timescale migrations (hypertables), Redis Streams consumer loop under Docker.

## Update log

<!-- newest first · one line per push: date · @handle · ACTION · branch · summary -->
<!-- log:insert -->
- 2026-09-23 · @Developer-Devanshhh · NOTE · refactor/production-structure · Code moved to backend/app/domain/{tasks,telemetry,environment,twin}, copilot/tools, iot/simulator (ADR-0002); behaviour and API unchanged
- 2026-09-23 · @Developer-Devanshhh · PUSH · feature/m01-operational-twin · M01 implemented: tasks/assignments/sessions/pre-checks + lifecycle, telemetry ingestion, context fusion + Redis twin (full/light refresh, intelligence slots, snapshots), twin/site/machine APIs + WS, environment adapter, 6 Copilot tools, generated contracts, deterministic simulator (S1, S6, --demo-g1)
- 2026-09-23 · @team · INIT · docs scaffold · Status file created from SPEC work packages
