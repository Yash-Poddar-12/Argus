"""Pure context fusion (no I/O). Reused by M09 through public.py to build modified twins.

Inputs are plain dicts from the stores; output is the OperationalTwin document
(contracts/schemas/twin/operational-twin.json).
"""

from __future__ import annotations

from datetime import datetime

EXCAVATOR_MODES = ("DIGGING", "SWINGING", "DUMPING", "IDLE", "TRAVELLING", "OFF")
DUMPER_MODES = ("LOADING", "HAULING", "DUMPING", "RETURNING", "IDLE", "OFF")
INTEL_SLOTS = ("safety", "risk", "eta", "anomaly")


def iso(ts: datetime | str | None) -> str | None:
    if ts is None or isinstance(ts, str):
        return ts
    return ts.isoformat().replace("+00:00", "Z")


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def machine_state_from_telemetry(prev: dict | None, point: dict) -> dict:
    """Fold one telemetry point into the machine's live state (keeps a short idle window)."""
    prev = prev or {}
    if prev.get("ts") and prev["ts"] > point["ts"]:
        return prev  # late/out-of-order point: history is persisted, live state stays newest
    idle_ratio = None
    if prev.get("ts"):
        elapsed = (datetime.fromisoformat(point["ts"].replace("Z", "+00:00"))
                   - datetime.fromisoformat(prev["ts"].replace("Z", "+00:00"))).total_seconds()
        if elapsed > 0:
            idle_ratio = max(0.0, min(1.0, (point["idle_seconds"] - prev.get("idle_seconds", 0)) / elapsed))
    window = (prev.get("idle_window") or [])[-29:]
    if idle_ratio is not None:
        window.append(round(idle_ratio, 3))
    health = "OK"
    if point["temperature_c"] >= 105 or point["fuel_pct"] <= 5:
        health = "CRITICAL"
    elif point["temperature_c"] >= 95 or point["fuel_pct"] <= 15:
        health = "WARNING"
    return {
        "machine_id": point["machine_id"], "site_id": point["site_id"], "ts": point["ts"],
        "operating_mode": point["operating_mode"], "fuel_pct": point["fuel_pct"], "fuel_rate_lph": point["fuel_rate_lph"],
        "speed_kmh": point["speed_kmh"], "rpm": point["rpm"], "engine_hours": point["engine_hours"],
        "load_cycles": point["load_cycles"], "idle_seconds": point["idle_seconds"], "temperature_c": point["temperature_c"],
        "seatbelt": point["seatbelt"], "location": {"lat": point["lat"], "lon": point["lon"]}, "health": health,
        "idle_window": window,
    }


def environmental_difficulty(env: dict | None) -> str | None:
    if not env:
        return None
    score = 0
    score += {"WET": 1, "MUD": 2, "ROCKY": 1}.get(env.get("soil", ""), 0)
    score += 1 if (env.get("rain_mm_h") or 0) >= 2 else 0
    score += 2 if (env.get("rain_mm_h") or 0) >= 10 else 0
    score += {"MODERATE": 1, "POOR": 2}.get(env.get("visibility", ""), 0)
    score += 1 if (env.get("temperature_c") or 0) >= 40 else 0
    return "HIGH" if score >= 3 else "MEDIUM" if score >= 1 else "LOW"


def productivity_state(machine: dict | None, task_status: str | None) -> str | None:
    if not machine or task_status not in ("IN_PROGRESS", "PAUSED"):
        return None
    if task_status == "PAUSED":
        return "PAUSED"
    window = machine.get("idle_window") or []
    if len(window) < 5:
        return "NORMAL"
    recent = sum(window[-10:]) / len(window[-10:])
    return "HIGH_IDLE" if recent >= 0.6 else "NORMAL"


def familiarity(completed_sessions_on_machine_type: int) -> str:
    n = completed_sessions_on_machine_type
    return "HIGH" if n >= 5 else "MEDIUM" if n >= 1 else "LOW"


def build_twin(*, now: datetime, operator: dict, machine: dict | None, machine_state: dict | None, task: dict | None,
               session: dict | None, environment: dict | None, site: dict | None, intelligence: dict[str, dict],
               familiarity_level: str | None) -> dict:
    """Assemble the twin. Intelligence slots are nullable so the twin is valid without M04/M06."""
    task_block = None
    if task:
        cycles_done = None
        if session and machine_state and session.get("start_load_cycles") is not None:
            cycles_done = max(0, machine_state["load_cycles"] - session["start_load_cycles"])
        target = task["target"]
        progress = None
        if target.get("unit") == "cycles" and cycles_done is not None and target.get("value"):
            progress = round(min(100.0, 100.0 * cycles_done / float(target["value"])), 1)
        task_block = {
            "task_id": task["task_id"], "title": task["title"], "task_type": task["task_type"],
            "status": task["status"], "zone_id": task.get("zone_id"), "priority": task["priority"],
            "target": target, "cycles_done": cycles_done, "progress_pct": progress,
            "planned_start": iso(task["planned_start"]), "planned_end": iso(task["planned_end"]),
            "session_id": session.get("session_id") if session else None,
            "actual_start": iso(session.get("actual_start")) if session else None,
        }
    machine_block = None
    if machine:
        live = {k: v for k, v in (machine_state or {}).items() if k not in ("idle_window", "site_id", "machine_id")}
        machine_block = {"machine_id": machine["machine_id"], "machine_type": machine["machine_type"],
                         "model": machine["model"], **({"telemetry_at": live.pop("ts")} if "ts" in live else {}), **live}
    env_block = dict(environment) if environment else None
    telemetry_age = None
    if machine_state and machine_state.get("ts"):
        telemetry_age = round((now - datetime.fromisoformat(machine_state["ts"].replace("Z", "+00:00"))).total_seconds(), 1)
    env_age = None
    if environment and environment.get("as_of"):
        env_age = round((now - datetime.fromisoformat(environment["as_of"].replace("Z", "+00:00"))).total_seconds(), 1)
    ps = productivity_state(machine_state, task["status"] if task else None)
    return {
        "operator_id": operator["operator_id"],
        "machine_id": machine["machine_id"] if machine else None,
        "task_id": task["task_id"] if task else None,
        "site_id": operator["site_id"],
        "as_of": iso(now),
        "state": {
            "operator": {"name": operator["name"], "status": operator["status"],
                         "experience_level": operator["experience_level"],
                         "certification_status": operator["certification_status"],
                         "preferred_language": operator.get("preferred_language", "en"),
                         "machine_familiarity": familiarity_level},
            "machine": machine_block,
            "task": task_block,
            "environment": env_block,
            "site": site,
        },
        "intelligence": {
            **{slot: intelligence.get(slot) for slot in INTEL_SLOTS},
            "productivity": {"state": ps} if ps else None,
            "environmental_difficulty": environmental_difficulty(environment),
        },
        "freshness": {"telemetry_age_s": telemetry_age, "environment_age_s": env_age},
    }


def intelligence_from_event(event_type: str, payload: dict, timestamp: str) -> tuple[str, dict] | None:
    """Map another module's event to a twin intelligence slot. The twin stores results; it never computes them."""
    if event_type == "safety.event.raised":
        return "safety", {"level": payload.get("severity"), "event_type": payload.get("event_type"),
                          "safety_event_id": payload.get("safety_event_id"), "source": "M04", "as_of": timestamp}
    if event_type == "prediction.risk.updated":
        return "risk", {"level": payload.get("risk_level"), "probability": payload.get("risk_probability"),
                        "model_version": payload.get("model_version"), "source": "M06", "as_of": timestamp}
    if event_type == "prediction.task_time.updated":
        def q(n: int):
            return payload.get(f"p{n}_duration_min", payload.get(f"p{n}"))

        return "eta", {"task_id": payload.get("task_id"), "p50_duration_min": q(50),
                       "p80_duration_min": q(80), "p90_duration_min": q(90),
                       "predicted_completion_at": payload.get("predicted_completion_at"),
                       "confidence_level": payload.get("confidence_level"), "contributors": payload.get("contributors", []),
                       "model_version": payload.get("model_version"), "source": "M06", "as_of": timestamp}
    if event_type == "operator.anomaly.detected":
        return "anomaly", {"severity": payload.get("severity"), "score": payload.get("anomaly_score"),
                           "signals": payload.get("contributing_signals", []), "source": "M06", "as_of": timestamp}
    return None
