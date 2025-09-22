#!/usr/bin/env bash
set -euo pipefail

wait_for() {
  local host="$1" port="$2"
  for i in {1..60}; do
    if nc -z "$host" "$port"; then
      echo "[entrypoint] $host:$port is up"
      return 0
    fi
    echo "[entrypoint] waiting for $host:$port ($i)"
    sleep 1
  done
  echo "[entrypoint] timeout waiting for $host:$port"
  return 1
}

wait_for "${REDIS_HOST:-redis}" "${REDIS_PORT:-6379}"

if [[ -n "${ALEMBIC_DATABASE_URL:-${DATABASE_URL:-}}" ]]; then
  echo "[entrypoint] running alembic upgrade head"
  alembic upgrade head || { echo "[entrypoint] alembic failed"; exit 1; }
else
  echo "[entrypoint] skipping alembic (no DATABASE_URL)"
fi

SCHEDULE_DIR="${BEAT_SCHEDULE_DIR:-/app/run}"
mkdir -p "$SCHEDULE_DIR"

case "${SERVICE:-api}" in
  api)
    echo "[entrypoint] starting API"
    exec uvicorn src.app:app --host "${APP_HOST:-0.0.0.0}" --port "${APP_PORT:-8000}" --proxy-headers
    ;;
  worker)
    echo "[entrypoint] starting Celery worker"
    exec celery -A src.core.celery_app:celery_app worker -l info
    ;;
  beat)
    echo "[entrypoint] starting Celery beat"
    exec celery -A src.core.celery_app:celery_app beat -l info --schedule "$SCHEDULE_DIR/celerybeat-schedule.db"
    ;;
  *)
    echo "[entrypoint] unknown SERVICE=${SERVICE}"
    exit 2
    ;;
esac
