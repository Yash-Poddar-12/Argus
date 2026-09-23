"""Seed demo data into the configured database: ``python -m backend.seed``.

Each module that has demo data exposes ``async def seed(session)`` in ``backend/modules/<m>/seed.py``;
``seed_all`` discovers and calls them in module order (no central edits needed).
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


async def seed_all(db: Database, verbose: bool = False) -> list[str]:
    seeded = []
    for info in sorted(pkgutil.iter_modules(modules_pkg.__path__), key=lambda i: i.name):
        try:
            mod = importlib.import_module(f"{modules_pkg.__name__}.{info.name}.seed")
        except ModuleNotFoundError as exc:
            if exc.name != f"{modules_pkg.__name__}.{info.name}.seed":
                raise
            continue
        if fn := getattr(mod, "seed", None):
            async with db.sessionmaker() as s:
                await fn(s)
            seeded.append(info.name)
            if verbose:
                print(f"seeded {info.name}")
    return seeded


async def main() -> None:
    settings = get_settings()
    import_all_models()
    db = Database(settings.database_url)
    if settings.db_auto_create:
        await db.create_all()
    await seed_all(db, verbose=True)
    await db.dispose()


if __name__ == "__main__":
    asyncio.run(main())
