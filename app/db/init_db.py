import asyncio

from app.db import Player, async_session_maker, create_db_and_tables


async def init_db() -> None:
    await create_db_and_tables()

    async with async_session_maker() as session:
        existing = (await session.execute(Player.__table__.select())).scalars().first()
        if existing:
            return

        players = [
            Player(name="Lionel Messi", image_url="https://example.com/messi.jpg", stat_value=91),
            Player(name="Cristiano Ronaldo", image_url="https://example.com/ronaldo.jpg", stat_value=89),
            Player(name="Kylian Mbappé", image_url="https://example.com/mbappe.jpg", stat_value=88),
            Player(name="Erling Haaland", image_url="https://example.com/haaland.jpg", stat_value=87),
        ]
        session.add_all(players)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(init_db())
