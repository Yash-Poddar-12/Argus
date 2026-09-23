# Event Catalog

> Every async event: one **producer** (single writer), any number of consumers. The envelope is in `CONTRACTS_GUIDE.md` §3. Payload schemas are in `contracts/events/<producer mXX>/<event_type>.v<N>.json`. The event-type prefix is the business domain (e.g. `operator.`), **not** the owner. Two modules can produce `operator.*` events; the folder and this table show who owns each one. **Edit only rows your module produces.** Consumers add themselves to the Consumers column through a PR the producer reviews.
>
> Status: `PLANNED` → `MOCKED` (example + mock emitter exist) → `LIVE` → `DEPRECATED`

## Streams

| Stream (topic) | Producer module | Retention intent |
|----------------|-----------------|------------------|
| `platform.events` | M00 | long |
| `task.events`, `assignment.events`, `session.events` | M01 | long |
| `machine.telemetry` | M01 (ingestion) | short in bus; persisted to Timescale |
| `machine.state`, `twin.events`, `environment.events` | M01 | medium |
| `safety.events`, `hazard.events`, `device.events` | M04 | long (safety audit) |
| `site_intel.events` | M05 | medium |
| `prediction.events`, `operator.events` | M06 | medium |
| `copilot.events` | M07 | medium |
| `training.events` | M08 | long |
| `scenario.events` | M09 | medium |
| `federated.events` | M10 | long |

Stream placement: M01's `operator.task.assigned` goes on `assignment.events`, `session.*` on `session.events`, `twin.updated` on `twin.events`. M06's `operator.*` events go on `operator.events`.

## M00 — Platform

| Event type | Payload (key fields) | Consumers | Status |
|------------|----------------------|-----------|--------|
| `platform.operator.created` / `.updated` | operator_id, site_id, experience_level, certification_status, status (+ `changed_fields` on updates) | M01, M06, M08 | LIVE |
| `platform.machine.created` / `.updated` | machine_id, machine_type, model, site_id, status, engine_hours | M01, M04, M05 | LIVE |
| `platform.site.created` / `.updated` | site_id, configuration | M04, M05 | LIVE |
| `platform.zone.updated` | site_id, zone_id, zone_type, geometry | M04, M05, M01 | LIVE |

## M01 — Operational Twin & core domain

| Event type | Payload (key fields) | Consumers | Status |
|------------|----------------------|-----------|--------|
| `task.created` / `task.updated` | task_id, site_id, task_type, zone_id, priority, target, planned_start, planned_end, status | M06, M05, M09 | LIVE |
| `operator.task.assigned` | assignment_id, task_id, operator_id, machine_id, assigned_by | M06, M08, M07 | LIVE |
| `assignment.updated` | assignment_id, changes, status | M06, M07 | LIVE |
| `session.machine.confirmed` | operator_id, machine_id | M08 (new machine → familiarization trigger) | LIVE |
| `session.precheck.completed` | session_id, machine_id, passed, failed_items[] | M04, M11 | LIVE |
| `task.started` / `.paused` / `.resumed` / `.completed` | session_id, task_id, operator_id, machine_id, at, pause_duration | M05, M06, M08, M11 | LIVE |
| `machine.telemetry.received` | machine_id, timestamp, engine_hours, fuel, fuel_rate, load_cycles, idle_seconds, speed, rpm, temperature, gps, operating_mode, seatbelt | M04 (optional), M05, M06 | LIVE |
| `machine.state.changed` | machine_id, from, to, at | M05, M06 | LIVE |
| `environment.conditions.updated` | site_id, zone_id?, weather, temperature, rain, visibility, soil_condition | M06, M07 | LIVE |
| `twin.updated` | operator_id, machine_id, task_id, changed_fields[], snapshot_ref | M05, M07, M09 | LIVE |

## M04 — IoT Hazard Mesh / Safety

| Event type | Payload (key fields) | Consumers | Status |
|------------|----------------------|-----------|--------|
| `safety.event.raised` | safety_event_id, event_type (SEATBELT_UNFASTENED, PROXIMITY_CRITICAL, RESTRICTED_ZONE_ENTRY, EMERGENCY…), severity, machine_id, operator_id, sensor_value, threshold, rule_id, risk_score?, decision_source (RULE/EDGE_ML/CLOUD_ML/HYBRID) | M01, M06, M08, M07, M11 | PLANNED |
| `safety.event.acknowledged` / `.resolved` | safety_event_id, by, at | M08, M11 | PLANNED |
| `hazard.proximity.detected` | subject_id, object_id, object_type (PERSON/MACHINE), distance_m, closing_speed_mps, severity | M01, M05, M06 | PLANNED |
| `hazard.zone.entered` / `.exited` | entity_id, zone_id, zone_type | M01, M05 | PLANNED |
| `device.state.changed` | device_id, device_type, attached_to, battery, online | M03 (via API), M11 | PLANNED |

## M05 — Site Operational Intelligence

| Event type | Payload (key fields) | Consumers | Status |
|------------|----------------------|-----------|--------|
| `site_intel.interaction_stats.updated` | site_id, edge_id, source_node, target_node, avg_wait, queue_time, trips_per_hour, utilization | M06, M09 | PLANNED |
| `site_intel.bottleneck.detected` | site_id, bottleneck_node, impact_min_per_hour, affected_nodes[], evidence | M06 (WHY: site-driven), M07, M03 | PLANNED |
| `site_intel.recommendation.created` | recommendation_id, description, expected_gain, safety_check_passed | M03, M07 | PLANNED |

## M06 — Operator Intelligence / ML

| Event type | Payload (key fields) | Consumers | Status |
|------------|----------------------|-----------|--------|
| `prediction.task_time.updated` | task_id, operator_id, machine_id, p50, p80, p90, confidence, confidence_level, contributors[], model_version | M01, M07, M09 | PLANNED |
| `prediction.risk.updated` | operator_id, machine_id, risk_probability, risk_level, factors[], model_version | M01, M04 (context only), M07 | PLANNED |
| `operator.anomaly.detected` | operator_id, anomaly_score, severity, contributing_signals[], window | M08, M07 | PLANNED |
| `operator.profile.updated` | operator_id, window, baselines (personal/machine/site/fleet) | M08, M11 | PLANNED |
| `operator.skill_profile.updated` | operator_id, skills[{skill, mastery, confidence, evidence}] | M08 | PLANNED |
| `operator.deviation.explained` | subject, deviation, attribution (OPERATOR/MACHINE/TASK/SITE/ENVIRONMENT/INTERACTION/UNKNOWN), evidence[], confidence | M07, M08, M02 (via WS through M01) | PLANNED |

## M07 — Copilot

| Event type | Payload (key fields) | Consumers | Status |
|------------|----------------------|-----------|--------|
| `copilot.proactive_message.created` | operator_id, priority (CRITICAL/HIGH/MEDIUM/INFO), message_key, language, text, source_event_id | M11 | PLANNED |
| `copilot.query.answered` | conversation_id, operator_id, intent, tools_called[], latency_ms, language | M11 | PLANNED |

## M08 — Training

| Event type | Payload (key fields) | Consumers | Status |
|------------|----------------------|-----------|--------|
| `training.recommended` | operator_id, training_id, reason, trigger, priority, expected_duration | M07, M11 | PLANNED |
| `training.started` / `training.completed` | session_id, operator_id, training_id, score? | M06, M11 | PLANNED |
| `training.impact.measured` | operator_id, training_id, metrics[{name, before, after, delta}], window, method: OBSERVED_ASSOCIATION | M11, M07 | PLANNED |

## M09 — Counterfactual

| Event type | Payload (key fields) | Consumers | Status |
|------------|----------------------|-----------|--------|
| `scenario.run.completed` | scenario_id, run_id, baseline_metrics, scenario_metrics, deltas, safety_constraints_ok, uncertainty | M03 (WS), M07, M11 | PLANNED |

## M10 — Federated

| Event type | Payload (key fields) | Consumers | Status |
|------------|----------------------|-----------|--------|
| `federated.model.published` | model_name, version, round, participating_sites, metrics | M06, M11 | PLANNED |

## Idempotency and ordering

- All consumers deduplicate on `event_id`, keeping a processed-ID set per consumer group with a TTL.
- Ordering is guaranteed only per stream **partition key**: `machine_id` for telemetry and hazard, `operator_id` for operator/twin, `site_id` for site_intel. Don't assume cross-stream ordering. Use `timestamp` and `correlation_id`.
- Replay from the edge can deliver late events; consumers must tolerate out-of-order timestamps.
