# CAT Operator & Site Intelligence Platform

> **An operator-first Human-Machine Operational Intelligence platform.** It understands the operator, machine, task, and environment together, predicts what is likely to happen, assists through a grounded multilingual voice/dashboard Copilot, learns from outcomes, and gives supervisors site-level decision support.

```text
Machine + Human + Task + Environment → Operational Twin → Understand → Predict → Assist → Human Decision → Learn
```

**Pitch:** One Operational Twin, several specialized intelligence engines, one grounded Operator Copilot, and a continuous feedback loop from real-world outcomes.

---

## Who uses it

| Role | What they get |
|------|---------------|
| **Operator** (primary) | My Day, My Machine, My Tasks, My Safety, My Performance, My Training, AI Copilot (voice + multilingual) |
| **Supervisor/Admin** (supporting) | Operator/machine/site CRUD, assignments, tasks and deadlines, site map, hazards, operational intelligence, what-if scenarios |

---

## How we build it: modular, in parallel

We're a team of 3–5 working **in parallel**, each on a different IDE or agent (Antigravity, Claude CLI, Codex CLI, …). The whole method is in **[`docs/01-architecture/MODULAR_WORKFLOW.md`](docs/01-architecture/MODULAR_WORKFLOW.md)**.

```text
M00 Foundation ──► M01 Operational Twin ──► ┬─ M02 Operator UX      ┬─ M05 Site Intelligence ┬─ M09 Counterfactual
   (Phase 0)          (Phase 1)             ├─ M03 Admin Console    ├─ M07 Copilot           ├─ M10 Federated ML
                                            ├─ M04 IoT Hazard Mesh  └─ M08 Training          └─ M11 Analytics/Eval
                                            └─ M06 Operator ML
                       Gate G1: contracts v1 frozen → everything after this runs in parallel on mocks
```

| Module | Spec | Status |
|--------|------|--------|
| M00 Foundation | [SPEC](docs/03-modules/M00-foundation/SPEC.md) | [STATUS](docs/03-modules/M00-foundation/STATUS.md) |
| M01 Operational Twin | [SPEC](docs/03-modules/M01-operational-twin/SPEC.md) | [STATUS](docs/03-modules/M01-operational-twin/STATUS.md) |
| M02 Operator Experience | [SPEC](docs/03-modules/M02-operator-experience/SPEC.md) | [STATUS](docs/03-modules/M02-operator-experience/STATUS.md) |
| M03 Supervisor/Admin Console | [SPEC](docs/03-modules/M03-admin-console/SPEC.md) | [STATUS](docs/03-modules/M03-admin-console/STATUS.md) |
| M04 IoT Hazard Mesh | [SPEC](docs/03-modules/M04-iot-hazard-mesh/SPEC.md) | [STATUS](docs/03-modules/M04-iot-hazard-mesh/STATUS.md) |
| M05 Site Operational Intelligence | [SPEC](docs/03-modules/M05-site-intelligence/SPEC.md) | [STATUS](docs/03-modules/M05-site-intelligence/STATUS.md) |
| M06 Operator Intelligence / ML | [SPEC](docs/03-modules/M06-operator-ml/SPEC.md) | [STATUS](docs/03-modules/M06-operator-ml/STATUS.md) |
| M07 Copilot | [SPEC](docs/03-modules/M07-copilot/SPEC.md) | [STATUS](docs/03-modules/M07-copilot/STATUS.md) |
| M08 Training | [SPEC](docs/03-modules/M08-training/SPEC.md) | [STATUS](docs/03-modules/M08-training/STATUS.md) |
| M09 Counterfactual Engine | [SPEC](docs/03-modules/M09-counterfactual/SPEC.md) | [STATUS](docs/03-modules/M09-counterfactual/STATUS.md) |
| M10 Federated Intelligence | [SPEC](docs/03-modules/M10-federated/SPEC.md) | [STATUS](docs/03-modules/M10-federated/STATUS.md) |
| M11 Analytics & Evaluation | [SPEC](docs/03-modules/M11-analytics-eval/SPEC.md) | [STATUS](docs/03-modules/M11-analytics-eval/STATUS.md) |

Live board: `python scripts/status.py board`

---

## Getting started

### For humans

1. Read [`AGENTS.md`](AGENTS.md). It's short and the rules apply to you too.
2. Find your module(s) in [`docs/00-project/TEAM_AND_OWNERSHIP.md`](docs/00-project/TEAM_AND_OWNERSHIP.md).
3. Read your module's `SPEC.md` and `STATUS.md`.
4. Branch from `develop`: `git checkout -b feature/mXX-wpY-short-name`.
5. Follow the push/pull status routine in [`docs/04-workflow/SYNC_PROTOCOL.md`](docs/04-workflow/SYNC_PROTOCOL.md).

### For agents / IDEs

| Tool | Auto-loaded file | Setup notes |
|------|------------------|-------------|
| Codex CLI | `AGENTS.md` | none |
| Claude Code (CLI / IDE) | `CLAUDE.md` → imports `AGENTS.md` | none |
| Antigravity | `AGENTS.md` / `GEMINI.md` (depends on version) | see [`AGENT_PLAYBOOK.md`](docs/04-workflow/AGENT_PLAYBOOK.md) |
| Anything else | point it at `AGENTS.md` | starter prompt in the playbook |

### Run locally (target, available after Gate G0)

```bash
git clone <repo> && cd <repo>
cp infra/env/base.env.example .env        # + any module env files you need
make up                                    # frontend + backend + Postgres/Timescale + Redis + event bus
make seed                                  # demo data: OP1001, EXC001, SITE_A, TASK001
make sim SCENARIO=S1                       # deterministic simulator
```

---

## Documentation map

See [`docs/INDEX.md`](docs/INDEX.md) for the full list and who owns each document.

| I want to… | Read |
|------------|------|
| Understand the product vision | [`MASTER_PROJECT_CONTEXT_AND_EXECUTION_PLAN.md`](MASTER_PROJECT_CONTEXT_AND_EXECUTION_PLAN.md) |
| Know the non-negotiable principles | [`docs/00-project/PRODUCT_PRINCIPLES.md`](docs/00-project/PRODUCT_PRINCIPLES.md) |
| See how parallel work is organized | [`docs/01-architecture/MODULAR_WORKFLOW.md`](docs/01-architecture/MODULAR_WORKFLOW.md) |
| Find who owns a folder | [`docs/01-architecture/REPO_STRUCTURE.md`](docs/01-architecture/REPO_STRUCTURE.md) |
| Change an API, event, or schema | [`docs/02-contracts/CONTRACTS_GUIDE.md`](docs/02-contracts/CONTRACTS_GUIDE.md) |
| Know what to do on push/pull | [`docs/04-workflow/SYNC_PROTOCOL.md`](docs/04-workflow/SYNC_PROTOCOL.md) |
| Open a PR | [`CONTRIBUTING.md`](CONTRIBUTING.md) |

## Non-goals

Autonomous machine control, generic fleet management, HR performance scoring, a generic LMS, an unrestricted chatbot, predictive maintenance as the main product, fully autonomous dispatch, and raw-telemetry dashboards as the value proposition.
