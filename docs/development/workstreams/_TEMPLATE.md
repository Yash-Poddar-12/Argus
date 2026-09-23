# MXX — Module Name

<!-- Copy to docs/development/workstreams/MXX-short-name.md for a new workstream. Keep it short and concrete. -->

| Field | Value |
|-------|-------|
| Phase | |
| Type | frontend / backend / edge / ML / research |
| Depends on (contracts) | |
| Consumed by | |
| Gate | |

## Objective

One paragraph: what this module delivers.

## Why this module exists

Which product principle / USP / demo scene it serves.

## Scope

-

## Out of scope

- (name the module that owns each excluded item)

## Where the code lives

List the folders this workstream writes. Reuse existing capability packages; add a new one only when there is real code for it.

Folders are created only when real code lands. Ownership rules and the full map: `docs/architecture/REPOSITORY_STRUCTURE.md`.

## Interfaces

**Produces:** APIs (link rows in `API_CATALOG.md`), events (`EVENT_CATALOG.md`), tables (`DATA_OWNERSHIP.md`), tools (`TOOL_AND_ML_CONTRACTS.md`).
**Consumes:** events / APIs / facades.

## Mock strategy

What mocks this module **provides** (WP0) and which mocks it **uses** until dependencies are LIVE.

## Internal architecture

`wiring.py`, `schemas.py`/`service.py`, `api/`, `domain/`, `adapters/`, `mocks/`. Note anything unusual.

## Work package plan

| WP | Title | Paths | Depends on | Est. |
|----|-------|-------|------------|------|
| MXX-WP0 | Contracts + schemas + service + mocks | | | 1 d |
| MXX-WP1 | | | | |

## Acceptance criteria

- [ ]

## Testing

Unit / contract / integration / simulation.

## Future extensions

## Known constraints

## Integration checklist

- [ ]

---

# Status

> **Only the module owner (and their agent) edits this file.** Update it in the same commit as your code, **before every push**.
> Shortcut: `python scripts/status.py log --module MXX --action PUSH --msg "..." [--wp MXX-WP1=DONE] [--state IN_PROGRESS]`
> States: `NOT_STARTED` · `IN_PROGRESS` · `MOCKED` (contract + mock shipped) · `BLOCKED` · `IN_REVIEW` · `DONE`

<!-- status:summary (parsed by scripts/status.py; keep the table shape) -->
| Field | Value |
|-------|-------|
| Module | MXX |
| Owner | @unassigned |
| Phase | |
| State | NOT_STARTED |
| Current focus | — |
| Contract version | — |
| Last updated | YYYY-MM-DD · @handle · — |
<!-- /status:summary -->

## Work packages

| WP | Title | State | Branch / PR | Notes |
|----|-------|-------|-------------|-------|
| MXX-WP0 | Contracts + schemas + service + mocks | NOT_STARTED | — | |

## Using mocks for

| Dependency | Mock source | Switch to real when |
|------------|-------------|---------------------|
| | | |

## Blockers

- none

## Contract changes (pending / recent)

- none

## Open questions

- none

## Update log

<!-- newest first · one line per push: date · @handle · ACTION · branch · summary -->
<!-- log:insert -->
