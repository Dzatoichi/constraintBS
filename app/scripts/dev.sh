#!/bin/bash

set -e

echo "Starting PostgreSQL..."
docker compose up -d postgres

echo "Applying migrations..."
uv run alembic upgrade head

echo "Starting FastAPI..."
uv run fastapi dev app/main.py