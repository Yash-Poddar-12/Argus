# Product Principles

> Mandatory unless explicitly superseded by a team decision recorded in master §115. Source: master §2, §80, §108–§112.

## North star

> **Don't give the operator more data. Give the operator better context, better explanations, better decisions, and better learning.**

## The 12 principles

| # | Principle | What it means in code |
|---|-----------|-----------------------|
| P1 | **Operator first** | Every feature traces to safer operation, less friction, better task understanding, efficiency, or capability. Supervisor/Admin features exist to support operators and the site. |
| P2 | **Context before conclusions** | Never infer from one metric. Consider operator, machine, task, site, environment, time, other machines, and external dependencies. |
| P3 | **Don't blame the operator** | Attribute deviations to OPERATOR / MACHINE / TASK / SITE / ENVIRONMENT / INTERACTION / UNKNOWN, and show the evidence. |
| P4 | **Safety-critical decisions are deterministic** | Seatbelt, critical proximity, restricted zones, and emergencies use rules + sensor validation + validated thresholds. ML is contextual evidence only. |
| P5 | **AI must be grounded** | The Copilot explains tool results. It never generates telemetry or operational facts itself. |
| P6 | **Explain important decisions** | Alerts, predictions, recommendations, and training all answer "Why?". |
| P7 | **Human in the loop** | Decision support only, never autonomous machine control. Phrase outputs as "The simulation indicates…", not as commands. |
| P8 | **Optimize safe productivity** | Every productivity recommendation passes a safety-constraint check before it's shown. |
| P9 | **Training must be measurable** | Measure behavior change after training, not completion. Report observed associations, not causation, unless the experiment design supports causation. |
| P10 | **Edge-first safety** | Safety alerts work with no cloud connection. |
| P11 | **Modular by contract** | Modules communicate through APIs, events, schemas, tool interfaces, and ML contracts. |
| P12 | **Replaceability** | Models, DBs, brokers, LLMs, and UI components sit behind interfaces. |

## Privacy and dignity

- Least privilege, data minimization, access logging, purpose limitation, site-scoped access.
- Keep safety support separate from punitive HR workflows.
- **Never show a single employee "score" that hides the evidence.** Show components and context.
- Operator-facing performance views are non-punitive: they show trends and suggest improvements, with no rankings against peers by default.

## Confidence and cold start

- Every prediction carries a confidence level (HIGH / MODERATE / LOW) and says why confidence is low (new machine, new operator, little history, missing environment data).
- Cold-start fallback order: personal → machine → site → task → fleet prior.

## Notification discipline

| Priority | Channel |
|----------|---------|
| CRITICAL | Immediate alert (edge, voice + visual) |
| HIGH | Operator action requested |
| MEDIUM | Coaching tip |
| LOW / INFO | Analytics and learning only, never pushed |

## Non-goals (don't drift into these)

Autonomous machine control · generic fleet management · HR performance scoring · generic LMS · unrestricted chatbot · predictive maintenance as the primary product · fully autonomous dispatch · raw telemetry visualization as the main value.

## Feature decision checklist

Paste this into a PR or ADR when proposing something new.

```text
Product    Does it help the operator (or the supervisor support the operator/site)? Safety / productivity / understanding / learning?
Module     Which module owns it? What does it consume/produce? New shared contract?
AI         Does it really need ML? Is deterministic logic safer? What data? What confidence? How is it explained?
UX         Does it reduce cognitive load? Usable with gloves or busy hands? Voice-capable? Actionable?
Safety     What happens if the cloud is down? Can a failure here cause an unsafe state?
Research   What hypothesis does it enable? Against which baseline? How is success measured?
Scale      Works for one machine? Conceptually for many sites? Event-driven where appropriate?
```
