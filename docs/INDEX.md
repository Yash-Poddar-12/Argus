# Documentation Index

Every markdown file in the repo, what it's for, and who maintains it. **TEAM** means anyone may edit through a reviewed PR.

## Root (auto-loaded by IDEs / agents)

| File | Purpose | Owner |
|------|---------|-------|
| `AGENTS.md` | **Canonical** rules for all agents and humans (Codex, Antigravity, others) | M00 / TEAM |
| `CLAUDE.md` | Claude Code pointer (`@AGENTS.md`) + Claude-specific notes | M00 |
| `GEMINI.md` | Gemini/Antigravity pointer to `AGENTS.md` | M00 |
| `README.md` | Overview, module table, getting started, doc map | M00 |
| `CONTRIBUTING.md` | Branches, commits, PRs, conflicts, dependencies | M00 |
| `MASTER_PROJECT_CONTEXT_AND_EXECUTION_PLAN.md` | Full product vision, architecture reference, research framing | TEAM |

## docs/00-project: what and who

| File | Purpose |
|------|---------|
| `PRODUCT_PRINCIPLES.md` | P1–P12, non-goals, feature decision checklist |
| `GLOSSARY.md` | Shared vocabulary (twin, WHY? Engine, slot, gate, WP, …) |
| `TEAM_AND_OWNERSHIP.md` | People ↔ modules ↔ slots, allocation for 3/4/5 people, CODEOWNERS mapping |

## docs/01-architecture: how it fits together

| File | Purpose |
|------|---------|
| `MODULAR_WORKFLOW.md` | **The core method**: phases, gates, parallel rules, conflict hotspots |
| `SYSTEM_ARCHITECTURE.md` | Layers, runtime components, data flow, edge vs cloud |
| `REPO_STRUCTURE.md` | Target tree + path → module ownership |
| `adr/ADR-0000-template.md` | Template for architecture decisions |
| `adr/ADR-0001-tech-stack.md` | Proposed default stack |

## docs/02-contracts: the interfaces between modules

| File | Purpose |
|------|---------|
| `CONTRACTS_GUIDE.md` | Contract layout, versioning, change process, mocks, contract tests |
| `API_CATALOG.md` | Every REST/WS endpoint → owning module → consumers |
| `EVENT_CATALOG.md` | Every event → producer → consumers → version |
| `DATA_OWNERSHIP.md` | Every table/store → single writer module |
| `TOOL_AND_ML_CONTRACTS.md` | Copilot tool registry + ML inference interfaces |

## docs/03-modules: one folder per module

Each folder contains `SPEC.md` (scope, contracts, work packages, acceptance criteria) and `STATUS.md` (live state and update log). Only the module owner edits them. `_TEMPLATE/` holds the blank templates for new modules.

`M00-foundation` · `M01-operational-twin` · `M02-operator-experience` · `M03-admin-console` · `M04-iot-hazard-mesh` · `M05-site-intelligence` · `M06-operator-ml` · `M07-copilot` · `M08-training` · `M09-counterfactual` · `M10-federated` · `M11-analytics-eval`

## docs/04-workflow: how we work day to day

| File | Purpose |
|------|---------|
| `SYNC_PROTOCOL.md` | **What to do on every push and pull** (status marking) |
| `INTEGRATION_CHECKPOINTS.md` | Gates G0–G4, checklists, demo-scene mapping |
| `DEFINITION_OF_DONE.md` | DoD for WPs, modules, contracts |
| `AGENT_PLAYBOOK.md` | Per-IDE setup, starter prompts, agent guardrails |

## docs/05-status: live state

| File | Purpose |
|------|---------|
| `STATUS_BOARD.md` | Index of module statuses + how to read the computed board |
| `sync-log/<handle>.md` | Each person's own push/pull log (only they edit it) |
| `sync-log/_TEMPLATE.md` | Copy this to create your log |

## .github

| File | Purpose |
|------|---------|
| `PULL_REQUEST_TEMPLATE.md` | PR checklist (module, contracts, STATUS updated) |
| `ISSUE_TEMPLATE/work_package.md` | One issue per WP |
| `ISSUE_TEMPLATE/contract_change.md` | Proposing a breaking contract change |
| `CODEOWNERS` | Enforces path ownership (fill in handles) |
