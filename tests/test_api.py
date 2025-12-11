import pytest
from httpx import AsyncClient

from app.app import app
from app.db import create_db_and_tables


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_random_players_and_verify(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{tmp_path}/test.db")
    await create_db_and_tables()

    from app.db import async_session_maker, Player  # noqa: E402

    async with async_session_maker() as session:
        p1 = Player(name="Player A", image_url="http://example.com/a.jpg", stat_value=10)
        p2 = Player(name="Player B", image_url="http://example.com/b.jpg", stat_value=20)
        session.add_all([p1, p2])
        await session.commit()

    async with AsyncClient(app=app, base_url="http://test") as client:
        r1 = await client.get("/api/player/random")
        assert r1.status_code == 200
        data = r1.json()
        assert len(data["players"]) == 2

        left, right = data["players"]
        payload = {
            "player_left_id": left["id"],
            "player_right_id": right["id"],
            "guess": "left",
        }
        r2 = await client.post("/api/game/verify", json=payload)
        assert r2.status_code == 200
        body = r2.json()
        assert "correct" in body
        assert "left_value" in body
        assert "right_value" in body
