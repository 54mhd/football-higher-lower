# Football Games – Higher or Lower & Trivia

![CI](https://github.com/54mhd/football-higher-lower/actions/workflows/ci.yml/badge.svg)

A FastAPI web application featuring two games:
- Higher or Lower: compare two football players by a single stat
- Football Trivia: multiple‑choice quiz with categories and difficulty

## Project Goal

Present two players and let the user guess who has the higher `stat_value`. The logic is simplified to comparing one numeric metric. Additionally, offer a trivia quiz with four options per question.

## Tech Stack

- FastAPI (backend)
- SQLite (`test.db`) via SQLAlchemy async
- HTML + JavaScript (no frontend framework)
- Docker, docker-compose
- GitHub Actions (CI)

## Project Structure

```text
project/
├── app/
│   ├── app.py           # FastAPI app, routes, CORS, middleware
│   ├── db/
│   │   ├── init_db.py   # Initialize and seed players
│   │   └── seed_players.sql
│   ├── db.py            # SQLAlchemy models and DB config
│   ├── images.py        # ImageKit example client (optional)
│   ├── schema.py        # Pydantic schemas (API I/O)
│   └── services/
│       ├── game_services.py  # Higher or Lower logic
│       ├── trivia_services.py# Trivia logic
│       └── player_importer.py
├── index.html           # Game selection menu (home)
├── game.html            # Higher or Lower UI
├── trivia.html          # Trivia UI
├── main.py              # Dev entry point (uvicorn)
├── pyproject.toml       # Dependencies & metadata
├── README.md            # This documentation
├── test.db              # SQLite DB (dev)
├── uv.lock              # uv lockfile (if using uv)
├── tests/
│   ├── __init__.py
│   └── test_app.py      # API and service tests
├── Dockerfile
├── docker-compose.yml
└── .github/
  └── workflows/
    └── ci.yml       # CI: tests and Docker build
```

## Backend Architecture

- `app/app.py`
  - FastAPI app instance
  - CORS via `CORSMiddleware`
  - Request timing middleware
  - Endpoints:
    - `GET /health`
    - `GET /` → serves `index.html`
    - `GET /game` → serves `game.html`
    - `GET /trivia` → serves `trivia.html`
    - `GET /api/player/random`
    - `POST /api/game/verify`
    - `GET /api/trivia/question`
    - `POST /api/trivia/verify`

- `app/db.py`
  - SQLite via SQLAlchemy async
  - `DATABASE_URL` env var or default `sqlite+aiosqlite:///./test.db`
  - Models:
    - `Player(id, name, image_url, stat_value)`
    - `Question(id, question_text, option_a, option_b, option_c, option_d, correct_answer, difficulty, category)`
  - Helpers:
    - `create_db_and_tables()`
    - `get_async_session()` → FastAPI dependency for `AsyncSession`

- `app/db/init_db.py`
  - Initialize DB and seed sample players
  - Used locally and in Docker builds

- `app/db/seed_players.sql`
  - Optional SQL seed script for players

- `app/schema.py`
  - Higher or Lower: `PlayerOut`, `RandomPlayersResponse`, `VerifyRequest`, `VerifyResponse`
  - Trivia: `QuestionOut`, `RandomQuestionResponse`, `TriviaVerifyRequest`, `TriviaVerifyResponse`
  - Common: `HealthResponse`

- `app/services/game_services.py`
  - `get_two_random_players(session)` → select two random players
  - `verify_guess(session, payload)` → compare `stat_value`

## Frontend

- `index.html` — game selection menu (two cards: Higher or Lower, Trivia)
- `game.html` — Higher or Lower gameplay (two player cards, hidden values, left/right guess)
- `trivia.html` — Trivia gameplay (question + A/B/C/D options, difficulty, category)
- Uses `fetch` to call backend endpoints

## Security & Configuration

- CORS enabled via `CORSMiddleware` (allow‑all for dev; restrict in prod)
- Input validation via Pydantic models
- Env vars from `.env` using `python-dotenv`
  - `DATABASE_URL` for SQLite/other DB
  - Optional ImageKit keys in `app/images.py`

## Local Run (without Docker)

### 1. Install dependencies

```bash
pip install -e .
```

### 2. Initialize database (players)

```bash
python -m app.db.init_db
```

Additionally (Trivia questions):

```bash
python -m app.db_init_trivia
```

### 3. Start dev server

```bash
python main.py
```

App will be available at `http://localhost:8000`.
Home page: game selection (Higher or Lower / Trivia).

## Run via Docker

### 1. Build image

```bash
docker build -t higher-lower-app .
```

### 2. Run container

```bash
docker-compose up --build
```

- Backend at `http://localhost:8000`
- SQLite persisted via volume (e.g. `./data`)
- Container server: `gunicorn` with `uvicorn` worker

## Testing

Tests use `pytest` and cover:
- Service logic (Higher or Lower)
- API endpoints availability and correctness
- DB initialization & CRUD

Run tests:

```bash
pytest
```

## CI/CD (GitHub Actions)

Workflow `.github/workflows/ci.yml` performs:
1. Set up Python
2. Install dependencies (`pip install -e .`)
3. Run tests (`pytest`)
4. Build Docker image

Use this pipeline as a base for deployment to any Docker‑compatible hosting.

## Games

- Higher or Lower: compare two random players; guess who has higher `stat_value`; score and streak tracking
- Football Trivia: four options (A/B/C/D), categories and difficulty; score and streak; highlight correct answer

## Quick Start

1. Install deps: `pip install -e .`
2. Seed players: `python -m app.db.init_db`
3. Seed trivia (optional): `python -m app.db_init_trivia`
4. Run server: `python main.py`
5. Open `http://localhost:8000` and choose a game

Key API endpoints:
- Higher or Lower: `GET /api/player/random`, `POST /api/game/verify`
- Trivia: `GET /api/trivia/question`, `POST /api/trivia/verify`

To add more Trivia questions, edit `app/db_init_trivia.py` (`SAMPLE_QUESTIONS`) and re‑run: `python -m app.db_init_trivia`.

## Implementation Summary (from previous docs)

- Added Football Trivia game with multiple‑choice questions
- Extended DB with `Question` model (id, text, options A–D, correct_answer, difficulty, category)
- New endpoints: `GET /trivia`, `GET /api/trivia/question`, `POST /api/trivia/verify`
- Redesigned `index.html` as a game selection menu
- Responsive UI using Tailwind CSS via CDN

## Feature Highlights

- Random player selection (Higher or Lower)
- Random question selection (Trivia)
- Score and streak tracking in both games
- Difficulty and category displayed in Trivia
- Immediate feedback; highlights correct answer on wrong selection

## Troubleshooting

- "No questions in the database": run `uv run python -m app.db_init_trivia`
- Page won’t load: ensure server running at `http://localhost:8000`
- Buttons not working: clear browser cache or try another browser
- Styling looks broken: Tailwind via CDN — ensure internet connectivity

## Security

- CORS for dev; restrict origins in prod
- Pydantic validation for requests
- SQLAlchemy ORM with async engine

## Future Enhancements

- Leaderboards and user accounts
- Admin panel for adding questions
- Question filtering by difficulty/category
- Timed modes and challenges

Last Updated: December 12, 2025

## Contributing

- Fork the repo and create a feature branch.
- Keep changes focused; follow existing code style and structure.
- Add or update tests in `tests/` when changing logic or endpoints.
- Run locally and ensure both games work before opening a PR.
- Open a pull request with a clear description of the change and screenshots (for UI).

Quick checks:

```bash
pytest
python -m app.db.init_db
python -m app.db_init_trivia
python main.py
```


