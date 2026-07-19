#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT_DIR"

if [ -f .env.firebat ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env.firebat
  set +a
fi

HOST_PORT=${HOST_PORT:-8701}
MAX_ATTEMPTS=${HEALTHCHECK_MAX_ATTEMPTS:-60}
SLEEP_SECONDS=${HEALTHCHECK_SLEEP_SECONDS:-2}
URL="http://127.0.0.1:${HOST_PORT}/health"

attempt=1
while [ "$attempt" -le "$MAX_ATTEMPTS" ]; do
  response=$(curl -fsS --max-time 8 "$URL" 2>/dev/null || true)
  if printf '%s' "$response" | grep -q '"status":"healthy"' \
    && printf '%s' "$response" | grep -q '"database":"ready"' \
    && printf '%s' "$response" | grep -q '"rag":"ready"'; then
    printf '[PASS] guided-agent-os healthcheck passed: %s\n' "$URL"
    printf '%s\n' "$response"
    exit 0
  fi

  printf '[WAIT] healthcheck attempt %s/%s\n' "$attempt" "$MAX_ATTEMPTS"
  attempt=$((attempt + 1))
  sleep "$SLEEP_SECONDS"
done

printf '[FAIL] healthcheck failed: %s\n' "$URL" >&2
docker compose --env-file .env.firebat -f compose.firebat.yml ps >&2 || true
docker compose --env-file .env.firebat -f compose.firebat.yml logs --tail=200 app >&2 || true
exit 1
