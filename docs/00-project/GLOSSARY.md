# Glossary

## Product terms

| Term | Meaning |
|------|---------|
| **HMOT / Operational Twin / Twin** | A continuously updated digital representation of the operator + machine + task + environment system. It has a **State layer** (what is happening) and an **Intelligence layer** (what it means). Owned by M01. |
| **Context fusion** | Combining telemetry, operator events, task state, environment, and site/device events into one normalized twin state. |
| **WHY? Engine** | The explainability layer that attributes predictions, alerts, and deviations to contributing factors and root-cause categories. Owned by M06, with site evidence from M05. |
| **Root-cause categories** | OPERATOR, MACHINE, TASK, SITE, ENVIRONMENT, INTERACTION, UNKNOWN. |
| **Site Awareness Mesh / Hazard Mesh** | The edge-first proximity and zone awareness layer (BLE/UWB tags, gateways). The safety branch is M04; the operational branch is M05. |
| **Machine Interaction Graph** | Nodes (machines, people, zones, resources) and edges (dependency, proximity, material flow) with statistics such as wait, queue, and utilization. M05. |
| **Safe Productivity Envelope** | The feasible region of high productivity without unacceptable risk. Recommendations must fall inside it. |
| **Personal Operating Fingerprint** | An operator's multi-baseline behavior profile (personal, machine, site, fleet). M06. |
| **Counterfactual / What-if** | Simulating a modified twin (e.g., move Dumper D2) and comparing predicted outcomes plus safety constraints. M09. |
| **Grounded Copilot** | A Copilot where every factual answer comes from a tool call. M07. |
| **Shift Huddle / Briefing** | The pre-shift summary: machine, tasks, conditions, watch-outs, ETA, focus. |
| **Pre-op check** | The operator's pre-operation machine checklist, part of the task session lifecycle (M01). |
| **Training impact** | Observed before/after behavior change around an intervention. M08 + M11. |
| **Federated fleet intelligence** | Sites train locally and share model updates, not raw logs. M10. |

## Workflow terms

| Term | Meaning |
|------|---------|
| **Module (MXX)** | A unit of ownership with its own paths, contracts, tables, and status. M00–M11. |
| **Work package (WP)** | A shippable slice of a module, sized at about 1–3 days, e.g. `M04-WP2`. Listed in the module's SPEC and tracked in its STATUS. |
| **Owner** | The person responsible for a module. Only the owner and their agents edit its paths. |
| **Contract** | A machine-readable interface in `contracts/`: OpenAPI, event schema, tool schema, or ML IO schema. |
| **Mock** | A contract-valid fake implementation of a module's outputs, used by consumers until the real one is ready. |
| **Slot** | A pre-registered route/feature folder inside an app owned by another module, delegated to a feature owner. |
| **Auto-discovery** | Core loads every `backend/modules/*/module.py` automatically, so nobody edits a central router. |
| **Gate (G0–G4)** | A team-wide integration checkpoint at the end of a phase. |
| **Contract freeze (v1)** | At G1 the M00/M01 contracts become v1. After that, breaking changes require the full change process. |
| **STATUS.md** | A module's live status and append-only update log. Updated on every push. |
| **Sync log** | A person's own log of pulls and pushes (`docs/05-status/sync-log/<handle>.md`). |
| **ADR** | Architecture Decision Record (`docs/01-architecture/adr/`). |

## Canonical demo identifiers

Use these IDs in fixtures, mocks, and tests so every module's demo data lines up.

| Entity | IDs |
|--------|-----|
| Site | `SITE_A` |
| Operators | `OP1001` (primary demo operator), `OP1002`, `OP1003` |
| Supervisor | `SUP001` |
| Machines | `EXC001` / E1 (excavator), `EXC002` / E2, `DMP001` / D1 (dumper), `DMP002` / D2 |
| Workers (wearables) | `WRK001` / W1, `WRK002` |
| Zones | `ZONE_A` (excavation), `ZONE_B` (soft ground), `ZONE_DISPOSAL`, `ZONE_RESTRICTED_1` |
| Tasks | `TASK001` (Excavation — Zone A, 50 cycles, 08:00–10:30), `TASK002`, `TASK003` |
| Simulator scenarios | `S1` normal, `S2` seatbelt, `S3` worker hazard, `S4` site bottleneck, `S5` operator drift, `S6` environmental delay |
