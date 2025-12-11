import asyncio
from pathlib import Path

from app.db import async_session_maker, create_db_and_tables
from app.services.player_importer import import_players_from_csv


async def init_db() -> None:
    await create_db_and_tables()

    root = Path(__file__).resolve().parents[1]
    csv_path = root / "db" / "players_source.csv"

    async with async_session_maker() as session:
        await import_players_from_csv(session, csv_path)


if __name__ == "__main__":
    asyncio.run(init_db())
