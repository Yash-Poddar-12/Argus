"""Pure task-domain rules (no I/O): task lifecycle state machine, pre-check evaluation, progress."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal

TaskStatus = Literal["PLANNED", "ASSIGNED", "IN_PROGRESS", "PAUSED", "COMPLETED", "CANCELLED"]
Action = Literal["assign", "unassign", "start", "pause", "resume", "complete", "cancel"]

# (from_status, action) -> to_status
TRANSITIONS: dict[tuple[str, str], str] = {
    ("PLANNED", "assign"): "ASSIGNED",
    ("ASSIGNED", "assign"): "ASSIGNED",       # reassignment before start
    ("ASSIGNED", "unassign"): "PLANNED",
    ("ASSIGNED", "start"): "IN_PROGRESS",
    ("IN_PROGRESS", "pause"): "PAUSED",
    ("PAUSED", "resume"): "IN_PROGRESS",
    ("IN_PROGRESS", "complete"): "COMPLETED",
    ("PAUSED", "complete"): "COMPLETED",
    ("PLANNED", "cancel"): "CANCELLED",
    ("ASSIGNED", "cancel"): "CANCELLED",
}

PRECHECK_VALID_FOR = timedelta(hours=12)
CONFIRMATION_VALID_FOR = timedelta(hours=12)


class TransitionError(ValueError):
    def __init__(self, status: str, action: str):
        super().__init__(f"Cannot {action} a task in status {status}")
        self.status, self.action = status, action


def next_status(status: str, action: str) -> str:
    try:
        return TRANSITIONS[(status, action)]
    except KeyError as exc:
        raise TransitionError(status, action) from exc


def allowed_actions(status: str) -> list[str]:
    return sorted({a for (s, a) in TRANSITIONS if s == status})


@dataclass(frozen=True)
class PrecheckOutcome:
    passed: bool
    failed_items: list[str]
    missing_items: list[str]


def evaluate_precheck(template_items: list[dict], results: list[dict]) -> PrecheckOutcome:
    """Pass only if every item is answered and every CRITICAL item is ok. Non-critical failures are recorded."""
    answered = {r["item_id"]: bool(r["ok"]) for r in results}
    missing = [i["item_id"] for i in template_items if i["item_id"] not in answered]
    failed = [i["item_id"] for i in template_items if answered.get(i["item_id"]) is False]
    critical_failed = [i["item_id"] for i in template_items if i.get("critical") and answered.get(i["item_id"]) is False]
    return PrecheckOutcome(passed=not missing and not critical_failed, failed_items=failed, missing_items=missing)


def is_recent(ts: datetime | None, now: datetime, window: timedelta) -> bool:
    return ts is not None and now - ts <= window


def cycles_progress(target: dict, cycles_done: int | None) -> float | None:
    if target.get("unit") != "cycles" or cycles_done is None or not target.get("value"):
        return None
    return round(min(100.0, 100.0 * cycles_done / float(target["value"])), 1)


def active_seconds(actual_start: datetime, now: datetime, pause_duration_s: float, paused_at: datetime | None) -> float:
    paused = pause_duration_s + ((now - paused_at).total_seconds() if paused_at else 0.0)
    return max(0.0, (now - actual_start).total_seconds() - paused)
