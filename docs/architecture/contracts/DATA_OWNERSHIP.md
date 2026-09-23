# Data Ownership

> **One writer per table / key space / bucket.** Other modules read through the owner's API, events, service/schemas functions, or a read model they build from events. They never `INSERT`/`UPDATE`/`DELETE` another module's tables and never write SQL joins across modules. Source: master §27–§34, §57.
>
> Resolves master §57 "Task/assignment → core/task domain": **Task, Assignment, TaskSession, and pre-checks belong to M01.**

## PostgreSQL (transactional)

| Table | Owner (writer) | Main readers | Notes |
|-------|----------------|--------------|-------|
| `users`, `user_site_scopes` | M00 | core auth | roles/permissions live in code (`backend/app/core/security/rbac.py`; modules add permissions via `wiring.py`) |
| `operators` | M00 | M01, M06, M08 via API/events | master data |
| `machines` | M00 | M01, M04, M05 | master data; `engine_hours` synced from telemetry by M00 on `machine.telemetry.received`, or kept in twin only (decide in M01-WP3) |
| `sites`, `zones` | M00 | M04, M05, M01 | zone geometry and type |
| `audit_log` | M00 | — | written through the core audit helper by any module; the helper is M00's |
| `tasks` | M01 | M02, M03, M05, M06, M09 | |
| `assignments` | M01 | M02, M03, M06, M08 | |
| `task_sessions` | M01 | M05, M06, M08, M11 | actual start/end, pauses |
| `precheck_templates`, `precheck_results` | M01 | M04, M11 | |
| `twin_snapshots` | M01 | M09, M11 | periodic + on significant change |
| `safety_events`, `incidents` | M04 | M01, M06, M08, M11 | |
| `safety_rules`, `zone_rules` | M04 | edge | pushed to the edge |
| `devices`, `device_state` | M04 | M03 | |
| `interaction_nodes`, `interaction_edges`, `interaction_stats` | M05 | M09, M06 | |
| `bottlenecks`, `site_recommendations` | M05 | M03, M07 | |
| `operator_behavior_profiles` | M06 | M08, M11 | multi-baseline |
| `task_predictions`, `prediction_contributions` | M06 | M01, M07, M09, M11 | |
| `risk_assessments`, `anomaly_detections` | M06 | M07, M08 | |
| `skill_profiles` | M06 | M08 | the skill **estimation** interface is M06; M08 consumes |
| `deviation_explanations` | M06 | M07, M02, M03 | WHY? engine output |
| `model_registry` | M06 | M10, M11 | M10 writes federated versions **through** M06's registry API |
| `copilot_conversations`, `copilot_messages`, `tool_call_logs` | M07 | M11 | |
| `proactive_notifications` | M07 | M11 | notification policy state |
| `knowledge_documents`, `knowledge_chunks` (pgvector) | M07 | — | RAG |
| `training_modules`, `training_triggers` | M08 | M02, M03 | |
| `operator_training` (sessions), `assessments`, `assessment_results` | M08 | M06, M11 | |
| `training_impact` | M08 | M11, M03 | observed associations only |
| `scenarios`, `scenario_runs`, `scenario_results` | M09 | M03, M07 | |
| `federated_rounds`, `model_update_meta` | M10 | M11 | metadata only, never raw site data |
| `kpi_snapshots`, `experiments`, `eval_results` | M11 | M03 | |

## TimescaleDB (hypertables)

| Hypertable | Owner | Partition |
|------------|-------|-----------|
| `machine_telemetry` | M01 | time, machine_id |
| `machine_state_changes` | M01 | time |
| `operator_events` | M01 | time, operator_id |
| `environment_events` | M01 | time, site_id |
| `hazard_events` | M04 | time, site_id |

## Redis key spaces

| Prefix | Owner | Content |
|--------|-------|---------|
| `twin:operator:{id}`, `twin:machine:{id}`, `task:active:{id}` | M01 | current state (rebuildable) |
| `risk:live:{operator_id}` | M04 (rule state) | live safety status |
| `pred:cache:*` | M06 | inference cache |
| `copilot:ctx:{conversation_id}` | M07 | short-term conversation context |
| `ws:*`, `bus:*`, `ratelimit:*`, `session:*` | M00 | infra |

## Object storage prefixes

| Prefix | Owner |
|--------|-------|
| `models/` | M06 (M10 writes through the M06 registry) |
| `datasets/`, `features/` | M06 |
| `training-media/` | M08 |
| `backend/app/copilot/knowledge/` | M07 |
| `reports/`, `experiments/` | M11 |
| `sim/` | M01 |

## Edge local store (SQLite on the gateway)

Owned entirely by M04: event buffer, local rule cache, device state, proximity graph.

## Rules of thumb

- Need data you don't own? Consume the owner's event and build **your own read model** in your own table (e.g., M05 keeps `interaction_nodes` built from M01/M04 events).
- Need the owner to store a new field? Open a contract PR on their schema. Don't add a column to their table.
- Migrations only ever touch your module's tables, on your module's Alembic branch.
