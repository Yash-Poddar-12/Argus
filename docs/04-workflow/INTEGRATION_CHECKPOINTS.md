# Integration Checkpoints (Gates G0–G4)

> A **gate** is where parallel work is proven to fit together. The integration lead (default: M00/M01 owner) runs it. It can be a short call or an async checklist in a PR. Passing a gate = merge `develop` → `main` + tag `gN`.

## Between gates

- **Daily (async):** everyone pushes STATUS updates; everyone runs `status.py changes` after pulling.
- **Twice a week (15 min):** `python scripts/status.py board`, blockers only, contract changes only.
- **Integration Friday (or equivalent):** each module flips at least one mock → real where the dependency is LIVE, and runs the demo path so far.

## G0 — Foundation ready (end of Phase 0)

- [ ] Every teammate: fresh clone → `make up` → healthy on their own machine/OS
- [ ] Module auto-discovery proven (a dummy module adds a route with zero core edits)
- [ ] Multi-branch Alembic proven (two modules' migrations apply with `upgrade heads`)
- [ ] Auth works for `OP1001` (operator) and `SUP001` (supervisor), with site scope enforced
- [ ] Both frontend shells render all pre-registered slots
- [ ] `make contracts` validates and regenerates the client; CI green on `develop`
- [ ] Target folder skeleton + per-module compose/env stubs exist
- [ ] `TEAM_AND_OWNERSHIP.md` filled in; CODEOWNERS active; ADR-0001 ACCEPTED (or amended)
- [ ] Every module's STATUS.md has an owner

## G1 — Operational core + contract freeze (end of Phase 1)

**The first true vertical slice (master §94):**

```text
Admin assigns OP1001 → EXC001 → TASK001 → operator sees assignment
→ simulator sends telemetry → twin updates → operator sees current state
```

- [ ] The slice above runs from the real admin UI shell to the real operator UI shell (screens can be rough)
- [ ] M01 acceptance criteria all ticked
- [ ] **M00 + M01 contracts tagged v1 and frozen**
- [ ] Every Phase-2 module has shipped **WP0** (contract + `public.py` + mocks) or has a date for it
- [ ] Simulator S1 is deterministic across machines (same seed → same output)

## G2 — Parallel product build (end of Phase 2) · Demo scenes 1–5

| Scene | Needs LIVE | May still be mocked |
|-------|-----------|---------------------|
| 1 Morning: login, machine, tasks, briefing, ETAs | M00, M01, M02 | M06 (ETA), M08 (focus) |
| 2 Pre-check passes | M01, M02 | — |
| 3 Live operation, telemetry | M01, M02 | — |
| 4 Hazard: worker enters proximity → edge alert → operator notified | **M04**, M02 | — |
| 5 Delay: ETA changes (Copilot explanation comes in G3) | **M06**, M01, M02 | M07 |

- [ ] Admin console: CRUD, tasks, assignments, site map with layers (M03)
- [ ] Offline edge test passes (M04)
- [ ] Task-time predictions with confidence + contributors from the real model (M06)

## G3 — Intelligence (end of Phase 3) · Demo scenes 6–10

| Scene | Needs LIVE |
|-------|-----------|
| 6 Root cause: delay is site-driven, not operator-driven | M06 WHY?, M05 evidence |
| 7 Repeated idle → training recommended | M06 anomaly/profile, M08 triggers |
| 8 Operator completes micro-learning (+ voice/multilingual Copilot moments) | M08, M07, M02 slots |
| 9 Impact: next tasks show improvement | M08 impact |
| 10 Supervisor sees interaction graph + bottleneck | M05, M03 site-intel slot |

- [ ] Copilot answers "Why is my task running late?" via tools only (M07 acceptance)
- [ ] Hindi and Tamil paths demoed end to end

## G4 — Advanced (end of Phase 4) · Demo scenes 11–12 + evaluation

| Scene | Needs LIVE |
|-------|-----------|
| 11 "What if I move Dumper D2?" | M09, M03 scenarios slot (+ M07 tool) |
| 12 Federated fleet learning story | M10 (or cut: narrated with architecture slide) |

- [ ] Evaluation report with baseline vs contextual comparisons (M11)
- [ ] Master §113 success criteria walkthrough, each item ticked or explicitly cut
- [ ] Full demo rehearsal from a clean `make up` + seed + scripted simulator run

## Hard-cut order if time runs short (master §99)

1. Drop M10 (narrate it instead)
2. Shrink M09 to the single D2 scenario
3. Shrink the M08 catalogue to 2 modules (Idle Management, Safe Operation)
4. Reduce M11 to RQ1/RQ2 tables
5. Never cut: twin, operator UX, live safety, task prediction, WHY?, grounded Copilot, one training loop, one site-interaction scenario
