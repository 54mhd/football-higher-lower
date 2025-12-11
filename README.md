# Higher or Lower – Football Edition

Учебный университетский проект на FastAPI: веб‑приложение в стиле
"Higher or Lower" для сравнения статистики футболистов.

## Цель проекта

Приложение показывает двух игроков и предлагает пользователю угадать,
у кого статистика (`stat_value`) выше. Логика упрощена до сравнения
одного числового показателя.

## Технологии

- FastAPI (backend)
- SQLite (`test.db`) через SQLAlchemy async
- HTML + JavaScript (frontend без фреймворков)
- Docker, docker-compose
- GitHub Actions (CI)

## Структура проекта

```text
project/
├── .env
├── .git/
├── .gitignore
├── .python-version
├── .venv/
├── app/
│   ├── app.py           # FastAPI-приложение, маршруты, middleware, CORS
│   ├── db/
│   │   ├── init_db.py   # Скрипт инициализации и заполнения БД
│   │   └── seed_players.sql  # SQL-скрипт с начальными записями
│   ├── db.py            # Модель Player и конфигурация SQLite/SQLAlchemy
│   ├── images.py        # Инициализация клиента ImageKit (пример работы с .env)
│   ├── __pycache__/
│   ├── schema.py        # Pydantic‑модели (I/O схемы API)
│   └── services/
│       ├── game_services.py  # Бизнес‑логика игры (random, verify)
│       └── __pycache__/
├── index.html           # Простой HTML/JS‑frontend
├── main.py              # Точка входа для локального dev‑запуска (uvicorn)
├── pyproject.toml       # Зависимости и метаданные проекта
├── README.md            # Это описание проекта
├── test.db              # Локальная SQLite‑БД (dev)
├── uv.lock              # Lock‑файл менеджера uv
├── tests/
│   ├── __init__.py
│   ├── test_api.py      # Тесты API‑эндпоинтов
│   ├── test_db.py       # Тесты работы с БД
│   └── test_services.py # Тесты сервисного слоя
├── Dockerfile
├── docker-compose.yml
└── .github/
    └── workflows/
        └── ci.yml       # CI: тесты и сборка Docker‑образа
```

## Архитектура backend

- `app/app.py`
  - Создание объекта `FastAPI`.
  - Подключение CORS (`CORSMiddleware`) для доступа с фронтенда.
  - Middleware логирования времени обработки запроса.
  - Эндпоинты:
    - `GET /health` — проверка работоспособности сервиса.
    - `GET /` — отдаёт `index.html` или fallback‑страницу.
    - `GET /api/player/random` — возвращает двух случайных игроков.
    - `POST /api/game/verify` — проверяет угадывание пользователя.

- `app/db.py`
  - Конфигурация SQLite через SQLAlchemy async.
  - URL берётся из переменной окружения `DATABASE_URL` или
    по умолчанию `sqlite+aiosqlite:///./test.db`.
  - Модель `Player`:
    - `id: int` (PK, autoincrement)
    - `name: str`
    - `image_url: str`
    - `stat_value: int`
  - Функции:
    - `create_db_and_tables()` — создание схемы БД.
    - `get_async_session()` — зависимость FastAPI для получения
      `AsyncSession`.

- `app/db/init_db.py`
  - Скрипт инициализации БД и заполнения несколькими игроками.
  - Используется как утилита и вызывается внутри Dockerfile.

- `app/db/seed_players.sql`
  - Альтернативный SQL‑скрипт вставки начальных игроков в таблицу.

- `app/schema.py`
  - `PlayerOut` — публичная модель игрока.
  - `RandomPlayersResponse` — ответ `GET /api/player/random`.
  - `VerifyRequest` — тело запроса `POST /api/game/verify`.
  - `VerifyResponse` — результат проверки угадывания.
  - `HealthResponse` — модель для `/health`.

- `app/services/game_services.py`
  - Инкапсулирует бизнес‑логику.
  - `get_two_random_players(session)` — выбирает двух случайных
    игроков через `ORDER BY RANDOM()` в SQLite.
  - `verify_guess(session, payload)` —
    - Загружает двух игроков по ID.
    - Сравнивает их `stat_value`.
    - Возвращает `correct`, `left_value`, `right_value`.

## Frontend

- `index.html` — простой SPA‑подобный интерфейс на чистом JS.
- Использует `fetch` для запросов к backend:
  - `GET /api/player/random` для получения двух игроков.
  - `POST /api/game/verify` для проверки гипотезы пользователя.
- Отображает:
  - Имя и аватар каждого игрока.
  - Кнопки "Left is higher" / "Right is higher".
  - Счёт и статус последнего ответа.

## Безопасность и конфигурация

- CORS включён через `CORSMiddleware` (по умолчанию разрешены все
  источники — для учебных целей; в проде следует сузить список).
- Валидация входных данных выполняется через Pydantic‑модели
  (`VerifyRequest`).
- Переменные окружения загружаются из `.env` при помощи `python-dotenv`.
  Основные переменные:
  - `DATABASE_URL` — строка подключения к SQLite (или другой БД).
  - Ключи для `imagekit` в `app/images.py` (опционально).

## Запуск локально (без Docker)

### 1. Установка зависимостей

```bash
uv sync
```

или (если `uv` не используется):

```bash
pip install -e .
```

### 2. Инициализация БД

```bash
uv run python -m app.db.init_db
```

### 3. Запуск dev‑сервера

```bash
uv run python main.py
```

Приложение будет доступно по адресу `http://localhost:8000`.

## Запуск через Docker

### 1. Сборка образа

```bash
docker build -t higher-lower-app .
```

### 2. Запуск контейнера

```bash
docker-compose up --build
```

- Backend доступен на `http://localhost:8000`.
- SQLite хранится в volume `./data`, чтобы данные не терялись при
  перезапуске контейнера.
- Сервер в контейнере — `gunicorn` с воркером `uvicorn`.

## Тестирование

Тесты написаны на `pytest` и покрывают:

- `tests/test_services.py` — логику сервиса `GameService`.
- `tests/test_api.py` — доступность и корректность API‑эндпоинтов.
- `tests/test_db.py` — создание таблиц и простые CRUD‑операции.

Запуск тестов:

```bash
uv run pytest
```

или

```bash
pytest
```

## CI/CD (GitHub Actions)

Workflow `.github/workflows/ci.yml` выполняет:

1. Установку Python.
2. Установку зависимостей через `uv sync`.
3. Запуск тестов (`pytest`).
4. Сборку Docker‑образа.

Этот pipeline можно использовать как основу для дальнейшего деплоя на
любой Docker‑совместимый хостинг.

