# Contracts Guide

> Contracts are how 3–5 people build in parallel without waiting for each other. **The files under `contracts/` are the source of truth.** The `.md` catalogs in this folder explain them and record ownership.

## 1. Layout

```text
contracts/
├── schemas/common/        M00  ids.json, event-envelope.json, error.json, pagination.json, geo.json
├── schemas/twin/          M01  operational-twin.json, twin-snapshot.json, context types
├── openapi/mXX-*.yaml     one OpenAPI 3.1 file per module (owner = that module)
├── events/mXX/<event_type>.v<N>.json    JSON Schema for the event payload, foldered by PRODUCING module
│   ├── ws/<WS_TYPE>.v<N>.json           WebSocket message payloads this module pushes
│   └── examples/<event_type>.v<N>.example.json
├── tools/<tool_name>.json Copilot tool schema (owner = module owning the data), _registry.json (M07)
└── ml/<interface>.json    ML inference input/output (M06); ml/federated/ (M10)
```

Every schema file has an `examples/` sibling with at least one valid example. **Mocks return these examples**, so mocks and contracts can't drift.

### Hand-written vs generated

| Kind | How it's produced | Drift protection |
|------|-------------------|------------------|
| OpenAPI per module | **Generated** from the module's FastAPI router by `uv run python scripts/contracts.py export` | CI runs `export --check`; the build fails if code and file differ |
| Event / tool / twin schemas of modules that define `contract_documents()` in `wiring.py` (tasks, telemetry, environment, twin, copilot today) | **Generated** from pydantic models by the same command | same |
| Everything else (M00 events, other modules' WP0 contracts) | Hand-written JSON Schema | `contracts.py check` (valid schema + valid examples) and publish-time validation in tests |

In tests the event bus runs with `validate_events=True`: publishing a payload that doesn't match its contract (or an event with **no** contract) fails the test. This is the producer-conformance check.

## 2. Naming

| Thing | Convention | Example |
|-------|------------|---------|
| REST path | `/api/v1/<plural-resource>/{id}/<sub>` | `/api/v1/tasks/{task_id}/start` |
| Event type | `<domain>.<entity>.<past_tense_verb>` | `hazard.proximity.detected` |
| Event stream (topic) | `<domain>.events` (telemetry: `machine.telemetry`) | `safety.events` |
| WS message type | `UPPER_SNAKE` | `TASK_ETA_UPDATED` |
| JSON fields | `snake_case` | `operator_id`, `p80_duration` |
| IDs | string, prefixed as in the glossary | `OP1001`, `EXC001`; UUIDs for generated records |
| Timestamps | ISO-8601 UTC with `Z` | `2026-09-23T08:00:00Z` |
| Durations | minutes as number unless the field name says otherwise | `p50_duration_min` |
| Enums | `UPPER_SNAKE` | `CRITICAL`, `SITE`, `EDGE_ML` |

## 3. Event envelope (all events)

Defined in `contracts/schemas/common/event-envelope.json` (M00):

```json
{
  "event_id": "uuid",
  "event_type": "operator.task.assigned",
  "event_version": "1.0",
  "timestamp": "2026-09-23T08:00:00Z",
  "site_id": "SITE_A",
  "source_id": "tasks",
  "correlation_id": "uuid-or-null",
  "payload": { "...": "validated by contracts/events/<area>/<event_type>.v1.json" }
}
```

Consumers **must be idempotent on `event_id`**. The edge replays buffered events after reconnecting.

## 4. Versioning and change process

### Versions

- **OpenAPI:** URL major (`/api/v1`) + `info.version` semver per module file.
- **Events:** `event_version` `MAJOR.MINOR`; the schema file carries the major version (`.v1.json`).
- **Tools / ML:** `version` field inside the schema file.

### Change types

| Change | Type | What you do |
|--------|------|-------------|
| Add optional field / new endpoint / new event type / new enum value that consumers may ignore | **Additive** (minor) | Bump minor, update example, update catalog row, normal PR |
| Add a required field, remove or rename a field, change type/meaning/units, remove an endpoint or event | **Breaking** (major) | Full process below |
| Fix a typo in a description | Patch | Normal PR |

### Breaking change process

1. Open a `contract_change` issue (`.github/ISSUE_TEMPLATE/contract_change.md`) listing affected consumers from the catalogs.
2. Add the **new version side by side** (`.v2.json`, `/api/v2/...`, or a new tool version). Don't edit v1 in place.
3. Producer emits or serves **both** until every consumer has migrated. Consumers tick themselves off in the issue.
4. Record it in your workstream Status section → "Contract changes" and in the catalog.
5. Remove v1 only after all consumers confirm, and no later than the next gate.

### Contract freeze

- At **Gate G1**, M00 and M01 contracts are tagged `v1` and frozen: additive changes only; breaking changes need the process above plus a team ack.
- Every other module freezes its **own** contracts at the end of its WP0 (first publish). Consumers may rely on them from then on.

## 5. Mocks

- Each module's `schemas.py`/`service.py` accessor returns the mock when `a mock setting` or the real implementation isn't registered.
- REST mocks: FastAPI routes under the module with `?mock=1`, or a generated mock server from OpenAPI (e.g., Prism) for frontend work.
- Frontend mocks: `frontend/src/features/<feature>/mocks/` import JSON from `contracts/**/examples/`.
- Mocks should include **scenario variants** (normal, high risk, low confidence) so consumers can build every UI state.

## 6. Contract tests (CI)

| Test | Owner | Checks |
|------|-------|--------|
| Schema validity | M00 CI | Every file in `contracts/` is valid JSON Schema / OpenAPI 3.1 |
| Example validity | M00 CI | Every example validates against its schema |
| Producer conformance | Producer | Real outputs (API responses, emitted events) validate against the schema |
| Consumer conformance | Consumer | Consumer code handles every example variant |
| Client drift | M00 CI | `frontend/src/lib/api/` matches what the OpenAPI files generate |
| Catalog sync | M00 CI (later) | Every event/endpoint in `contracts/` appears in the catalogs and vice versa |

## 7. Catalog maintenance

The catalogs (`API_CATALOG.md`, `EVENT_CATALOG.md`, `DATA_OWNERSHIP.md`, `TOOL_AND_ML_CONTRACTS.md`) are shared files, but **each row belongs to the module in its Owner column**. Only edit your own rows. Rows are grouped by module so edits from different modules land in different parts of the file and rarely conflict.
