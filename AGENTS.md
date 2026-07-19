# Agent Operating Guide

## Project identity

Guided Agent OS is a reusable, form-driven controlled agent platform. It validates structured intake, asks clarification questions, normalizes input, persists runs, retrieves local knowledge through ChromaDB, generates grounded answers through an optional local OpenAI-compatible model, creates planned-only tool/API plans, and routes sensitive work to human review.

The platform does **not** execute SQL, tools, external APIs, account actions, payments, submissions, email, or destructive operations. Do not overstate planned output as real execution.

## Current implemented scope

- FastAPI API server
- Freelance, public-enterprise, and controlled-RAG templates
- SQLite/SQLAlchemy run persistence
- deterministic normalization and clarification
- LangGraph controlled workflow
- local Markdown knowledge base and persistent ChromaDB index
- deterministic local embeddings
- optional Ollama/OpenAI-compatible grounded answer generation
- graceful retrieval-only fallback when the model is unavailable
- planned-only tool/API recommendations
- guarded human approve/reject status transitions

Keep README, API descriptions, tests, and deployment reports aligned with this actual scope.

## Repository workflow

1. Inspect `main`, open PRs, relevant routes, workflow nodes, persistence models, RAG services, tests, and CI before editing.
2. Work on a dedicated branch and preserve unrelated worktree changes.
3. Implement the smallest complete change without activating planned features early.
4. Run narrow tests first, then the full required verification.
5. Open a Draft PR, inspect GitHub Actions, fix failures from logs and artifacts, and report exact validation boundaries.
6. Merge only when authorized and all required checks are successful.

## Required verification

```bash
python -m pytest tests
python -m unittest discover -s tests
python -m compileall app tests scripts
git diff --check
```

Container or deployment changes must additionally prove:

- production image build
- non-root container startup
- SQLite and ChromaDB readiness
- RAG query with non-empty retrieved context
- graceful behavior without Ollama
- agent-run persistence after container recreation
- image version and revision metadata

## Safety and truthfulness

- Never commit `.env`, `.env.firebat`, credentials, API keys, private data, database files, ChromaDB state, or model artifacts.
- Do not add automatic email, applications, payments, crawling, posting, account actions, direct SQL execution, or tool execution unless explicitly authorized as a separate scoped task.
- Human approval changes status only; it does not secretly execute a planned action.
- Do not delete persistent volumes or reset user data without explicit authorization.
- Do not claim Ollama, GPU inference, external integrations, or tool execution were validated unless they were actually exercised.

## Firebat deployment

- Compose file: `compose.firebat.yml`
- host binding: `127.0.0.1:8701`
- Tailnet HTTPS port: `8445`
- API documentation: `/docs`
- health: `/health`
- version: `/version`
- persistent volume: `firebat-guided-agent-os-data`
- deployment: `sh scripts/deploy-firebat.sh`

Firebat is a private Tailnet deployment. The local LLM endpoint is optional. The service must remain usable in retrieval-only mode when Ollama is absent.
