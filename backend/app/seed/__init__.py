"""Demo data using the canonical IDs from docs/product/GLOSSARY.md. Run: ``python -m app.seed``.

Dev/demo only. Seeders run in dependency order and are idempotent.
"""

from __future__ import annotations

from app.core.database import Database
from app.seed import platform, tasks

SEEDERS = [("platform", platform.seed), ("tasks", tasks.seed)]


async def seed_all(db: Database, verbose: bool = False) -> list[str]:
    done = []
    for name, fn in SEEDERS:
        async with db.sessionmaker() as s:
            await fn(s)
        done.append(name)
        if verbose:
            print(f"seeded {name}")
    return done
