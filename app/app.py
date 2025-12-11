# app/routers/game_router.py

import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, List

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_async_session,create_db_and_tables
from .db_init import init_db
from .db_init_trivia import seed_questions
from .schema import (
    CountResponse,
    HealthResponse,
    RandomPlayersResponse,
    RandomQuestionResponse,
    TriviaVerifyRequest,
    TriviaVerifyResponse,
    VerifyRequest,
    VerifyResponse,
)
from .services.game_services import GameService
from .services.trivia_services import TriviaService


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    # Startup - Initialize database with players and questions
    logger.info("Initializing database...")
    try:
        await init_db()
        logger.info("Players imported successfully")
    except Exception as e:
        logger.error(f"Error importing players: {e}")
    
    try:
        await seed_questions()
        logger.info("Questions seeded successfully")
    except Exception as e:
        logger.error(f"Error seeding questions: {e}")
    
    yield
    # Shutdown
    logger.info("Application shutting down")


app = FastAPI(title="Higher or Lower - Football Edition", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def request_timing_middleware(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "request completed",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
        },
    )
    return response


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    root = Path(__file__).resolve().parents[1]
    frontend_path = root / "index.html"
    if frontend_path.exists():
        return FileResponse(frontend_path)
    html = """<!DOCTYPE html><html><head><title>Higher or Lower</title></head>
    <body><h1>Higher or Lower - Football Edition</h1>
    <p>Landing page not found. Please add index.html to the project root.</p></body></html>"""
    return HTMLResponse(content=html)


@app.get("/games", response_class=HTMLResponse)
async def game_page() -> HTMLResponse:
    root = Path(__file__).resolve().parents[1]
    frontend_path = root / "game.html"
    if frontend_path.exists():
        return FileResponse(frontend_path)
    html = """<!DOCTYPE html><html><head><title>Higher or Lower - Game</title></head>
    <body><h1>Game page not found</h1>
    <p>Please add game.html to the project root.</p></body></html>"""
    return HTMLResponse(content=html)


@app.get("/trivia", response_class=HTMLResponse)
async def trivia_page() -> HTMLResponse:
    root = Path(__file__).resolve().parents[1]
    frontend_path = root / "trivia.html"
    if frontend_path.exists():
        return FileResponse(frontend_path)
    html = """<!DOCTYPE html><html><head><title>Football Trivia</title></head>
    <body><h1>Trivia page not found</h1>
    <p>Please add trivia.html to the project root.</p></body></html>"""
    return HTMLResponse(content=html)


@app.get("/api/player/random", response_model=RandomPlayersResponse)
async def get_random_players(
    session: AsyncSession = Depends(get_async_session),
) -> RandomPlayersResponse:
    try:
        return await GameService.get_two_random_players(session)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/games/verify", response_model=VerifyResponse)
async def verify_game(
    payload: VerifyRequest,
    session: AsyncSession = Depends(get_async_session),
) -> VerifyResponse:
    try:
        return await GameService.verify_guess(session, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/trivia/question", response_model=RandomQuestionResponse)
async def get_random_question(
    exclude: str | None = Query(
        default=None,
        description="Comma separated question IDs that have already been asked",
    ),
    session: AsyncSession = Depends(get_async_session),
) -> RandomQuestionResponse:
    try:
        exclude_ids: List[int] = []
        if exclude:
            exclude_ids = [int(x) for x in exclude.split(",") if x.strip().isdigit()]
        return await TriviaService.get_random_question(session, exclude_ids)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/trivia/count", response_model=CountResponse)
async def get_trivia_count(
    session: AsyncSession = Depends(get_async_session),
) -> CountResponse:
    return await TriviaService.get_question_count(session)


@app.post("/api/trivia/verify", response_model=TriviaVerifyResponse)
async def verify_trivia_answer(
    payload: TriviaVerifyRequest,
    session: AsyncSession = Depends(get_async_session),
) -> TriviaVerifyResponse:
    try:
        return await TriviaService.verify_answer(session, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
