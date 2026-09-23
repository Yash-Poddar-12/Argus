# M07 — Copilot (voice · multilingual · tool-grounded) · STATUS

> **Only the module owner (and their agent) edits this file.** Update it in the same commit as your code, **before every push**.
> Shortcut: `python scripts/status.py log --module M07 --action PUSH --msg "..." [--wp M07-WP1=DONE] [--state IN_PROGRESS]`
> States: `NOT_STARTED` · `IN_PROGRESS` · `MOCKED` (contract + mock shipped) · `BLOCKED` · `IN_REVIEW` · `DONE`
> Spec: [SPEC.md](SPEC.md)

<!-- status:summary (parsed by scripts/status.py; keep the table shape) -->
| Field | Value |
|-------|-------|
| Module | M07 |
| Owner | @unassigned |
| Phase | 3 |
| State | NOT_STARTED |
| Current focus | — |
| Contract version | — |
| Last updated | 2026-09-23 · @team · status file created |
<!-- /status:summary -->

## Work packages

| WP | Title | State | Branch / PR | Notes |
|----|-------|-------|-------------|-------|
| M07-WP0 | Contracts + tool registry format + mock tool executor (returns contract examples) | NOT_STARTED | — | |
| M07-WP1 | Orchestration: intent → tools → LLM explanation, `LLMProvider` interface, grounding guard | NOT_STARTED | — | |
| M07-WP2 | Conversation context + query API + persistence | NOT_STARTED | — | |
| M07-WP3 | Multilingual: detection, message keys, translation adapter (en/hi/ta) | NOT_STARTED | — | |
| M07-WP4 | Voice: STT/TTS adapters + `/copilot/voice` | NOT_STARTED | — | |
| M07-WP5 | RAG: ingestion, pgvector, `search_knowledge` with citations | NOT_STARTED | — | |
| M07-WP6 | Proactive notifications + notification policy (priority, dedupe, cooldown) | NOT_STARTED | — | |
| M07-WP7 | Evaluation set: 50+ operator questions → expected tools/facts; grounding + latency metrics | NOT_STARTED | — | |
| M07-SLOT | Copilot slot UI (if held) | NOT_STARTED | — | |

## Using mocks for

| Dependency | Mock source | Switch to real when |
|------------|-------------|---------------------|
| All tools | mock tool executor returning `contracts/tools/examples/*` | each tool owner LIVE |
| LLM | fake LLMProvider in tests | keys configured |

## Blockers

- none

## Contract changes (pending / recent)

- none

## Open questions

- none

## Update log

<!-- newest first · one line per push: date · @handle · ACTION · branch · summary -->
<!-- log:insert -->
- 2026-09-23 · @team · INIT · docs scaffold · Status file created from SPEC work packages
