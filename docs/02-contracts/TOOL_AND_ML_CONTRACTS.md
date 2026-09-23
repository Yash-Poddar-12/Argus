# Copilot Tool & ML Contracts

## Part A — Copilot tool registry

**Principle (P5):** every operational fact in a Copilot answer comes from a tool result. The LLM explains, translates, and summarizes, and never invents numbers or states.

**Ownership split:**
- **Tool schema + implementation** belong to the module that owns the underlying data (`contracts/tools/<tool_name>.json`, implemented in that module's `public.py`).
- **Registry, orchestration, and permissioning** belong to M07 (`contracts/tools/_registry.json` lists enabled tools and versions).
- Until the owning module implements a tool, M07 uses the mock returning `contracts/tools/examples/<tool_name>.example.json`.

| Tool | Owner | Backed by | Status |
|------|-------|-----------|--------|
| `get_current_machine_state(machine_id)` | M01 | twin / Redis | PLANNED |
| `get_current_task(operator_id)` | M01 | tasks + session | PLANNED |
| `get_task_progress(task_id)` | M01 | session + telemetry | PLANNED |
| `get_machine_health(machine_id)` | M01 | telemetry-derived state | PLANNED |
| `get_weather(site_id)` | M01 | environment adapter | PLANNED |
| `get_site_conditions(site_id, zone_id?)` | M01 | environment + zone state | PLANNED |
| `get_safety_index(operator_id)` | M04 | live rule state + M06 risk evidence | PLANNED |
| `get_recent_alerts(operator_id, since?)` | M04 | safety_events | PLANNED |
| `get_alert_details(safety_event_id)` | M04 | safety_events (why: rule, values, thresholds) | PLANNED |
| `get_nearby_hazards(operator_id)` | M04 | proximity graph | PLANNED |
| `get_nearby_machines(machine_id)` | M04 | proximity graph | PLANNED |
| `get_site_bottlenecks(site_id)` | M05 | interaction graph | PLANNED |
| `predict_task_duration(task_id)` | M06 | task-time model | PLANNED |
| `get_operator_performance(operator_id, window?)` | M06 | behavior profile | PLANNED |
| `explain_operational_deviation(subject, metric, window)` | M06 | WHY? engine | PLANNED |
| `get_operator_training(operator_id)` | M08 | training history + recommendations | PLANNED |
| `run_what_if_scenario(scenario_spec)` | M09 | counterfactual engine | PLANNED |
| `search_knowledge(query, language)` | M07 | RAG over approved docs | PLANNED |

### Tool schema shape (`contracts/tools/<tool_name>.json`)

```json
{
  "name": "predict_task_duration",
  "version": "1.0",
  "owner": "M06",
  "description": "Predict remaining duration for a task given current operator/machine/context.",
  "input_schema":  { "type": "object", "properties": { "task_id": { "type": "string" } }, "required": ["task_id"] },
  "output_schema": { "$ref": "../ml/task-prediction.v1.json" },
  "permissions": ["OPERATOR:self", "SUPERVISOR_ADMIN:site"],
  "safety_critical": false,
  "latency_budget_ms": 800
}
```

`safety_critical: true` tools (e.g., `get_safety_index`) must return deterministic rule state. The Copilot may **relay** these results but never **override** them.

## Part B — ML inference contracts (owner M06)

All ML sits behind these interfaces (master §26). Frontend, Copilot, and other modules never depend on model internals. Schemas: `contracts/ml/*.v1.json`. Access: `backend.modules.m06_ml.public`.

```python
predict_task_duration(ctx: TaskContext) -> TaskPrediction
calculate_operational_risk(ctx: RiskContext) -> RiskPrediction
detect_operator_anomaly(ctx: BehaviorContext) -> AnomalyPrediction
estimate_skill_profile(operator_id: str) -> SkillProfile
explain_operational_deviation(req: DeviationRequest) -> DeviationExplanation
```

### Common output fields (every prediction)

| Field | Type | Notes |
|-------|------|-------|
| `model_name`, `model_version` | string | always present |
| `confidence` | 0–1 | |
| `confidence_level` | HIGH / MODERATE / LOW | |
| `confidence_reason` | string? | e.g. "limited history for this machine/task" |
| `contributors` | `[{feature, value, contribution, unit, direction}]` | SHAP or equivalent; `contribution` in output units (e.g., minutes) |
| `data_freshness_s` | number | age of the newest input |
| `fallback_level` | PERSONAL / MACHINE / SITE / TASK / FLEET | cold-start level used |

### Specific outputs

| Output | Extra fields |
|--------|--------------|
| `TaskPrediction` | `task_id`, `p50_duration_min`, `p80_duration_min`, `p90_duration_min`, `predicted_completion_at` |
| `RiskPrediction` | `risk_probability`, `risk_level` (LOW/MEDIUM/HIGH/CRITICAL), `factors[]`. **Evidence only; never triggers an alert by itself** |
| `AnomalyPrediction` | `anomaly_score`, `severity`, `contributing_signals[]`, `baseline_used` |
| `SkillProfile` | `skills[{skill, mastery_probability, confidence, evidence[], last_observed, trend}]` |
| `DeviationExplanation` | `observed`, `expected`, `attribution[{category, share, evidence[]}]` with categories OPERATOR/MACHINE/TASK/SITE/ENVIRONMENT/INTERACTION/UNKNOWN, `conclusion_text_key` |

### Canonical mock (used by M01, M02, M07, M09 until M06 is live)

```json
{
  "model_name": "task_time_lgbm", "model_version": "mock-0.1",
  "task_id": "TASK001",
  "p50_duration_min": 92, "p80_duration_min": 104, "p90_duration_min": 111,
  "confidence": 0.82, "confidence_level": "HIGH",
  "contributors": [
    { "feature": "wet_soil", "value": true, "contribution": 7, "unit": "min", "direction": "+" },
    { "feature": "idle_trend", "value": 0.31, "contribution": 4, "unit": "min", "direction": "+" },
    { "feature": "operator_baseline", "value": -0.05, "contribution": -2, "unit": "min", "direction": "-" }
  ],
  "data_freshness_s": 12, "fallback_level": "PERSONAL"
}
```
