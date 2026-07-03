#!/bin/sh
set -eu

mode="${1:-api}"

if [ "$mode" = "api" ]; then
  alembic -c alembic.ini upgrade head
  exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers "${WEB_CONCURRENCY:-2}"
fi

if [ "$mode" = "worker" ]; then
  exec rq worker ingestion --url "${REDIS_URL}"
fi

echo "Unknown process mode: $mode" >&2
exit 1
