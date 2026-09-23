# M10 — Federated Fleet Intelligence

| Field | Value |
|-------|-------|
| Phase | 4 (**first to cut** under the hard-cut rule) |
| Type | ML research/prototype (`ml/federated/`) |
| Depends on (contracts) | M06 (model interfaces, registry) |
| Consumed by | M06 (receives global model versions), M11 |
| Gate | G4 (scene 12) |

## Objective

Show how site-level models (e.g., task-time, hazard risk) can improve across sites using **model updates instead of raw operational logs**, with an honest threat model and stated privacy limits.

## Scope

- Partition simulator data into ≥ 3 synthetic sites with different conditions (terrain, weather, machine age)
- Local training client per site (framework option: Flower, or a minimal custom FedAvg)
- Central aggregator (FedAvg; optionally FedProx)
- Global model versions published **through M06's model registry** (M10 never writes M06 tables directly)
- Evaluation: local-only vs federated vs centralized (upper bound) per site
- Documentation: threat model, secure-aggregation assumptions, update leakage risk, poisoning considerations, what is **not** protected

## Out of scope

Production privacy guarantees (don't fake them; master §71), differential privacy (future), real multi-site deployment.

## Where the code lives

`ml/federated/`.

Folders are created only when real code lands. Ownership rules and the full map: `docs/architecture/REPOSITORY_STRUCTURE.md`.

## Work package plan

| WP | Title | Est. |
|----|-------|------|
| M10-WP0 | Design note + threat model + contract for federated model metadata | 1 d |
| M10-WP1 | Multi-site data partitioning from simulator | 1 d |
| M10-WP2 | Local client + aggregator (FedAvg) | 2 d |
| M10-WP3 | Publish to M06 registry + `federated.model.published` | 1 d |
| M10-WP4 | Evaluation: local vs federated vs centralized | 1–2 d |
| M10-WP5 | Privacy limits write-up (feeds research report) | 1 d |

## Acceptance criteria

- [ ] No raw rows leave a site partition during a federated round (verified by the code path and a test)
- [ ] Federated model beats local-only on at least one data-poor site, reported with metrics
- [ ] Threat model and limitations documented in plain language

## Known constraints

Only start after the core product works convincingly (master §97).

---

# Status

> **Only the workstream owner (and their agent) edits this file.** Update it in the same commit as your code, **before every push**.
> Shortcut: `python scripts/status.py log --module M10 --action PUSH --msg "..." [--wp M10-WP1=DONE] [--state IN_PROGRESS]`
> States: `NOT_STARTED` · `IN_PROGRESS` · `MOCKED` (contract + mock shipped) · `BLOCKED` · `IN_REVIEW` · `DONE`

<!-- status:summary (parsed by scripts/status.py; keep the table shape) -->
| Field | Value |
|-------|-------|
| Module | M10 |
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
| M10-WP0 | Design note + threat model + contract for federated model metadata | NOT_STARTED | — | |
| M10-WP1 | Multi-site data partitioning from simulator | NOT_STARTED | — | |
| M10-WP2 | Local client + aggregator (FedAvg) | NOT_STARTED | — | |
| M10-WP3 | Publish to M06 registry + `federated.model.published` | NOT_STARTED | — | |
| M10-WP4 | Evaluation: local vs federated vs centralized | NOT_STARTED | — | |
| M10-WP5 | Privacy limits write-up (feeds research report) | NOT_STARTED | — | |

## Using mocks for

| Dependency | Mock source | Switch to real when |
|------------|-------------|---------------------|
| M06 registry | `m06_ml.public` mock | M06-WP8 LIVE |

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
