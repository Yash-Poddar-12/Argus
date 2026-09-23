import asyncio

from app.config import get_settings
from app.core.database import Database
from app.registry import import_all_models
from app.seed import seed_all


async def _main() -> None:
    settings = get_settings()
    import_all_models()
    db = Database(settings.database_url)
    if settings.db_auto_create:
        await db.create_all()
    await seed_all(db, verbose=True)
    await db.dispose()


def run() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    run()
