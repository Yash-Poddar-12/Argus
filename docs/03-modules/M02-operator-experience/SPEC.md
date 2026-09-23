# M02 — Operator Experience

| Field | Value |
|-------|-------|
| Phase | 2 (can start UI with mocks during Phase 0/1) |
| Type | Frontend (`frontend/apps/operator`) |
| Depends on (contracts) | M00, M01; mocks of M04, M06, M07, M08 |
| Consumed by | operators |
| Gate | G2 (scenes 1–5), G3 (scenes 6–10 UI) |

## Objective

The operator's shift in one app: **My Day, My Machine, My Tasks, My Safety, My Performance, My Training, AI Copilot**, designed for gloves, noise, sunlight, and divided attention.

## Why this module exists

The operator is the primary user (P1). Every backend capability becomes valuable only when it reaches the operator as **context, explanation, and a next action** rather than raw data.

## Scope

- Login, machine confirmation, pre-op checklist (T01–T03)
- **Shift briefing / huddle** (master §66), composed client-side from M01 tasks + conditions, M06 ETA, M04 watch-outs, M08 focus
- **My Day:** task sequence, ETAs, conditions, priority notices, recommended action, "What changed since yesterday?" (§67)
- **My Tasks / live operation:** start/pause/resume/complete, progress, live ETA with confidence and a WHY? drawer (contributors)
- **My Machine:** live state (fuel, hours, mode, utilization), machine alerts, location map
- **My Safety:** current status, recent events, nearby hazards, "Why did I get this alert?" (rule, values, threshold); full-screen **CRITICAL alert overlay** with acknowledge (T07)
- **My Performance:** personal trends, baselines, idle/cycle/fuel, recent improvements. **Non-punitive**: no peer ranking, always shows context (P3)
- **Notification center:** priority-tiered (CRITICAL/HIGH/MEDIUM/INFO), coaching tips, anti-spam display rules
- **i18n** of UI strings (en, hi, ta initial) via M00's scaffold
- **Slots** (delegable, default M02 builds them against mocks): `copilot` (M07), `training` (M08)
- Connectivity banner (offline / reconnecting); safety alerts still arrive from the edge path when the cloud UI is stale (display only; delivery is M04's job)

## Out of scope

ML calculations, safety decisions, data truth (never compute ETA/risk in the UI), backend endpoints. If a view needs data no API provides, request it from the owning module and mock it meanwhile.

## Owned paths

`frontend/apps/operator/**` except `src/app/copilot/`, `src/features/copilot/`, `src/app/training/`, `src/features/training/` when those slots are delegated (see `TEAM_AND_OWNERSHIP.md`).

## Inputs

REST: M00 auth/operators; M01 tasks, sessions, prechecks, twin, conditions, machine state; M04 operator safety, event detail, ack; M06 performance, deviation explanation; M08 recommendations/sessions; M07 query/voice.
WS `/ws/operators/{id}`: `TASK_UPDATE`, `TASK_ETA_UPDATED`, `MACHINE_STATE_UPDATE`, `TWIN_UPDATE`, `SAFETY_ALERT`, `HAZARD_UPDATE`, `COPILOT_PROACTIVE_MESSAGE`, `TRAINING_RECOMMENDATION`.

## Outputs

User actions via REST only. M02 produces no events and owns no tables.

## Mock strategy

`src/features/<feature>/mocks/` import examples from `contracts/**/examples/`. A dev toggle `NEXT_PUBLIC_USE_MOCKS=feature1,feature2` plus a **WS replay mock** plays a recorded S1–S6 event sequence so every screen can be built before the backends exist.

## Work packages

| WP | Title | Depends on | Est. |
|----|-------|------------|------|
| M02-WP0 | Mock layer + WS replay mock + fixture scenarios S1–S6 | M00-WP4, contract examples | 1 d |
| M02-WP1 | Login → machine confirm → pre-op checklist | M00 auth, M01 prechecks | 1–2 d |
| M02-WP2 | My Day + shift briefing + "What changed?" | M01, mocks M04/M06/M08 | 2 d |
| M02-WP3 | My Tasks + live operation (lifecycle, progress, ETA + WHY? drawer) | M01, mock M06 | 2 d |
| M02-WP4 | My Machine (live state, alerts, map) | M01 | 1–2 d |
| M02-WP5 | My Safety + CRITICAL alert overlay + ack + "why this alert" | mock/real M04 | 2 d |
| M02-WP6 | My Performance (non-punitive trends, baselines, deviation explanations) | mock/real M06 | 2 d |
| M02-WP7 | Notification center + priority tiers + coaching tips | all WS types | 1 d |
| M02-WP8 | i18n (en/hi/ta UI strings), accessibility + glove/sunlight pass | — | 1–2 d |
| M02-SLOT-C | Copilot slot UI (text + push-to-talk, tool trace "sources", language picker) | mock/real M07 | 2 d |
| M02-SLOT-T | Training slot UI (recommendations with reasons, micro-learning player, assessment, impact) | mock/real M08 | 2 d |

## Acceptance criteria

- [ ] Demo scenes 1–5 run on real M01 data, with M04/M06 real or mocked
- [ ] SAFETY_ALERT CRITICAL shows a full-screen overlay within 300 ms of the WS message and can't be dismissed without acknowledging
- [ ] Every prediction shown has a confidence level and an accessible "Why?"
- [ ] Performance views show evidence and context, with no single opaque score
- [ ] Touch targets ≥ 48 px, WCAG AA contrast, usable at 360 px width, works in landscape tablet
- [ ] UI fully switchable to Hindi and Tamil with no layout breakage
- [ ] Each screen handles loading, empty, error, stale-data, and low-confidence states

## Testing

Component tests (Vitest), Playwright happy paths for scenes 1–5, visual check in all three languages, axe accessibility scan.

## Future extensions

Native/mobile wrapper (PWA first), in-cab display mode, offline cache of today's tasks, haptic alerts.

## Known constraints

Voice capture uses the browser API in the demo, which needs HTTPS or localhost.

## Integration checklist

- [ ] Mocks switched off one feature at a time as each backend goes LIVE (track in STATUS)
- [ ] No business logic duplicated from backend modules
