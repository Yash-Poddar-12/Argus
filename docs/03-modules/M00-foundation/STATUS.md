# M00 — Foundation · STATUS

> **Only the module owner (and their agent) edits this file.** Update it in the same commit as your code, **before every push**.
> Shortcut: `python scripts/status.py log --module M00 --action PUSH --msg "..." [--wp M00-WP1=DONE] [--state IN_PROGRESS]`
> States: `NOT_STARTED` · `IN_PROGRESS` · `MOCKED` (contract + mock shipped) · `BLOCKED` · `IN_REVIEW` · `DONE`
> Spec: [SPEC.md](SPEC.md)

<!-- status:summary (parsed by scripts/status.py; keep the table shape) -->
| Field | Value |
|-------|-------|
| Module | M00 |
| Owner | @unassigned |
| Phase | 0 |
| State | NOT_STARTED |
| Current focus | — |
| Contract version | — |
| Last updated | 2026-09-23 · @team · status file created |
<!-- /status:summary -->

## Work packages

| WP | Title | State | Branch / PR | Notes |
|----|-------|-------|-------------|-------|
| M00-WP1 | Repo skeleton, compose base, Makefile, CI | NOT_STARTED | — | |
| M00-WP2 | Backend core: settings, DB, Alembic branches, EventBus, WS gateway, logging, health, registry | NOT_STARTED | — | |
| M00-WP3 | Auth, RBAC, site scope, master data CRUD + events + seed | NOT_STARTED | — | |
| M00-WP4 | Frontend workspace, UI kit, API client gen, both app shells with pre-registered slots, i18n scaffold, WS hook | NOT_STARTED | — | |
| M00-WP5 | Contracts baseline: common schemas, envelope, per-module OpenAPI skeletons, validation script | NOT_STARTED | — | |

## Using mocks for

| Dependency | Mock source | Switch to real when |
|------------|-------------|---------------------|
| — | — | — |

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
