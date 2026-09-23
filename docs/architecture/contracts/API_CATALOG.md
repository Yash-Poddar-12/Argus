# API Catalog

> Every REST and WebSocket endpoint, its owning module, and its known consumers. Base path `/api/v1`. The exact shapes are in `contracts/openapi/argus-api.yaml`. **Edit only your module's section.** Paths must be unique across modules, so check here before adding one.
>
> Status: `PLANNED` → `MOCKED` → `LIVE` → `DEPRECATED`
>
> M00 and M01 endpoints are LIVE; their OpenAPI files are **generated from code** (`uv run python scripts/contracts.py export`). Interactive docs: `http://localhost:8000/docs`.

## M00 — Platform

| Method | Path | Purpose | Consumers | Status |
|--------|------|---------|-----------|--------|
| POST | `/auth/login` | Login, returns JWT | M02, M03 | LIVE |
| GET | `/auth/me` | Current identity, role, permissions, site scope | M02, M03 | LIVE |
| GET/POST | `/operators` | List/create operators | M03 | LIVE |
| GET/PATCH | `/operators/{operator_id}` | Read/update operator | M02, M03, M07 | LIVE |
| GET/POST | `/machines` | List/create machines | M03 | LIVE |
| GET/PATCH | `/machines/{machine_id}` | Read/update machine master data | M02, M03 | LIVE |
| GET/POST | `/sites` | List/create sites | M03 | LIVE |
| GET/PATCH | `/sites/{site_id}` | Read/update site | M03 | LIVE |
| GET/POST | `/sites/{site_id}/zones` | Site zones (geometry, type) | M03, M04, M05 | LIVE |
| PATCH | `/sites/{site_id}/zones/{zone_id}` | Update zone | M03 | LIVE |
| GET | `/health`, `/ready`, `/version`, `/metrics` | Observability (no `/api/v1` prefix) | infra | LIVE |

## M01 — Operational Twin & core domain

| Method | Path | Purpose | Consumers | Status |
|--------|------|---------|-----------|--------|
| POST | `/tasks` | Create task | M03 | LIVE |
| GET/PATCH | `/tasks/{task_id}` | Read/update task (deadline, target, assistance) | M02, M03, M07 | LIVE |
| GET | `/sites/{site_id}/tasks` | Site task list (filters) | M03 | LIVE |
| POST | `/tasks/{task_id}/assign` | Shortcut: create assignment | M03 | LIVE |
| POST | `/assignments` | Assign operator + machine to task | M03 | LIVE |
| PATCH | `/assignments/{assignment_id}` | Update/cancel assignment | M03 | LIVE |
| GET | `/operators/{operator_id}/tasks/today` | Operator's tasks for today | M02, M07 | LIVE |
| POST | `/operators/{operator_id}/machine/confirm` | Confirm assigned machine (T02) | M02 | LIVE |
| GET | `/machines/{machine_id}/precheck` | Pre-op checklist template | M02 | LIVE |
| POST | `/machines/{machine_id}/precheck` | Submit pre-op check (T03) | M02 | LIVE |
| POST | `/tasks/{task_id}/start` · `/pause` · `/resume` · `/complete` | Task session lifecycle (T05, T08–T10) | M02 | LIVE |
| GET | `/tasks/{task_id}/summary` | Post-task summary (T11) | M02 | LIVE |
| POST | `/telemetry` | Ingest machine telemetry batch (simulator / edge forwarder) | simulator, M04 edge | LIVE |
| GET | `/machines/{machine_id}/state` | Current machine state | M02, M03, M07 | LIVE |
| GET | `/machines/{machine_id}/telemetry` | Telemetry history (time range) | M02, M03, M06 | LIVE |
| GET | `/operators/{operator_id}/twin` | Current operational twin (state + intelligence layer) | M02, M07, M09 | LIVE |
| GET | `/sites/{site_id}/twin` | Site-level twin snapshot (all active twins) | M03, M05, M09 | LIVE |
| GET | `/sites/{site_id}/conditions` | Environment + site conditions | M02, M07 | LIVE |
| POST | `/sites/{site_id}/conditions` | Record conditions (simulator, supervisor, future weather provider) | simulator, M03 | LIVE |

## M04 — IoT Hazard Mesh / Safety

| Method | Path | Purpose | Consumers | Status |
|--------|------|---------|-----------|--------|
| POST | `/safety/events` | Ingest safety/hazard events from edge (idempotent on `event_id`) | edge | PLANNED |
| GET | `/safety/events/{event_id}` | Event detail incl. "why" (rule, sensor values, thresholds) | M02, M07 | PLANNED |
| POST | `/safety/events/{event_id}/acknowledge` | Operator acknowledges (T07) | M02 | PLANNED |
| GET | `/operators/{operator_id}/safety` | Operator safety status + recent events | M02, M07 | PLANNED |
| GET | `/machines/{machine_id}/alerts` | Machine alerts | M02, M03 | PLANNED |
| GET | `/sites/{site_id}/hazards` | Active hazards + proximity graph snapshot | M03, M05 | PLANNED |
| GET/PUT | `/sites/{site_id}/safety-rules` | Safety rules and thresholds (pushed to edge) | M03 | PLANNED |
| GET/POST | `/sites/{site_id}/devices` | Device/tag registry | M03 | PLANNED |

## M05 — Site Operational Intelligence

| Method | Path | Purpose | Consumers | Status |
|--------|------|---------|-----------|--------|
| GET | `/sites/{site_id}/interaction-graph` | Nodes, edges, edge statistics | M03, M09 | PLANNED |
| GET | `/sites/{site_id}/bottlenecks` | Detected bottlenecks + impact | M03, M07, M06 | PLANNED |
| GET | `/sites/{site_id}/utilization` | Machine utilization + fleet balance | M03 | PLANNED |
| GET | `/sites/{site_id}/recommendations` | Operational recommendations (safety-checked) | M03 | PLANNED |

## M06 — Operator Intelligence / ML

| Method | Path | Purpose | Consumers | Status |
|--------|------|---------|-----------|--------|
| POST | `/predictions/task-time` | Task duration P50/P80/P90 + contributors | M01, M07, M09 | PLANNED |
| POST | `/predictions/risk` | Contextual risk probability + factors | M04, M07, M09 | PLANNED |
| POST | `/predictions/anomaly` | Behavior anomaly score + signals | M08, M07 | PLANNED |
| POST | `/explanations/deviation` | WHY? engine: root-cause attribution with evidence | M02, M03, M07 | PLANNED |
| GET | `/operators/{operator_id}/performance` | Trends, baselines, fingerprint, "what changed" | M02, M03, M07 | PLANNED |
| GET | `/operators/{operator_id}/skills` | Skill profile | M08, M02 | PLANNED |
| GET | `/models` | Model registry: versions, metrics | M11, M10 | PLANNED |

## M07 — Copilot

| Method | Path | Purpose | Consumers | Status |
|--------|------|---------|-----------|--------|
| POST | `/copilot/query` | Text query → grounded answer + tool trace | M02 | PLANNED |
| POST | `/copilot/voice` | Audio → STT → answer → text + TTS audio | M02 | PLANNED |
| GET | `/copilot/conversations/{conversation_id}` | Conversation history | M02 | PLANNED |
| GET | `/copilot/languages` | Supported languages | M02 | PLANNED |

## M08 — Training

| Method | Path | Purpose | Consumers | Status |
|--------|------|---------|-----------|--------|
| GET | `/training/modules` | Catalogue | M02, M03 | PLANNED |
| GET | `/training/recommendations/{operator_id}` | Recommended modules + reasons | M02, M07 | PLANNED |
| POST | `/training/{training_id}/start` | Start a session (T13) | M02 | PLANNED |
| POST | `/training/sessions/{session_id}/complete` | Complete + assessment score (T14) | M02 | PLANNED |
| GET | `/operators/{operator_id}/training` | Operator training history + impact | M02, M03, M07 | PLANNED |
| GET/PUT | `/training/triggers` | Trigger rules config | M03 | PLANNED |

> Note: master §35 lists `POST /training/{session_id}/complete`. It is namespaced to `/training/sessions/{session_id}/complete` here so it can't collide with `/training/{training_id}/...`.

## M09 — Counterfactual

| Method | Path | Purpose | Consumers | Status |
|--------|------|---------|-----------|--------|
| POST | `/scenarios` | Define scenario (modifications to twin) | M03, M07 | PLANNED |
| GET | `/scenarios/{scenario_id}` | Scenario + latest results | M03, M07 | PLANNED |
| POST | `/scenarios/{scenario_id}/run` | Run simulation → comparison + safety check + uncertainty (T17) | M03, M07 | PLANNED |

## M11 — Analytics

| Method | Path | Purpose | Consumers | Status |
|--------|------|---------|-----------|--------|
| GET | `/analytics/kpis` | Site/operator KPIs (time range) | M03 | PLANNED |
| GET | `/analytics/experiments/{experiment_id}` | Evaluation results | M03 | PLANNED |

---

## WebSocket channels (gateway owned by M00; message types owned by producer)

| Channel | Audience | Auth scope |
|---------|----------|-----------|
| `/ws/operators/{operator_id}` | That operator's app | the operator, or a supervisor for that site |
| `/ws/machines/{machine_id}` | Machine views | site scope |
| `/ws/sites/{site_id}` | Admin console | SUPERVISOR_ADMIN for that site |

| Message type | Producer | Channels |
|--------------|----------|----------|
| `TASK_UPDATE` | M01 | operator, site |
| `TASK_ETA_UPDATED` | M01 (attaches M06 prediction to the twin) | operator, site |
| `MACHINE_STATE_UPDATE` | M01 | operator, machine, site |
| `TWIN_UPDATE` | M01 | operator, site |
| `SAFETY_ALERT` | M04 | operator, machine, site |
| `HAZARD_UPDATE` | M04 | operator, site |
| `SITE_INTEL_UPDATE` | M05 | site |
| `COPILOT_PROACTIVE_MESSAGE` | M07 | operator |
| `TRAINING_RECOMMENDATION` | M08 | operator |

WS message shape: `{ "type": "SAFETY_ALERT", "version": "1.0", "timestamp": "...", "data": { ... } }`. The `data` schema is `contracts/events/<area>/ws/<TYPE>.v1.json`.
