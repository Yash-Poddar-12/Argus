# Documentation index

Three sections. Each answers one kind of question.

## product/: what we're building and why

| File | Purpose |
|------|---------|
| `MASTER_PROJECT_CONTEXT_AND_EXECUTION_PLAN.md` | Full product vision, USPs, models, demo story, research framing (read by section) |
| `PRODUCT_PRINCIPLES.md` | P1–P12, privacy, notification discipline, non-goals, feature decision checklist |
| `GLOSSARY.md` | Shared vocabulary + canonical demo IDs (OP1001, EXC001, SITE_A, TASK001…) |

## architecture/: how the system is built

| File | Purpose |
|------|---------|
| `REPOSITORY_STRUCTURE.md` | **Where code belongs**, layer/dependency rules, ownership areas |
| `SYSTEM_ARCHITECTURE.md` | Runtime components, flows (assignment, hazard, copilot, training), storage, edge vs cloud |
| `architecture/contracts/CONTRACTS_GUIDE.md` | Contract layout, generated vs hand-written, versioning and breaking-change process |
| `architecture/contracts/API_CATALOG.md` · `EVENT_CATALOG.md` · `DATA_OWNERSHIP.md` · `TOOL_AND_ML_CONTRACTS.md` | Every endpoint, event, table and tool with its owner and consumers |
| `decisions/` | ADRs: 0001 tech stack, 0002 repository structure, 0000 template |

## development/: how we work

| File | Purpose |
|------|---------|
| `PARALLEL_WORKFLOW.md` | Workstreams, phases and gates, conflict-free parallel rules |
| `TEAM_AND_OWNERSHIP.md` | People ↔ ownership areas ↔ workstreams (fill in at kickoff) |
| `SYNC_PROTOCOL.md` | What to do on every push and pull (status marking) |
| `INTEGRATION_CHECKPOINTS.md` | Gates G0–G4 and demo-scene mapping |
| `DEFINITION_OF_DONE.md` | DoD for work packages, workstreams, contract and safety changes |
| `AGENT_PLAYBOOK.md` | Per-IDE setup and prompts for Claude Code, Codex CLI, Antigravity, others |
| `workstreams/MXX-*.md` | One file per workstream: plan (scope, WPs, acceptance) + Status (edited by its owner) |
| `sync-log/<handle>.md` | Each person's push/pull log |

`research/` is created with the first evaluation write-up (M11).
