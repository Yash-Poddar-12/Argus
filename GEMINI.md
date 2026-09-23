# GEMINI.md

This pointer is for Gemini-based agents, including Antigravity setups that read `GEMINI.md`.

**The canonical rules are in [`AGENTS.md`](AGENTS.md). Read it fully before doing anything.** Don't duplicate or override rules here. If your tool also reads `AGENTS.md` directly, this file changes nothing.

Minimum reminders if you only read this file:

1. Identify the module (`docs/01-architecture/MODULAR_WORKFLOW.md`) and edit only its paths (`docs/01-architecture/REPO_STRUCTURE.md`).
2. Cross-module communication goes through `contracts/` only. Use mocks for unfinished dependencies.
3. Safety decisions are deterministic. The Copilot answers only from tool results.
4. Update your module's `STATUS.md` before every push. Log your pulls in `docs/05-status/sync-log/<handle>.md`.
