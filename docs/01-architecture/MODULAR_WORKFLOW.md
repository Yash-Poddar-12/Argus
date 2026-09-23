# Modular Workflow

> **What this is:** How a team of 3–5 people, each using a different IDE or coding agent (Antigravity, Claude CLI, Codex CLI, or none), builds this platform **in parallel without stepping on each other**.
>
> **Read after:** `AGENTS.md` → `README.md` → `docs/00-project/PRODUCT_PRINCIPLES.md`
> **Read next:** `docs/01-architecture/REPO_STRUCTURE.md` (who owns which folder) → your module's `SPEC.md` → `docs/04-workflow/SYNC_PROTOCOL.md`

---

## 1. The idea in one picture

```text
                    ┌──────────────────────────────────────────┐
  PHASE 0           │  M00  FOUNDATION                         │   everyone contributes,
  (base)            │  repo · infra · backend core · auth ·    │   split into work packages
                    │  frontend shell · event bus · contracts  │   that live in different folders
                    └────────────────────┬─────────────────────┘
                                         │  Gate G0: "one command runs everything"
                    ┌────────────────────▼─────────────────────┐
  PHASE 1           │  M01  OPERATIONAL TWIN (core domain)     │   tasks · assignments · sessions ·
  (base)            │                                          │   simulator · twin state · twin API
                    └────────────────────┬─────────────────────┘
                                         │  Gate G1: contracts v1 FROZEN + vertical slice works
      ┌──────────────┬───────────────────┼───────────────────┬──────────────┐
      ▼              ▼                   ▼                   ▼              ▼
  PHASE 2+     M02 Operator UX     M03 Admin Console    M04 IoT Mesh    M06 Operator ML
  (parallel)   M07 Copilot         M08 Training         M05 Site Intel  M09 Counterfactual
               M10 Federated       M11 Analytics
      │              │                   │                   │              │
      └──────────────┴── talk ONLY through contracts/ + mocks ┴──────────────┘
```

**Two rules make this work:**

1. **Only M00 and M01 are true prerequisites.** Everything after Gate G1 depends on the *contracts* of M00/M01 (and of each other), never on another teammate's unfinished code.
2. **Every folder has exactly one owner.** If two people never edit the same file, they can't get a merge conflict. Shared integration points are handled by *auto-discovery* and *pre-registered slots* (§5) instead of a central file that everyone edits.

---

## 2. Module map

| ID | Module | Phase | Type | Depends on (contracts only) | Produces for |
|----|--------|-------|------|-----------------------------|--------------|
| **M00** | Foundation | 0 | Base | — | everyone |
| **M01** | Operational Twin (core domain) | 1 | Base | M00 | everyone |
| M02 | Operator Experience (operator app) | 2 | Frontend | M00, M01 (+ mocks of M04, M06, M07, M08) | operators |
| M03 | Supervisor/Admin Console (admin app) | 2 | Frontend | M00, M01 (+ mocks of M04, M05, M09) | supervisors |
| M04 | IoT Hazard Mesh (edge + safety events) | 2 | Edge/backend | M00, M01 | M01, M02, M03, M05, M06 |
| M06 | Operator Intelligence / ML (+ WHY? Engine) | 2 | ML/backend | M00, M01 (+ mock of M04) | M02, M07, M08, M09 |
| M05 | Site Operational Intelligence | 3 | Backend | M01, M04 | M03, M06, M09 |
| M07 | Copilot (voice, multilingual, grounded) | 3 | AI/backend | M01, M06 (+ mocks of all tools) | M02 |
| M08 | Training (closed loop) | 3 | Backend | M01, M06 | M02, M03, M11 |
| M09 | Counterfactual Engine | 4 | Backend | M01, M05, M06 | M03, M07 |
| M10 | Federated Intelligence | 4 | ML | M06 | M06 |
| M11 | Analytics & Evaluation | 4* | Research | read-only on all | reports |

\* M11 can start lightweight at any time (metrics definitions, eval harness) because it only reads.

**Phase numbers are start-no-earlier-than hints, not waterfalls.** Because every module can build against mocks, a Phase-3 module can start the day Gate G1 passes if someone is free.

Full specs: `docs/03-modules/MXX-*/SPEC.md`. Live status: `docs/03-modules/MXX-*/STATUS.md`.

---

## 3. Phases and gates

A **gate** is a checkpoint the whole team verifies together (≈30 min call or async checklist). Details and checklists: `docs/04-workflow/INTEGRATION_CHECKPOINTS.md`.

| Phase | Goal | Modules | Exit gate |
|-------|------|---------|-----------|
| **0 — Foundation** | Repo runs with one command; contracts skeleton exists | M00 (split into 5 WPs across the team) | **G0** — `clone → one command → frontend + backend + Postgres + Redis + event bus healthy`; CI green |
| **1 — Operational core** | First vertical slice | M01 (split into 5 WPs) | **G1** — Admin assigns `OP1001 → EXC001 → TASK001`; operator sees it; simulator telemetry updates the twin; operator sees live state. **Contracts v1 frozen.** |
| **2 — Parallel product build** | Product surfaces + safety + ML | M02, M03, M04, M06 | **G2** — Demo scenes 1–5 run end-to-end (login → briefing → task → hazard alert → ETA) with real M04/M06, mocks elsewhere |
| **3 — Intelligence** | Differentiators | M05, M07, M08 | **G3** — Demo scenes 6–10 (root cause, training loop, site bottleneck, copilot answers via tools, multilingual) |
| **4 — Advanced** | Research depth | M09, M10, M11 | **G4** — Scenes 11–12 + evaluation report vs machine-only baseline |

**Hard cut rule** (master §99): if time runs short, drop M10 first, then trim M09 to a single scenario, then shrink M08's catalogue. Never drop the M01 twin, live safety (M04), task prediction (M06), the WHY? Engine, or grounded Copilot answers.

### What people do during Phases 0 and 1 (nobody waits)

M00 and M01 are each split into **work packages (WPs) that live in different folders**, so 3–5 people can build the base together:

| Phase 0 WP | Folder(s) | Suggested owner |
|------------|-----------|-----------------|
| M00-WP1 Repo, compose, CI | `infra/`, `.github/`, root config | Person A |
| M00-WP2 Backend core (config, DB, event bus, logging, health, WS gateway, module discovery) | `backend/core/` | Person A |
| M00-WP3 Auth, RBAC, master data (users/operators/machines/sites) | `backend/modules/m00_platform/` | Person C |
| M00-WP4 Frontend shell, UI kit, API client generation, both app shells with **pre-registered slots** | `frontend/packages/`, `frontend/apps/*/` (shell only) | Person B |
| M00-WP5 Contracts baseline (common schemas, event envelope, OpenAPI skeleton per module) | `contracts/` | Person D/E (or A) |

| Phase 1 WP | Folder(s) | Suggested owner |
|------------|-----------|-----------------|
| M01-WP0 Contracts v1 draft: twin schema, APIs, events, tools, `public.py` + mocks (**day 1**, unblocks everyone) | `contracts/…m01…`, `m01_twin/public.py` | Person A |
| M01-WP1 Task / Assignment / TaskSession / pre-check domain + APIs | `backend/modules/m01_twin/tasks/` | Person A |
| M01-WP2 Simulator core (deterministic, seeded) | `simulator/core/` | Person D |
| M01-WP3 Twin state, context fusion, Redis projection | `backend/modules/m01_twin/twin/` | Person A |
| M01-WP4 Twin query API + WebSocket channels | `backend/modules/m01_twin/api/` | Person C |
| M01-WP5 Environment/weather adapter (mock-first) | `backend/modules/m01_twin/environment/` | Person E (or B) |
| M01-WP6 G1 vertical-slice end-to-end test + seed tasks | `backend/tests/m01_twin/` | Integration lead |

Meanwhile, **Phase 2 owners start early on their own folders using mocks** (clickable operator UI with fixture data, ML notebooks on simulator output, edge proximity math with unit tests). This is safe because it only touches their own paths.

---

## 4. The parallel-work contract (the 8 rules)

These are mandatory for humans and agents alike.

1. **One owner per path.** `docs/01-architecture/REPO_STRUCTURE.md` maps every folder to a module; `docs/00-project/TEAM_AND_OWNERSHIP.md` maps modules to people. Only edit files your module owns.
2. **Talk through contracts, not code.** Cross-module communication happens only via `contracts/` (OpenAPI, event JSON Schemas, Copilot tool schemas, ML IO schemas) and each module's `public.py` facade. Never import another module's internal package. Allowed imports: `backend/core/*`, `backend/modules/<other>/public.py`, generated clients, and `contracts/`.
3. **Mock-first (WP0).** Every module's first work package is **WP0: contract + `public.py` + mocks** of its outputs (plus `contracts/**/examples/`), shipped **before** real logic. Consumers build against the mock; the real implementation is swapped in behind the same contract (`MXX_USE_MOCK=false`).
4. **One writer per table / event stream.** `docs/02-contracts/DATA_OWNERSHIP.md` and `EVENT_CATALOG.md`. Others read via API, events, or read models.
5. **Additive by default.** Adding optional fields/endpoints/events = minor bump, no approval needed beyond a normal PR. Renaming, removing, or changing meaning = **breaking** → follow the change process in `docs/02-contracts/CONTRACTS_GUIDE.md` (new version side-by-side, notify consumers, deprecate).
6. **Register by discovery, not by editing central files.** See §5.
7. **Mark status on every push and pull.** See §6 and `docs/04-workflow/SYNC_PROTOCOL.md`.
8. **Safety-critical logic is deterministic and lives in M04.** No LLM (M07) or ML model (M06) may be the sole decider of a safety alert. (Master P4, P10.)

---

## 5. Conflict hotspots and how we defuse them

Merge conflicts come from a small number of shared files. Each has a designed-in solution:

| Hotspot | Why it conflicts | Solution |
|---------|------------------|----------|
| Backend router / app factory | Everyone adds their router | `backend/core/registry.py` **auto-discovers** `backend/modules/*/module.py` (each exposes `router`, `event_handlers`, `ws_channels`, `startup`). Adding a module never edits core. |
| DB migrations | Linear revision chains collide | One Alembic **branch per module** (`branch_labels=("m04_safety",)`, `version_locations` = `backend/migrations/<module>/`). Run `alembic upgrade heads`. Never touch another module's tables. |
| Frontend routes & nav menu | Everyone adds pages/menu items | M00-WP4 **pre-registers a slot** (folder + placeholder page + nav entry) for every known feature on day one. Later work only fills your own slot folder. New slots = small PR to the app owner. |
| `docker-compose` | Everyone adds services | `infra/compose/base.yml` (M00) + `infra/compose/<module>.yml` per module, combined with `-f` or `include:`. |
| `.env.example` | Everyone adds variables | `infra/env/<module>.env.example` per module; M00's loader merges them. Prefix variables with the module (`M07_LLM_MODEL`). |
| Lockfiles (`uv.lock`, `pnpm-lock.yaml`) | Any dependency change rewrites them | Never hand-merge. On conflict: take `develop`'s version, then re-run `uv lock` / `pnpm install` and commit. Declare deps in your module's section/package where the tool supports it. |
| Shared types / API client | Hand edits drift | `frontend/packages/api-client` is **generated** from `contracts/openapi/*.yaml` by CI/script. Nobody hand-edits it. |
| Status tracking | One big status table = constant conflicts | Status lives in **your module's** `STATUS.md`; pull acknowledgements live in **your own** sync log file. The board is computed, not edited (`python scripts/status.py board`). |
| Copilot tool registry | Tool implementers and M07 both edit | Tool **schemas** live in `contracts/tools/<tool>.json` owned by the module that owns the underlying data; M07 owns the loader and orchestration only. |

If you find a new hotspot, raise it in your STATUS.md "Blockers" section and propose a discovery/slot pattern for it.

---

## 6. Status and sync (summary)

Full protocol: `docs/04-workflow/SYNC_PROTOCOL.md`.

```text
BEFORE every push                         AFTER every pull
─────────────────                         ────────────────
1. Update your module STATUS.md:          1. See what changed in shared areas:
   - WP states                               python scripts/status.py changes
   - "Last updated" line                  2. If a contract you consume changed,
   - append one line to Update log           read it and adapt (or note a blocker)
2. Commit it WITH the code                3. Append a PULL line to YOUR sync log
3. Push                                      docs/05-status/sync-log/<handle>.md
                                             (committed with your next push)
```

Helper: `python scripts/status.py log --module M02 --action PUSH --msg "..."` appends the line and bumps the date for you.

---

## 7. How a module is structured internally

Every backend module follows the same shape so any agent can navigate any module:

```text
backend/modules/mXX_name/
├── module.py          # discovery entry: router, event_handlers, ws_channels, startup
├── public.py          # the ONLY importable surface: DTOs + Protocols + get_x() (real or mock)
├── api/               # FastAPI routers (thin)
├── domain/            # pure logic, no I/O — most unit tests target this
├── adapters/          # DB repos, event publishers, external services
├── mocks/             # mock implementations of THIS module's outputs
└── README.md          # optional, 10 lines: what lives where
backend/migrations/mXX_name/   # this module's Alembic branch
backend/tests/mXX_name/        # unit + contract + integration tests
```

Frontend feature slots follow:

```text
frontend/apps/<app>/src/app/<route>/        # route (Next.js App Router folder)
frontend/apps/<app>/src/features/<feature>/ # components, hooks, state, mocks
```

---

## 8. Refinement: modules are meant to change

Modules and work packages are **starting boundaries, not permanent walls**. To refine:

| Change | Who decides | How |
|--------|-------------|-----|
| Add/split/merge WPs inside a module | Module owner | Edit your `SPEC.md` + `STATUS.md` |
| Move a responsibility between modules | Both owners | ADR in `docs/01-architecture/adr/`, update both SPECs, `REPO_STRUCTURE.md`, and ownership tables |
| New module | Team | ADR + new `docs/03-modules/MXX-*/` folder from the template + slot/discovery registration |
| Reassign a module to another person | Team | Edit `TEAM_AND_OWNERSHIP.md` and `.github/CODEOWNERS` |
| Change product intent | Team | Update `MASTER_PROJECT_CONTEXT_AND_EXECUTION_PLAN.md` + change log §115 |

---

## 9. Precedence (when docs disagree)

The product principles (`docs/00-project/PRODUCT_PRINCIPLES.md`, master §2) always apply; nothing below overrides them. For everything else:

1. `contracts/**` — exact shapes (machine-readable wins over prose)
2. `docs/03-modules/MXX-*/SPEC.md` — module scope and behavior
3. `docs/02-contracts/*.md` — ownership catalogs
4. This file + `REPO_STRUCTURE.md` — process and boundaries
5. `MASTER_PROJECT_CONTEXT_AND_EXECUTION_PLAN.md` — product intent and vision

If a lower item contradicts a higher one, the higher one wins **and** whoever notices fixes the lower doc (or raises it) in the same PR.
