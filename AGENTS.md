# AGENTS.md: rules for every coding agent and human in this repo

> Canonical instructions for all tools (Codex CLI and Antigravity read this file; Claude Code via `CLAUDE.md`; Gemini via `GEMINI.md`). **Change rules here only.**

## 0. What ARGUS is

An operator-first construction-equipment platform built around a **Human-Machine Operational Twin** (operator + machine + task + environment). Two roles only: **Operator** and **Supervisor/Admin**. Vision: `docs/product/MASTER_PROJECT_CONTEXT_AND_EXECUTION_PLAN.md` (read the section you need, not all of it).

## 1. Read before you change anything

1. `README.md`: what runs where, how to run it
2. `docs/architecture/REPOSITORY_STRUCTURE.md`: **where code belongs, dependency rules, ownership areas**
3. `docs/product/PRODUCT_PRINCIPLES.md`: non-negotiables (safety, grounding, don't blame the operator)
4. Your workstream file `docs/development/workstreams/MXX-*.md` (plan + status)
5. The contracts you touch: `contracts/**` and `docs/architecture/contracts/*.md`

## 2. Know what you may edit

- Find your **ownership area** in `REPOSITORY_STRUCTURE.md` §6 and work inside it. Shared paths (contracts, `components/`, `lib/`, `core/`) change only through a deliberate, reviewed PR.
- If the task needs edits in another area, stop and say so. Propose the change instead of making it.

## 3. Rules

| # | Rule |
|---|------|
| R1 | **Don't create folders speculatively.** No empty packages, no new top-level directories (needs an ADR). M00–M11 are *workstreams*, never folder names. |
| R2 | **Reuse existing abstractions.** New backend capability = a package in `backend/app/domain/<area>/` (models, schemas, service, wiring) + a thin `backend/app/api/v1/<area>.py`. Not a new service, app or framework per feature. |
| R3 | **Respect layers** (enforced by `backend/tests/test_architecture.py`): `core` never imports business code; routes stay thin (no queries); other capabilities are used via their **service/schemas**, never their tables; Copilot tools call services, never the database. |
| R4 | **Frontend talks only to the backend API/WebSocket** (`frontend/src/lib/api`, `lib/websocket`). Never databases, ML or LLM providers directly. |
| R5 | **Safety-critical decisions are deterministic** (rules + sensor validation). ML is evidence; **an LLM never decides safety**. |
| R6 | **The Copilot never invents facts.** Every operational fact comes from a tool → domain service → authoritative data. |
| R7 | **Preserve contracts.** Don't rename routes, schema classes, WS messages or event names casually. Additive changes are fine; breaking changes follow `docs/architecture/contracts/CONTRACTS_GUIDE.md` §4. |
| R8 | **Generated files are never hand-edited**: `contracts/openapi/argus-api.yaml`, generated event/tool schemas, `frontend/src/lib/api/generated/`. Run `python scripts/dev.py contracts`. Don't hand-merge lockfiles. |
| R9 | **Migrations are linear**: `python scripts/dev.py revision -m "..."`, review the file, never edit merged history. |
| R10 | **Tests come with the change**, and you run them after any structural change: `python scripts/dev.py check`. |
| R11 | **Update docs when architecture changes**: `REPOSITORY_STRUCTURE.md`, the relevant catalog, an ADR for new top-level folders/runtimes. |
| R12 | **No secrets** in code, logs or docs. Placeholders go in `.env.example`. |
| R13 | **Don't blame the operator**: deviations are attributed across OPERATOR/MACHINE/TASK/SITE/ENVIRONMENT/INTERACTION/UNKNOWN with evidence. |

## 4. Commands

```bash
uv sync                               # Python deps (repo root)
python scripts/dev.py api             # backend, lite mode (SQLite + in-memory bus), seeded → :8000/docs
python scripts/dev.py web             # frontend → :3000 (op1001 / sup001, password demo1234)
python scripts/dev.py sim --demo-g1   # simulator: assign → pre-check → start → live telemetry
python scripts/dev.py test [area]     # backend tests (core, platform, tasks, twin, iot, integration)
python scripts/dev.py contracts       # regenerate + validate contracts, regenerate frontend API types
python scripts/dev.py check           # everything CI runs
python scripts/dev.py up              # full Docker stack
```

## 5. Status on every push and pull

- Before pushing: `python scripts/status.py log --module MXX --action PUSH --msg "..." [--wp MXX-WPn=STATE]` (updates your workstream's Status section + your sync log). Commit it with the code.
- After pulling: `python scripts/status.py changes`, then `python scripts/status.py log --action PULL --msg "..."`.
- Details: `docs/development/SYNC_PROTOCOL.md`. Git conventions: `CONTRIBUTING.md` (no AI co-author trailers).
