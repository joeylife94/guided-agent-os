# Guided Agent OS

Guided Agent OS is a **controlled enterprise AI Agent proof** built with FastAPI, LangGraph, SQLite, ChromaDB, a local multilingual embedding model, and an optional local OpenAI-compatible LLM endpoint.

The Proof v1.0 goal is deliberately narrow: demonstrate a traceable browser workflow in which a user request is validated, grounded in internal knowledge, routed through human approval when needed, allowed to execute only one approved read-only tool, persisted, and auditable end to end.

`GUIDED_AGENT_OS_MASTER.md` is the single authoritative execution contract for current Proof status, evidence, risks, and next actions.

---

## What is proven today

The frozen Proof path is implemented and verified through P1–P5:

- structured intake with required-field validation
- clarification questions for missing context
- deterministic normalization
- persistent agent runs in SQLite
- semantic RAG with persistent ChromaDB collections
- multilingual embedding with `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Korean and English intended-source retrieval
- grounded answer/citation structure with graceful local-LLM unavailable fallback
- deterministic tool planning and risk routing
- human approval/reject boundary
- deterministic Tool Registry + read-only allowlist
- real approved proof-tool execution via `legacy_db_lookup`
- block paths for no approval, reject, unregistered tool, unauthorized tool, and invalid parameters
- browser Operator Workspace served by FastAPI
- persisted execution result
- append-only lifecycle audit events
- persisted Audit Timeline rendered in the Operator Workspace
- fixed 22-case evaluation suite with **22/22 PASS**

The current implementation is a **Deployable Controlled AI Agent Proof**, not a production SaaS platform.

---

## Golden Path

```text
Structured Intake
        ↓
Validation / Clarification
        ↓
Normalization
        ↓
Semantic RAG
        ↓
Grounded Answer + Citation
        ↓
Tool Planning
        ↓
Risk / Policy Check
        ↓
Human Approval
        ↓
Allowlisted Read-only Tool Execution
        ↓
Persisted Result
        ↓
Persistent Audit Timeline
```

The LLM does **not** directly invoke tools. Execution is performed only by the backend executor after approval and allowlist/parameter checks.

---

## Proof architecture

```text
Browser Operator Workspace
          │
          ▼
       FastAPI
          │
          ▼
   LangGraph Workflow
   ├─ validation / clarification
   ├─ normalization
   ├─ semantic RAG
   ├─ grounded answer
   ├─ tool plan
   └─ human-review routing
          │
          ├──────────────► ChromaDB
          │                 ├─ domain_knowledge
          │                 ├─ agent_policy
          │                 └─ tool_catalog
          │
          ├──────────────► Optional local OpenAI-compatible LLM
          │
          ▼
 Human Approval Boundary
          │
          ▼
 Tool Registry + Read-only Allowlist
          │
          ▼
   `legacy_db_lookup`
          │
          ▼
 SQLite AgentRun + RunAuditEvent
```

---

## Safety boundary

Proof v1.0 intentionally constrains execution:

- no direct LLM tool invocation
- one deterministic proof tool: `legacy_db_lookup`
- read-only allowlist
- strict `record_id` parameter contract
- explicit approval for controlled execution
- reject/no-approval paths cannot execute
- unregistered or per-run unauthorized tools cannot execute
- invalid parameters cannot execute
- no arbitrary SQL execution
- no database writes
- no real Oracle/customer production integration
- no automatic email, Slack, posting, or external-account actions

The proof tool uses a deterministic local fixture. It demonstrates the **control architecture**, not customer-system integration performance.

---

## Semantic RAG

The Proof runtime uses:

- ChromaDB persistent collections
- local Markdown knowledge under `app/knowledge/`
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- 384-dimensional embeddings
- Korean/English retrieval verification

The semantic model was selected after `BAAI/bge-m3` proved unstable inside the frozen 1536 MiB Firebat container envelope.

The local LLM path is optional. When the configured local model endpoint is unavailable, the service remains healthy and returns retrieved context/citations for review rather than inventing successful inference.

Positive final-stack local-LLM inference remains a separate Proof v1.0 closure item and is not silently counted as completed evidence.

---

## Evaluation evidence

The fixed Proof suite contains **22 cases**:

| Category | Result |
|---|---:|
| Retrieval | 8 / 8 PASS |
| Grounding / citation structure | 4 / 4 PASS |
| Routing / policy | 4 / 4 PASS |
| Tool control | 6 / 6 PASS |
| **Total** | **22 / 22 PASS** |

The first real execution returned 21/22 PASS. The only failure was retrieval case `R03`, where `tools/approved-tools.md` ranked 5 instead of the frozen Top-3 expectation. The expectation was not weakened; the knowledge document was clarified to state its controlled-agent purpose explicitly, and the rerun placed it at rank 1.

Durable evaluation evidence recorded in the Master:

- Proof Evaluation run id: `32177070127`
- tested PR head: `40033b966994dc06332cf858d1b4a781a1168347`
- artifact: `guided-agent-proof-eval`
- artifact id: `9339491975`
- artifact digest: `sha256:ab24f530331d9e90dda4ff4fad552f8e36a3735dbd924e1365002f7819f3935b`
- machine-readable result: `proof-eval-results.json`

The grounding/citation cases in GitHub CI used the documented unavailable-local-LLM fallback because no reachable local model endpoint was present in that environment.

---

## Run locally with Docker Compose

### 1. Prepare environment

```bash
cp .env.firebat.example .env.firebat
```

The example is already configured for the Proof semantic model:

```env
RAG_EMBEDDING_PROVIDER=bge_m3
RAG_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

`RAG_EMBEDDING_PROVIDER=bge_m3` is a legacy provider identifier retained for compatibility; runtime model metadata identifies the actual MiniLM model.

### 2. Optional local LLM

By default the container expects an OpenAI-compatible endpoint reachable from Docker at:

```env
LOCAL_LLM_BASE_URL=http://host.docker.internal:11434/v1
LOCAL_LLM_MODEL=qwen2.5:7b-instruct
```

Ollama or another compatible local endpoint can be used. If it is unavailable, the fallback path remains operational.

### 3. Start

```bash
docker compose -f compose.firebat.yml up --build -d
```

Default host binding:

```text
http://127.0.0.1:8701
```

Open the root URL for the Operator Workspace.

### 4. Health check

```bash
curl http://127.0.0.1:8701/health
```

The container healthcheck requires the API, database, and RAG index to be ready.

### 5. Stop

```bash
docker compose -f compose.firebat.yml down
```

The named Docker volume `firebat-guided-agent-os-data` preserves SQLite, Chroma, and model-cache data across restarts.

---

## Core API surface

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | runtime/database/RAG health |
| `GET` | `/version` | version metadata |
| `POST` | `/api/agents/{agent_type}/runs` | create an Agent run |
| `GET` | `/api/agents/runs/{run_id}` | reload a persisted run |
| `POST` | `/api/agents/runs/{run_id}/approve` | approve eligible controlled execution |
| `POST` | `/api/agents/runs/{run_id}/reject` | reject pending execution |
| `GET` | `/api/agents/runs/{run_id}/events` | reload persisted lifecycle audit events |
| `POST` | `/api/rag/rebuild-index` | rebuild local knowledge index |
| `GET` | `/api/rag/query` | query one RAG collection |
| `GET` | `/api/rag/query-all` | query all RAG collections |
| `POST` | `/api/rag/answer` | grounded RAG answer with optional local LLM |

For the browser Golden Path, use the Operator Workspace at `/` rather than Swagger.

---

## Known limitations

Proof v1.0 deliberately accepts these limitations:

- `legacy_db_lookup` uses a deterministic local fixture rather than a customer system.
- execution result currently shares an existing persisted raw-output field rather than a dedicated execution-result table.
- the semantic provider identifier is still named `bge_m3` for compatibility even though MiniLM is the actual Proof model.
- the CPU-oriented Python image still resolves a relatively large Torch dependency footprint.
- browser CI depends on Chrome + Selenium availability.
- authentication, OAuth/SSO, multi-tenancy, complex RBAC, destructive tools, external-account actions, Kubernetes, HA, and enterprise observability are outside the frozen Proof v1.0 scope.
- positive local-LLM inference with the final semantic stack still requires final closure evidence or an explicit closure decision.

---

## Proof status

P1–P5 are closed with evidence. Phase 6 is the final packaging/closure phase.

For exact evidence IDs, commit/run references, accepted risks, and the current next action, read:

- [`GUIDED_AGENT_OS_MASTER.md`](GUIDED_AGENT_OS_MASTER.md) — authoritative Proof contract
- [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) — compatibility pointer to the Master
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — compatibility pointer to the Master

Long-term product ideas are intentionally separated from the frozen Proof scope. Proof v1.0 should not be interpreted as a production-ready enterprise platform.
