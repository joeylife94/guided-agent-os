#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT_DIR"

for command in git docker curl; do
  if ! command -v "$command" >/dev/null 2>&1; then
    printf '[FAIL] required command not found: %s\n' "$command" >&2
    exit 1
  fi
done

if ! docker compose version >/dev/null 2>&1; then
  printf '[FAIL] docker compose plugin is required\n' >&2
  exit 1
fi

if [ ! -f .env.firebat ]; then
  cp .env.firebat.example .env.firebat
  chmod 600 .env.firebat
  printf '[INFO] created .env.firebat from the safe template\n'
fi

current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
  printf '[FAIL] deploy from main only; current branch: %s\n' "$current_branch" >&2
  exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
  printf '[FAIL] worktree is not clean; commit or stash changes before deploying\n' >&2
  exit 1
fi

git fetch origin main
local_head=$(git rev-parse HEAD)
remote_head=$(git rev-parse origin/main)

if [ "$local_head" != "$remote_head" ]; then
  printf '[INFO] fast-forwarding main to origin/main\n'
  git pull --ff-only origin main
  local_head=$(git rev-parse HEAD)
fi

APP_VERSION=$(printf '%s' "$local_head" | cut -c1-12)
GIT_REVISION=$local_head
export APP_VERSION GIT_REVISION

printf '[INFO] building guided-agent-os@%s\n' "$APP_VERSION"
docker compose --env-file .env.firebat -f compose.firebat.yml build --pull app

docker compose --env-file .env.firebat -f compose.firebat.yml up -d --remove-orphans

sh scripts/healthcheck-firebat.sh

printf '[PASS] deploy complete: guided-agent-os@%s\n' "$APP_VERSION"
printf '[INFO] local API docs: http://127.0.0.1:%s/docs\n' "${HOST_PORT:-8701}"
printf '[INFO] local LLM is optional; missing Ollama does not make the service unhealthy\n'
