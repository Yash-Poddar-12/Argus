# Changelog

Notable changes to ARGUS. Newest first. API/event/schema changes also appear in the contract catalogs.

## 2026-09-23: Production repository restructure (ADR-0002)

**Structure**
- 8 meaningful top-level folders (`backend`, `frontend`, `ml`, `contracts`, `infra`, `docs`, `scripts`, `.github`) instead of 17. Removed empty placeholders `edge/`, `knowledge/`, `content/`, `analytics/` (and `ml/` placeholders, now documented in `ml/README.md`).
- Backend is one package, `app`: `core/` (infrastructure), `api/v1/` (thin routes, auto-included), `domain/{platform,tasks,telemetry,environment,twin}/` (capabilities with auto-discovered `wiring.py`), `copilot/tools/`, `iot/simulator/`, `seed/`, `schemas/`.
- Simulator moved from `simulator/` to `backend/app/iot/simulator/` (run: `python -m app.iot.simulator`).
- Frontend: two Next.js apps + two workspace packages merged into one app with `/operator/*` and `/supervisor/*` areas, `features/`, `components/{ui,layout}`, `lib/{api,websocket,i18n}`, `hooks/`.
- Contracts: one generated `contracts/openapi/argus-api.yaml` (replaces 9 per-module files, 7 of them empty); events organized by business area (`contracts/events/{platform,tasks,telemetry,environment,twin}/`).
- Docs: `docs/{product,architecture,development}/`; each workstream's SPEC+STATUS merged into `docs/development/workstreams/MXX-*.md`.
- Infra: root `docker-compose.yml` and `.env.example`; Dockerfiles next to their code; single frontend service on port 3000.

**Compatibility**
- REST API surface **unchanged**: same 45 operations, paths, methods, request/response schema names and status codes (verified by diff against the pre-restructure OpenAPI). WebSocket endpoint, message types and event types unchanged.
- Changed: frontend routes are now `/operator/<page>` and `/supervisor/<page>` on one port (3000); `GET /version` returns `capabilities` (list of names) instead of `modules`; event envelope `source_id` values are capability names (`platform`, `tasks`, `telemetry`, `environment`, `twin`).
- Migrations: existing revisions kept; merge revision `a1b2c3d4e5f6` joins the old per-module branches; `alembic upgrade head` now works (pre-restructure databases verified to upgrade).

**Quality**
- New `backend/tests/test_architecture.py`: layer rules (core ↛ business code, thin routes, Copilot ↛ database, no cross-domain table imports), top-level allow-list, no phase-numbered folders, no empty packages.
- Frontend ESLint (Next core-web-vitals + TypeScript) added; fixed 3 React issues it found (state set in effects → `useSyncExternalStore`, ref written during render).
- CI: backend (lint, contracts, migrations, tests), frontend (API-type drift, lint, typecheck, build), Docker (compose config + image build).

## 2026-09-23: M01 Operational Twin
Task domain + guarded lifecycle, telemetry ingestion, environment, operational twin (Redis projection, intelligence slots, snapshots), Copilot tools, deterministic simulator, G1 vertical slice.

## 2026-09-23: M00 Foundation
Backend core (config, DB, event bus, state store, WebSockets, auth/RBAC, logging, health/metrics), platform master data, contracts tooling, frontend shells, dev tooling, Docker Compose, CI.

## 2026-09-23: Workflow documentation
Multi-IDE agent rules, modular workflow, contracts catalogs, workstream specs, sync protocol.
