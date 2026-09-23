# ADR-0001: Default tech stack

| Field | Value |
|-------|-------|
| Status | **PROPOSED**: confirm at kickoff, then set to ACCEPTED. Implemented as amended below (M00, 2026-09-23) |
| Date | 2026-09-23 |
| Author | team |
| Affected modules | all |
| Contract changes | none (establishes baseline) |

## Context

The master plan fixes the *kinds* of stores and patterns (PostgreSQL, a time-series store, Redis, pgvector, REST + WS, event-driven, edge-first) but not the concrete frameworks. The team works across several IDEs and agents, so we need one boring, well-documented stack that every agent writes well, and that keeps ML, Copilot, and backend in the same language.

## Decision (proposed)

| Concern | Choice | Replaceable behind |
|---------|--------|--------------------|
| Backend language/framework | Python 3.12, FastAPI, Pydantic v2 | OpenAPI contracts |
| ORM / migrations | SQLAlchemy 2.x, Alembic (one branch per module) | repository adapters |
| Python deps | `uv` (single `pyproject.toml`, dependency groups per module) | — |
| Relational + time-series + vectors | PostgreSQL 16 + TimescaleDB + pgvector (single container for dev) | repository adapters |
| Live state / cache | Redis 7 | `StateStore` interface |
| Event bus | Redis Streams for MVP | `EventBus` interface (`publish`, `subscribe`, consumer groups, idempotency by `event_id`); Kafka/NATS later |
| Frontend | TypeScript, Next.js (App Router, file-based routes, which make slots conflict-free), pnpm workspaces | — |
| UI | `frontend/packages/ui` (Tailwind + headless primitives), MapLibre GL for site map, Recharts for charts | design tokens |
| API client | Generated from `contracts/openapi/*.yaml` (e.g., `openapi-typescript`) | — |
| Edge | Python asyncio service; MQTT (Mosquitto) as the simulated device transport; SQLite local buffer | `DeviceAdapter` interface (BLE/UWB later) |
| ML | pandas, scikit-learn (IsolationForest), LightGBM, SHAP; joblib artifacts + model card; MLflow optional | M06 inference interfaces |
| LLM | Anthropic Claude via a `LLMProvider` interface. Default to the latest models (e.g., `claude-sonnet-5` for low-latency turns, `claude-opus-5-5` for complex reasoning). Model IDs live in config, not code. | `LLMProvider` |
| STT / TTS | Adapter interface; browser Web Speech API for the demo, server-side STT/TTS optional | `SpeechProvider` |
| Tests | pytest (+ JSON Schema contract tests), Vitest, Playwright for key demo paths | — |
| Lint/format | ruff + mypy (backend), eslint + prettier + tsc (frontend) | — |
| CI | GitHub Actions: lint, typecheck, tests, contract validation, api-client drift check | — |
| Local run | Docker Compose (`infra/compose/base.yml` + per-module files), `Makefile` wrappers | — |

## Implementation notes (M00, 2026-09-23)

- **Lite mode:** `APP_ENV=lite` runs on SQLite + in-memory event bus + in-memory state store, so the backend and all tests run without Docker. Docker Compose runs the full stack (Postgres/Timescale/pgvector, Redis Streams, MQTT).
- **UI styling:** plain CSS design tokens in `frontend/packages/ui/src/tokens.css` instead of Tailwind (fewer moving parts across teammates' toolchains). Revisit if M02/M03 prefer Tailwind.
- **Versions resolved:** FastAPI 0.14x, Next.js 16, React 19, TypeScript pinned to 5.x (TS 7's native compiler isn't used by Next's type check yet).
- **OpenAPI is generated from code** per module (`scripts/contracts.py export`); CI fails if the committed contract drifts from the code. Event schemas are hand-written JSON Schema and validated at publish time in tests.
- **Task runner:** `scripts/dev.py` (Python) with an optional `Makefile` wrapper, because several teammates are on Windows without make.

## Options considered

| Option | Pros | Cons |
|--------|------|------|
| Python backend (chosen) | Same language as ML and Copilot; strong agent familiarity; FastAPI generates OpenAPI | Lower raw throughput than Go/Node, which is irrelevant at our scale |
| Node/NestJS backend | One language with the frontend | ML and Copilot would need a second runtime anyway |
| Microservices per module | Hard isolation | Too much ops overhead for 3–5 people. Module boundaries + contracts give most of the benefit |
| Kafka from day one | Production-grade | Heavy for dev. The `EventBus` interface lets us switch later |

## Consequences

- Positive: one backend deployable, one language for backend/ML/Copilot, file-based routing avoids nav/route conflicts, and every infra choice sits behind an interface.
- Risks: Redis Streams lacks Kafka's retention and replay semantics, so edge replay deduplicates on `event_id` in the consumer. One Postgres container carries three extensions; if the image is a problem, split into two containers.
- Follow-ups: M00-WP1/WP2 implement the interfaces; revisit at G2 if event volume or latency needs it.
