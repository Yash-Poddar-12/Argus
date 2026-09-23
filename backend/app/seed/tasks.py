"""Idempotent M01 demo data: pre-op checklist templates and today's tasks (docs/product/GLOSSARY.md IDs).

Tasks are created PLANNED and unassigned: Gate G1 starts with the supervisor assigning OP1001 -> EXC001 -> TASK001.
"""

from __future__ import annotations

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.tasks.models import PrecheckTemplate, Task

TEMPLATES = {
    "EXCAVATOR": [
        ("walkaround", "Walk-around: no leaks, damage or loose parts", True),
        ("tracks", "Tracks and undercarriage OK", True),
        ("bucket", "Bucket, teeth and pins secure", True),
        ("hydraulics", "Hydraulic hoses: no leaks or damage", True),
        ("seatbelt", "Seatbelt works and is undamaged", True),
        ("mirrors_camera", "Mirrors and camera clean and adjusted", True),
        ("horn_alarm", "Horn and travel alarm work", True),
        ("fluids", "Engine oil, coolant and fuel levels checked", False),
        ("cab_clean", "Cab clean, controls free of obstruction", False),
    ],
    "DUMPER": [
        ("walkaround", "Walk-around: no leaks, damage or loose parts", True),
        ("tyres", "Tyres: pressure and condition OK", True),
        ("brakes", "Service and parking brakes tested", True),
        ("body_hoist", "Body and hoist cylinders OK", True),
        ("seatbelt", "Seatbelt works and is undamaged", True),
        ("mirrors_camera", "Mirrors and camera clean and adjusted", True),
        ("lights_horn", "Lights, horn and reversing alarm work", True),
        ("fluids", "Engine oil, coolant and fuel levels checked", False),
    ],
    "DEFAULT": [
        ("walkaround", "Walk-around: no leaks, damage or loose parts", True),
        ("seatbelt", "Seatbelt works and is undamaged", True),
        ("horn_alarm", "Horn and alarms work", True),
        ("fluids", "Fluid levels checked", False),
    ],
}

# task_id, title, type, zone, priority, target, start (site-local hh:mm), duration min, assistance
TASKS = [
    ("TASK001", "Excavation — Zone A", "EXCAVATION", "ZONE_A", "HIGH", {"unit": "cycles", "value": 50}, (8, 0), 150,
     [{"kind": "MACHINE", "resource_id": "DMP002", "note": "Dumper D2 assists with haulage"}]),
    ("TASK002", "Trenching — Zone B (soft ground)", "TRENCHING", "ZONE_B", "MEDIUM", {"unit": "cycles", "value": 30},
     (11, 0), 120, []),
    ("TASK003", "Haulage to disposal", "HAULING", "ZONE_DISPOSAL", "MEDIUM", {"unit": "cycles", "value": 20}, (8, 0), 180, []),
]


async def seed(session: AsyncSession) -> None:
    for machine_type, items in TEMPLATES.items():
        tid = f"PRECHECK_{machine_type}"
        if await session.get(PrecheckTemplate, tid) is None:
            session.add(PrecheckTemplate(template_id=tid, machine_type=machine_type,
                                         items=[{"item_id": i, "label": label, "critical": c} for i, label, c in items]))
    tz = ZoneInfo("Asia/Kolkata")  # SITE_A timezone (m00 seed)
    today = datetime.now(tz).date()
    for task_id, title, ttype, zone, prio, target, (hh, mm), minutes, assistance in TASKS:
        if await session.get(Task, task_id) is None:
            start = datetime.combine(today, time(hh, mm), tzinfo=tz)
            session.add(Task(task_id=task_id, site_id="SITE_A", zone_id=zone, title=title, task_type=ttype, priority=prio,
                             target=target, planned_start=start, planned_end=start + timedelta(minutes=minutes),
                             assistance=assistance, status="PLANNED", created_by="seed"))
    await session.commit()
