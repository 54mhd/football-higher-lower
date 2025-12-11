import csv
from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Player


def _build_avatar_url(name: str) -> str:
    """Generate an avatar URL for a player using a public avatar service.

    We rely on robohash.org, which produces a deterministic image per input
    string, so each player gets a unique image without storing real photos.
    """

    safe_name = quote_plus(name.strip() or "Player")
    # robohash.org generates unique avatars based on the text
    return f"https://robohash.org/{safe_name}.png?set=set5&bgset=bg1"


async def import_players_from_csv(session: AsyncSession, csv_path: Path) -> None:
    """Import or refresh players in the database from a CSV source.

    CSV format:
    name,image_url,stat_value

    Колонка image_url читается, но игнорируется: мы всегда генерируем
    детерминированный avatar-URL из имени игрока, чтобы не зависеть от
    внешних ссылок в файле.
    """

    if not csv_path.exists():
        return

    # naive approach: clear table and re-fill for demo/demo purposes
    await session.execute(Player.__table__.delete())

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        players: list[Player] = []
        for row in reader:
            name = (row.get("name") or "").strip()
            try:
                stat_value = int((row.get("stat_value") or "0").strip())
            except ValueError:
                stat_value = 0

            if not name:
                continue

            image_url = _build_avatar_url(name)

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
