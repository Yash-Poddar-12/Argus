"""Pure task-domain rules (no I/O): pre-check evaluation, recency windows, progress and active time."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

PRECHECK_VALID_FOR = timedelta(hours=12)


CONFIRMATION_VALID_FOR = timedelta(hours=12)


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
