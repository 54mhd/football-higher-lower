import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.db import Player
from app.services.game_services import GameService


class _Base(DeclarativeBase):
    pass


@pytest.fixture()
async def memory_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    class LocalPlayer(Player.__bases__[0]):  # reuse mapped attributes via inheritance base
        __tablename__ = "players"
        __table__ = Player.__table__

    async with engine.begin() as conn:
        await conn.run_sync(Player.metadata.create_all)

    async with async_session() as session:
        p1 = Player(name="Player A", image_url="http://example.com/a.jpg", stat_value=10)
        p2 = Player(name="Player B", image_url="http://example.com/b.jpg", stat_value=20)
        session.add_all([p1, p2])
        await session.commit()
        yield session


@pytest.mark.asyncio
async def test_get_two_random_players(memory_session):
    resp = await GameService.get_two_random_players(memory_session)
    assert len(resp.players) == 2


@pytest.mark.asyncio
async def test_verify_guess(memory_session):
    resp = await GameService.get_two_random_players(memory_session)
    left, right = resp.players

    result = await GameService.verify_guess(
        memory_session,
        payload=type("Obj", (), {
            "player_left_id": left.id,
            "player_right_id": right.id,
            "guess": "right",
        })(),
    )

    assert isinstance(result.correct, bool)
    assert result.left_value >= 0
    assert result.right_value >= 0
