# M08 — Training (closed-loop)

| Field | Value |
|-------|-------|
| Phase | 3 (catalogue content and trigger rules can start any time after G1) |
| Type | Backend module + content (+ operator training slot, admin training-admin slot) |
| Depends on (contracts) | M01, M04, M06 |
| Consumed by | M02, M03, M07, M11 |
| Gate | G3 (scenes 7–9: repeated behavior → recommendation → micro-learning → impact) |

## Objective

Detect skill and behavior gaps, recommend **targeted** training with a clear reason, deliver micro-learning and assessments, and **measure observed behavior change** afterwards. This is not a generic LMS (P9, non-goals).

## Scope

- Training catalogue (content in `content/training/`, metadata in DB): category, machine_type, skill_area, difficulty, duration, format, passing score
- Seed modules from master §62: Safe Excavator Operation, Cycle Optimization, Idle Management, Machine Familiarization, Site Safety Briefing, Working Around Personnel
- Sessions + assessments (start, progress, complete, score)
- **Trigger engine** (rules, master §33): `SEATBELT_VIOLATION >= 3 in 7d`, `CYCLE_TIME_DEVIATION >= 15% for N tasks`, `IDLE +30% vs personal baseline with no site explanation` (uses the M06 WHY? attribution so site-driven idle doesn't trigger training, per P3), `NEW_MACHINE_ASSIGNMENT`, `NEW_SITE`, `INCIDENT_OCCURRED`, `CERTIFICATION_EXPIRY`
- Recommendation engine: rules + M06 skill gaps → `{training_module, reason, priority, expected_duration, trigger}`
- **Impact measurement:** before/after windows around completion, per-metric deltas, labeled `OBSERVED_ASSOCIATION` (no causal claims)
- Tool: `get_operator_training`
- Slots: operator `training`, admin `training-admin` (delegable)

## Out of scope

Skill estimation models (M06 provides them), causal inference (M11 research), content authoring tools.

## Owned paths

`backend/modules/m08_training/`, `backend/migrations/m08_training/`, `backend/tests/m08_training/`, `content/training/`, `contracts/openapi/m08-training.yaml`, `contracts/events/m08/`, `contracts/tools/get_operator_training.json`; slots if held.

## Interfaces

APIs in `API_CATALOG.md` § M08; events `training.*`; tables `training_modules`, `training_triggers`, `operator_training`, `assessments`, `assessment_results`, `training_impact`. Consumes `safety.event.*`, `operator.anomaly.detected`, `operator.profile.updated`, `operator.skill_profile.updated`, `operator.deviation.explained`, `operator.task.assigned`, `session.machine.confirmed`, `task.completed`.

## Work packages

| WP | Title | Est. |
|----|-------|------|
| M08-WP0 | Contracts + `public.py` + mocks (recommendation with reason, impact example) | 1 d |
| M08-WP1 | Catalogue + content format + 6 seed micro-modules (en; hi/ta titles) | 2 d |
| M08-WP2 | Sessions + assessments | 1–2 d |
| M08-WP3 | Trigger engine (event-driven rules, windows) | 2 d |
| M08-WP4 | Recommendation engine + reasons + priority | 1–2 d |
| M08-WP5 | Impact measurement (before/after, observed association) | 2 d |
| M08-SLOT-T | Operator training slot UI (if held) | 2 d |
| M08-SLOT-TA | Admin training-admin slot UI (if held) | 1–2 d |

## Acceptance criteria

- [ ] S5 (operator drift, no external cause) → Idle Management recommended with a human-readable reason; S4/S6 (site/environment cause) → **no** idle training triggered
- [ ] Three seatbelt events in 7 days → Safe Excavator Operation recommended at HIGH priority
- [ ] New machine assignment → Machine Familiarization
- [ ] Impact report shows before/after deltas labeled as observed association, with window sizes
- [ ] Recommendations deduplicated (no re-recommending a module completed in the last N days unless the trigger recurs)

## Testing

Trigger rule unit tests with synthetic event streams; scenario tests with the simulator; contract tests.

## Future extensions

Learning-to-rank personalization, Bayesian mastery (with M06), spaced repetition, simulation-based training, instructor-led integration.

## Known constraints

Keep training separate from punitive HR workflows (privacy principles). Recommendations are framed as support.

## Integration checklist

- [ ] M02 training slot live
- [ ] M07 answers "What should I train on next?" via `get_operator_training`
- [ ] M11 receives impact events
