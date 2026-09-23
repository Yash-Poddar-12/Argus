"""Pure task rules: lifecycle state machine and pre-check evaluation."""

import pytest

from app.domain.tasks import rules
from app.domain.tasks import state_machine as sm


def test_lifecycle_transitions():
    s = "PLANNED"
    for action, expected in [("assign", "ASSIGNED"), ("start", "IN_PROGRESS"), ("pause", "PAUSED"),
                             ("resume", "IN_PROGRESS"), ("complete", "COMPLETED")]:
        s = sm.next_status(s, action)
        assert s == expected
    for status, action in [("PLANNED", "start"), ("IN_PROGRESS", "resume"), ("COMPLETED", "pause"),
                           ("IN_PROGRESS", "cancel"), ("CANCELLED", "assign")]:
        with pytest.raises(sm.TransitionError):
            sm.next_status(status, action)
    assert sm.allowed_actions("IN_PROGRESS") == ["complete", "pause"]


def test_precheck_rules():
    items = [{"item_id": "seatbelt", "critical": True}, {"item_id": "cab_clean", "critical": False}]
    ok = rules.evaluate_precheck(items, [{"item_id": "seatbelt", "ok": True}, {"item_id": "cab_clean", "ok": False}])
    assert ok.passed and ok.failed_items == ["cab_clean"]
    bad = rules.evaluate_precheck(items, [{"item_id": "seatbelt", "ok": False}, {"item_id": "cab_clean", "ok": True}])
    assert not bad.passed
    missing = rules.evaluate_precheck(items, [{"item_id": "seatbelt", "ok": True}])
    assert not missing.passed and missing.missing_items == ["cab_clean"]
