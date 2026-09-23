"""Idempotent demo master data using the canonical IDs from docs/00-project/GLOSSARY.md.

Dev/demo only: every demo user's password is ``demo1234``.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import hash_password
from backend.modules.m00_platform.models import Machine, Operator, Site, User, UserSiteScope, Zone

DEMO_PASSWORD = "demo1234"
SITE = {"site_id": "SITE_A", "name": "Site A (demo quarry)", "location": {"lat": 12.9716, "lon": 77.5946},
        "timezone": "Asia/Kolkata", "configuration": {"operating_radius_m": {"EXCAVATOR": 8, "DUMPER": 6}}}


def _square(lon: float, lat: float, d: float = 0.0006) -> dict:
    return {"type": "Polygon", "coordinates": [[[lon - d, lat - d], [lon + d, lat - d], [lon + d, lat + d],
                                                [lon - d, lat + d], [lon - d, lat - d]]]}


ZONES = [
    ("ZONE_A", "Excavation Zone A", "TASK", _square(77.5946, 12.9716)),
    ("ZONE_B", "Soft ground Zone B", "SOFT_GROUND", _square(77.5962, 12.9716)),
    ("ZONE_DISPOSAL", "Disposal Zone", "DISPOSAL", _square(77.5980, 12.9730)),
    ("ZONE_RESTRICTED_1", "Restricted: blasting store", "RESTRICTED", _square(77.5930, 12.9740, 0.0003)),
]
OPERATORS = [
    ("OP1001", "Ravi Kumar", "SENIOR", "hi"),
    ("OP1002", "Anita Rao", "INTERMEDIATE", "en"),
    ("OP1003", "Karthik S", "JUNIOR", "ta"),
]
MACHINES = [
    ("EXC001", "EXCAVATOR", "CAT 320", "CAT0320E1001", 4210.5),
    ("EXC002", "EXCAVATOR", "CAT 336", "CAT0336E2002", 2875.0),
    ("DMP001", "DUMPER", "CAT 745", "CAT0745D1001", 6120.0),
    ("DMP002", "DUMPER", "CAT 745", "CAT0745D2002", 5980.0),
]
USERS = [("op1001", "OPERATOR", "OP1001"), ("op1002", "OPERATOR", "OP1002"), ("op1003", "OPERATOR", "OP1003"),
         ("sup001", "SUPERVISOR_ADMIN", None)]


async def seed_platform(session: AsyncSession) -> None:
    if await session.get(Site, SITE["site_id"]) is None:
        session.add(Site(**SITE))
        await session.flush()
    for zone_id, name, zone_type, geometry in ZONES:
        if await session.get(Zone, zone_id) is None:
            session.add(Zone(zone_id=zone_id, site_id="SITE_A", name=name, zone_type=zone_type, geometry=geometry))
    for op_id, name, level, lang in OPERATORS:
        if await session.get(Operator, op_id) is None:
            session.add(Operator(operator_id=op_id, name=name, site_id="SITE_A", experience_level=level,
                                 preferred_language=lang))
    for m_id, m_type, model, serial, hours in MACHINES:
        if await session.get(Machine, m_id) is None:
            session.add(Machine(machine_id=m_id, site_id="SITE_A", machine_type=m_type, model=model,
                                serial_number=serial, engine_hours=hours))
    from sqlalchemy import select

    for username, role, op_id in USERS:
        user = await session.scalar(select(User).where(User.username == username))
        if user is None:
            user = User(username=username, password_hash=hash_password(DEMO_PASSWORD), role=role, operator_id=op_id)
            session.add(user)
            await session.flush()
            session.add(UserSiteScope(user_id=user.user_id, site_id="SITE_A"))
    await session.commit()


seed = seed_platform
