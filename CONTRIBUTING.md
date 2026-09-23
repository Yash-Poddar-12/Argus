# Contributing

This applies to every teammate and every agent. The rules are in `AGENTS.md`; where code goes is in `docs/architecture/REPOSITORY_STRUCTURE.md`. This file covers the Git mechanics.

## 1. Branches

```text
main        demo-ready only; merged from develop at each gate (G0…G4). Protected.
develop     integration branch; all PRs target this. Protected (PR + 1 review + CI green).
feature/mXX-wpY-short-name     normal work, named after the workstream WP (e.g. feature/m04-wp2-proximity-rules)
contract/short-name            contract-only changes (reviewed by consumers too)
fix/short-name                 bug fixes
refactor/short-name            structural changes (need `python scripts/dev.py check` green)
docs/short-name                docs-only changes
```

- Always branch from an up-to-date `develop`.
- One branch = one work package inside one ownership area. Changes in two areas go in two PRs.
- Keep branches short-lived (≤ 2–3 days). Rebase on `develop` often: `git pull --rebase origin develop`.

## 2. Daily loop

```bash
# start of session
git checkout develop && git pull --rebase
python scripts/status.py changes            # what changed in contracts / docs / other workstreams
python scripts/status.py log --action PULL --msg "pulled develop; noted <...>"
git checkout feature/mXX-wpY-... && git rebase develop

# ... work ...
python scripts/dev.py check                 # what CI runs (or the relevant subset: test, lint, contracts)

# before every push
python scripts/status.py log --module MXX --action PUSH --msg "<what changed>"
git add -A && git commit -m "mXX(wpY): <summary>"
git push -u origin HEAD
```

Details and edge cases: `docs/development/SYNC_PROTOCOL.md`.

## 3. Commit messages

```text
mXX(wpY): imperative summary            m01(wp3): fuse telemetry into twin state
contract(<area>): …                     contract(tasks): add p90 to TaskPrediction v1.1
refactor: …                             refactor: move simulator under backend/app/iot
docs: …                                 docs: clarify ownership areas
chore: …                                chore: bump ruff
```

**No AI co-author trailers.** Commits are authored by the teammate who made them. Don't add `Co-Authored-By:` lines for AI tools (Claude, Codex, Gemini, …), and turn off automatic attribution in your agent's settings if it adds one. This keeps the repo's contributor list to the actual team.

## 4. Pull requests

- Target `develop`. Fill in `.github/PULL_REQUEST_TEMPLATE.md` completely.
- **Required in every PR:** the workstream's Status section updated; tests for the change; no edits outside your ownership area (CODEOWNERS will flag them); CI green (includes the architecture rules).
- **Contract PRs** (`contracts/**`, or code that changes generated contracts) need a review from the owner **and** at least one consumer listed in `docs/architecture/contracts/EVENT_CATALOG.md` / `API_CATALOG.md`.
- Prefer PRs under ~400 changed lines (generated files excluded).
- Squash-merge into `develop`. Merge `develop` → `main` only at gates, with a tag `g0`, `g1`, …

## 5. Resolving conflicts

| Conflict in | Do this |
|-------------|---------|
| Files in your ownership area | Resolve normally |
| Another area's files | You shouldn't have edited them. Drop your changes to those files and raise it with the owner |
| Lockfiles (`uv.lock`, `frontend/pnpm-lock.yaml`) | Take `develop`'s version, then `uv lock` / `pnpm install`, commit |
| Generated files (`contracts/openapi/argus-api.yaml`, generated event/tool schemas, `frontend/src/lib/api/generated/`) | Accept either side, then regenerate: `python scripts/dev.py contracts` |
| Migrations (two new heads) | The later branch re-parents its revision onto the other (keep history linear) |
| Your workstream status update log | Keep both lines, newest first |

## 6. Code review expectations

- Review within one working day. If you're blocked on a review, say so in your workstream status → Blockers.
- Reviewers check: scope matches the workstream plan, contract compliance, tests, ownership boundaries, layer rules, safety rules (R5/R6 in AGENTS.md), no speculative folders (R1).
- Reviews can be done by an agent, but a human approves merges into `develop`.

## 7. Adding dependencies

- Python: runtime deps in `backend/pyproject.toml`; dev tooling in the root `pyproject.toml` dev group. Mention it in the PR.
- JS: `frontend/package.json`, in the PR that needs it.
- New infrastructure (a container, broker, DB) or a new top-level folder/runtime needs an ADR (`docs/architecture/decisions/`).
