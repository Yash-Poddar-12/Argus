# GEMINI.md

Pointer for Gemini-based agents, including Antigravity setups that read `GEMINI.md`.

**The canonical rules are in [`AGENTS.md`](AGENTS.md). Read it fully before doing anything.** Don't duplicate or override rules here.

Minimum reminders if you only read this file:

1. Where code belongs, the layer rules and your ownership area: `docs/architecture/REPOSITORY_STRUCTURE.md`.
2. Don't create new folders or services speculatively. Reuse the capability packages in `backend/app/domain/` and the features in `frontend/src/features/`.
3. Frontend talks only to the backend API. Safety decisions are deterministic. The Copilot answers only from tool results.
4. Run `python scripts/dev.py check` after structural changes, and update your workstream status before every push (`python scripts/status.py log ...`).
