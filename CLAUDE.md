# CLAUDE.md

All project rules live in `AGENTS.md` so every IDE/agent follows the same rules. Claude Code loads that file through the import below.

@AGENTS.md

## Claude Code notes

- Put personal preferences in `CLAUDE.local.md` (gitignored), not here.
- Before editing, confirm the module and its owned paths (`docs/01-architecture/REPO_STRUCTURE.md`). Refuse edits outside them and explain why.
- When a task finishes, run or propose `python scripts/status.py log --module MXX --action PUSH --msg "..."` before pushing.
