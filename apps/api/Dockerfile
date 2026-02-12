# Build context: apps/api
FROM python:3.12-slim AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy project files and install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy app code (for image; overwritten by volume in dev)
COPY . .

EXPOSE 8000

# Sync on start when volume overwrites; then run uvicorn with reload
CMD ["sh", "-c", "uv sync --frozen && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
