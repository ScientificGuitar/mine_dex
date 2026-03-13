FROM python:3.13-slim-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY --from=ghcr.io/astral-sh/uv:0.9.27 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock /app/

RUN uv sync --locked

COPY . /app

CMD ["sh", "-c", "uv run alembic upgrade head && uv run src/bot.py"]