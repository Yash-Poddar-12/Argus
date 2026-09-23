# M04 — IoT Hazard Mesh (edge + safety)

| Field | Value |
|-------|-------|
| Phase | 2 (proximity math and rule engine can start during Phase 0/1) |
| Type | Edge service + backend module + simulator scenarios |
| Depends on (contracts) | M00, M01 |
| Consumed by | M01 (twin safety slot), M02, M03, M05, M06, M07, M08, M11 |
| Gate | G2 (scene 4 hazard alert), RQ5 evaluation |

## Objective

Edge-first, **deterministic** site safety: detect machine–person and machine–machine proximity, restricted/hazard zone entry, seatbelt-while-moving, and emergencies. Raise **local alerts without a cloud round-trip**, buffer and replay to the cloud, and serve safety state and "why" to the rest of the platform.

## Why this module exists

Safety must keep working when the network doesn't (P10), and it must never depend on an LLM or a single ML score (P4). Isolating it in its own process and module lets it be tested, audited, and hardened on its own.

## Scope

**Edge (`edge/`):**
- `DeviceAdapter` interface; MQTT simulated adapter (BLE/UWB real adapters later)
- Local entity state: positions, velocities, headings, machine mode, seatbelt, zone membership
- Proximity engine: distances, closing speed, time-to-contact, operating-radius per machine type
- Zone logic: point-in-polygon geofences from M00 zones + M04 zone rules
- **Local safety rules engine:** deterministic rules with **sensor validation** (staleness, debounce, plausibility). Rules are versioned and configured from the cloud
- Local alert emitter (to the operator device channel) and local SQLite **buffer + replay** with `event_id` dedupe
- Optional edge ML hook (contextual evidence only)

**Cloud (`backend/modules/m04_safety/`):**
- Idempotent ingestion `POST /safety/events`, persistence, ack/resolve
- Operator/machine/site safety APIs; WS `SAFETY_ALERT`, `HAZARD_UPDATE`
- Safety rules and device registry APIs; rule push to the edge
- Tools: `get_safety_index`, `get_recent_alerts`, `get_alert_details`, `get_nearby_hazards`, `get_nearby_machines`

**Simulator (`simulator/scenarios/hazard/`):** S2 seatbelt, S3 worker hazard, machine–machine proximity, restricted-zone entry, network-drop scenario.

## Out of scope

Operational interaction analytics such as queues and bottlenecks (M05), risk ML models (M06; M04 may consume their output as evidence), and UI (M02/M03).

## Owned paths

`edge/`, `backend/modules/m04_safety/`, `backend/migrations/m04_safety/`, `backend/tests/m04_safety/`, `simulator/scenarios/hazard/`, `contracts/openapi/m04-safety.yaml`, `contracts/events/m04/`, `contracts/tools/{get_safety_index,get_recent_alerts,get_alert_details,get_nearby_hazards,get_nearby_machines}.json`, `infra/compose/m04.yml`.

## Interfaces

Produces the `safety.*`, `hazard.*`, and `device.*` events, the APIs in `API_CATALOG.md` § M04, and the tables `safety_events`, `incidents`, `safety_rules`, `zone_rules`, `devices`, `device_state`, plus the `hazard_events` hypertable.

Consumes `machine.telemetry.received` (M01) for machine speed/mode/seatbelt, `platform.zone.updated` (M00), and optionally `prediction.risk.updated` (M06) as evidence.

### Safety event fields (master §30)

`event_id, timestamp, machine_id, operator_id, site_id, event_type, severity, sensor_value, threshold, rule_id, rule_version, risk_score?, decision_source (RULE | EDGE_ML | CLOUD_ML | HYBRID), acknowledged_at, resolved_at`

## Work packages

| WP | Title | Paths | Est. |
|----|-------|-------|------|
| M04-WP0 | Contracts + `public.py` + mocks (events, APIs, tools) + example alert fixtures | contracts, cloud module | 1 d |
| M04-WP1 | Edge skeleton: DeviceAdapter, MQTT sim adapter, local state store | `edge/` | 1–2 d |
| M04-WP2 | Proximity engine (distance, closing speed, TTC, radius per machine type) | `edge/` | 2 d |
| M04-WP3 | Zone logic (geofence, entry/exit, hysteresis) | `edge/` | 1 d |
| M04-WP4 | Deterministic rules engine + sensor validation + rule versioning | `edge/` | 2 d |
| M04-WP5 | Local alert path + SQLite buffer + replay + dedupe | `edge/` | 1–2 d |
| M04-WP6 | Cloud ingestion, persistence, ack, safety APIs, WS pushes, tools | `backend/modules/m04_safety/` | 2 d |
| M04-WP7 | Rule/threshold config API + push to edge + device registry | both | 1–2 d |
| M04-WP8 | Hazard simulator scenarios + offline/latency test harness | `simulator/scenarios/hazard/` | 1–2 d |

## Acceptance criteria

- [ ] Simulated case `EXC001 speed=8, worker distance=5 m, closing speed=2 m/s` → HIGH proximity alert (master §82)
- [ ] Seatbelt unfastened + machine moving → alert; unfastened + parked → no alert
- [ ] Local alert latency p95 ≤ 200 ms from sensor message to alert emit (simulated)
- [ ] With cloud connectivity **cut**, local alerts keep firing; on reconnect, buffered events replay and the cloud holds no duplicates
- [ ] Every alert carries `rule_id`, `rule_version`, sensor values, and threshold, so "why" is fully answerable
- [ ] No code path lets the cloud API or UI suppress an edge safety rule without a versioned, audited rule change
- [ ] Stale or implausible sensor data is flagged and doesn't silently suppress alerts (fail-safe default documented)

## Testing

Pure-function unit tests for geometry, rules, and validation; property-based tests for proximity; simulation tests S2/S3; offline test; latency benchmark (feeds M11 RQ5).

## Future extensions

Real BLE/UWB adapters, trajectory prediction, edge ML (TFLite/ONNX), device mTLS, multi-gateway mesh.

## Known constraints

Positions in simulation are ideal; add configurable noise and dropout to keep validation logic honest.

## Integration checklist

- [ ] M01 twin shows the safety slot from real events
- [ ] M02 overlay driven by real `SAFETY_ALERT`
- [ ] M05 receives `hazard.*` events for interaction graph
