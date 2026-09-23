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

## Owned paths

`ml/federated/`, `contracts/ml/federated/`, `contracts/events/m10/`, `backend/migrations/m10_federated/` (metadata tables, if needed), `backend/tests/m10_federated/`.

## Work packages

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
