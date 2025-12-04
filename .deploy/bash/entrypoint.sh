#!/bin/sh
set -e

if [ ! -f /app/.env ]; then
    cp /app/env/.env.example /app/.env
fi

if [ ! -f /app/.env.db ]; then
    cp /app/env/.env.db.example /app/.env.db
fi

cd /app/src

echo "=== Initializing Database ==="
pipenv run python -c "
import asyncio
from infrastructure.db.session import init_db

asyncio.run(init_db())
"
echo ""

WORKERS=$((2 * $(nproc) + 1))

echo "Starting FastAPI with $WORKERS workers"
exec pipenv run uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers "$WORKERS"
