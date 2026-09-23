# MXX — Module Name

<!-- Copy this folder to docs/03-modules/MXX-short-name/ for a new module. Follow master §54. Keep it short and concrete. -->

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

## Owned paths

`backend/modules/mXX_name/`, `backend/migrations/mXX_name/`, `backend/tests/mXX_name/`, `contracts/openapi/mXX-name.yaml`, `contracts/events/mXX/`, …

## Interfaces

**Produces:** APIs (link rows in `API_CATALOG.md`), events (`EVENT_CATALOG.md`), tables (`DATA_OWNERSHIP.md`), tools (`TOOL_AND_ML_CONTRACTS.md`).
**Consumes:** events / APIs / facades.

## Mock strategy

What mocks this module **provides** (WP0) and which mocks it **uses** until dependencies are LIVE.

## Internal architecture

`module.py`, `public.py`, `api/`, `domain/`, `adapters/`, `mocks/`. Note anything unusual.

## Work packages

| WP | Title | Paths | Depends on | Est. |
|----|-------|-------|------------|------|
| MXX-WP0 | Contracts + `public.py` + mocks | | | 1 d |
| MXX-WP1 | | | | |

## Acceptance criteria

- [ ]

## Testing

Unit / contract / integration / simulation.

## Future extensions

## Known constraints

## Integration checklist

- [ ]
