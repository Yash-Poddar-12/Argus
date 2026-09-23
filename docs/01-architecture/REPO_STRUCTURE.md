# Repository Structure & Path Ownership

> Every path below has **one owning module**. Only that module's owner (or their agent) edits it.
> Module → person mapping: `docs/00-project/TEAM_AND_OWNERSHIP.md`. Enforcement: `.github/CODEOWNERS`.
>
> The tree is the **target layout**. M00-WP1 creates the skeleton (empty folders + `.gitkeep`) in Phase 0 so later work only fills in owned folders.

## 1. Target tree

```text
/
├── AGENTS.md                      M00  canonical agent rules (all IDEs)
├── CLAUDE.md / GEMINI.md          M00  thin pointers to AGENTS.md
├── README.md / CONTRIBUTING.md    M00
├── MASTER_PROJECT_CONTEXT_AND_EXECUTION_PLAN.md   TEAM (product intent; change via PR + §115 log)
│
├── contracts/                     machine-readable source of truth
│   ├── schemas/common/            M00  ids, envelope, error, pagination, geo, time
│   ├── schemas/twin/              M01  OperationalTwin, TwinSnapshot, context types
│   ├── openapi/
│   │   ├── m00-platform.yaml      M00  auth, users, operators, machines, sites
│   │   ├── m01-twin.yaml          M01  tasks, assignments, sessions, prechecks, twin
│   │   ├── m04-safety.yaml        M04
│   │   ├── m05-site-intel.yaml    M05
│   │   ├── m06-predictions.yaml   M06
│   │   ├── m07-copilot.yaml       M07
│   │   ├── m08-training.yaml      M08
│   │   ├── m09-scenarios.yaml     M09
│   │   └── m11-analytics.yaml     M11
│   ├── events/mXX/            owner = MXX (the producer): <event_type>.v<N>.json, ws/, examples/
│   ├── tools/<tool_name>.json     owner = module owning the data behind the tool (see TOOL_AND_ML_CONTRACTS.md)
│   ├── ml/                        M06  inference input/output schemas
│   └── ml/federated/              M10
│
├── backend/
│   ├── core/                      M00  config, db session, event bus, auth deps, rbac, logging,
│   │                                   errors, health, ws gateway, module registry (auto-discovery)
│   ├── modules/
│   │   ├── m00_platform/          M00  users, operators, machines, sites (master data)
│   │   ├── m01_twin/              M01  tasks/, twin/, api/, environment/
│   │   ├── m04_safety/            M04  cloud-side safety/hazard event ingestion + APIs
│   │   ├── m05_site_intel/        M05
│   │   ├── m06_ml/                M06  inference adapters, feature assembly, WHY? engine
│   │   ├── m07_copilot/           M07
│   │   ├── m08_training/          M08
│   │   ├── m09_scenarios/         M09
│   │   └── m11_analytics/         M11
│   ├── migrations/<module>/       same owner as the module (one Alembic branch each)
│   └── tests/<module>/            same owner as the module
│
├── frontend/
│   ├── packages/ui/               M00  design system (tokens, primitives). Changes: PR reviewed by M00 + M02/M03
│   ├── packages/api-client/       GENERATED from contracts/openapi — never hand-edit
│   ├── apps/operator/             M02  shell, layout, nav, My Day / Machine / Tasks / Safety / Performance
│   │   └── src/
│   │       ├── app/copilot/ + features/copilot/        M07 slot (delegable, default M02 with M07 mocks)
│   │       └── app/training/ + features/training/      M08 slot (delegable, default M02)
│   └── apps/admin/                M03  shell, CRUD, assignments, tasks, site map, config
│       └── src/
│           ├── app/site-intel/ + features/site-intel/  M05 slot
│           ├── app/scenarios/ + features/scenarios/    M09 slot
│           ├── app/training-admin/ + features/training-admin/  M08 slot
│           └── app/analytics/ + features/analytics/    M11 slot
│
├── edge/                          M04  gateway, device adapters (BLE/UWB/MQTT sim), proximity engine,
│                                       zone logic, local rules, local buffer + replay
├── simulator/
│   ├── core/                      M01  seeded clock, entities, telemetry generator, event emitter, CLI
│   └── scenarios/
│       ├── core/                  M01  S1 normal, S6 environmental delay, task lifecycle
│       ├── hazard/                M04  S2 seatbelt, S3 worker hazard, machine proximity
│       ├── site/                  M05  S4 site bottleneck, dumper shortage, queueing
│       └── behavior/              M06  S5 operator drift, high idle, machine slowdown
├── ml/                            M06  datasets (gitignored), features, training pipelines, notebooks, model cards
│   └── federated/                 M10
├── knowledge/                     M07  RAG corpus (manuals, procedures, FAQs) + ingestion config
├── content/training/              M08  training modules, assessments
├── analytics/                     M11  eval harness, experiment configs, reports
│
├── infra/
│   ├── compose/base.yml           M00
│   ├── compose/<module>.yml       owner of that module
│   └── env/<module>.env.example   owner of that module
├── scripts/                       M00  (scripts/status.py etc.)  — module-specific scripts go in the module folder
├── .github/                       M00  workflows, PR/issue templates, CODEOWNERS
│
└── docs/
    ├── INDEX.md                   M00
    ├── 00-project/                TEAM (principles, glossary, team & ownership)
    ├── 01-architecture/           M00 + TEAM (architecture, workflow, ADRs)
    ├── 02-contracts/              catalogs: each row edited only by the row's owning module
    ├── 03-modules/MXX-*/          owner of MXX (SPEC.md, STATUS.md)
    ├── 04-workflow/               M00 + TEAM (sync protocol, gates, DoD, agent playbook)
    └── 05-status/
        ├── STATUS_BOARD.md        M00 (static index; values computed by scripts/status.py)
        └── sync-log/<handle>.md   that person only
```

## 2. Owned-path summary per module

| Module | Owns (write) | Delegated slots it may fill |
|--------|--------------|-----------------------------|
| M00 | `backend/core/`, `backend/modules/m00_platform/`, `frontend/packages/ui/`, `infra/compose/base.yml`, `scripts/`, `.github/`, `contracts/schemas/common/`, `contracts/openapi/m00-platform.yaml`, `contracts/events/m00/`, root docs | — |
| M01 | `backend/modules/m01_twin/`, `simulator/core/`, `simulator/scenarios/core/`, `contracts/schemas/twin/`, `contracts/openapi/m01-twin.yaml`, `contracts/events/m01/` | — |
| M02 | `frontend/apps/operator/` (except slots) | — |
| M03 | `frontend/apps/admin/` (except slots) | — |
| M04 | `edge/`, `backend/modules/m04_safety/`, `simulator/scenarios/hazard/`, `contracts/openapi/m04-safety.yaml`, `contracts/events/m04/` | — |
| M05 | `backend/modules/m05_site_intel/`, `simulator/scenarios/site/`, `contracts/openapi/m05-site-intel.yaml`, `contracts/events/m05/` | admin `site-intel` |
| M06 | `ml/` (except `federated/`), `backend/modules/m06_ml/`, `simulator/scenarios/behavior/`, `contracts/ml/`, `contracts/openapi/m06-predictions.yaml`, `contracts/events/m06/` | — |
| M07 | `backend/modules/m07_copilot/`, `knowledge/`, `contracts/openapi/m07-copilot.yaml`, `contracts/events/m07/`, `contracts/tools/_registry.json` | operator `copilot` |
| M08 | `backend/modules/m08_training/`, `content/training/`, `contracts/openapi/m08-training.yaml`, `contracts/events/m08/` | operator `training`, admin `training-admin` |
| M09 | `backend/modules/m09_scenarios/`, `contracts/openapi/m09-scenarios.yaml`, `contracts/events/m09/` | admin `scenarios` |
| M10 | `ml/federated/`, `contracts/ml/federated/`, `contracts/events/m10/` | — |
| M11 | `analytics/`, `backend/modules/m11_analytics/`, `contracts/openapi/m11-analytics.yaml` | admin `analytics` |

All modules also own: `backend/migrations/<module>/`, `backend/tests/<module>/`, `infra/compose/<module>.yml`, `infra/env/<module>.env.example`, `docs/03-modules/<module>/`.

## 3. Delegated slots

A **slot** is a folder inside another module's app that is pre-registered (route + nav entry + placeholder) by the app owner and then handed to a feature owner.

- The **app owner** (M02/M03) owns layout, navigation, theming, auth guard, and the slot's existence.
- The **slot owner** owns everything inside `app/<route>/` and `features/<feature>/` for that slot.
- A slot is **delegable**: by default the app owner builds it against the feature module's mocks; if the feature owner has capacity, they take it over. Record who holds each slot in `TEAM_AND_OWNERSHIP.md`.

## 4. Things nobody hand-edits

- `frontend/packages/api-client/**` (generated)
- lockfiles during conflict resolution (regenerate instead)
- `docs/05-status/STATUS_BOARD.md` values (the table is an index; live values come from each `STATUS.md`)
- anything under another module's owned path
