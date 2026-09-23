# M09 — Counterfactual Engine ("What if?")

| Field | Value |
|-------|-------|
| Phase | 4 (scenario DSL and comparison UI can start on mocks after G2) |
| Type | Backend module (+ admin scenarios slot) |
| Depends on (contracts) | M01 (twin, fusion via `public.py`), M05 (graph), M06 (predictions), M04 (safety rules) |
| Consumed by | M03, M07 |
| Gate | G4 (scene 11 "What if I move Dumper D2?") |

## Objective

Let operators and supervisors explore **what would happen if** something changed, without controlling any machine. Build a modified twin, run predictions and site simulation, evaluate safety constraints, and return a comparison with uncertainty, phrased as decision support.

## Scope

- Scenario spec (DSL/JSON) for supported modifications:
  - Supervisor: move resource (D2 from E1 → E2), add/remove resource, change deadline, zone unavailable
  - Operator: reduce idle by X%, weather persists, next task starts late
- Twin cloning + modification (reuses M01 pure fusion logic through `public.py`)
- Evaluation: M06 predictions on the modified context + a lightweight site simulation over the M05 graph (e.g., discrete-event queue model)
- **Safety constraint evaluation** (M04 rules/thresholds + M06 risk evidence). A scenario that violates constraints is shown as not viable
- Comparison: baseline vs scenario metrics, deltas, uncertainty range, and the key assumptions
- Phrasing: "The simulation indicates…" (P7). Never an instruction
- Tool: `run_what_if_scenario`

## Out of scope

Executing any change, autonomous dispatch, optimization search over all possible scenarios (future).

## Owned paths

`backend/modules/m09_scenarios/`, `backend/migrations/m09_scenarios/`, `backend/tests/m09_scenarios/`, `contracts/openapi/m09-scenarios.yaml`, `contracts/events/m09/`, `contracts/tools/run_what_if_scenario.json`; slot `frontend/apps/admin/src/{app,features}/scenarios/` if held.

## Work packages

| WP | Title | Est. |
|----|-------|------|
| M09-WP0 | Contracts + `public.py` + mocks (the D2 reallocation example from master §11.5) | 1 d |
| M09-WP1 | Scenario spec + validation + persistence | 1–2 d |
| M09-WP2 | Twin/graph cloning + modification | 2 d |
| M09-WP3 | Evaluation: M06 predictions + site queue simulation | 2–3 d |
| M09-WP4 | Safety constraint evaluation | 1–2 d |
| M09-WP5 | Comparison, uncertainty, assumptions, phrasing | 1 d |
| M09-WP6 | `run_what_if_scenario` tool for M07 | 0.5 d |
| M09-SLOT | Admin scenarios slot UI (if held) | 2 d |

## Acceptance criteria

- [ ] "Move D2 from E1 → E2" on S4 returns per-machine throughput deltas, site throughput change, safety constraints status, and an uncertainty range, reproducibly for a seed
- [ ] A scenario that breaks a safety constraint is flagged as not viable, with the constraint named
- [ ] Output never uses imperative phrasing; always lists assumptions
- [ ] Runs in < 10 s for the demo site

## Testing

Unit tests on modifications, deterministic simulation tests, contract tests, golden-file tests for the flagship scenario.

## Future extensions

Multi-step scenarios, optimization search with safety constraints, operator-facing voice what-ifs, calibration against observed outcomes (with M11).

## Known constraints

Accuracy is bounded by M05/M06 quality on simulated data. State the uncertainty clearly.
