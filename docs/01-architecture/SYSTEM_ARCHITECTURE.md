# System Architecture

> Condensed, implementation-oriented view of master §27–§39, §59, §78–§81, with each component mapped to its owning module. For vision and rationale, see the master file.

## 1. Layered view (with owners)

```text
┌─────────────────────────────── EXPERIENCE ────────────────────────────────┐
│  Operator app (M02)                         Admin console (M03)           │
│   My Day · Machine · Tasks · Safety ·        CRUD · Assignments · Tasks · │
│   Performance · [Training slot M08] ·        Site map · [Site-intel M05] ·│
│   [Copilot slot M07]                         [Scenarios M09] · Config     │
└───────────────┬──────────────────────── REST + WebSocket ──────┬──────────┘
                │                                                 │
┌───────────────▼─────────────── BACKEND (one FastAPI app, modules auto-discovered) ───────┐
│ core (M00): auth · RBAC/site scope · event bus · WS gateway · logging · health · registry │
│                                                                                           │
│ m00_platform  users/operators/machines/sites                                              │
│ m01_twin      tasks · assignments · sessions · pre-checks · context fusion · twin API     │
│ m04_safety    cloud-side safety/hazard events, acknowledgements, safety rule config       │
│ m05_site_intel interaction graph · queues · bottlenecks · utilization · recommendations   │
│ m06_ml        feature assembly · anomaly · risk · task-time · skill · WHY? engine         │
│ m07_copilot   intent · tool orchestration · RAG · LLM · STT/TTS · language · proactive    │
│ m08_training  catalogue · sessions · assessments · triggers · recommendations · impact    │
│ m09_scenarios scenario builder · modified twin · model calls · safety check · compare     │
│ m11_analytics KPIs · model metrics · experiment results                                   │
└──────┬───────────────────────────┬──────────────────────────────┬────────────────────────┘
       │                           │                              │
┌──────▼──────┐   ┌────────────────▼───────────────┐   ┌──────────▼─────────┐
│ PostgreSQL  │   │ Event fabric (M00 abstraction) │   │ Redis (M00 infra)  │
│ + Timescale │   │ Redis Streams (MVP) → Kafka/   │   │ live twin state,   │
│ + pgvector  │   │ NATS later, same interface     │   │ cache, WS fan-out  │
└─────────────┘   └────────────────▲───────────────┘   └────────────────────┘
                                   │ events (deduplicated by event_id)
┌──────────────────────────── EDGE / SITE (M04) ───────────────────────────────┐
│ device adapters (BLE/UWB/MQTT sim) → proximity engine → zone logic →         │
│ LOCAL SAFETY RULES → local alert (no cloud round-trip)                        │
│                    └→ local buffer → replay to cloud when connected          │
└──────────────────────────────────▲───────────────────────────────────────────┘
                                   │
                 Simulator (M01 core + per-module scenarios), deterministic seed
                                   │
┌──────────────────────────── OFFLINE / ML (M06, M10, M11) ─────────────────────┐
│ ml/ pipelines: features → train → evaluate → model artifact + model card     │
│ ml/federated: local clients → aggregator → versioned global model            │
│ analytics/: evaluation harness, baseline vs contextual comparisons           │
└───────────────────────────────────────────────────────────────────────────────┘
```

**Why one backend app with modules instead of microservices?** A 3–5 person team moves faster with one deployable and strict module boundaries. Auto-discovery plus contract-only imports keep us microservice-ready (P12): any module can be split out later behind the same OpenAPI and event contracts. The edge (M04) is the exception: it's a separate process because it must run without the cloud (P10).

## 2. Communication patterns

| Pattern | Use for | Example |
|---------|---------|---------|
| REST (sync) | CRUD, queries, commands from UI | `POST /api/v1/tasks/{id}/start` |
| WebSocket (push) | Live updates to UI | `/ws/operators/{operator_id}` → `SAFETY_ALERT`, `TASK_ETA_UPDATED` |
| Events (async) | Module-to-module reactions | `operator.task.assigned` → twin update → prediction → briefing |
| In-process facade call | Low-latency calls inside the backend (e.g., model inference) | `from backend.modules.m06_ml.public import get_task_time_predictor` → `predict_task_duration(ctx) -> TaskPrediction` |
| Tool call | Copilot fact retrieval | `get_current_machine_state()` → M01 facade or API |

**Rule:** a module never imports another module's internals. The only importable surface of a module is its **`public.py` facade**, which contains only:
- Pydantic DTOs that mirror `contracts/` schemas,
- `Protocol` interfaces,
- accessor functions (`get_x()`) that return the real implementation, or the **mock** when `MXX_USE_MOCK=true` or the real one isn't ready.

Each module publishes its `public.py` with mocks as its **WP0**, so consumers are never blocked.

## 3. Key flows

### 3.1 Assignment → operator (Gate G1 vertical slice)

```text
Admin UI (M03) ─POST /assignments─► m01_twin ─persist─► emits operator.task.assigned
     ─► m01_twin twin projection updated ─► WS /ws/operators/OP1001: TASK_UPDATE
     ─► m06_ml consumes → TaskPrediction → emits prediction.task_time.updated
     ─► m01_twin attaches ETA to twin ─► WS: TASK_ETA_UPDATED ─► Operator UI (M02)
```

### 3.2 Hazard (edge-first)

```text
Simulator/devices ─► edge (M04) proximity engine ─► local rule fires ─► local alert (≤ 200 ms target)
                                                  └► hazard.proximity.detected ─► cloud m04_safety
     ─► persisted ─► m01_twin updates risk context ─► WS SAFETY_ALERT ─► Operator UI
     ─► m06 (risk evidence), m05 (interaction stats), m08 (training triggers) consume
```

### 3.3 Copilot question

```text
Operator voice ─► M02 copilot slot ─► POST /copilot/voice ─► STT ─► language detect ─► intent
   ─► tool selection ─► tools (M01 twin, M06 predict/explain, M04 alerts, M05 site) ─► structured results
   ─► LLM explanation (grounded, cites tool results) ─► translate ─► text + TTS ─► UI
```

### 3.4 Training loop

```text
m06 behavior profile / m04 safety events ─► m08 trigger evaluation ─► training.recommended
   ─► Operator completes module + assessment ─► training.completed
   ─► m08 impact job compares before/after windows ─► training.impact.measured ─► M02 / M03 / M11
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
