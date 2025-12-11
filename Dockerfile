FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

COPY . .

ENV DATABASE_URL=sqlite+aiosqlite:///./data/test.db
RUN mkdir -p /app/data

RUN uv run python -m app.db_init

EXPOSE 8000

CMD ["uv", "run", "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "app.app:app"]
