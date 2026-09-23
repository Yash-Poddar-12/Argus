"""Task lifecycle state machine (pure, no I/O)."""

from __future__ import annotations

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
