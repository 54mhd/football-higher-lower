import csv
from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy.ext.asyncio import AsyncSession
from app.db import Player


async def import_players_from_csv(session: AsyncSession, csv_path: Path) -> None:
    """
    Import players from CSV.

    CSV format:
    name,image_url,stat_value
    """

    if not csv_path.exists():
        return

    # Clear table for fresh import
    await session.execute(Player.__table__.delete())

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        players: list[Player] = []

        for row in reader:
            name = (row.get("name") or "").strip()
            if not name:
                continue

            # use CSV image_url
            image_url = (row.get("image_url") or "").strip()

            # fallback to robohash ONLY if CSV has no image
            if not image_url:
                safe = quote_plus(name)
                image_url = f"https://robohash.org/{safe}.png?set=set5&bgset=bg1"

            # stat value
            try:
                stat_value = int((row.get("stat_value") or "0").strip())
            except ValueError:
                stat_value = 0

            players.append(
                Player(
                    name=name,
                    image_url=image_url,
                    stat_value=stat_value,
                )
            )

    if players:
        session.add_all(players)
        await session.commit()
