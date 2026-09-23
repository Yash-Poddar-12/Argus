# Contributing

This applies to every teammate and every agent. The rules are in `AGENTS.md`. This file covers the Git mechanics.

## 1. Branches

```text
main        demo-ready only; merged from develop at each gate (G0…G4). Protected.
develop     integration branch; all PRs target this. Protected (PR + 1 review + CI green).
feature/mXX-wpY-short-name     normal work (e.g. feature/m04-wp2-proximity-rules)
contract/mXX-short-name        contract-only changes (reviewed by consumers too)
fix/mXX-short-name             bug fixes
docs/short-name                docs-only changes
```

- Always branch from an up-to-date `develop`.
- One branch = one module (and ideally one WP). If you need changes in two modules, open two PRs.
- Keep branches short-lived (≤ 2–3 days). Rebase on `develop` often: `git pull --rebase origin develop`.

## 2. Daily loop

```bash
# start of session
git checkout develop && git pull --rebase
python scripts/status.py changes            # what changed in contracts / other modules
python scripts/status.py log --person <handle> --action PULL --msg "pulled develop; noted <...>"
git checkout feature/mXX-wpY-... && git rebase develop

# ... work ...

# before every push
python scripts/status.py log --module MXX --action PUSH --msg "<what changed>"
git add -A && git commit -m "mXX(wpY): <summary>"
git push -u origin HEAD
```

Details and edge cases: `docs/04-workflow/SYNC_PROTOCOL.md`.

## 3. Commit messages

```text
mXX(wpY): imperative summary            m01(wp3): fuse telemetry into twin state
mXX(contract): …                        m06(contract): add p90 to TaskPrediction v1.1
docs: …                                 docs: clarify slot ownership
chore(m00): …                           chore(m00): bump ruff
```

**No AI co-author trailers.** Commits are authored by the teammate who made them. Don't add `Co-Authored-By:` lines for AI tools (Claude, Codex, Gemini, …), and turn off automatic attribution in your agent's settings if it adds one. This keeps the repo's contributor list to the actual team.

## 4. Pull requests

- Target `develop`. Fill in `.github/PULL_REQUEST_TEMPLATE.md` completely.
- **Required in every PR:** the module's `STATUS.md` updated; tests for the change; no edits outside owned paths (CODEOWNERS will flag them).
- **Contract PRs** (`contracts/**`) need a review from the owner **and** at least one consumer listed in `docs/02-contracts/EVENT_CATALOG.md` / `API_CATALOG.md`.
- Prefer PRs under ~400 changed lines (generated files excluded).
- Squash-merge into `develop`. Merge `develop` → `main` only at gates, with a tag `g0`, `g1`, …

## 5. Resolving conflicts

| Conflict in | Do this |
|-------------|---------|
| Your own module files | Resolve normally |
| Another module's files | You shouldn't have edited them. Drop your changes to those files and raise it with the owner |
| Lockfiles | `git checkout --theirs <lockfile>` (develop's), then `uv lock` / `pnpm install`, commit |
| `frontend/packages/api-client` | Discard both sides and regenerate: `make contracts` |
| Your `STATUS.md` update log | Keep both lines, newest first |

## 6. Code review expectations

- Review within one working day. If you're blocked on a review, say so in your STATUS.md → Blockers.
- Reviewers check: scope matches SPEC, contract compliance, tests, ownership boundaries, safety rules (R5/R6 in AGENTS.md).
- Reviews can be done by an agent, but a human approves merges into `develop`.

## 7. Adding dependencies

- Python: add to the backend `pyproject.toml`, in your module's dependency group where possible. Mention it in the PR.
- JS: add to your app's `package.json` (`frontend/apps/<app>`), not the root, unless it's tooling owned by M00.
- New infrastructure (a new container, broker, or DB) needs an ADR (`docs/01-architecture/adr/`).
