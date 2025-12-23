FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml alembic.ini README.md ./
COPY app ./app

FROM base AS prod
RUN python -m pip install -U pip && pip install --no-cache-dir .
EXPOSE 8000
CMD ["python", "-m", "app.core.entrypoint"]

FROM base AS dev
COPY tests ./tests
RUN python -m pip install -U pip && pip install --no-cache-dir ".[dev]"
EXPOSE 8000
CMD ["python", "-m", "app.core.entrypoint"]