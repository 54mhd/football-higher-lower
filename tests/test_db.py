import pytest

from app.db import Player, create_db_and_tables, async_session_maker, engine


@pytest.mark.asyncio
async def test_create_tables_and_insert_player(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{tmp_path}/test.db")
    await create_db_and_tables()

    async with async_session_maker() as session:
        player = Player(name="Test Player", image_url="http://example.com/x.jpg", stat_value=42)
        session.add(player)
        await session.commit()

        players = (await session.execute(Player.__table__.select())).scalars().all()
        assert len(players) == 1
        assert players[0].name == "Test Player"
