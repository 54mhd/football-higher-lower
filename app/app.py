# app/routers/game_router.py

import logging
import time
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.schema import (
    HealthResponse,
    RandomPlayersResponse,
    VerifyRequest,
    VerifyResponse,
)
from app.services.game_services import GameService


logger = logging.getLogger(__name__)


app = FastAPI(title="Higher or Lower - Football Edition")


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


@app.get("/game", response_class=HTMLResponse)
async def game_page() -> HTMLResponse:
    root = Path(__file__).resolve().parents[1]
    frontend_path = root / "game.html"
    if frontend_path.exists():
        return FileResponse(frontend_path)
    html = """<!DOCTYPE html><html><head><title>Higher or Lower - Game</title></head>
    <body><h1>Game page not found</h1>
    <p>Please add game.html to the project root.</p></body></html>"""
    return HTMLResponse(content=html)


@app.get("/api/player/random", response_model=RandomPlayersResponse)
async def get_random_players(
    session: AsyncSession = Depends(get_async_session),
) -> RandomPlayersResponse:
    try:
        return await GameService.get_two_random_players(session)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/game/verify", response_model=VerifyResponse)
async def verify_game(
    payload: VerifyRequest,
    session: AsyncSession = Depends(get_async_session),
) -> VerifyResponse:
    try:
        return await GameService.verify_guess(session, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
