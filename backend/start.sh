#!/usr/bin/env bash
# Apply any pending DB migrations, then boot the API.
# Used as the CMD of the production Docker image and the Procfile web process.
set -euo pipefail

echo "[start] running alembic upgrade head"
alembic upgrade head

echo "[start] launching uvicorn on :8000"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
