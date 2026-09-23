# CLAUDE.md

All project rules live in `AGENTS.md` so every IDE/agent follows the same rules. Claude Code loads it here:

@AGENTS.md

## Claude Code notes

- Personal preferences go in `CLAUDE.local.md` (gitignored), not here.
- Before editing, check the ownership area and layer rules in `docs/architecture/REPOSITORY_STRUCTURE.md`. Don't edit outside them without saying why.
- After structural changes run `python scripts/dev.py check`. Before pushing, run or propose `python scripts/status.py log --module MXX --action PUSH --msg "..."`.
