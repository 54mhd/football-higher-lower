import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.app import app
from app.db import Base, Player, Question, get_async_session
from app.services.trivia_services import TriviaService
from app.schema import TriviaVerifyRequest


@pytest_asyncio.fixture()
async def session_maker(tmp_path, monkeypatch):
    db_url = f"sqlite+aiosqlite:///{tmp_path}/test.db"
    monkeypatch.setenv("DATABASE_URL", db_url)

    engine = create_async_engine(db_url, future=True)
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield Session

    await engine.dispose()


@pytest_asyncio.fixture()
async def client(session_maker):
    async def override_get_async_session():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_async_session] = override_get_async_session
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


async def seed_players(session: AsyncSession):
    session.add_all(
        [
            Player(name="Player A", image_url="http://example.com/a.jpg", stat_value=10),
            Player(name="Player B", image_url="http://example.com/b.jpg", stat_value=20),
        ]
    )
    await session.commit()


async def seed_questions(session: AsyncSession):
    session.add_all(
        [
            Question(
                question_text="Who won the 2018 World Cup?",
                option_a="France",
                option_b="Croatia",
                option_c="Germany",
                option_d="Brazil",
                correct_answer="A",
                difficulty="easy",
                category="World Cup",
            ),
            Question(
                question_text="Which club has the most UCL titles?",
                option_a="Barcelona",
                option_b="Real Madrid",
                option_c="AC Milan",
                option_d="Liverpool",
                correct_answer="B",
                difficulty="medium",
                category="Champions League",
            ),
        ]
    )
    await session.commit()


@pytest.mark.asyncio
async def test_health_endpoint(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_random_players_and_verify(session_maker, client):
    async with session_maker() as session:
        await seed_players(session)

    r1 = await client.get("/api/player/random")
    assert r1.status_code == 200
    players = r1.json()["players"]
    assert len(players) == 2

    left, right = players
    payload = {
        "player_left_id": left["id"],
        "player_right_id": right["id"],
        "guess": "left",
    }
    r2 = await client.post("/api/game/verify", json=payload)
    assert r2.status_code == 200
    body = r2.json()
    assert set(body.keys()) == {"correct", "left_value", "right_value"}


@pytest.mark.asyncio
async def test_trivia_count_and_question_exclude(session_maker, client):
    async with session_maker() as session:
        await seed_questions(session)

    count_resp = await client.get("/api/trivia/count")
    assert count_resp.status_code == 200
    assert count_resp.json()["total_questions"] == 2

    first = await client.get("/api/trivia/question")
    assert first.status_code == 200
    first_id = first.json()["question"]["id"]

    second = await client.get(f"/api/trivia/question?exclude={first_id}")
    assert second.status_code == 200
    assert second.json()["question"]["id"] != first_id


@pytest.mark.asyncio
async def test_trivia_verify(session_maker, client):
    async with session_maker() as session:
        await seed_questions(session)

    q_resp = await client.get("/api/trivia/question")
    question = q_resp.json()["question"]

    async with session_maker() as session:
        stored = (
            await session.execute(select(Question).where(Question.id == question["id"]))
        ).scalar_one()
        correct_letter = stored.correct_answer

    verify = await client.post(
        "/api/trivia/verify",
        json={"question_id": question["id"], "selected_answer": correct_letter},
    )
    assert verify.status_code == 200
    result = verify.json()
    assert result["correct"] is True
    assert result["correct_answer"] == correct_letter
    assert "explanation" in result


@pytest.mark.asyncio
async def test_trivia_service_verify_answer(session_maker):
    async with session_maker() as session:
        await seed_questions(session)
        q = (await session.execute(select(Question).limit(1))).scalar_one()

        correct = await TriviaService.verify_answer(
            session, TriviaVerifyRequest(question_id=q.id, selected_answer="A")
        )
        wrong = await TriviaService.verify_answer(
            session, TriviaVerifyRequest(question_id=q.id, selected_answer="C")
        )

    assert correct.correct is True
    assert wrong.correct is False
    assert wrong.correct_answer == q.correct_answer
