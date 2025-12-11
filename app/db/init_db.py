import asyncio
from pathlib import Path

from app.db import Player, async_session_maker, create_db_and_tables
from app.services.player_importer import import_players_from_csv


async def init_db() -> None:
    await create_db_and_tables()

    csv_path = Path(__file__).resolve().parent / "players_source.csv"

    async with async_session_maker() as session:
        existing = (await session.execute(Player.__table__.select())).scalars().first()
        if existing:
            return

        # Import players from the CSV source (commits internally)
        await import_players_from_csv(session, csv_path)


if __name__ == "__main__":
    asyncio.run(init_db())
