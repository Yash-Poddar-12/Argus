# CAT Operator & Site Intelligence Platform
## Master Product, Architecture, Research, Modular Execution & AI-Agent Context

> **Document purpose:** This is the single comprehensive context document for a multi-person, multi-agent engineering team building an operator-first intelligent construction equipment platform.
>
> **Primary audience:** Senior architects, product leads, ML engineers, backend/frontend engineers, IoT/edge engineers, researchers, and coding agents such as Codex CLI, Claude CLI, Antigravity, and other IDE agents.
>
> **Usage:** Feed this document to a high-capability AI model as project context before asking it to plan, implement, review, refactor, or generate work. The model should treat the architectural contracts and product principles in this document as the default source of truth unless a newer explicit decision supersedes them.
>
> **Repository structure (2026-09-23, ADR-0002):** code is organized by capability, not by M-number: `backend/app/{core,api/v1,domain/<capability>,copilot,iot}`, `frontend/src/{app,features,components,lib}`, `ml/`, `contracts/`. M00–M11 below are delivery workstreams. Where code goes: `docs/architecture/REPOSITORY_STRUCTURE.md`.
>
> **How this file relates to the rest of the repo (added 2026-09-23):** This file holds the **product intent and vision**. Day-to-day execution lives in smaller files that every IDE/agent loads:
>
> | Need | File |
> |------|------|
> | Rules for every agent/human (Codex, Claude, Antigravity, …) | `AGENTS.md` (`CLAUDE.md` / `GEMINI.md` point to it) |
> | **Modular parallel workflow** (phases, gates, conflict-free rules) | `docs/development/PARALLEL_WORKFLOW.md` |
> | Who owns which folder | `docs/architecture/REPOSITORY_STRUCTURE.md` |
> | Module scope + work packages | `docs/development/workstreams/MXX-*.md` |
> | Live module status (updated on every push) | `docs/development/workstreams/MXX-*.md` + `python scripts/status.py board` |
> | Push/pull status marking | `docs/development/SYNC_PROTOCOL.md` |
> | Exact interfaces | `contracts/**` + `docs/architecture/contracts/*.md` |
> | Full doc index | `docs/README.md` |
>
> Precedence when documents disagree: product principles (§2) always apply; then `contracts/**` > module `SPEC.md` > contract catalogs > workflow docs > this file for implementation details. Product intent changes are made **here** and logged in §115.

---

# 0. EXECUTIVE SUMMARY

## 0.1 Product in one sentence

**An operator-first Human-Machine Operational Intelligence platform that continuously understands the operator, machine, task, and environment; predicts what is likely to happen; assists the operator through a grounded multilingual voice/dashboard copilot; learns from outcomes; and gives supervisors/admins site-level operational decision support.**

## 0.2 Product thesis

Traditional construction equipment software is often centered on:

- machine telemetry,
- fleet dashboards,
- alerts,
- maintenance,
- utilization,
- historical reports.

This project is centered on a different unit of intelligence:

> **The human + machine + task + environment operating together in the real world.**

The core proposition is therefore:

```text
Machine + Human + Task + Environment
                    ↓
      Human-Machine Operational Twin
                    ↓
           Contextual Intelligence
                    ↓
        Understand → Predict → Assist
                    ↓
              Human Decision
                    ↓
                   Learn
                    ↓
             Better Operator
                    ↓
          Better Site Operations
```

## 0.3 Primary user vs supporting user

There are only **two product roles**:

### Primary role: Operator

The product is fundamentally built around the operator's shift.

The operator receives:

- daily tasks,
- assigned machine,
- pre-operation checks,
- live machine state,
- safety alerts,
- hazard awareness,
- task-time predictions,
- explanations,
- coaching,
- training,
- performance insights,
- a voice/dashboard copilot,
- multilingual assistance.

### Supporting role: Supervisor/Admin

Supervisor/Admin actions exist primarily to support the operator and the site.

They perform:

- operator CRUD,
- machine CRUD,
- site CRUD,
- assignment,
- task creation and updates,
- deadline changes,
- task assistance,
- safety configuration,
- IoT/site configuration,
- operational monitoring,
- site-level decision support,
- reports and historical analysis.

**Do not turn Supervisor/Admin into a second equally elaborate product unless explicitly requested later.**

The design principle is:

> Every Supervisor/Admin action should have a clear operational consequence for an operator, a machine, a task, or site safety/productivity.

---

# 1. PRODUCT VISION

## 1.1 The problem

Heavy-equipment operation is not just a machine telemetry problem.

An operator is simultaneously dealing with:

- machine behavior,
- task requirements,
- changing site conditions,
- other machines,
- nearby workers,
- environmental conditions,
- deadlines,
- safety requirements,
- machine familiarity,
- personal operating habits.

A telemetry dashboard shows data.

The proposed platform aims to provide **operational understanding and assistance**.

## 1.2 Desired transformation

### Old model

```text
Machine
  ↓
Telemetry
  ↓
Dashboard
  ↓
Human interprets information
```

### Proposed model

```text
Human + Machine + Task + Environment
                ↓
         Operational Twin
                ↓
       Contextual Intelligence
                ↓
     ┌──────────┼──────────┐
     ↓          ↓          ↓
   Safety   Productivity   Skills
     ↓          ↓          ↓
     └──────────┼──────────┘
                ↓
        Operator Copilot
                ↓
         Human Decision
                ↓
             Outcome
                ↓
        Learning / Feedback
```

## 1.3 Product north star

> **Do not give the operator more data. Give the operator better context, better explanations, better decisions, and better learning.**

---

# 2. CORE PRODUCT PRINCIPLES

These principles are mandatory unless explicitly superseded.

## P1 — Operator First

The operator is the primary user and center of the product.

Every major feature should be traceable to:

- making operation safer,
- reducing operational friction,
- improving task understanding,
- improving efficiency,
- improving operator capability.

## P2 — Context Before Conclusions

Do not infer operator fault from one metric.

Always consider:

```text
Operator
Machine
Task
Site
Environment
Time
Other machines
External dependencies
```

## P3 — Don't Blame the Operator

A deviation is not automatically an operator problem.

The system should classify potential cause as:

- operator-driven,
- machine-driven,
- task-driven,
- site-driven,
- environment-driven,
- interaction/network-driven,
- unknown/insufficient evidence.

## P4 — Safety-Critical Decisions Are Deterministic

Do not delegate safety-critical decisions to an LLM.

Examples:

- seatbelt violation,
- critical proximity,
- restricted zone violation,
- emergency state.

Use:

- deterministic rules,
- sensor validation,
- edge logic,
- validated thresholds,
- optionally ML as contextual evidence.

## P5 — AI Must Be Grounded

The Copilot must not free-generate telemetry facts.

Every operational factual answer should originate from one or more authoritative tools/functions such as:

- live telemetry,
- task-time prediction service,
- safety index service,
- operational twin query,
- training profile query,
- hazard mesh service,
- scenario engine.

The LLM explains tool results rather than inventing them.

## P6 — Explain Important Decisions

The system should answer:

> Why?

For alerts, predictions, recommendations, and training.

## P7 — Human Remains in the Decision Loop

The platform is decision support, not uncontrolled autonomous machine operation.

## P8 — Optimize Safe Productivity

Do not optimize productivity independently from safety.

## P9 — Training Must Be Measurable

Course completion is not enough.

Training effectiveness should ultimately be measured through observed behavioral change.

## P10 — Edge-First Safety

Safety-relevant functionality must continue when cloud connectivity is unavailable.

## P11 — Modular by Contract

Modules communicate through contracts:

- APIs,
- events,
- schemas,
- tool interfaces,
- ML inference contracts.

## P12 — Replaceability

Models, databases, brokers, and UI components should be replaceable behind interfaces where practical.

---

# 3. USER ROLES AND AUTHORIZATION MODEL

## 3.1 Role model

There are two product-facing roles:

```text
OPERATOR
SUPERVISOR_ADMIN
```

Supervisor and Admin are merged at the product UX level for this project.

A future RBAC implementation may still retain internal permissions.

## 3.2 Operator capabilities

Operator can:

- authenticate,
- confirm assigned machine,
- run pre-operation checks,
- view assigned tasks,
- start/pause/resume/complete tasks,
- receive real-time safety alerts,
- inspect current machine state,
- view hazard context,
- ask the copilot questions,
- receive proactive recommendations,
- access training,
- complete assessments,
- view performance insights,
- view training impact.

## 3.3 Supervisor/Admin capabilities

Supervisor/Admin can:

- create/update operators,
- create/update machines,
- create/update sites,
- assign operators to machines,
- assign operators to tasks,
- update task deadlines,
- add task assistance/resources,
- configure safety/site rules,
- configure IoT devices,
- view site state,
- view machine interactions,
- inspect bottlenecks,
- review site safety/efficiency insights,
- simulate operational changes,
- review operator support context.

## 3.4 Authorization principle

Do not hard-code application behavior around role names.

Prefer:

```text
Identity
  ↓
Role
  ↓
Permissions
  ↓
Organization/Site Scope
  ↓
Resource
```

A Supervisor/Admin can only access the resources within their authorized organization/site scope.

---

# 4. SIGNATURE CONCEPT — HUMAN-MACHINE OPERATIONAL TWIN

## 4.1 Definition

### Human-Machine Operational Twin (HMOT)

> A continuously updated, context-aware digital representation of a real-world operator-machine-task-environment system, enriched with current state, historical behavior, risk, performance, predictions, and skill context.

The twin is not "a digital clone of a human."

It models the **operational relationship**.

## 4.2 Formal abstraction

The operational state can be thought of as:

```text
OperationalState(t)
    = f(
        Human(t),
        Machine(t),
        Task(t),
        Environment(t),
        Site(t),
        Time(t),
        InteractionContext(t)
      )
```

## 4.3 Four foundational dimensions

### Human

- operator identity
- experience
- certification
- machine familiarity
- safety baseline
- productivity baseline
- efficiency baseline
- behavior profile
- training history
- skill state

### Machine

- machine identity
- model/type
- engine hours
- fuel
- RPM/speed
- load cycles
- idle
- machine health
- location
- operating mode

### Task

- task ID
- task type
- zone
- target
- planned start/end
- current progress
- expected duration
- predicted completion
- dependencies

### Environment

- weather
- temperature
- rain
- visibility
- terrain
- soil condition
- zone state
- nearby personnel
- nearby machines
- restricted areas
- site congestion

## 4.4 Twin layers

The Twin should conceptually contain two layers.

### State Layer

Answers:

> What is happening now?

Example:

```text
Operator: OP1001
Machine: EXC001
Task: Excavation Zone A
Progress: 48%
Seatbelt: Fastened
Speed: 8.2
Fuel: 62%
Nearby workers: 2
```

### Intelligence Layer

Answers:

> What does it mean?

Example:

```text
Safety risk: LOW
Productivity state: NORMAL
Task ETA: 10:42
Behavior anomaly: LOW
Operator machine familiarity: HIGH
Environmental difficulty: MEDIUM
Prediction confidence: HIGH
```

## 4.5 Twin is NOT just a database row

A useful conceptual formula:

```text
Twin
= Current State
+ Context
+ Historical State
+ Derived Features
+ Predictions
+ Recommendations
```

---

# 5. END-TO-END OPERATOR FLOW

## 5.1 Main journey

```text
LOGIN
  ↓
IDENTITY
  ↓
MACHINE CONFIRMATION
  ↓
PRE-OPERATION CHECK
  ↓
SHIFT BRIEFING
  ↓
TODAY'S TASKS
  ↓
START TASK
  ↓
LIVE OPERATION
  ↓
SAFETY / HAZARD MONITORING
  ↓
TASK PROGRESS + ETA
  ↓
COACHING / COPILOT
  ↓
PAUSE / RESUME IF NEEDED
  ↓
TASK COMPLETE
  ↓
TASK SUMMARY
  ↓
PERFORMANCE INSIGHTS
  ↓
TRAINING / LEARNING
  ↓
NEXT TASK
  ↓
SHIFT CLOSE
```

## 5.2 Key transaction list

```text
T01 Authenticate operator
T02 Confirm machine
T03 Complete pre-operation check
T04 Retrieve today's tasks
T05 Start task
T06 Receive live telemetry
T07 Receive/respond to safety alert
T08 Pause task
T09 Resume task
T10 Complete task
T11 Review task summary
T12 Review performance
T13 Start training
T14 Complete training
T15 Ask Copilot
T16 Receive proactive Copilot notification
T17 Run What-if scenario
```

---

# 6. OPERATOR EXPERIENCE

## 6.1 Main navigation

```text
My Day
My Machine
My Tasks
My Safety
My Performance
My Training
AI Copilot
```

## 6.2 My Day

Should show:

- current machine,
- task sequence,
- task ETAs,
- shift briefing,
- current conditions,
- priority notices,
- recommended action.

## 6.3 My Machine

Should show:

- machine state,
- fuel,
- engine hours,
- current operating state,
- utilization,
- machine alerts,
- current location/map.

## 6.4 My Safety

Should show:

- current safety status,
- recent safety events,
- nearby hazard awareness,
- safety context,
- why an alert occurred.

## 6.5 My Performance

Should show:

- personal trends,
- task efficiency,
- idle pattern,
- cycle performance,
- safety compliance,
- fuel efficiency,
- recent improvements.

Do not make it punitive.

## 6.6 My Training

Should show:

- recommended modules,
- reason for recommendation,
- duration,
- priority,
- progress,
- assessment,
- completed history,
- training impact.

---

# 7. SUPERVISOR/ADMIN EXPERIENCE

The supporting console should be operational and practical rather than a competing product.

## 7.1 Major areas

```text
Overview
Operators
Machines
Sites
Tasks
Assignments
Safety / Hazards
Operational Intelligence
Training Administration
Reports
Configuration
```

## 7.2 Assignment example

Supervisor/Admin:

```text
Operator:
OP1001

Machine:
EXC001

Task:
Excavation — Zone A

Start:
08:00

Target:
50 cycles

Deadline:
10:30

Additional Assistance:
Dumper D2
```

Once saved:

```text
assignment.created
        ↓
operator task state updated
        ↓
operator sees task
        ↓
task prediction generated
        ↓
shift briefing updated
```

---

# 8. USP STACK

The platform should not look like a collection of unrelated AI features.

Organize the differentiators into these layers.

## USP 1 — Human-Machine Operational Twin

> Understand the complete human-machine-task-environment context.

## USP 2 — Don't Blame the Operator / WHY? Engine

> Attribute deviations using context rather than assuming operator fault.

## USP 3 — Voice + Multilingual Tool-Grounded Copilot

> One operational point of contact for the operator's shift.

## USP 4 — IoT Site Awareness / Hazard Mesh

> Real-time machine-person-machine interaction awareness, edge-first.

## USP 5 — Safe Operational Decision Engine

> Turn site interactions into actionable productivity and safety decisions.

## USP 6 — Personalized Closed-Loop Training

> Detect skill/behavior gaps, intervene, and measure whether behavior improves.

## USP 7 — Counterfactual Operational Copilot

> Allow operator/supervisor to explore “what if” scenarios without directly controlling the machine.

## USP 8 — Federated Fleet Intelligence

> Improve site-level models globally using privacy-preserving collaborative model updates rather than centralizing raw operational histories.

---

# 9. USP — “DON’T BLAME THE OPERATOR”

## 9.1 Principle

A deviation is a signal, not a verdict.

Example:

```text
Idle time = 55 minutes
```

Do not immediately conclude:

```text
Operator inefficient
```

Instead investigate:

```text
Operator behavior?
Machine state?
Task state?
Dumper availability?
Site congestion?
Weather?
Terrain?
Restricted area?
Other machine?
```

## 9.2 Root cause categories

```text
OPERATOR
MACHINE
TASK
SITE
ENVIRONMENT
INTERACTION
UNKNOWN
```

## 9.3 Example

```text
Observed:
Idle ↑

Context:
Dumper unavailable ↑
Site queue ↑
Operator behavior normal

Conclusion:
Site-driven delay likely
```

This should be visible in the WHY? Engine.

---

# 10. WHY? ENGINE

The WHY? Engine is an explainability layer.

## 10.1 For task-time predictions

Example:

```text
Predicted completion: 10:42

Contributors:

Wet soil            +7 min
Idle trend          +4 min
Current cycle rate  +3 min
Operator baseline   -2 min
Machine age         +1 min
```

## 10.2 For safety events

Example:

```text
Why did I receive this alert?

Seatbelt detected unfastened
+
machine operating
+
operator active
+
hazard zone active

Alert triggered by:
Seatbelt safety rule
```

## 10.3 For operational efficiency

Example:

```text
Why is Excavator E1 underutilized?

42% of non-productive time
comes from waiting for dumpers.

Dumper D2:
average queue = 8.4 min
```

---

# 11. COUNTERFACTUAL COPILOT

## 11.1 Purpose

Answer:

> What would happen if we changed something?

This is decision support, not direct machine control.

## 11.2 Operator scenarios

Examples:

- “What if I reduce idle?”
- “What if current weather continues?”
- “What happens if my next task starts late?”
- “Why is this task slower than normal?”

## 11.3 Supervisor/Admin scenarios

Examples:

- “What if I move Dumper D2 to Excavator E2?”
- “What if I add another dumper?”
- “What happens if the task deadline is reduced?”
- “What if this zone becomes unavailable?”

## 11.4 Architecture

```text
Current Operational Twin
        ↓
Scenario Builder
        ↓
Modified Twin
        ↓
Prediction Models
        ↓
Safety Constraint Evaluation
        ↓
Scenario Comparison
        ↓
Explainable Recommendation
```

## 11.5 Example

```text
CURRENT
E1 throughput: 42 loads/hour
E2 throughput: 31 loads/hour

SCENARIO:
Move D2 from E1 → E2

Predicted:
E1: 39 loads/hour
E2: 37 loads/hour
Site throughput: +4.8%
Safety constraints: unchanged
```

Do not phrase output as an autonomous command.

Use:

> “The simulation indicates…”

---

# 12. VOICE + DASHBOARD COPILOT

## 12.1 Product role

The Copilot is:

> **The operator's single point of contact for the shift.**

## 12.2 Interaction modes

```text
Voice
Tap
Dashboard cards
Proactive alert
```

## 12.3 Multilingual architecture

```text
Voice Input
    ↓
Speech-to-Text
    ↓
Language Detection
    ↓
Operational Intent
    ↓
Tool Selection
    ↓
Authoritative Tool
    ↓
Structured Result
    ↓
LLM Explanation
    ↓
Translation / Language Adaptation
    ↓
Text / Speech Output
```

The underlying safety and telemetry services remain language-independent.

## 12.4 Grounded tool-calling model

```text
Operator:
“How long will this trenching job take?”

        ↓

Agent
        ↓
predict_task_duration()
        ↓

{
  p50: 87,
  p80: 94,
  confidence: 0.84,
  factors: [...]
}

        ↓
LLM
        ↓
Natural-language explanation
```

## 12.5 Recommended tool registry

```text
get_current_machine_state()
get_current_task()
get_task_progress()
predict_task_duration()
get_safety_index()
get_recent_alerts()
get_alert_details()
get_nearby_hazards()
get_operator_performance()
get_operator_training()
get_machine_health()
get_weather()
get_site_conditions()
get_nearby_machines()
run_what_if_scenario()
explain_operational_deviation()
```

## 12.6 Proactive Copilot

The Copilot should proactively surface:

- seatbelt unfastened,
- nearby worker hazard,
- nearby machine conflict,
- task running long,
- abnormal machine condition,
- unusual operator pattern,
- task dependency delay,
- training recommendation.

The Copilot should not spam.

Introduce priority levels:

```text
CRITICAL
HIGH
MEDIUM
INFO
```

and a notification policy.

---

# 13. MULTILINGUAL DESIGN

Language should be treated as an interaction layer, not domain logic.

Suggested architecture:

```text
Canonical operational entities
        ↓
Language-neutral event/result
        ↓
Language adapter
        ↓
Operator language
```

Potential supported languages should be configurable.

For hackathon/demo, choose a small initial set such as:

- English
- Hindi
- Tamil

The architecture should allow adding others without rewriting business logic.

---

# 14. IOT SITE AWARENESS / HAZARD MESH

## 14.1 Product idea

Create a local site awareness layer using:

- BLE,
- UWB,
- machine-mounted tags,
- worker wearable tags,
- edge gateways,
- site zones.

The system creates a real-time local proximity graph.

## 14.2 Safety use cases

Detect:

- machine-to-person proximity,
- machine-to-machine proximity,
- restricted-zone entry,
- hazard-zone presence,
- rapidly closing distance,
- potential collision trajectory.

## 14.3 Edge-first architecture

```text
Machine / Worker Devices
        ↓
BLE / UWB / Local Links
        ↓
Edge Gateway
        ↓
Local Proximity Engine
        ↓
Local Safety Decision
        ↓
Local Alert

Parallel:
        ↓
Event stream
        ↓
Cloud / Site Intelligence
```

The safety alert must not require a cloud round trip.

## 14.4 Site Awareness concept

The broader capability should eventually include:

```text
Position
Velocity
Direction
Machine state
Task
Zone
Proximity
Queue state
Utilization
Machine interaction
```

Thus the Hazard Mesh becomes part of:

# Site Awareness Mesh

with two major branches:

```text
SITE AWARENESS MESH
       │
       ├── Safety Intelligence
       │      ├── proximity
       │      ├── hazard
       │      └── zone
       │
       └── Operational Intelligence
              ├── machine interactions
              ├── queues
              ├── bottlenecks
              ├── utilization
              └── material flow
```

---

# 15. MACHINE INTERACTION GRAPH

## 15.1 Concept

Do not create hardcoded point-to-point integrations between every machine.

Instead model the site as a dynamic graph.

```text
Node = machine / person / zone / operational resource
Edge = interaction / dependency / proximity / material flow
```

Example:

```text
Dumper D1 ── loading dependency ──► Excavator E1
Dumper D2 ── loading dependency ──► Excavator E1
Excavator E1 ── material flow ──► Disposal Zone
Worker W1 ── proximity ──► Excavator E1
```

## 15.2 Edge statistics

For an edge between E1 and D1:

```text
Average wait
Average load time
Average unload time
Trips/hour
Utilization
Queue time
Interaction efficiency
Safety events
```

## 15.3 Why this matters

You can detect:

- machine imbalance,
- queueing,
- dispatch problems,
- site bottlenecks,
- unnecessary idle,
- resource underutilization,
- unsafe interaction patterns.

---

# 16. OPERATIONAL DECISION ENGINE

## 16.1 Purpose

The Decision Engine converts site intelligence into decision candidates.

It should answer:

- Where is the bottleneck?
- Which machine is waiting?
- Which machine is underutilized?
- Which machine dependency is causing delay?
- Would reallocation help?
- Would the proposed change increase safety exposure?

## 16.2 Example

```text
Excavator E1
  ↑ waiting
  ↓
Dumper D2
  ↑ queue
  ↓
Disposal Zone
  ↑ congestion
```

Decision insight:

> “Dumper D2 is contributing 18 minutes/hour of avoidable queue time at E1. Reallocation or dispatch adjustment may increase site throughput.”

## 16.3 Safety constraint

Every productivity recommendation must pass:

```text
Safety constraint check
```

before being shown as a viable scenario.

---

# 17. SAFETY + PRODUCTIVITY MODEL

Avoid optimizing one dimension independently.

The platform can track:

```text
Safety
Productivity
Machine Utilization
Fleet Balance
Operator Readiness
Fuel/Energy Efficiency
Environmental Difficulty
```

A derived score may exist, but the individual components must remain visible.

Conceptually:

```text
Safe Productivity Envelope

Productivity ↑
        │
        │     feasible area
        │   ┌──────────────
        │  /
        │ /
        └────────────────→
                   Risk ↑
```

The system should surface:

> High productivity opportunity without unacceptable safety exposure.

---

# 18. PERSONAL OPERATING FINGERPRINT

## 18.1 Concept

Each operator has a baseline.

Example:

```text
Cycle time: 52 sec
Idle: 18 min/task
Fuel: 4.8 L/hr
Seatbelt compliance: 98%
```

Today:

```text
Cycle time: 68 sec
Idle: 51 min/task
Fuel: 5.9 L/hr
Seatbelt compliance: 94%
```

The system detects behavioral drift.

## 18.2 Multi-baseline approach

Compare:

```text
Current
   ↓
Personal baseline
Machine baseline
Site baseline
Fleet baseline
```

This reduces unfair attribution.

---

# 19. ML/AI MODEL STRATEGY

Do not create models merely to increase the model count.

Recommended architecture:

## M1 — Behavior Anomaly Model

### Question

> Is this operator's current behavior unusual?

### MVP

- Isolation Forest

### Advanced

- temporal autoencoder,
- LSTM/temporal model,
- sequence transformer.

### Inputs

- idle,
- cycle time,
- load cycles,
- fuel,
- speed,
- safety events,
- task state,
- machine context,
- site context.

### Output

```text
anomaly_score
severity
contributing_signals
```

---

# 20. M2 — Task-Time Predictor

### Question

> How long will this task take for this operator/machine/context?

### MVP

- LightGBM or XGBoost

### Advanced

- temporal model,
- Temporal Fusion Transformer,
- sequence + context fusion.

### Features

- task type,
- task complexity,
- machine,
- operator,
- operator baseline,
- machine age/engine hours,
- cycle time,
- idle,
- load cycles,
- environmental conditions,
- site conditions.

### Output

```text
P50
P80
P90
confidence
feature contributions
model_version
```

---

# 21. M3 — Contextual Risk Model

### Question

> How risky is the current operational state?

### MVP

- XGBoost/gradient boosting classifier.

### Inputs

- seatbelt,
- proximity,
- speed,
- machine state,
- task type,
- worker presence,
- zone,
- environment,
- recent events,
- operator history.

### Output

```text
risk_probability
risk_level
contributing_factors
```

### Critical rule

ML is contextual evidence.

Hard safety conditions remain deterministic.

---

# 22. M4 — Skill Estimation Engine

### Question

> Which operational skills does this operator currently demonstrate, and where are the gaps?

Potential dimensions:

```text
Safety
Machine operation
Positioning
Cycle optimization
Idle management
Fuel efficiency
Proximity awareness
Task execution
```

### MVP

Hybrid:

```text
rules
+
behavior metrics
+
training assessment
+
historical outcomes
```

### Research

- Bayesian Knowledge Tracing,
- probabilistic mastery estimation.

---

# 23. M5 — Training Recommendation Engine

### Question

> What should the operator learn next?

Use a hybrid engine.

Inputs:

```text
Skill gaps
Behavior patterns
Safety events
Machine assignment
Site assignment
Training history
Certification status
Recent incidents
```

Output:

```text
training_module
reason
priority
expected_duration
trigger
```

### MVP

Rule-driven.

### Advanced

Learning-to-rank or personalization model once enough feedback data exists.

---

# 24. OPTIONAL M6 — INTERVENTION IMPACT MODEL

### Question

> Did training or coaching actually change real-world operator behavior?

Potential research methods:

- interrupted time-series,
- causal inference,
- propensity-based analysis,
- causal forests,
- Bayesian structural approaches.

Do not claim causality from a simple before/after comparison.

The hackathon implementation can use:

```text
Before metric
Training
After metric
Observed change
```

and label it as an observed association rather than proven causal effect.

---

# 25. INTELLIGENCE COMPONENTS THAT ARE NOT CONVENTIONAL ML

Some logic should remain deterministic/hybrid.

## Root Cause Engine

Initially:

```text
Rules + evidence graph
```

## Safety Decision Engine

```text
Rules + sensor validation + ML context
```

## Notification Policy

```text
Priority rules + user context
```

## Training assignment

```text
Rule + skill engine
```

---

# 26. ML CONTRACT

All ML should be behind stable service interfaces.

Example:

```python
predict_task_duration(context) -> TaskPrediction
calculate_operational_risk(context) -> RiskPrediction
detect_operator_anomaly(context) -> AnomalyPrediction
estimate_skill_profile(context) -> SkillProfile
```

Do not make frontend or Copilot dependent on raw model implementation details.

---

# 27. DATA ARCHITECTURE

## 27.1 Storage responsibilities

### PostgreSQL

Transactional/business entities:

```text
users
operators
machines
sites
tasks
assignments
task_sessions
training_modules
training_sessions
safety_rules
incidents
```

### TimescaleDB / time-series store

High-volume time-series:

```text
machine_telemetry
operator_events
environment_events
hazard_events
machine_state_changes
```

### Redis

Real-time/current state:

```text
current_machine_state
current_operator_state
active_task_state
live_risk_state
websocket_state
cache
```

### Object storage

Raw/large files:

```text
raw telemetry
simulation assets
training videos
documents
model artifacts
research datasets
reports
```

### Vector database / pgvector

RAG knowledge:

```text
machine manuals
training content
safety procedures
site procedures
FAQs
approved operational documentation
```

---

# 28. CORE DATA MODEL

## Operator

```text
operator_id
name
experience_level
certification_status
site_id
status
created_at
```

## Machine

```text
machine_id
model
serial_number
machine_type
site_id
status
engine_hours
created_at
```

## Site

```text
site_id
name
location
configuration
status
```

## Task

```text
task_id
site_id
task_type
zone_id
priority
target
planned_start
planned_end
status
```

## Assignment

```text
assignment_id
task_id
operator_id
machine_id
assigned_by
start_time
end_time
status
```

## Task Session

```text
session_id
task_id
operator_id
machine_id
actual_start
actual_end
pause_duration
status
```

---

# 29. TELEMETRY MODEL

Suggested fields:

```text
timestamp
machine_id
engine_hours
fuel
fuel_rate
load_cycles
idle_seconds
speed
rpm
temperature
gps
operating_mode
```

Partition by:

```text
time
machine_id
```

where supported.

---

# 30. SAFETY EVENT MODEL

```text
event_id
timestamp
machine_id
operator_id
site_id
event_type
severity
sensor_value
threshold
risk_score
decision_source
acknowledged_at
resolved_at
```

`decision_source` may be:

```text
RULE
EDGE_ML
CLOUD_ML
HYBRID
```

---

# 31. OPERATOR BEHAVIOR PROFILE

```text
operator_id

window_start
window_end

avg_idle_time
avg_cycle_time
avg_fuel_rate
seatbelt_compliance
proximity_events
safety_event_rate

machine_specific_baseline
site_specific_baseline

anomaly_score
updated_at
```

---

# 32. TASK PREDICTION

```text
prediction_id
task_id
operator_id
machine_id

p50_duration
p80_duration
p90_duration

confidence

model_version
prediction_timestamp
```

Optional explainability table:

```text
prediction_id
feature
value
contribution
```

---

# 33. TRAINING DATA MODEL

## Training Module

```text
training_id
title
category
machine_type
skill_area
difficulty
duration
format
content_uri
passing_score
status
```

## Operator Training

```text
session_id
operator_id
training_id
reason
priority
status
started_at
completed_at
score
```

## Training Trigger

```text
trigger_id
training_id
trigger_type
threshold
window
priority
```

Examples:

```text
SEATBELT_VIOLATION >= 3 in 7 days
CYCLE_TIME_DEVIATION >= 15% for N tasks
NEW_MACHINE_ASSIGNMENT
INCIDENT_OCCURRED
CERTIFICATION_EXPIRY
```

---

# 34. SITE MACHINE INTERACTION MODEL

Conceptual graph:

```text
node_id
node_type
site_id
state
position
```

Edge:

```text
edge_id
source_node
target_node
interaction_type
created_at
active
```

Interaction statistics:

```text
avg_wait
avg_interaction_duration
queue_time
frequency
utilization
safety_events
efficiency
```

---

# 35. API ARCHITECTURE

Use REST for standard operations and WebSockets for live updates.

## Authentication

```http
POST /api/v1/auth/login
```

## Operator

```http
GET /api/v1/operators/{operator_id}
GET /api/v1/operators/{operator_id}/twin
GET /api/v1/operators/{operator_id}/tasks/today
GET /api/v1/operators/{operator_id}/performance
GET /api/v1/operators/{operator_id}/training
GET /api/v1/operators/{operator_id}/safety
```

## Machine

```http
GET /api/v1/machines/{machine_id}
GET /api/v1/machines/{machine_id}/state
GET /api/v1/machines/{machine_id}/telemetry
GET /api/v1/machines/{machine_id}/alerts
```

## Tasks

```http
POST /api/v1/tasks
GET /api/v1/tasks/{task_id}
PATCH /api/v1/tasks/{task_id}
POST /api/v1/tasks/{task_id}/assign
POST /api/v1/tasks/{task_id}/start
POST /api/v1/tasks/{task_id}/pause
POST /api/v1/tasks/{task_id}/resume
POST /api/v1/tasks/{task_id}/complete
```

## Assignment

```http
POST /api/v1/assignments
PATCH /api/v1/assignments/{assignment_id}
```

## Safety

```http
POST /api/v1/safety/events
GET /api/v1/safety/events/{event_id}
POST /api/v1/safety/events/{event_id}/acknowledge
```

## Prediction

```http
POST /api/v1/predictions/task-time
POST /api/v1/predictions/risk
POST /api/v1/predictions/anomaly
```

## Training

```http
GET /api/v1/training/recommendations/{operator_id}
POST /api/v1/training/{training_id}/start
POST /api/v1/training/sessions/{session_id}/complete
```

(Path namespaced under `/sessions/` so it can't collide with `/training/{training_id}/…`. Full ownership-annotated list: `docs/architecture/contracts/API_CATALOG.md`.)

## Copilot

```http
POST /api/v1/copilot/query
POST /api/v1/copilot/voice
```

## Scenario

```http
POST /api/v1/scenarios
GET /api/v1/scenarios/{scenario_id}
POST /api/v1/scenarios/{scenario_id}/run
```

---

# 36. WEBSOCKET ARCHITECTURE

Example:

```text
/ws/operators/{operator_id}
/ws/machines/{machine_id}
/ws/sites/{site_id}
```

Operator receives:

```text
SAFETY_ALERT
TASK_UPDATE
TASK_ETA_UPDATED
HAZARD_UPDATE
MACHINE_STATE_UPDATE
COPILOT_PROACTIVE_MESSAGE
TRAINING_RECOMMENDATION
```

---

# 37. EVENT-DRIVEN ARCHITECTURE

Avoid direct point-to-point coupling whenever events are appropriate.

Suggested topics:

```text
operator.events
machine.telemetry
machine.state
task.events
assignment.events
safety.events
hazard.events
site.events
prediction.events
training.events
copilot.events
```

Example event:

```json
{
  "event_id": "uuid",
  "event_type": "operator.task.assigned",
  "version": "1.0",
  "timestamp": "2026-09-23T08:00:00Z",
  "site_id": "SITE_A",
  "operator_id": "OP1001",
  "task_id": "TASK123",
  "machine_id": "EXC001"
}
```

---

# 38. EVENT FLOW EXAMPLES

## Task assignment

```text
Supervisor/Admin
    ↓
Assignment API
    ↓
Assignment persisted
    ↓
operator.task.assigned
    ↓
Operator projection
    ↓
Task visible in operator UI
    ↓
Task-time prediction
    ↓
Shift briefing updated
```

## Safety event

```text
Sensor
    ↓
Edge Gateway
    ↓
Local Safety Engine
    ↓
hazard/safety event
    ↓
Operator WebSocket
    ↓
Immediate alert
```

Parallel:

```text
Event
    ↓
Cloud event stream
    ↓
Historical storage
    ↓
Behavior / Analytics
```

## Training recommendation

```text
Behavior Engine
    ↓
Skill Gap
    ↓
Training Recommendation
    ↓
training.recommended
    ↓
Operator UI
```

---

# 39. EDGE-CLOUD ARCHITECTURE

## Edge responsibilities

- device ingestion,
- protocol adapters,
- proximity calculations,
- safety rules,
- local ML where latency matters,
- local buffering,
- offline operation,
- event replay.

## Cloud responsibilities

- historical analytics,
- fleet learning,
- ML training,
- task prediction at scale,
- training analytics,
- RAG/LLM,
- reporting,
- federated aggregation,
- centralized configuration.

## Offline flow

```text
Cloud unavailable
       ↓
Edge continues safety
       ↓
Local event buffer
       ↓
Connectivity returns
       ↓
Replay events
       ↓
Deduplicate by event_id
       ↓
Cloud state catches up
```

---

# 40. IDE / AGENT INDEPENDENT DEVELOPMENT MODEL

The team may use:

- Codex CLI,
- Claude CLI,
- Antigravity,
- local IDE copilots,
- human development.

They must all obey the same repository contracts.

## Per-tool entry files

```text
AGENTS.md    canonical rules. Codex CLI and Antigravity read it; edit rules ONLY here
CLAUDE.md    Claude Code entry: imports @AGENTS.md
GEMINI.md    Gemini/Antigravity pointer to AGENTS.md
```

Setup per tool and ready-made starter prompts: `docs/development/AGENT_PLAYBOOK.md`.

## Agent reading order

Every coding agent should read:

```text
1. AGENTS.md
2. README.md
3. docs/product/PRODUCT_PRINCIPLES.md
4. docs/development/PARALLEL_WORKFLOW.md
5. docs/architecture/REPOSITORY_STRUCTURE.md          (which paths the module may edit)
6. docs/architecture/SYSTEM_ARCHITECTURE.md     (as needed)
7. docs/development/workstreams/MXX-*.md and workstream status     (relevant module)
8. relevant contracts: contracts/** + docs/architecture/contracts/*.md
```

## Agent rule

Do not ask another teammate to finish a dependency if a contract/mock can unblock the work.

Every agent session starts with `python scripts/status.py changes` (what changed since the last pull) and ends with a proposed `python scripts/status.py log --module MXX --action PUSH ...` (see §116).

---

# 41. MODULAR DEVELOPMENT STRATEGY

## Fundamental rule

Only two modules are mandatory prerequisites:

```text
MODULE 00 — FOUNDATION
MODULE 01 — OPERATIONAL TWIN
```

After those are stable, the team should branch into independent modules.

## Dependency structure

```text
                 MODULE 00
                FOUNDATION
                     │
                     ▼
                 MODULE 01
            OPERATIONAL TWIN
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
       M02          M03          M04
   Operator UX   Admin UX     IoT Mesh
        │            │            │
        └────────────┼────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
       M05          M06          M07
   Site Intel      ML        Copilot
        │            │            │
        └────────────┼────────────┘
                     │
             ┌───────┴───────┐
             ▼               ▼
            M08             M09
         Training       Counterfactual
             │               │
             └───────┬───────┘
                     ▼
                    M10
               Federated ML
                     │
                     ▼
                    M11
             Analytics/Research
```

## Reading the diagram correctly (added 2026-09-23)

- The arrows are **contract** dependencies, not "wait until the code is finished" dependencies. After Gate G1 (M00 + M01 contracts frozen at v1), every module can be built in parallel against **mocks**.
- Every module's first work package is **WP0: contract + service/schemas functions + mocks**, so consumers are unblocked within about a day of a module starting.
- M00 and M01 are themselves split into work packages that live in **different folders**, so 3–5 people can build the base together without conflicts (`docs/development/PARALLEL_WORKFLOW.md` §3).
- Parallel safety comes from **one owner per path** (`docs/architecture/REPOSITORY_STRUCTURE.md`), **auto-discovery** of backend modules, **pre-registered frontend slots**, per-module migrations/compose/env files, and **per-module status files** (MODULAR_WORKFLOW §5).
- Phases are "start no earlier than" hints. Module boundaries and WPs can be refined; the refinement process is in MODULAR_WORKFLOW §8.

---

# 42. MODULE INVENTORY

## M00 — FOUNDATION

Purpose:

Create the stable technical substrate.

Owns:

- repository conventions,
- environment management,
- backend shell,
- frontend shell,
- database connection,
- migrations,
- Redis,
- event bus abstraction,
- authentication,
- basic RBAC,
- logging,
- error handling,
- health checks,
- CI baseline,
- shared domain identifiers,
- master data (users, operators, machines, sites, zones),
- backend module registry (auto-discovery of `backend/app/domain/*/wiring.py`),
- WebSocket gateway,
- frontend app shells with pre-registered feature slots,
- contracts baseline (common schemas, event envelope),
- status tooling (`scripts/status.py`).

Spec and work packages: `docs/development/workstreams/M00-foundation.md`.

Does NOT own:

- domain intelligence,
- final operator UX,
- ML,
- IoT behavior,
- training.

---

# 43. M01 — OPERATIONAL TWIN

Purpose:

Create the shared operator-machine-task-environment context model.

Owns:

- twin state,
- context fusion,
- current state,
- state projection,
- state history,
- twin snapshots,
- twin query API,
- **core task domain**: tasks, assignments, task sessions, machine confirmation, pre-operation checks (resolves §57),
- telemetry ingestion,
- simulator core (other modules add scenarios under `backend/app/iot/simulator/scenarios/<theme>.py`),
- environment/weather adapter.

The twin's intelligence-layer fields (risk, ETA, anomaly, safety) are **filled by events** from M04/M06 and are nullable, so M01 is complete at G1 without them.

Spec and work packages: `docs/development/workstreams/M01-operational-twin.md`.

Consumes:

- M00 entities,
- telemetry,
- operator events,
- task events,
- environmental signals,
- site/device events.

Produces:

- operational twin state,
- normalized context,
- twin update events.

Does NOT own:

- final safety decision,
- model training,
- copilot,
- training recommendation,
- site operational optimization.

---

# 44. M02 — OPERATOR EXPERIENCE

Owns:

- operator web/mobile UI,
- My Day,
- My Machine,
- My Tasks,
- My Safety,
- My Performance,
- My Training,
- Copilot UI shell,
- live state visualization,
- proactive notification UI.

Consumes:

- Twin API,
- task APIs,
- safety events,
- predictions,
- training recommendations,
- Copilot outputs.

Does NOT own:

- ML calculations,
- database truth,
- safety decisions.

---

# 45. M03 — SUPERVISOR/ADMIN CONSOLE

Owns:

- operator CRUD,
- machine CRUD,
- site CRUD,
- assignment,
- tasks,
- deadlines,
- resources/assistance,
- site map,
- site state,
- operational insights visualization,
- configuration screens.

Consumes:

- operational twin,
- hazard events,
- operational intelligence,
- task services.

Does NOT own:

- ML implementation,
- IoT sensor algorithms,
- Copilot reasoning.

---

# 46. M04 — IOT HAZARD MESH

Owns:

- BLE/UWB integration abstraction,
- wearable devices,
- machine tags,
- site edge gateway,
- proximity engine,
- zone logic,
- local safety rules,
- local device state.

Produces:

- proximity events,
- hazard events,
- zone events,
- device state.

Must be independently testable with simulated device data.

---

# 47. M05 — SITE OPERATIONAL INTELLIGENCE

Owns:

- machine interaction graph,
- queue analytics,
- fleet balance,
- machine utilization,
- site bottleneck detection,
- material-flow relationships,
- site throughput intelligence,
- dispatch insights,
- operational recommendations.

Consumes:

- twin state,
- hazard mesh events,
- telemetry,
- task state.

---

# 48. M06 — OPERATOR INTELLIGENCE / ML

Owns:

- operator baselines,
- anomaly model,
- risk model,
- task-time predictor,
- feature engineering,
- skill estimation interfaces,
- model registry/inference adapters,
- explainability metadata.

Must publish stable model contracts.

---

# 49. M07 — COPILOT

Owns:

- tool registry,
- agent orchestration,
- intent routing,
- multilingual interaction,
- voice input/output,
- RAG,
- LLM integration,
- conversation context,
- proactive notification generation.

Must enforce:

```text
Operational factual answer
    ↓
Tool call
    ↓
Authoritative result
    ↓
LLM explanation
```

---

# 50. M08 — TRAINING

Owns:

- training catalogue,
- training modules,
- training sessions,
- assessments,
- skill gaps,
- training recommendations,
- training impact measurement,
- operator learning history.

---

# 51. M09 — COUNTERFACTUAL ENGINE

Owns:

- scenario definitions,
- state modifications,
- simulation,
- model invocation,
- safety constraint evaluation,
- scenario comparison,
- uncertainty reporting.

---

# 52. M10 — FEDERATED INTELLIGENCE

Later-stage module.

Owns:

- local FL client,
- local training process,
- model update generation,
- secure aggregation strategy,
- central aggregator,
- model version distribution,
- site model lifecycle.

Never expose raw site logs to central aggregation under the proposed federated architecture.

---

# 53. M11 — ANALYTICS & EVALUATION

Owns:

- system metrics,
- safety metrics,
- model metrics,
- training impact,
- operational KPIs,
- experiment tracking,
- research evaluation.

---

# 54. MODULE CONTRACT TEMPLATE

Every module specification must use this structure. A ready-to-copy version is in `docs/development/workstreams/` (SPEC.md + workstream status), and all twelve module specs (M00–M11) exist under `docs/development/workstreams/`.

```md
# Module X — Name

## Objective

## Why This Module Exists

## Scope

## Out of Scope

## Inputs

## Outputs

## Owned Components

## APIs

## Events Consumed

## Events Produced

## Database Ownership

## External Dependencies

## Mock Interfaces

## Internal Architecture

## Acceptance Criteria

## Testing

## Future Extensions

## Known Constraints

## Integration Checklist
```

---

# 55. PARALLEL TEAM ALLOCATION

> The allocation actually in use (names, handles, slot holders, per-phase plan) lives in `docs/development/TEAM_AND_OWNERSHIP.md`, which also includes Phase 0/1 work-package splits so nobody is idle while the base is built. The tables below are the original starting point.

## Team of 3

### Person A

```text
M00
M01
Contracts
Data foundation
```

### Person B

```text
M02
M07
M08
```

### Person C

```text
M03
M04
M05
M06
```

## Team of 4

### Person A

Platform + Operational Twin

### Person B

Operator UX + Copilot + Training

### Person C

IoT + Site Intelligence + Admin

### Person D

ML + Counterfactual + Evaluation

## Team of 5

### Person A

M00 + M01 + API/Data/Event contracts

### Person B

M02 + M07

### Person C

M03 + M04

### Person D

M05 + M06 + M09

### Person E

M08 + M10 + M11 + research/evaluation

---

# 56. MOCK-FIRST DEVELOPMENT

Cross-module work must not block on unfinished dependencies.

Example:

Copilot can use:

```python
predict_task_duration(...)
```

from a mock implementation before the real model exists.

Example mocked response:

```json
{
  "p50": 92,
  "p80": 104,
  "p90": 111,
  "confidence": 0.82,
  "factors": [
    {
      "name": "wet_soil",
      "impact_minutes": 7
    },
    {
      "name": "idle_trend",
      "impact_minutes": 4
    }
  ]
}
```

Once M06 is ready, the implementation is swapped behind the contract.

---

# 57. DATABASE OWNERSHIP RULE

One module owns the write behavior for a table/entity.

Other modules consume via:

- API,
- events,
- read models,
- approved shared repository interfaces.

Avoid multiple modules directly mutating the same tables.

Example:

```text
Operator master data → M00/platform ownership
Task/assignment → M01 (core task domain lives in the Operational Twin module)
Twin state → M01
Hazard events → M04
Predictions → M06
Training → M08
Copilot conversations → M07
```

Exact implementation may evolve, but ownership must be explicit. The full table-by-table list is in `docs/architecture/contracts/DATA_OWNERSHIP.md`.

## 57.1 Ownership decisions for cross-cutting capabilities (added 2026-09-23)

| Capability | Owner | Notes |
|------------|-------|-------|
| WHY? Engine / root-cause attribution ("Don't blame the operator") | M06 | Uses site evidence from M05 (`site_intel.bottleneck.detected`) and context from M01 |
| Safety decision + safety index | M04 | Deterministic rules at the edge; M06 risk is evidence only |
| Notification policy (priority, dedupe, anti-spam) | M07 | CRITICAL safety alerts are delivered by M04 regardless of the Copilot |
| Shift briefing / huddle | M02 | Composed client-side from M01, M04, M06, M08 APIs |
| Pre-operation check | M01 | Part of the task-session lifecycle |
| Telemetry ingestion + simulator core | M01 | Scenario plugins owned per module |
| Copilot tools | Owner of the underlying data | M07 owns the registry and orchestration (`docs/architecture/contracts/TOOL_AND_ML_CONTRACTS.md`) |
| Frontend feature slots (copilot, training, site-intel, scenarios, analytics) | App owner (M02/M03) pre-registers; slot is delegable to the feature module | `docs/architecture/REPOSITORY_STRUCTURE.md` §3 |

---

# 58. EVENT OWNERSHIP RULE

Events should have:

- source owner,
- version,
- schema,
- producer,
- consumers,
- idempotency behavior.

Every event has:

```text
event_id
event_type
event_version
timestamp
site_id
source_id
payload
```

No silent event schema changes.

---

# 59. DATA FLOW — COMPLETE

```text
PHYSICAL WORLD
│
├── Machine
├── Operator
├── Worker
├── Site
├── Environment
└── Other Machines
        │
        ▼
INGESTION
│
├── CAN/J1939 adapters
├── BLE/UWB
├── mobile/web actions
└── environmental sources
        │
        ▼
EDGE
│
├── normalization
├── local state
├── local safety rules
├── proximity detection
└── buffering
        │
        ▼
EVENT / STREAM LAYER
        │
        ▼
CONTEXT FUSION
        │
        ▼
HUMAN-MACHINE OPERATIONAL TWIN
        │
        ├── Safety
        ├── Productivity
        ├── Behavior
        ├── Environment
        └── Site interactions
        │
        ▼
INTELLIGENCE ENGINES
│
├── Anomaly
├── Risk
├── ETA
├── Skill
├── Site efficiency
└── Root cause
        │
        ▼
DECISION / ASSISTANCE
│
├── Safety alert
├── Coaching
├── Prediction
├── Training
├── What-if scenario
└── Copilot response
        │
        ▼
HUMAN DECISION
        │
        ▼
OUTCOME
        │
        ▼
LEARNING LOOP
```

---

# 60. OPERATOR LEARNING LOOP

```text
Real operation
     ↓
Behavior observation
     ↓
Pattern / skill gap
     ↓
Personalized intervention
     ↓
Training / coaching
     ↓
Post-training assessment
     ↓
Real-world monitoring
     ↓
Behavior change
     ↓
Training impact
     ↓
Updated operator profile
```

---

# 61. TRAINING PHILOSOPHY

“Operator training” means:

> Improving the operator’s safe and effective use of equipment through targeted instruction, practice, scenario learning, and measurable post-training behavioral improvement.

It is not simply an LMS.

## Training categories

1. Safety & compliance
2. Machine familiarization
3. Operational efficiency
4. Skill-based operation
5. Site-specific briefing
6. Incident-triggered learning

## Formats

- micro-learning,
- interactive simulation,
- scenario assessment,
- guided checklists,
- machine familiarization,
- instructor-led integration in future.

---

# 62. TRAINING RECOMMENDATION EXAMPLES

```text
3 seatbelt violations in 7 days
→ Safe Excavator Operation

Cycle time +20% above personal baseline for 10 tasks
→ Cycle Optimization

Idle +30% above personal baseline with no site explanation
→ Idle Management

New machine assignment
→ Machine Familiarization

New site assignment
→ Site Safety Briefing

Near-miss involving worker proximity
→ Working Around Personnel
```

---

# 63. TRAINING IMPACT

Use:

```text
Before
   ↓
Intervention
   ↓
After
```

Example:

```text
Before training
Seatbelt compliance = 89%
Idle = 42 min

Training
Safe & Efficient Operation

After training
Seatbelt compliance = 98%
Idle = 27 min
```

Report:

```text
Observed safety compliance change: +9 percentage points
Observed idle change: -15 minutes
```

Do not claim causation without an appropriate experimental design.

---

# 64. OPERATOR SKILL GRAPH

A richer future representation:

```text
                OPERATOR X
                     │
       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
    SAFETY       MACHINE        EFFICIENCY
       │          SKILLS            │
   ┌───┼───┐    ┌──┼───┐       ┌───┼───┐
   ↓   ↓   ↓    ↓  ↓   ↓       ↓   ↓   ↓
Seat Prox Emerg Pos Cycle Load Idle Fuel Task
belt imity            Ops  handling
```

Each skill can contain:

```text
mastery probability
confidence
evidence
last observed
training history
trend
```

---

# 65. DYNAMIC MICRO-COACHING

Not every signal should become an alert.

Use:

```text
Critical
  → Immediate alert

High
  → Operator action

Medium
  → Coaching

Low
  → Analytics / learning
```

Example:

```text
💡 COACHING TIP

Your last five cycles are ~8 seconds slower
than your normal baseline.

Try optimizing machine positioning.
```

---

# 66. SHIFT HUDDLE

Before starting the day:

```text
GOOD MORNING OP1001

Machine:
EXC001

Task:
Excavation — Zone A

Conditions:
Wet soil
High truck traffic
31°C

Watch-outs:
Pedestrian crossing
Soft ground in Zone B

Estimated duration:
2h 15m

Today's focus:
Safe positioning
Minimize unnecessary idle

[START SHIFT]
```

This gives the product a daily operating ritual.

---

# 67. “WHAT CHANGED?” VIEW

The system should summarize:

```text
WHAT CHANGED SINCE YESTERDAY?

Safety compliance       +4%
Task efficiency         +8%
Idle time              -12 min

New condition:
Wet soil

Training:
Safe Operation completed
```

---

# 68. OPERATIONAL SCENARIO — EXCAVATOR + TWO DUMPERS

Use this as one of the flagship demos.

## Current site

```text
Excavator E1
Dumper D1
Dumper D2
Disposal Zone
```

System observes:

```text
E1 loading cycle: 5.5 min

D1 queue: 1 min
D2 queue: 7 min

Disposal congestion:
HIGH
```

Machine interaction graph identifies:

```text
D2
 ↓
queue
 ↓
disposal zone
 ↓
system delay
```

Supervisor sees:

```text
Bottleneck:
Disposal Zone

Impact:
18 min/hour estimated non-productive time

Affected:
E1, D2
```

Then Supervisor asks:

> What happens if D2 is reassigned?

Counterfactual engine simulates.

This is the site intelligence story.

---

# 69. SITE MAP UX

The Supervisor/Admin map should display:

```text
Machines
Operators
Workers
Hazard zones
Restricted zones
Task zones
Machine routes
Proximity alerts
Congestion
Weather/environment
```

Map layers should be togglable.

Avoid cluttering the default state.

Recommended default:

```text
Active machines
Active operator/task
Critical hazards
Current task zones
Major site conditions
```

---

# 70. MACHINE-TO-MACHINE / DEVICE COMMUNICATION

## Safety mode

Local:

```text
Machine ↔ Machine
Machine ↔ Worker
```

used for proximity/hazard detection.

## Operational mode

Avoid N² communication.

Instead:

```text
Device
  ↓
Event
  ↓
Site event fabric
  ↓
Operational state
  ↓
Interaction graph
  ↓
Decision engine
```

This is scalable and easier to reason about.

---

# 71. FEDERATED FLEET INTELLIGENCE

## Product idea

Sites retain their operational histories locally.

Each site trains local model updates.

A central aggregator combines model updates.

```text
Site A local data
      ↓
Local model update ──┐
                     │
Site B local data    │
      ↓              │
Local model update ──┼──► Aggregator
                     │
Site C local data    │
      ↓              │
Local model update ──┘
            ↓
        Global model
            ↓
   redistributed to sites
```

## Potential use

### Collaborative hazard detection

A terrain/weather/machine-age pattern observed at one site can improve the global model.

### Collaborative task prediction

Aggregate learned patterns without centralizing raw logs.

## Important

Federated learning is a later module and should not be faked as production privacy.

Document:

- threat model,
- secure aggregation assumptions,
- update leakage risk,
- model poisoning considerations,
- privacy limits.

---

# 72. RESEARCH FRAMING

A defensible research contribution should focus on the integrated mechanism rather than making sweeping “first-ever” claims.

Potential central research proposition:

> A context-aware human-machine operational model that jointly represents operator behavior, machine state, task context, environmental conditions, and site interactions for personalized safety, productivity prediction, and adaptive skill development.

Potential research questions:

### RQ1

Does adding operator/task/environment context improve anomaly detection compared with machine-only baselines?

### RQ2

Does contextual feature fusion improve task-time prediction accuracy?

### RQ3

Does context-aware root-cause attribution reduce false attribution to operators?

### RQ4

Does behavior-driven personalized training lead to measurable behavioral improvement?

### RQ5

Does edge-first safety reduce alert latency and improve availability under network interruption?

### RQ6

Can operational interaction graphs improve dispatch/bottleneck detection?

---

# 73. BASELINE VS PROPOSED MODEL

A strong experiment should compare:

## Baseline

```text
Machine telemetry only
```

against:

## Proposed

```text
Machine
+
Operator
+
Task
+
Environment
+
Site interaction context
```

Then measure differences.

---

# 74. EVALUATION METRICS

## Safety

- precision,
- recall,
- F1,
- false alert rate,
- mean alert latency,
- critical alert miss rate.

## Anomaly

- precision,
- recall,
- F1,
- false positives,
- detection delay.

## Task prediction

- MAE,
- RMSE,
- MAPE where appropriate,
- R²,
- prediction interval coverage.

## Training

- completion rate,
- assessment score,
- observed pre/post changes,
- behavior recurrence,
- retention.

## System

- p50/p95 latency,
- throughput,
- event loss,
- recovery time,
- offline continuity,
- WebSocket delivery latency.

---

# 75. DEMO STORY

The demo should be a narrative, not a list of features.

## Scene 1 — Morning

Operator logs in.

System shows:

```text
Assigned machine
Tasks
Shift briefing
Environmental conditions
Estimated task durations
```

## Scene 2 — Start operation

Pre-check passes.

## Scene 3 — Live operation

Telemetry appears.

## Scene 4 — Hazard

Worker enters proximity.

Edge system generates alert.

Operator gets voice/dashboard notification.

## Scene 5 — Delay

Task ETA changes.

Copilot explains why.

## Scene 6 — Root cause

System determines delay is site-driven rather than operator-driven.

## Scene 7 — Repeated behavior

Operator later shows repeated idle pattern.

Training is recommended.

## Scene 8 — Training

Operator completes a micro-learning module.

## Scene 9 — Impact

Next tasks show improvement.

## Scene 10 — Supervisor decision

Supervisor sees machine interaction graph and operational bottleneck.

## Scene 11 — Counterfactual

Supervisor asks:

> “What if I move Dumper D2?”

Scenario engine answers with productivity + safety implications.

## Scene 12 — Research/future

Federated fleet learning shows how model improvements can propagate across sites without centralizing raw logs.

---

# 76. WHAT MAKES THIS NOT A BASIC MVP?

The platform should be perceived as:

### Not

```text
IoT dashboard
+
chatbot
+
ML predictor
```

### But

```text
A shared operational intelligence layer
                    ↓
Human-Machine Operational Twin
                    ↓
specialized intelligence
                    ↓
closed-loop operator assistance
                    ↓
measurable operator development
                    ↓
site-level operational decisions
```

---

# 77. PRODUCT DIFFERENTIATION HIERARCHY

## Tier 1 — Core

- Operational Twin
- Operator-first UX
- Live safety
- Task management
- Task ETA
- Behavior analytics
- Training

## Tier 2 — Strong differentiators

- WHY? Engine
- Don't Blame the Operator
- Grounded voice copilot
- Multilingual interaction
- Site Awareness Mesh
- Machine Interaction Graph
- Safe Productivity decision layer

## Tier 3 — Research/advanced

- Counterfactual simulation
- Federated learning
- Bayesian skill mastery
- intervention impact modelling
- richer temporal models.

---

# 78. SYSTEM ARCHITECTURE — REFERENCE

```text
                         ┌───────────────────────────┐
                         │    OPERATOR EXPERIENCE    │
                         │                           │
                         │ My Day                    │
                         │ My Machine                │
                         │ My Safety                 │
                         │ My Tasks                  │
                         │ My Performance            │
                         │ My Training               │
                         │ Copilot                   │
                         └─────────────┬─────────────┘
                                       │
                                  REST / WS
                                       │
                         ┌─────────────▼─────────────┐
                         │        API GATEWAY        │
                         └─────────────┬─────────────┘
                                       │
           ┌───────────────────────────┼──────────────────────────┐
           │                           │                          │
           ▼                           ▼                          ▼
     Task / Assignment            Safety Service             Copilot Service
           │                           │                          │
           └───────────────────────────┼──────────────────────────┘
                                       │
                              Operational Twin
                                       │
              ┌────────────────────────┼─────────────────────────┐
              │                        │                         │
              ▼                        ▼                         ▼
         Site Intelligence       Operator ML               Training
              │                        │                         │
              └────────────────────────┼─────────────────────────┘
                                       │
                                 Event Fabric
                                       │
                      ┌────────────────┼────────────────┐
                      ▼                ▼                ▼
                  PostgreSQL       Time-series       Redis
                      │                │                │
                      └────────────────┼────────────────┘
                                       │
                                  Data Lake
                                       │
                                  ML Training
                                       │
                                 Fleet Learning

                 EDGE / SITE LAYER
                 ─────────────────

Machine ─┐
Worker ──┼─ BLE/UWB ─► Edge Gateway ─► Local Safety
Device ──┘                         └──► Event Stream
```

---

# 79. SECURITY ARCHITECTURE

Minimum:

```text
OIDC/OAuth2
JWT
RBAC
Site scope
TLS
Encryption at rest
Audit logs
Secrets management
Device identity
mTLS for machine/edge communication where applicable
```

## Safety security principle

Do not allow an ordinary frontend/API compromise to bypass safety rules at the edge.

---

# 80. PRIVACY PRINCIPLES

Operator behavior data should be handled carefully.

Principles:

- least privilege,
- data minimization,
- access logging,
- purpose limitation,
- role/scope-based access,
- clear separation between safety support and punitive HR workflows.

Do not create an employee “score” that hides the underlying evidence.

Show the evidence and context.

---

# 81. OBSERVABILITY

Every service should expose:

```text
/health
/ready
/version
/metrics
```

Log with:

```text
request_id
trace_id
operator_id where appropriate
machine_id where appropriate
site_id
event_id
model_version where appropriate
```

Never log secrets or unnecessary sensitive payloads.

---

# 82. TESTING STRATEGY

## Unit tests

- rules,
- domain logic,
- feature calculations,
- permissions,
- serializers.

## Contract tests

- API contract,
- event schema,
- ML interface,
- Copilot tool interface.

## Integration tests

- assignment → operator,
- telemetry → twin,
- hazard → alert,
- training → operator.

## Simulation tests

Create deterministic machine/worker scenarios.

Example:

```text
EXC001 speed = 8
worker distance = 5m
worker closing speed = 2m/s
```

Expected:

```text
HIGH proximity risk
```

## Offline edge test

Turn off cloud connectivity.

Expected:

```text
Local safety still functions.
```

---

# 83. DATA SIMULATION

Because real industrial sensor data may not be available, build a simulator.

The simulator should support:

```text
normal operation
high idle
seatbelt violation
worker proximity
machine proximity
wet soil
queueing
dumper shortage
machine slowdown
task delay
task completion
```

It should be deterministic with a seed so demos and tests are repeatable.

---

# 84. SAMPLE SIMULATION SCENARIOS

## S1 Normal

```text
Seatbelt true
Speed normal
No proximity
Idle normal
```

## S2 Seatbelt

```text
Seatbelt false
Machine moving
```

## S3 Worker hazard

```text
Worker enters operating radius
Closing velocity high
```

## S4 Site bottleneck

```text
Dumper D1/D2 arrive irregularly
Disposal zone congested
Excavator waits
```

## S5 Operator drift

```text
Idle > baseline
Cycle time > baseline
No external cause
```

## S6 Environmental delay

```text
Wet soil
Cycle time increases
No operator deviation
```

---

# 85. FEATURE STORE / CONTEXT FEATURES

Useful derived features:

```text
idle_deviation_personal
idle_deviation_machine
idle_deviation_site

cycle_time_deviation_personal
cycle_time_deviation_machine

fuel_efficiency_deviation

recent_safety_event_count
recent_proximity_event_count

task_progress_rate
task_remaining_work

operator_machine_familiarity
operator_task_familiarity

site_congestion
machine_queue_time

environmental_difficulty

time_since_last_training
training_mastery_probability
```

This is more valuable than feeding raw telemetry indiscriminately.

---

# 86. MODEL EXPLAINABILITY

Use SHAP or an equivalent explainability mechanism for tabular models when suitable.

Expose:

```text
prediction
confidence
major contributors
data freshness
model version
```

Example:

```text
ETA = 87 min
Confidence = 84%

Top contributors:
Wet soil +7m
Idle +4m
Machine age +1m
Operator baseline -2m
```

---

# 87. CONFIDENCE-AWARE DESIGN

The system should distinguish:

```text
High confidence
Moderate confidence
Low confidence
```

Low confidence might occur when:

- new machine,
- new operator,
- new task,
- insufficient history,
- missing environmental data.

Example:

> “Estimated duration: 87 minutes. Confidence is moderate because limited history exists for this machine/task combination.”

---

# 88. COLD START STRATEGY

If operator history does not exist:

```text
Personal history
     ↓ unavailable
Machine history
     ↓
Site history
     ↓
Task history
     ↓
Fleet prior
```

As data accumulates:

```text
Fleet
 ↓
Site
 ↓
Machine
 ↓
Operator
```

This is an important ML/product behavior.

---

# 89. API / EVENT / DATABASE CONTRACT AS SOURCE OF TRUTH

The repository should contain both human-readable and machine-readable contracts.

Recommended:

```text
contracts/
├── openapi/mXX-*.yaml      one OpenAPI file per module (avoids a single shared file everyone edits)
├── schemas/common/         shared ids, event envelope, error, pagination (M00)
├── schemas/twin/           Operational Twin schema (M01)
├── events/mXX/             event payload schemas, foldered by PRODUCING module
├── tools/                  Copilot tool schemas (owned by the module owning the data)
└── ml/                     ML inference input/output schemas (M06)
```

The markdown docs explain the intent.

The contract files define exact structure.

Versioning, the breaking-change process, mocks and contract tests: `docs/architecture/contracts/CONTRACTS_GUIDE.md`. Catalogs: `API_CATALOG.md`, `EVENT_CATALOG.md`, `DATA_OWNERSHIP.md`, `TOOL_AND_ML_CONTRACTS.md` in the same folder.

---

# 90. CHANGE MANAGEMENT RULE

If anyone wants to change:

- an API field,
- entity name,
- event name,
- event schema,
- database ownership,
- ML output,
- Copilot tool name,

they must:

1. update the contract,
2. document compatibility impact,
3. update dependent module docs,
4. add/update tests,
5. communicate the change.

Do not silently break another teammate's module.

---

# 91. GIT / BRANCH STRATEGY

Suggested:

```text
main                               demo-ready; merged from develop at each gate, tagged g0…g4
develop                            integration branch; all PRs target it
feature/mXX-wpY-short-name         e.g. feature/m04-wp2-proximity-rules
contract/mXX-short-name            contract-only changes (owner + a consumer review)
fix/mXX-short-name
docs/short-name
```

Commit format: `mXX(wpY): imperative summary`. Full rules: `CONTRIBUTING.md`.

Prefer small PRs.

PR should state:

```text
Module
Change
Contract changes
Dependencies
Tests
Screenshots/demo if UI
```

---

# 92. DEFINITION OF DONE

A module is not done merely because code exists.

Definition of done:

```text
[ ] Scope completed
[ ] Out-of-scope respected
[ ] Contract defined
[ ] Unit tests
[ ] Integration/contract tests where appropriate
[ ] Error handling
[ ] Logging/observability
[ ] Mock dependency support
[ ] Documentation updated
[ ] Local startup verified
[ ] No accidental cross-module ownership
[ ] Demo path verified
[ ] Module workstream status updated (see §116)
```

Levels (work package, module, contract change, safety-relevant change): `docs/development/DEFINITION_OF_DONE.md`. Gate checklists: `docs/development/INTEGRATION_CHECKPOINTS.md`.

---

# 93. PHASED EXECUTION PLAN

## PHASE 0 — FOUNDATION

Goal:

Make the repository runnable and establish contracts.

Deliver:

- repo structure,
- backend shell,
- frontend shell,
- PostgreSQL,
- Redis,
- event bus,
- auth,
- basic domain entities,
- migrations,
- OpenAPI,
- event schemas,
- test framework,
- CI.

Exit criteria:

```text
Clone repository
    ↓
Run one command
    ↓
Frontend + backend + DB + Redis + event bus available
```

---

# 94. PHASE 1 — OPERATIONAL CORE

Goal:

Build the first usable end-to-end operator data context.

Deliver:

- Operator,
- Machine,
- Site,
- Task,
- Assignment,
- Task Session,
- telemetry simulator,
- context fusion,
- first Twin API,
- live machine state.

Exit criteria:

```text
Supervisor/Admin assigns OP1001 → EXC001 → TASK001
               ↓
Operator sees assignment
               ↓
Simulator sends telemetry
               ↓
Twin updates
               ↓
Operator sees current state
```

This is the first true vertical slice.

---

# 95. PHASE 2 — PARALLEL PRODUCT BUILD

Teams work independently on:

```text
M02 Operator UX
M03 Supervisor/Admin Console
M04 IoT Hazard Mesh
M06 Operator ML
```

Use mocks where dependencies are unfinished.

---

# 96. PHASE 3 — INTELLIGENCE + COPILOT + TRAINING

Build:

```text
M05 Site Intelligence
M07 Copilot
M08 Training
```

Integrate with outputs from Phase 2.

---

# 97. PHASE 4 — ADVANCED INTELLIGENCE

Build:

```text
M09 Counterfactual Engine
M10 Federated Intelligence
M11 Analytics/Evaluation
```

Only do M10 if the core product works convincingly first.

---

# 98. PRIORITY STACK

## P0 — Essential

```text
Operator authentication
Machine assignment
Tasks
Pre-check
Live telemetry
Operational Twin
Safety event
Task-time prediction
Basic operator UX
Basic Supervisor/Admin console
```

## P1 — Differentiation

```text
WHY? Engine
Behavior anomaly
Voice Copilot
Multilingual Copilot
IoT Hazard Mesh
Training recommendation
Training impact
Site machine interaction
```

## P2 — Advanced

```text
Counterfactual engine
Federated learning
Bayesian skill model
advanced temporal models
rich simulation
```

---

# 99. HARD CUT RULE

If time is running out:

### Keep

```text
Operational Twin
Operator UX
Live safety
Task prediction
WHY? Engine
Grounded Copilot
One strong training loop
One strong site interaction scenario
```

### Cut/Reduce

```text
Full federated production implementation
Large training catalogue
Many ML models
Complex admin analytics
Complex maintenance
```

A coherent system beats many shallow features.

---

# 100. FINAL REFERENCE OPERATOR SCENARIO

```text
08:00
Operator logs in

08:01
Machine confirmed

08:02
Pre-check passes

08:03
Shift briefing

08:05
Task starts

08:15
Normal operation

08:28
Worker enters hazard radius

08:28
Edge safety alert

08:29
Operator corrects situation

09:10
Task ETA updates

09:11
Operator asks:
“Why is my task running late?”

09:11
Copilot calls:
predict_task_duration()
get_site_conditions()
get_machine_state()

09:11
Copilot explains:
wet soil + higher idle + site queue

10:30
Task completes

10:31
Performance summary

10:32
Repeated idle behavior detected across prior tasks

10:32
Training recommendation generated

10:35
Operator completes micro-learning

10:43
Assessment

Next days
Behavior monitored

Following week
Training impact shown
```

---

# 101. FINAL REFERENCE SUPERVISOR/ADMIN SCENARIO

```text
07:30
Supervisor/Admin logs in

07:31
Creates/updates task

07:32
Assigns OP1001 → EXC001

07:32
Operator receives task

08:00
Site map shows active machines

09:00
Operational graph detects:
Dumper D2 queueing

09:01
WHY? Engine attributes delay to disposal-zone congestion

09:02
Supervisor asks:
“What if I move D2?”

09:03
Counterfactual engine simulates

09:03
Result:
Throughput opportunity
+
Safety constraint analysis

09:04
Supervisor makes human decision

09:10
System monitors outcome
```

---

# 102. THE PRODUCT FLYWHEEL

```text
          REAL OPERATION
                 │
                 ▼
        OPERATIONAL TWIN
                 │
                 ▼
        CONTEXTUAL UNDERSTANDING
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
      SAFETY  PRODUCTIVITY SKILLS
        │        │        │
        └────────┼────────┘
                 ▼
             ASSISTANCE
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
      ALERT   PREDICT   COACH
                 │
                 ▼
          HUMAN DECISION
                 │
                 ▼
              OUTCOME
                 │
                 ▼
              LEARN
                 │
                 ▼
         UPDATED OPERATOR
             PROFILE
                 │
                 ▼
       BETTER FUTURE ASSISTANCE
```

---

# 103. THE SITE FLYWHEEL

```text
Machines + People + Tasks + Environment
                  │
                  ▼
            Site Awareness
                  │
                  ▼
        Machine Interaction Graph
                  │
                  ▼
       Bottleneck / Hazard Detection
                  │
                  ▼
          Counterfactual Analysis
                  │
                  ▼
        Supervisor/Admin Decision
                  │
                  ▼
               Outcome
                  │
                  ▼
         Better Site Intelligence
```

---

# 104. THE OVERALL PLATFORM LOOP

```text
                     OPERATOR LOOP
                           │
                           ▼
                 Human-Machine Twin
                           │
                           ▼
                    Intelligence
                           │
                           ▼
                       Copilot
                           │
                           ▼
                   Operator Action
                           │
                           ▼
                    Behavior Change
                           │
                           └─────────────┐
                                         │
                                         ▼
                                    Twin Update

                     SITE LOOP
                           │
                           ▼
                    Site Awareness
                           │
                           ▼
                 Operational Graph
                           │
                           ▼
                   Decision Engine
                           │
                           ▼
                Supervisor/Admin Decision
                           │
                           ▼
                        Outcome
                           │
                           └──────────────► Site Update
```

---

# 105. ONE-LINE ARCHITECTURE PITCH

> **One Operational Twin, multiple specialized intelligence engines, one grounded Operator Copilot, and a continuous feedback loop from real-world outcomes back into the system.**

---

# 106. ONE-LINE PRODUCT PITCH

> **We are moving construction equipment software from machine monitoring to operator intelligence: understanding the human-machine-task-environment context, assisting decisions in real time, and continuously developing safer and more efficient operators.**

---

# 107. ONE-LINE RESEARCH PITCH

> **We investigate whether contextual human-machine-task-environment modeling can improve operational prediction, anomaly detection, explanation, and adaptive operator development compared with machine-only approaches.**

---

# 108. ARCHITECTURE PRINCIPLES FOR FUTURE AI AGENTS

When an AI agent is asked to implement anything in this repository:

1. First identify the module.
2. Identify module ownership.
3. Read the relevant contracts.
4. Identify upstream and downstream interfaces.
5. Prefer an adapter/mock if an upstream dependency is unfinished.
6. Never silently change shared schemas.
7. Do not place safety-critical reasoning inside the LLM.
8. Do not allow the Copilot to invent operational facts.
9. Do not create a second competing source of truth.
10. Keep implementation modular enough to replace components.
11. Preserve the operator-first product principle.
12. Add tests before or with integration work.
13. Update documentation when behavior or contracts change.
14. When ambiguous, preserve the existing architecture and document the ambiguity instead of inventing major new architecture.
15. Optimize for a coherent end-to-end vertical slice before adding breadth.

---

# 109. FINAL DECISION FRAMEWORK FOR NEW FEATURES

For every proposed feature, ask:

### Product

- Does this help the operator?
- Does it help the Supervisor/Admin support the operator/site?
- Does it improve safety, productivity, understanding, or learning?

### Architecture

- Which module owns it?
- What does it consume?
- What does it produce?
- Does it introduce a new shared contract?

### AI

- Does the feature actually require ML?
- Is deterministic logic safer?
- What data supports the model?
- What confidence/uncertainty is involved?
- How is the result explained?

### UX

- Does this reduce cognitive load?
- Can an operator use it with gloves/hands busy?
- Can it work via voice?
- Is the information actionable?

### Safety

- What happens if the cloud is unavailable?
- Is an unsafe state possible if this component fails?

### Research

- What hypothesis does this enable?
- What baseline will it be compared against?
- How will success be measured?

### Scalability

- Does the design work for one machine?
- Can it conceptually scale to many machines/sites?
- Is it event-driven where appropriate?

---

# 110. FINAL NORTH STAR

The project should ultimately feel like:

```text
                         OPERATOR
                            │
                            ▼
                  “What is happening?”
                            │
                            ▼
               HUMAN-MACHINE OPERATIONAL
                         TWIN
                            │
                            ▼
                   “Why is it happening?”
                            │
                            ▼
                     WHY? ENGINE
                            │
                            ▼
                “What happens next?”
                            │
                            ▼
                  PREDICTION ENGINE
                            │
                            ▼
                  “What should I do?”
                            │
                            ▼
                     COPILOT
                            │
                            ▼
                  HUMAN DECISION
                            │
                            ▼
                “Did it actually help?”
                            │
                            ▼
                 TRAINING / LEARNING
                            │
                            ▼
                    BETTER OPERATOR
```

And at the site level:

```text
Machines + Workers + Operators + Tasks + Environment
                        │
                        ▼
                 SITE AWARENESS
                        │
                        ▼
             MACHINE INTERACTION GRAPH
                        │
                        ▼
            BOTTLENECK / HAZARD / FLOW
                        │
                        ▼
              DECISION ENGINE
                        │
                        ▼
               SUPERVISOR/ADMIN
                        │
                        ▼
                  HUMAN ACTION
                        │
                        ▼
                 SITE OUTCOME
```

---

# 111. FINAL IMPLEMENTATION ORDER

The recommended implementation sequence is:

```text
PHASE 0
Foundation
    ↓
PHASE 1
Operational Twin
    ↓
PHASE 2
Parallel:
    Operator UX
    Supervisor/Admin
    IoT Hazard Mesh
    Operator ML
    ↓
PHASE 3
    Site Intelligence
    Copilot
    Training
    ↓
PHASE 4
    Counterfactual
    Federated Intelligence
    Research Evaluation
```

The architecture should remain modular enough that any one advanced module can be delayed or replaced without collapsing the core.

---

# 112. NON-GOALS

Unless explicitly added later, do not make the project about:

- autonomous machine control,
- generic fleet-management software,
- generic HR performance scoring,
- generic LMS,
- unrestricted chatbot,
- predictive maintenance as the primary product,
- fully autonomous dispatch,
- raw telemetry visualization as the main value proposition.

Those may exist as supporting capabilities but are not the product thesis.

---

# 113. FINAL SUCCESS CRITERIA

The project is successful when a reviewer/judge can understand all of the following from one coherent demo:

1. A Supervisor/Admin assigns a machine and task to an operator.
2. The operator immediately receives that context.
3. The operator has a live Operational Twin.
4. A real-time hazard can be detected at the edge.
5. The system explains why an alert or prediction occurred.
6. The task-time predictor adapts to operator/machine/context.
7. The Copilot retrieves real operational facts via tools.
8. The Copilot can communicate by voice and in multiple languages.
9. Persistent operator behavior can trigger personalized training.
10. Training impact can be measured through subsequent operation.
11. Multiple machines can form a site interaction graph.
12. The Supervisor/Admin can use that graph to understand bottlenecks and evaluate scenarios.
13. The architecture remains modular and scalable.
14. The research evaluation can compare contextual intelligence against machine-only baselines.
15. Advanced privacy-preserving fleet learning can be added without rewriting the core.

---

# 114. MASTER PRINCIPLE

> **The platform should not merely observe work. It should understand work, assist work, learn from work, and use what it learns to make the next operation safer and more effective.**

---

# 115. STATUS / CHANGE LOG TEMPLATE

Use this section to track major architectural changes.

```text
Date:
Decision:
Why:
Affected modules:
Contract changes:
Migration needed:
Owner:
Status:
```

## Change log

```text
Date:              2026-09-23
Decision:          Introduced the multi-IDE modular workflow documentation set: AGENTS.md (canonical) + CLAUDE.md/GEMINI.md
                   pointers, docs/ tree (principles, workflow, repo ownership, contracts catalogs, 12 module SPEC/STATUS
                   pairs, sync protocol, gates, DoD, agent playbook), scripts/status.py, .github templates.
                   Resolved ownership: task/assignment/session/pre-check → M01; WHY? engine → M06; notification policy → M07;
                   shift briefing → M02 (client-side composition); Copilot tools → data-owning module.
                   Event contracts foldered by producing module (contracts/events/<area>/); one OpenAPI file per module.
                   (superseded by ADR-0002: capabilities are used via service/schemas; WP0 = contract + facade + mocks.
                   Proposed default stack in ADR-0001 (status PROPOSED).
Why:               3–5 people working in parallel across Antigravity, Claude CLI, Codex CLI need identical rules,
                   one owner per path, and conflict-free status tracking on every push/pull.
Affected modules:  all
Contract changes:  none yet (establishes layout and conventions)
Migration needed:  no
Owner:             team
Status:            ACCEPTED (docs); ADR-0001 PROPOSED
```

---

# 116. PARALLEL WORKFLOW & STATUS PROTOCOL (SUMMARY)

The full method is in `docs/development/PARALLEL_WORKFLOW.md`. The short version:

```text
PHASE 0  M00 Foundation (5 WPs in separate folders; whole team)     → Gate G0: one command runs everything
PHASE 1  M01 Operational Twin (WP0 contracts on day 1)                → Gate G1: vertical slice + contracts v1 FROZEN
PHASE 2+ M02 M03 M04 M06 → M05 M07 M08 → M09 M10 M11                  → Gates G2–G4 = demo scenes 1–12
         all in parallel, talking only through contracts/ + service interfaces + mocks
```

**The parallel-work rules:** one owner per path · cross-module communication via contracts only · mock-first (WP0) · one writer per table/event · additive-by-default contract changes · register by discovery (no central file edits) · status marked on every push and pull · safety logic deterministic in M04.

**Status marking (every teammate, every agent):**

```text
Before push:  python scripts/status.py log --module MXX --action PUSH --msg "..." [--wp MXX-WPn=STATE]
              → updates docs/development/workstreams/MXX-*.md + your sync log; commit it WITH the code
After pull:   python scripts/status.py changes            → contract changes + teammates' new log lines
              python scripts/status.py log --action PULL --msg "..."   → your own sync log only
Anytime:      python scripts/status.py board              → live board of all modules
```

Each status file has exactly one writer (module owner or the person themselves), so status tracking never causes merge conflicts. Details: `docs/development/SYNC_PROTOCOL.md`.

