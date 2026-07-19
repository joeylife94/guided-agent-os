# Firebat Deployment

Guided Agent OS runs on Firebat as a private Tailnet API service with persistent SQLite and ChromaDB state.

## Runtime layout

```text
Tailnet HTTPS :8445
  -> 127.0.0.1:8701
  -> firebat-guided-agent-os:8000
     -> /app/data/agent_os.db
     -> /app/data/chroma
     -> optional Firebat-host Ollama :11434
```

The host port is loopback-only. The service is not exposed directly on the LAN or public internet.

## First deployment

```bash
cd ~/dev/repos/guided-agent-os
git checkout main
git pull --ff-only origin main
sh scripts/deploy-firebat.sh
sudo tailscale serve --bg --https=8445 http://127.0.0.1:8701
tailscale serve status
```

The deploy script creates `.env.firebat` from the safe template when it is missing. No API key or model credential is required for retrieval-only operation.

## Verification

```bash
sh scripts/healthcheck-firebat.sh
curl -fsS http://127.0.0.1:8701/version
curl -fsS 'http://127.0.0.1:8701/api/rag/query-all?q=legacy%20database&top_k=1'

docker compose --env-file .env.firebat -f compose.firebat.yml ps
docker compose --env-file .env.firebat -f compose.firebat.yml logs --tail=100 app
docker volume inspect firebat-guided-agent-os-data
```

The default browser entry point is:

```text
http://127.0.0.1:8701/docs
```

## Optional Ollama

The container uses the Firebat host gateway by default:

```text
http://host.docker.internal:11434/v1
```

When a compatible model is unavailable, `/api/rag/answer` returns retrieved context, citations, limitations, and an unavailable model status. This is an expected degraded mode, not a service-health failure.

To use another OpenAI-compatible local endpoint, edit `.env.firebat` and redeploy:

```text
LOCAL_LLM_BASE_URL=http://host.docker.internal:11434/v1
LOCAL_LLM_MODEL=qwen2.5:7b-instruct
LOCAL_LLM_TIMEOUT=5
```

Do not claim model inference was validated until the configured model has been called successfully.

## Persistence and backup

The named volume is:

```text
firebat-guided-agent-os-data
```

Normal container recreation and `docker compose down` preserve the volume. Do not use `down -v` unless deletion is explicitly intended.

A simple host-side backup can be created with:

```bash
mkdir -p backups/guided-agent-os

docker run --rm \
  -v firebat-guided-agent-os-data:/source:ro \
  -v "$PWD/backups/guided-agent-os:/backup" \
  alpine:3.22 \
  tar -czf /backup/guided-agent-os-data.tar.gz -C /source .
```

The archive contains both the SQLite database and ChromaDB index. Treat it as private application state.

## Operational boundary

The deployment supports guided intake, persistence, RAG retrieval, optional grounded generation, planned-only tool recommendations, and human review status changes. It does not execute tools, SQL, external APIs, account actions, email, submissions, or payments.

## Disable Tailnet proxy

```bash
sudo tailscale serve --https=8445 off
```
