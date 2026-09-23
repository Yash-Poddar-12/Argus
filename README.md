# ARGUS: CAT Operator & Site Intelligence Platform

> **Operator-first human-machine operational intelligence.** ARGUS understands the operator, machine, task and environment together (the **Operational Twin**), predicts what's likely to happen, assists through a grounded multilingual Copilot, and gives supervisors site-level decision support.

```text
Operator + Machine + Task + Environment → Operational Twin → Contextual Intelligence → Operator + Site Decisions
```

Two roles: **Operator** (own shift, machine, tasks, safety, performance, training, Copilot) and **Supervisor/Admin** (machines, assignments, tasks, site configuration, safety monitoring, site intelligence).

## Repository at a glance

```text
backend/     FastAPI app (package `app`): core · api/v1 · domain/<capability> · copilot · iot/simulator · seed
frontend/    Next.js app: /operator and /supervisor areas · features/<feature> · components · lib
ml/          ML research, training, evaluation (no API routes; backend calls it through interfaces)
contracts/   openapi/ · events/<area>/ · tools/ · schemas/   (machine-readable source of truth)
infra/       Docker service configs            docs/  product · architecture · development
scripts/     dev.py (task runner) · contracts.py · status.py
```

Where does code go? **[`docs/architecture/REPOSITORY_STRUCTURE.md`](docs/architecture/REPOSITORY_STRUCTURE.md)** (tree, "where does this belong?" table, dependency rules, ownership areas). Why it's shaped this way: [ADR-0002](docs/architecture/decisions/ADR-0002-production-repository-structure.md).

## Run it

Needs Python 3.12+ with [uv](https://docs.astral.sh/uv/) and Node 20+. Docker is optional.

```bash
git clone https://github.com/Yash-Poddar-12/Argus.git && cd Argus
python scripts/dev.py setup          # uv sync + frontend install
python scripts/dev.py api            # backend (SQLite + in-memory bus, demo data) → http://localhost:8000/docs
python scripts/dev.py web            # frontend → http://localhost:3000   (op1001 or sup001 / demo1234)
python scripts/dev.py sim --demo-g1  # simulator: assign OP1001→EXC001→TASK001, pre-check, start, live telemetry

python scripts/dev.py up             # full stack in Docker: Postgres/Timescale, Redis, MQTT, backend, frontend
python scripts/dev.py check          # everything CI runs (lint, contracts, tests, frontend lint/typecheck/build)
```

## Working on it (3–5 people, any IDE or agent)

1. Read [`AGENTS.md`](AGENTS.md): the rules for humans and agents (Claude Code, Codex CLI, Antigravity, Gemini).
2. Find your ownership area in [`REPOSITORY_STRUCTURE.md` §6](docs/architecture/REPOSITORY_STRUCTURE.md) and your workstream in [`docs/development/workstreams/`](docs/development/workstreams/README.md).
3. Branch from `develop`, follow [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`docs/development/SYNC_PROTOCOL.md`](docs/development/SYNC_PROTOCOL.md) (status on every push/pull).

| Workstream | What it delivers | State |
|------------|------------------|-------|
| M00 Foundation | core, auth/RBAC, platform master data, tooling, CI, frontend shell | built |
| M01 Operational Twin | tasks + lifecycle, telemetry, environment, twin, Copilot tools, simulator | built |
| M02–M11 | operator UX, supervisor console, IoT hazard mesh, site intelligence, ML, Copilot, training, counterfactual, federated, evaluation | planned: see workstream files |

Live status board: `python scripts/status.py board`

## Documentation

| Need | Read |
|------|------|
| Product vision, principles, glossary | [`docs/product/`](docs/product/) |
| Architecture, contracts, decisions | [`docs/architecture/`](docs/architecture/) |
| How we work (parallel workflow, sync protocol, gates, DoD, agent playbook) | [`docs/development/`](docs/development/) |
| Everything, indexed | [`docs/README.md`](docs/README.md) |
| What changed | [`CHANGELOG.md`](CHANGELOG.md) |

## Non-goals

Autonomous machine control, generic fleet management, HR performance scoring, a generic LMS, an unrestricted chatbot, predictive maintenance as the main product, fully autonomous dispatch, raw-telemetry dashboards as the value proposition.
