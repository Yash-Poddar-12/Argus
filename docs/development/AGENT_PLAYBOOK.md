# Agent Playbook: working across IDEs and agents

> The team uses different tools (Antigravity, Claude CLI, Codex CLI, plain IDEs). This page gets every tool to follow the **same** rules, which all live in `AGENTS.md`.

## 1. How each tool picks up the rules

| Tool | Reads automatically | What to do |
|------|---------------------|------------|
| **Codex CLI** | `AGENTS.md` (repo root; nested `AGENTS.md` files also apply to their subtree) | Nothing extra |
| **Claude Code** (CLI, desktop, IDE extension) | `CLAUDE.md`, which imports `@AGENTS.md` | Put personal tweaks in `CLAUDE.local.md` (gitignored) |
| **Antigravity** | Workspace rules / `AGENTS.md` / `GEMINI.md`, depending on version and settings | Check that it loads `AGENTS.md`. If not, add a workspace rule that says "Follow AGENTS.md at the repo root" (or rely on `GEMINI.md`, which points there) |
| **Cursor / Copilot / others** | Their own rule files | Add a one-line rule pointing to `AGENTS.md`. Don't copy the rules (copies drift) |

**Single source of truth:** only `AGENTS.md` contains rules. Pointer files (`CLAUDE.md`, `GEMINI.md`, any tool-specific rule file) just redirect. If you want to change a rule, change `AGENTS.md` in a PR.

**Optional module-level rules:** a module owner may add a short `AGENTS.md` inside their own folder (e.g., `edge/AGENTS.md`: "all rule changes need a versioned rule id"). Codex applies nested files automatically. Claude Code loads nested `CLAUDE.md` files, so add a one-line `CLAUDE.md` with `@AGENTS.md` next to it if you want both.

## 2. Starter prompt (paste at the start of a session)

Works in any agent. Fill in the brackets.

```text
You are working in the CAT Operator & Site Intelligence Platform repo.
My module: [MXX — name]. Work package: [MXX-WPn — title]. My handle: [@handle].

Before coding:
1. Read AGENTS.md, then docs/development/PARALLEL_WORKFLOW.md and REPOSITORY_STRUCTURE.md.
2. Read docs/development/workstreams/ and workstream status.
3. Read the contracts this WP touches (contracts/** and docs/architecture/contracts/*.md).
4. Run: python scripts/status.py changes   (tell me if any contract I consume changed)

Rules: edit only paths owned by [MXX]; use mocks behind contracts for unfinished dependencies;
never change another module's contracts/tables; safety logic is deterministic; Copilot facts come from tools.

Task: [describe the WP slice].
When done: list files changed, tests run + results, and propose the exact
`python scripts/status.py log --module [MXX] --action PUSH --msg "..." --wp [MXX-WPn]=<STATE>` command.
```

## 3. Prompts for common jobs

**Ship WP0 (contract + facade + mocks):**
```text
Implement [MXX]-WP0: write the contract files listed in SPEC "Owned paths" (OpenAPI, events, tools/ML as relevant)
with at least one example each (normal + one edge case), backend/app/domain/<area>/{schemas,events,service,wiring}.py exposing DTOs, event payloads
and get_x() accessors that return mocks built from those examples, and contract tests validating examples.
Update the catalog rows for my module to status MOCKED. Don't implement real logic yet.
```

**Swap a mock for the real dependency:**
```text
Dependency [MYY] marked [MYY-WPn] DONE. Switch my module from its mock to the real implementation via
the owning capability's service.py / API. Keep the mock available for tests. Update workstream status "Using mocks for".
```

**Review a teammate's PR (any agent):**
```text
Review this diff against AGENTS.md rules R1–R13, the module SPEC, and the contracts. Flag: edits outside owned
paths, contract changes without version bump/catalog update, cross-module internal imports, safety logic in ML/LLM,
Copilot answers not grounded in tool results, missing tests, missing workstream status update.
```

## 4. Guardrails for agents

- **Scope lock:** if the agent proposes edits outside your module's paths, reject them and open a request to the owner instead.
- **No "helpful" refactors** of shared code (`backend/core`, `packages/ui`, contracts of other modules) inside a feature PR.
- **Generated code:** never let an agent hand-edit `frontend/src/lib/api/`; run `make contracts`.
- **Lockfiles:** agents should not hand-merge them. Regenerate instead.
- **Secrets:** agents must use placeholders in `.env.example`; real keys stay in your local `.env` (gitignored).
- **Long context:** agents don't need the whole master file. Point them to specific sections (e.g., "master §20 task-time predictor").

## 5. Keeping agents' context fresh after pulls

After `git pull`, tell the agent: *"Run `python scripts/status.py changes` and summarize anything that affects [MXX]."* This is how an agent in one IDE learns about contract changes made by an agent in another.
