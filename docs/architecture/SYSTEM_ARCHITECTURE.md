# System Architecture

> Implementation view of master §27–§39, §59, §78–§81. Where each piece lives in the repo: `REPOSITORY_STRUCTURE.md`. Built today: platform, tasks, telemetry, environment, twin, Copilot tools, simulator. Everything marked *(planned)* is a future capability package.

## 1. Layered view

```text
┌──────────────────────────────── FRONTEND (one Next.js app) ─────────────────────────────────┐
│  /operator  My Day · Machine · Tasks · Safety · Performance · Training · Copilot             │
│  /supervisor Overview · Operators · Machines · Sites · Tasks · Assignments · Site map ·       │
│              Safety · Site intelligence · Scenarios · Training admin · Analytics             │
└───────────────┬────────────────────────── REST + WebSocket ──────────────────┬──────────────┘
                │                                                              │
┌───────────────▼──────────── BACKEND (one FastAPI app: backend/app) ──────────────────────────┐
│ api/v1       thin routes (auto-included)                                                     │
│ core         auth · RBAC/site scope · event bus · state store · WS gateway · logging · health│
│ domain/      platform (users, sites, zones, operators, machines)                             │
│              tasks (tasks, assignments, sessions, pre-checks, lifecycle)                     │
│              telemetry (idempotent ingestion, history) · environment (conditions)            │
│              twin (context fusion, Redis projection, intelligence slots, snapshots)          │
│              safety · operations · training                                   (planned)      │
│ intelligence anomaly · risk · task-time · skill · WHY? engine · counterfactual  (planned)    │
│ copilot      tool registry + tools over domain services · agent · RAG · voice   (tools built)│
│ iot          simulator (built) · device adapters · proximity · zone rules      (planned)    │
└──────┬───────────────────────────┬──────────────────────────────┬────────────────────────────┘
       │                           │                              │
┌──────▼──────┐   ┌────────────────▼───────────────┐   ┌──────────▼─────────┐
│ PostgreSQL  │   │ Event bus (core abstraction)   │   │ Redis              │
│ + Timescale │   │ Redis Streams (MVP) → Kafka/   │   │ live twin state,   │
│ + pgvector  │   │ NATS later, same interface     │   │ cache              │
└─────────────┘   └────────────────▲───────────────┘   └────────────────────┘
                                   │ events (deduplicated by event_id)
┌──────────────────────── EDGE / SITE (IoT; own runtime `edge/` once deployable) ─────────────┐
│ device adapters (BLE/UWB/MQTT) → proximity engine → zone logic →                             │
│ LOCAL SAFETY RULES → local alert (no cloud round-trip) · local buffer → replay to cloud      │
└──────────────────────────────────▲───────────────────────────────────────────────────────────┘
                                   │
              Simulator (backend/app/iot/simulator): deterministic, seeded scenarios
                                   │
┌──────────────────────────────── ml/ (offline) ────────────────────────────────────────────────┐
│ features → train → evaluate → model artifact + model card · federated prototype · evaluation │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Why one backend app instead of microservices?** A 3–5 person team moves faster with one deployable and strict internal boundaries (capability packages, contracts, architecture tests). Capabilities can still be split out later behind the same OpenAPI and event contracts (P12). The edge gateway is the exception: it must keep working without the cloud (P10), so it becomes its own runtime (`edge/`) when implemented.

## 2. Communication patterns

| Pattern | Use for | Example |
|---------|---------|---------|
| REST (sync) | CRUD, queries, commands from UI | `POST /api/v1/tasks/{id}/start` |
| WebSocket (push) | Live updates to UI | `/ws/operators/{operator_id}` → `SAFETY_ALERT`, `TASK_ETA_UPDATED` |
| Events (async) | Capability-to-capability reactions | `operator.task.assigned` → twin update → prediction → briefing |
| In-process service call | Reads/commands across capabilities inside the backend | `from app.domain.platform import service as platform` → `await platform.get_machine(...)` |
| Intelligence interface | Model inference behind a stable interface *(planned)* | `app.intelligence.task_time.predict_task_duration(ctx) -> TaskPrediction` (ML adapter or mock) |
| Tool call | Copilot fact retrieval | `get_current_machine_state()` → twin service |

**Rule:** a capability is used only through its `service.py` functions and `schemas.py` types (or REST/events), never through its tables. `backend/tests/test_architecture.py` enforces it.

## 3. Key flows

### 3.1 Assignment → operator (Gate G1 vertical slice)

```text
Supervisor UI ─POST /assignments─► domain/tasks ─persist─► emits operator.task.assigned
     ─► domain/twin projection updated ─► WS /ws/operators/OP1001: TASK_UPDATE
     ─► intelligence (task-time) consumes → TaskPrediction → emits prediction.task_time.updated
     ─► domain/twin attaches ETA to twin ─► WS: TASK_ETA_UPDATED ─► Operator UI
```

### 3.2 Hazard (edge-first)

```text
Simulator/devices ─► edge (M04) proximity engine ─► local rule fires ─► local alert (≤ 200 ms target)
                                                  └► hazard.proximity.detected ─► cloud domain/safety
     ─► persisted ─► domain/twin updates risk context ─► WS SAFETY_ALERT ─► Operator UI
     ─► m06 (risk evidence), m05 (interaction stats), m08 (training triggers) consume
```

### 3.3 Copilot question

```text
Operator voice ─► operator Copilot view ─► POST /copilot/voice ─► STT ─► language detect ─► intent
   ─► tool selection ─► tools (twin, predictions/explanations, safety alerts, site intelligence) ─► structured results
   ─► LLM explanation (grounded, cites tool results) ─► translate ─► text + TTS ─► UI
```

### 3.4 Training loop

```text
m06 behavior profile / m04 safety events ─► m08 trigger evaluation ─► training.recommended
   ─► Operator completes module + assessment ─► training.completed
   ─► domain/training impact job compares before/after windows ─► training.impact.measured ─► M02 / M03 / M11
```

## 4. Storage (single writer per store, see DATA_OWNERSHIP.md)

| Store | Holds | Notes |
|-------|-------|-------|
| PostgreSQL | Transactional entities | One Alembic branch per module |
| TimescaleDB hypertables | Telemetry, operator/environment/hazard events, state changes | Partition by time (+ machine_id) |
| Redis | Current twin state, active task state, live risk, WS fan-out, cache | Rebuildable from events and DB |
| pgvector | RAG embeddings (M07) | Can move to a dedicated vector DB behind an interface |
| Object storage (local: MinIO or filesystem) | Model artifacts, training media, datasets, reports | Path prefix per module |
| Edge local store (SQLite) | Event buffer, local rules, device state | M04 only |

## 5. Edge vs cloud responsibilities

| Edge (M04) | Cloud (backend) |
|------------|-----------------|
| Device ingestion, protocol adapters | Historical analytics, fleet learning |
| Proximity calculations, zone logic | ML training, task prediction at scale |
| **Safety rules and local alerts** | RAG/LLM, Copilot |
| Local ML where latency matters | Reporting, federated aggregation |
| Buffering, offline operation, event replay | Centralized configuration (pushed to edge) |

Offline: cloud unavailable → edge keeps doing safety → buffer → reconnect → replay → deduplicate by `event_id` → cloud catches up.

## 6. Cross-cutting (all owned by M00, used by all)

- **Auth:** OIDC-ready JWT; roles `OPERATOR`, `SUPERVISOR_ADMIN`; permissions + site scope (Identity → Role → Permissions → Site scope → Resource). Don't hard-code role-name checks in modules. Use `require_permission("tasks:assign")`.
- **Observability:** every service exposes `/health`, `/ready`, `/version`, `/metrics`. Structured logs carry `request_id`, `trace_id`, `site_id`, `event_id`, plus `operator_id`, `machine_id`, `model_version` where relevant. No secrets or unnecessary PII.
- **Errors:** one error envelope (`contracts/schemas/common/error.json`).
- **Security:** TLS, encrypted secrets, audit log for admin writes, device identity + mTLS for edge (post-MVP). A frontend or API compromise must not be able to bypass edge safety rules.
