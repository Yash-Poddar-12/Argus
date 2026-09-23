# M09 — Counterfactual Engine ("What if?") · STATUS

> **Only the module owner (and their agent) edits this file.** Update it in the same commit as your code, **before every push**.
> Shortcut: `python scripts/status.py log --module M09 --action PUSH --msg "..." [--wp M09-WP1=DONE] [--state IN_PROGRESS]`
> States: `NOT_STARTED` · `IN_PROGRESS` · `MOCKED` (contract + mock shipped) · `BLOCKED` · `IN_REVIEW` · `DONE`
> Spec: [SPEC.md](SPEC.md)

<!-- status:summary (parsed by scripts/status.py; keep the table shape) -->
| Field | Value |
|-------|-------|
| Module | M09 |
| Owner | @unassigned |
| Phase | 4 |
| State | NOT_STARTED |
| Current focus | — |
| Contract version | — |
| Last updated | 2026-09-23 · @team · status file created |
<!-- /status:summary -->

## Work packages

| WP | Title | State | Branch / PR | Notes |
|----|-------|-------|-------------|-------|
| M09-WP0 | Contracts + `public.py` + mocks (the D2 reallocation example from master §11.5) | NOT_STARTED | — | |
| M09-WP1 | Scenario spec + validation + persistence | NOT_STARTED | — | |
| M09-WP2 | Twin/graph cloning + modification | NOT_STARTED | — | |
| M09-WP3 | Evaluation: M06 predictions + site queue simulation | NOT_STARTED | — | |
| M09-WP4 | Safety constraint evaluation | NOT_STARTED | — | |
| M09-WP5 | Comparison, uncertainty, assumptions, phrasing | NOT_STARTED | — | |
| M09-WP6 | `run_what_if_scenario` tool for M07 | NOT_STARTED | — | |
| M09-SLOT | Admin scenarios slot UI (if held) | NOT_STARTED | — | |

## Using mocks for

| Dependency | Mock source | Switch to real when |
|------------|-------------|---------------------|
| M05 graph | `contracts/openapi/m05-site-intel.yaml` examples | M05-WP2 LIVE |
| M06 predictions | `m06_ml.public` mock | M06-WP3 LIVE |

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
