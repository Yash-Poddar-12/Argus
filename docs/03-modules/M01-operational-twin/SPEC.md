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
- **Simulator core:** seeded clock, entities from seed data, telemetry generator per machine type, event emitter, CLI `make sim SCENARIO=S1 SEED=42 SPEED=10x`, scenario plugin interface (other modules add scenarios in `simulator/scenarios/<module>/`)
- **Environment adapter:** weather/soil/visibility per site/zone, mock-first (scripted by the simulator) with a pluggable real provider
- **Twin:** state layer (current operator/machine/task/environment state in Redis) + intelligence-layer **slots** filled by events from other modules (risk from M04/M06, ETA from M06, anomaly from M06, familiarity etc.); snapshots in `twin_snapshots`
- **Twin API + WS:** operator twin, site twin, conditions; push `TASK_UPDATE`, `TASK_ETA_UPDATED`, `MACHINE_STATE_UPDATE`, `TWIN_UPDATE`
- **Tools** (implementation in `public.py`): `get_current_machine_state`, `get_current_task`, `get_task_progress`, `get_machine_health`, `get_weather`, `get_site_conditions`

## Out of scope

Safety decisions (M04), predictions (M06). The twin **stores and serves** their outputs but never computes them. Also out: copilot, training recommendations, site optimization.

## Owned paths

`backend/modules/m01_twin/{tasks,twin,api,environment}/`, `backend/migrations/m01_twin/`, `backend/tests/m01_twin/`, `simulator/core/`, `simulator/scenarios/core/`, `contracts/schemas/twin/`, `contracts/openapi/m01-twin.yaml`, `contracts/events/m01/`, `contracts/tools/{get_current_machine_state,get_current_task,get_task_progress,get_machine_health,get_weather,get_site_conditions}.json`.

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

## Work packages

| WP | Title | Paths | Depends on | Est. |
|----|-------|-------|------------|------|
| M01-WP0 | Contracts v1 draft: twin schema, m01 OpenAPI, m01 events, tool schemas, `public.py` with mocks | `contracts/…`, `public.py`, `mocks/` | M00-WP5 | 1 d |
| M01-WP1 | Task / Assignment / TaskSession / pre-check / machine-confirm domain + APIs + events | `m01_twin/tasks/` | M00-WP2/WP3 | 2–3 d |
| M01-WP2 | Simulator core + scenarios S1, S6 + plugin interface | `simulator/core/`, `simulator/scenarios/core/` | WP0 | 2 d |
| M01-WP3 | Telemetry ingestion + context fusion + Redis twin projection + snapshots | `m01_twin/twin/` | WP1, WP2 | 2–3 d |
| M01-WP4 | Twin query API + WS pushes + tool implementations | `m01_twin/api/` | WP3 | 1–2 d |
| M01-WP5 | Environment/weather adapter (mock-first) + conditions API | `m01_twin/environment/` | WP0 | 1 d |
| M01-WP6 | G1 vertical-slice end-to-end test + seed tasks | `backend/tests/m01_twin/` | WP1–WP5 | 1 d |

## Acceptance criteria (G1)

- [ ] `POST /assignments` for OP1001 → EXC001 → TASK001 emits `operator.task.assigned` and pushes `TASK_UPDATE` to `/ws/operators/OP1001` in < 1 s
- [ ] `GET /operators/OP1001/tasks/today` returns TASK001
- [ ] Machine confirm → pre-check → start → pause → resume → complete: all transitions validated (illegal transitions rejected) and emitted
- [ ] `make sim SCENARIO=S1 SEED=42` produces identical telemetry on every run; the twin updates within 2 s of ingestion
- [ ] `GET /operators/OP1001/twin` returns a schema-valid twin; intelligence fields null when M04/M06 are absent, filled when mock events are published
- [ ] Twin can be rebuilt from DB + events after a Redis flush
- [ ] All six tools return schema-valid results
- [ ] Contracts tagged **v1** and frozen

## Testing

State-machine unit tests; fusion unit tests (out-of-order and late telemetry); simulator determinism test; contract tests for APIs, events, and tools; the G1 end-to-end test.

## Future extensions

Richer environment sources (real weather API), twin history/time-travel queries, per-zone site twin, CAN/J1939 ingestion adapter.

## Known constraints

Keep fusion logic in `domain/` (pure) so M09 can reuse it through `public.py` to build **modified** twins for counterfactuals.

## Integration checklist

- [ ] M02 and M03 can render real twin/task data (not just mocks)
- [ ] M04, M06, and M05 have consumed a real `machine.telemetry.received` stream
- [ ] Tag `g1` on `main`
