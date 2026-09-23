"""Seed demo data into the configured database: ``python -m backend.seed``.

Each module that has demo data exposes ``async def seed(session)`` in ``backend/modules/<m>/seed.py``;
this runner discovers and calls them in module order (no central edits needed).
"""

from __future__ import annotations

import asyncio
import importlib
import pkgutil

import backend.core.audit  # noqa: F401
import backend.modules as modules_pkg
from backend.core.config import get_settings
from backend.core.db import Database
from backend.core.registry import import_all_models


async def main() -> None:
    settings = get_settings()
    import_all_models()
    db = Database(settings.database_url)
    if settings.db_auto_create:
        await db.create_all()
    for info in sorted(pkgutil.iter_modules(modules_pkg.__path__), key=lambda i: i.name):
        try:
            mod = importlib.import_module(f"{modules_pkg.__name__}.{info.name}.seed")
        except ModuleNotFoundError:
            continue
        fn = getattr(mod, "seed", None) or getattr(mod, "seed_platform", None)
        if fn:
            async with db.sessionmaker() as s:
                await fn(s)
            print(f"seeded {info.name}")
    await db.dispose()


if __name__ == "__main__":
    asyncio.run(main())
