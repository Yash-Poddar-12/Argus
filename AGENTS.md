# AGENTS.md — Rules for every coding agent and human in this repo

> This file is the **single canonical instruction file** for all tools: Codex CLI and Antigravity read it directly; Claude Code reads it through `CLAUDE.md`; Gemini-based tools through `GEMINI.md`. **Edit rules here, not in the pointer files.**

## 0. What we are building (30 seconds)

**CAT Operator & Site Intelligence Platform:** an operator-first platform built around a **Human-Machine Operational Twin** (operator + machine + task + environment). It predicts, explains ("WHY?"), and assists through a grounded, multilingual voice/dashboard Copilot. Supervisors/Admins get site-level decision support. Full vision: `MASTER_PROJECT_CONTEXT_AND_EXECUTION_PLAN.md`.

## 1. Reading order (do this before writing code)

1. `AGENTS.md` (this file)
2. `README.md`
3. `docs/00-project/PRODUCT_PRINCIPLES.md`
4. `docs/01-architecture/MODULAR_WORKFLOW.md`
5. `docs/01-architecture/REPO_STRUCTURE.md`
6. The module's `docs/03-modules/MXX-*/SPEC.md` and `STATUS.md`
7. The contracts the task touches: `contracts/**` + `docs/02-contracts/*.md`

For deep product context (why a feature exists, demo story, research framing) read the relevant section of the master file. Don't load all 4,700 lines unless you need them.

## 2. Before you touch anything, answer these

1. **Which module** does this task belong to? (`docs/01-architecture/MODULAR_WORKFLOW.md` §2)
2. **Which paths** does that module own? (`REPO_STRUCTURE.md` §2). Only edit those paths.
3. **Which contracts** does it consume/produce? Read them first.
4. **Is an upstream dependency unfinished?** Use or write a **mock** behind the contract. Don't implement another module's logic.

If the task needs a change outside your module's paths, **stop and say so**. Propose the change (contract PR or note in `STATUS.md` → Blockers) and don't make the edit yourself.

## 3. Hard rules

| # | Rule |
|---|------|
| R1 | **Stay in your module's paths.** Never edit another module's files, migrations, tables, or contracts. |
| R2 | **Cross-module = contracts only.** Never import another module's internals. Allowed: `backend/core/*`, another module's **`public.py` facade** (DTOs + Protocols + accessors only), `contracts/`, generated `frontend/packages/api-client`. |
| R3 | **No silent contract changes.** Additive changes are fine with a version bump. Breaking changes follow `docs/02-contracts/CONTRACTS_GUIDE.md` §4. |
| R4 | **One writer per table / event stream** (`docs/02-contracts/DATA_OWNERSHIP.md`, `EVENT_CATALOG.md`). |
| R5 | **Safety-critical decisions are deterministic** (rules + sensor validation, at the edge, in M04). ML is evidence only; the LLM never decides safety. |
| R6 | **The Copilot never invents operational facts.** Every factual answer comes from a tool call → authoritative result → LLM explanation. |
| R7 | **Don't blame the operator.** Deviations get attributed across OPERATOR / MACHINE / TASK / SITE / ENVIRONMENT / INTERACTION / UNKNOWN, with the evidence shown. |
| R8 | **Register by discovery.** Don't edit central routers, nav files, compose base, or env base. Use your module's `module.py`, your slot, `infra/compose/<module>.yml`, `infra/env/<module>.env.example`. |
| R9 | **Never hand-edit generated code** (`frontend/packages/api-client`) or hand-merge lockfiles. Regenerate them. |
| R10 | **Mark status on every push and pull** (§5). |
| R11 | **Tests come with the change.** Unit tests for domain logic; contract tests for anything in `contracts/`. |
| R12 | **No secrets in code, logs, or docs.** Use `infra/env/*.env.example` with placeholder values. |
| R13 | **When ambiguous, keep the existing architecture** and write the ambiguity down (STATUS.md → Open questions) rather than inventing new architecture. |

## 4. Module structure you should produce

```text
backend/modules/mXX_name/{module.py, public.py, api/, domain/, adapters/, mocks/}
backend/migrations/mXX_name/      backend/tests/mXX_name/
frontend/apps/<app>/src/app/<route>/   frontend/apps/<app>/src/features/<feature>/
```

`public.py` is the only file other modules may import. `domain/` is pure logic with no I/O. `adapters/` does the I/O. `api/` stays thin. `mocks/` returns contract-valid fixtures. **WP0 of every module = contract + `public.py` + mocks**, shipped first.

## 5. Status protocol (every push, every pull)

**Before pushing:**
1. Update `docs/03-modules/MXX-*/STATUS.md`: WP states, `Last updated`, and one new line at the top of **Update log**.
   Shortcut: `python scripts/status.py log --module MXX --action PUSH --msg "<what changed>"`
2. Commit the STATUS.md change **in the same push** as the code.

**After pulling:**
1. Run `python scripts/status.py changes` to see which contracts and module statuses changed.
2. If a contract you consume changed, adapt or record a blocker.
3. Append a PULL entry to your own `docs/05-status/sync-log/<handle>.md`.
   Shortcut: `python scripts/status.py log --action PULL --msg "<what you noticed>"` (handle comes from `git config github.user`/`user.name`, or pass `--handle`)

Full detail: `docs/04-workflow/SYNC_PROTOCOL.md`.

**Agents:** When you finish a task, **suggest** the STATUS.md update (or make it if you were asked to commit). Don't mark a WP `DONE` unless it meets `docs/04-workflow/DEFINITION_OF_DONE.md`.

## 6. Git conventions

- Branches: `feature/mXX-wpY-short-name`, `fix/mXX-short-name`, `contract/mXX-short-name`, `docs/short-name`. Base and PR target: `develop`.
- Commits: `mXX(wpY): imperative summary`, e.g. `m04(wp2): add closing-speed proximity rule`.
- Small PRs. Every PR fills `.github/PULL_REQUEST_TEMPLATE.md`, including the "STATUS.md updated" checkbox.
- Rebase your branch on `develop` before opening a PR. Don't force-push shared branches.

Full detail: `CONTRIBUTING.md`.

## 7. Default tech stack

Proposed in `docs/01-architecture/adr/ADR-0001-tech-stack.md`. Check that ADR's status before assuming. In short: Python 3.12 + FastAPI + SQLAlchemy/Alembic; PostgreSQL + TimescaleDB + pgvector; Redis (state + Streams event bus behind an interface); Next.js + TypeScript (pnpm workspaces); Python edge service; scikit-learn / LightGBM / SHAP; LLM behind a provider interface.

## 8. Commands

`scripts/dev.py` works everywhere (no make/bash needed); `make <target>` is a thin wrapper around it.

```bash
uv sync                                   # Python deps (once)
python scripts/dev.py api                 # backend in LITE mode: SQLite + in-memory bus, auto-seeded, :8000
python scripts/dev.py web operator        # operator app :3000   (admin app: web admin -> :3001)
python scripts/dev.py up                  # full stack via Docker Compose (Postgres/Timescale, Redis, MQTT)
python scripts/dev.py test [m01_twin]     # tests (all, or one module)
python scripts/dev.py contracts           # export OpenAPI from code + validate contracts + regenerate api-client
python scripts/dev.py revision --module m01_twin -m "msg"   # migration on your module's Alembic branch
python scripts/status.py board            # live module status board
python scripts/status.py changes          # what changed since your last pull
```

## 9. Done means

See `docs/04-workflow/DEFINITION_OF_DONE.md`. Short version: in scope, contract defined, tests pass, mocks provided, errors and logging handled, docs and STATUS updated, no cross-module ownership violated, demo path verified.
