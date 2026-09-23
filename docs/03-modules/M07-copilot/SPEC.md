# M07 — Copilot (voice · multilingual · tool-grounded)

| Field | Value |
|-------|-------|
| Phase | 3 (orchestration can start on mock tools right after G1) |
| Type | AI backend module (+ operator copilot slot) |
| Depends on (contracts) | M01, M04, M05, M06, M08, M09 tools (all mockable) |
| Consumed by | M02 |
| Gate | G3 (scenes 5 "why is my task late", 8 multilingual/voice) |

## Objective

The operator's **single point of contact for the shift**: voice, tap, cards, and proactive messages. Every operational fact comes from an authoritative tool. The LLM only explains, translates, and summarizes.

## Scope

- Pipeline: input (text/voice) → STT → language detection → intent → **tool selection** → tool calls → structured results → LLM explanation (grounded) → language adaptation → text + TTS
- `LLMProvider`, `SpeechProvider`, `Translator` interfaces (model IDs in config; see ADR-0001)
- **Tool registry** loader (`contracts/tools/_registry.json`), per-tool permissions (operator: self only), timeouts, and fallbacks when a tool fails ("I can't get that right now", never a guess)
- **Grounding guard:** every number/state in an answer must appear in a tool result from this turn. If not, regenerate or answer without it. Tool trace is returned to the UI as "sources"
- Conversation context (short-term, Redis) + persistence
- RAG over approved docs only (`knowledge/`: manuals, safety procedures, site procedures, FAQs) with the `search_knowledge` tool, pgvector, and citations
- **Proactive copilot:** consumes events (safety, hazard, ETA slip, anomaly, training recommended, dependency delay) → **notification policy** (priority CRITICAL/HIGH/MEDIUM/INFO, dedupe, cooldowns, quiet rules) → `COPILOT_PROACTIVE_MESSAGE`
- Multilingual: en, hi, ta initially; language is an interaction layer only (message keys + adapter), and business logic stays language-neutral
- Copilot slot UI in the operator app if held (see M02-SLOT-C)

## Out of scope

Safety decisions. CRITICAL safety alerts are delivered by M04 regardless of the Copilot; the Copilot may **echo** them, never gate them. Also out: computing predictions (M06) and owning tool data (other modules).

## Owned paths

`backend/modules/m07_copilot/`, `backend/migrations/m07_copilot/`, `backend/tests/m07_copilot/`, `knowledge/`, `contracts/openapi/m07-copilot.yaml`, `contracts/events/m07/`, `contracts/tools/_registry.json`, `contracts/tools/search_knowledge.json`; slot `frontend/apps/operator/src/{app,features}/copilot/` if held.

## Interfaces

APIs in `API_CATALOG.md` § M07; events `copilot.*`; tables `copilot_conversations`, `copilot_messages`, `tool_call_logs`, `proactive_notifications`, `knowledge_documents`, `knowledge_chunks`.

Example answer payload:

```json
{
  "conversation_id": "…", "language": "hi",
  "answer_text": "…", "answer_audio_url": "…",
  "tool_trace": [
    { "tool": "predict_task_duration", "version": "1.0", "input": {"task_id": "TASK001"}, "result_ref": "…", "latency_ms": 212 },
    { "tool": "get_site_conditions", "version": "1.0", "input": {"site_id": "SITE_A"}, "result_ref": "…", "latency_ms": 40 }
  ],
  "grounded": true, "confidence_level": "HIGH"
}
```

## Work packages

| WP | Title | Est. |
|----|-------|------|
| M07-WP0 | Contracts + tool registry format + mock tool executor (returns contract examples) | 1 d |
| M07-WP1 | Orchestration: intent → tools → LLM explanation, `LLMProvider` interface, grounding guard | 3 d |
| M07-WP2 | Conversation context + query API + persistence | 1 d |
| M07-WP3 | Multilingual: detection, message keys, translation adapter (en/hi/ta) | 2 d |
| M07-WP4 | Voice: STT/TTS adapters + `/copilot/voice` | 1–2 d |
| M07-WP5 | RAG: ingestion, pgvector, `search_knowledge` with citations | 2 d |
| M07-WP6 | Proactive notifications + notification policy (priority, dedupe, cooldown) | 2 d |
| M07-WP7 | Evaluation set: 50+ operator questions → expected tools/facts; grounding + latency metrics | 1–2 d |
| M07-SLOT | Copilot slot UI (if held) | 2 d |

## Acceptance criteria

- [ ] "Why is my task running late?" calls `predict_task_duration` + `get_site_conditions` (+ `explain_operational_deviation`) and explains using only their results (reference scenario master §100, 09:11)
- [ ] Grounding guard: on the eval set, 0 answers contain numbers or states absent from tool results
- [ ] Same question in Hindi/Tamil → same tools, same facts, answer in that language
- [ ] Tool failure → honest fallback, no fabricated value
- [ ] Proactive: no more than N non-critical messages per operator per 10 min (configurable); duplicates suppressed
- [ ] Text answer p95 < 4 s, voice round-trip p95 < 6 s (demo hardware)
- [ ] Every tool call logged with version and latency (feeds M11)

## Testing

Unit tests on routing and the grounding guard (with a fake LLM), contract tests on tool IO, the eval set run in CI against a mocked LLM, and a smaller live-LLM eval run manually.

## Future extensions

More languages, offline/on-device STT, supervisor copilot (site questions + `run_what_if_scenario`), fine-grained intent models.

## Known constraints

LLM keys and model IDs come from `infra/env/m07.env.example` placeholders. Never commit real keys. Cost and latency: prefer the faster model for routine turns.

## Integration checklist

- [ ] Each tool flipped from mock → real as its owner goes LIVE (tracked in STATUS)
- [ ] M02 copilot slot shows the tool trace as "sources"
