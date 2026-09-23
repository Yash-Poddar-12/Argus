# M00 — Foundation · STATUS

> **Only the module owner (and their agent) edits this file.** Update it in the same commit as your code, **before every push**.
> Shortcut: `python scripts/status.py log --module M00 --action PUSH --msg "..." [--wp M00-WP1=DONE] [--state IN_PROGRESS]`
> States: `NOT_STARTED` · `IN_PROGRESS` · `MOCKED` (contract + mock shipped) · `BLOCKED` · `IN_REVIEW` · `DONE`
> Spec: [SPEC.md](SPEC.md)

<!-- status:summary (parsed by scripts/status.py; keep the table shape) -->
| Field | Value |
|-------|-------|
| Module | M00 |
| Owner | @Developer-Devanshhh |
| Phase | 0 |
| State | IN_REVIEW |
| Current focus | G0 verification (Docker stack) |
| Contract version | m00-platform 1.0.0 (generated) · events v1 |
| Last updated | 2026-09-23 · @Developer-Devanshhh · core fixes found while building M01: nested-router path coll |
<!-- /status:summary -->

## Work packages

| WP | Title | State | Branch / PR | Notes |
|----|-------|-------|-------------|-------|
| M00-WP1 | Repo skeleton, compose base, Makefile, CI | IN_REVIEW | — | |
| M00-WP2 | Backend core: settings, DB, Alembic branches, EventBus, WS gateway, logging, health, registry | IN_REVIEW | — | |
| M00-WP3 | Auth, RBAC, site scope, master data CRUD + events + seed | IN_REVIEW | — | |
| M00-WP4 | Frontend workspace, UI kit, API client gen, both app shells with pre-registered slots, i18n scaffold, WS hook | IN_REVIEW | — | |
| M00-WP5 | Contracts baseline: common schemas, envelope, per-module OpenAPI skeletons, validation script | IN_REVIEW | — | |

## Using mocks for

| Dependency | Mock source | Switch to real when |
|------------|-------------|---------------------|
| — | — | — |

## Blockers

- none

## Verification notes

- Verified locally (Windows, no Docker): 17 backend tests (auth/RBAC/site scope, CRUD + contract-validated events, in-memory + Redis Streams bus (fakeredis), module auto-discovery, WS auth, Alembic heads == models, contracts check + OpenAPI drift), lite-mode server smoke test, `next build` of both apps, typecheck of all packages.
- **Not yet verified:** `python scripts/dev.py up` (Docker Compose stack: Timescale image, Redis, MQTT, containers). Needs a teammate with Docker for the G0 checklist.
- G0 items still open: every teammate runs the stack; branch protection + CODEOWNERS; ADR-0001 → ACCEPTED.

## Contract changes (pending / recent)

- none

## Open questions

- none

## Update log

<!-- newest first · one line per push: date · @handle · ACTION · branch · summary -->
<!-- log:insert -->
- 2026-09-23 · @Developer-Devanshhh · PUSH · feature/m01-operational-twin · core fixes found while building M01: nested-router path collection (FastAPI 0.14x), RedisStateStore.keys bug, seed_all discovery, generated contract documents in scripts/contracts.py
- 2026-09-23 · @Developer-Devanshhh · PUSH · feature/m00-foundation · M00 implemented: core (config, db, event bus memory+Redis Streams, state, WS gateway, auth/RBAC, registry, errors, logging, health/metrics), m00_platform CRUD+events+seed, Alembic branches, contracts baseline + tooling, frontend workspace + both app shells with slots, dev.py, compose, CI
- 2026-09-23 · @team · INIT · docs scaffold · Status file created from SPEC work packages
