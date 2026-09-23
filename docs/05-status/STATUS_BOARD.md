# Status Board

> **This page is a static index. Don't type status values here** (shared tables cause merge conflicts).
> Live board: run `python scripts/status.py board` (terminal) or `python scripts/status.py board --markdown` (paste into chat or a PR).
> Protocol: [`docs/04-workflow/SYNC_PROTOCOL.md`](../04-workflow/SYNC_PROTOCOL.md)

## Modules

| Phase | Module | Status file | Spec |
|-------|--------|-------------|------|
| 0 | M00 Foundation | [STATUS](../03-modules/M00-foundation/STATUS.md) | [SPEC](../03-modules/M00-foundation/SPEC.md) |
| 1 | M01 Operational Twin | [STATUS](../03-modules/M01-operational-twin/STATUS.md) | [SPEC](../03-modules/M01-operational-twin/SPEC.md) |
| 2 | M02 Operator Experience | [STATUS](../03-modules/M02-operator-experience/STATUS.md) | [SPEC](../03-modules/M02-operator-experience/SPEC.md) |
| 2 | M03 Supervisor/Admin Console | [STATUS](../03-modules/M03-admin-console/STATUS.md) | [SPEC](../03-modules/M03-admin-console/SPEC.md) |
| 2 | M04 IoT Hazard Mesh | [STATUS](../03-modules/M04-iot-hazard-mesh/STATUS.md) | [SPEC](../03-modules/M04-iot-hazard-mesh/SPEC.md) |
| 2 | M06 Operator Intelligence / ML | [STATUS](../03-modules/M06-operator-ml/STATUS.md) | [SPEC](../03-modules/M06-operator-ml/SPEC.md) |
| 3 | M05 Site Operational Intelligence | [STATUS](../03-modules/M05-site-intelligence/STATUS.md) | [SPEC](../03-modules/M05-site-intelligence/SPEC.md) |
| 3 | M07 Copilot | [STATUS](../03-modules/M07-copilot/STATUS.md) | [SPEC](../03-modules/M07-copilot/SPEC.md) |
| 3 | M08 Training | [STATUS](../03-modules/M08-training/STATUS.md) | [SPEC](../03-modules/M08-training/SPEC.md) |
| 4 | M09 Counterfactual Engine | [STATUS](../03-modules/M09-counterfactual/STATUS.md) | [SPEC](../03-modules/M09-counterfactual/SPEC.md) |
| 4 | M10 Federated Intelligence | [STATUS](../03-modules/M10-federated/STATUS.md) | [SPEC](../03-modules/M10-federated/SPEC.md) |
| 4 | M11 Analytics & Evaluation | [STATUS](../03-modules/M11-analytics-eval/STATUS.md) | [SPEC](../03-modules/M11-analytics-eval/SPEC.md) |

## Gates

| Gate | Criteria | Tag |
|------|----------|-----|
| G0 Foundation ready | [checklist](../04-workflow/INTEGRATION_CHECKPOINTS.md#g0--foundation-ready-end-of-phase-0) | `g0` |
| G1 Vertical slice + contract freeze | [checklist](../04-workflow/INTEGRATION_CHECKPOINTS.md#g1--operational-core--contract-freeze-end-of-phase-1) | `g1` |
| G2 Demo scenes 1–5 | [checklist](../04-workflow/INTEGRATION_CHECKPOINTS.md#g2--parallel-product-build-end-of-phase-2--demo-scenes-15) | `g2` |
| G3 Demo scenes 6–10 | [checklist](../04-workflow/INTEGRATION_CHECKPOINTS.md#g3--intelligence-end-of-phase-3--demo-scenes-610) | `g3` |
| G4 Scenes 11–12 + evaluation | [checklist](../04-workflow/INTEGRATION_CHECKPOINTS.md#g4--advanced-end-of-phase-4--demo-scenes-1112--evaluation) | `g4` |

Gate results are recorded as `NOTE` entries in the integration lead's sync log and as git tags. Nobody edits this table.

## Personal sync logs

One file per person in [`sync-log/`](sync-log/). The first `python scripts/status.py log …` you run creates yours from [`_TEMPLATE.md`](sync-log/_TEMPLATE.md).
