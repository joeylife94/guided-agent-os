#!/bin/sh
set -eu

printf '[guided-agent-os] starting version=%s revision=%s\n' \
  "${APP_VERSION:-dev}" "${GIT_REVISION:-unknown}"

python scripts/bootstrap_firebat.py

printf '[guided-agent-os] starting FastAPI on 0.0.0.0:8000\n'
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 1 \
  --proxy-headers \
  --no-access-log
