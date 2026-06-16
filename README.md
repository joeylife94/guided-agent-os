# Guided Agent OS

A reusable **Form-driven AI Agent OS** for turning structured user intake into stateful, traceable AI workflows.

The goal is not to build one freelance agent. The goal is to build a reusable platform where new agents can be added through templates, schemas, prompts, and workflow configuration with minimal new code. Users should be guided through forms instead of needing to write perfect prompts.

See [docs/PRODUCT_DIRECTION.md](docs/PRODUCT_DIRECTION.md) for the long-term product direction and [AGENTS.md](AGENTS.md) for project guidelines.

---

## Use cases

### 1. Freelance Opportunity Evaluator

Submit a freelance project opportunity via the API. The agent will:

1. Validate that all required fields are present
2. Ask clarification questions if anything is missing
3. Normalize the intake payload
4. Return `validated` when the minimal intake is complete

### 2. Public Enterprise AI Agent Intake

Submit an internal public-sector or enterprise AI-agent use case via the API. The agent will:

1. Validate business, user, data-source, and expected-capability fields
2. Ask clarification questions for missing enterprise context
3. Normalize and persist the intake record
4. Prepare structured context for later RAG scope, backend API/tool scope, security review, audit-log design, and human approval design

This use case is aimed at projects where the final AI agent must operate inside a controlled enterprise environment with internal data, legacy systems, role-based access, auditability, and human review.

Detailed document: [`docs/public-enterprise-ai-agent.md`](docs/public-enterprise-ai-agent.md)

---

## Current implementation status

Current agent intake capabilities:

- FastAPI API server
- Template-driven agent types (Freelance, Public Enterprise AI)
- Required-field validation
- Clarification question generation
- Deterministic input normalization
- SQLite/SQLAlchemy persistence for agent runs
- Future-phase approve/reject endpoints
- LangGraph workflow foundation

Current RAG capability:

- **Phase 1: Multi-Collection RAG Engine** - Complete
  - Local Markdown knowledge base under `app/knowledge/`
  - Deterministic local document chunking and embeddings
  - Persistent ChromaDB index at `./data/chroma`
  - API-only indexing and retrieval endpoints
- **Phase 2: Local LLM + RAG Answer Generation** - Complete
  - Local LLM integration through an Ollama/local OpenAI-compatible endpoint
  - Grounded answer generation from retrieved context
  - Source citations with similarity scores
  - Graceful degradation when LLM unavailable
  - POST `/api/rag/answer` endpoint

Planned/future phases:

- Phase 3: LLM analysis and scoring
- Phase 4: Action drafting with tool constraints
- Phase 5: Human review and approval workflow
- Archive workflow
- RAG integration with agent workflows
- Controlled tool/API execution

---

## Phase 1: Multi-Collection RAG Engine

Guided Agent OS includes a **local ChromaDB-based RAG engine** with three knowledge collections:

- **`domain_knowledge`**: Business manuals, operational procedures, and incident guides
- **`agent_policy`**: Agent behavior rules, decision-making standards, and source citation requirements
- **`tool_catalog`**: Approved tools, legacy system guidelines, and query template policies

This local RAG foundation allows the Agent backend to:
- Load Markdown documents from `app/knowledge/`
- Embed documents using deterministic local embeddings
- Persist ChromaDB collections at `./data/chroma`
- Query specific collections or search across all collections
- Return retrieved chunks with full metadata and similarity scores

The RAG engine is not wired into LangGraph workflows, UI flows, SQL execution, or external tool actions. Phase 2 uses it only through the local `/api/rag/answer` endpoint.

### RAG API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/rag/rebuild-index` | Rebuild the ChromaDB index from local documents |
| `GET` | `/api/rag/query` | Query a specific collection |
| `GET` | `/api/rag/query-all` | Query all collections |

### Example: Rebuild the RAG index

```bash
curl -X POST http://localhost:8000/api/rag/rebuild-index
```

Response:
```json
{
  "status": "indexed",
  "collections": {
    "domain_knowledge": 10,
    "agent_policy": 8,
    "tool_catalog": 7
  }
}
```

### Example: Query all collections

```bash
curl "http://localhost:8000/api/rag/query-all?q=How should an AI agent handle legacy database access?&top_k=2"
```

Response structure:
```json
{
  "query": "How should an AI agent handle legacy database access?",
  "results": {
    "domain_knowledge": [...],
    "agent_policy": [...],
    "tool_catalog": [...]
  }
}
```

Each result includes:
- `content`: The retrieved document chunk
- `metadata`: `doc_id`, `title`, `source_path`, `collection`, `chunk_index`
- `score`: Similarity score (0-1)

---

## Phase 2: Local LLM + RAG Answer Generation

Guided Agent OS can now generate **grounded answers** using retrieved context from all RAG collections through a local LLM.

The system:
- Accepts a user question via the API
- Retrieves relevant context from all three RAG collections (domain knowledge, agent policy, tool catalog)
- Builds a grounded prompt instructing the LLM to answer only from retrieved context
- Calls a local LLM through an **Ollama/local OpenAI-compatible API** (no cloud API keys required)
- Returns:
  - Generated answer
  - Source citations with similarity scores
  - Retrieved context by collection
  - Known limitations
  - Model metadata and availability status
- **Gracefully degrades** when the local LLM is unavailable, returning the retrieved context for review

### Local LLM Configuration

The system defaults to **Ollama** at `http://localhost:11434/v1` with the **qwen2.5:7b-instruct** model.

Configure via environment variables:

```bash
export LOCAL_LLM_BASE_URL=http://localhost:11434/v1
export LOCAL_LLM_MODEL=qwen2.5:7b-instruct
export LOCAL_LLM_TIMEOUT=30
```

Use a local OpenAI-compatible endpoint such as Ollama, LM Studio, or Text Generation WebUI. The Phase 2 RAG answerer does not call OpenAI or any cloud API.

### RAG Answer Endpoint

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/rag/answer` | Generate a grounded answer from RAG + local LLM |

### Example: Generate an answer

```bash
curl -X POST http://localhost:8000/api/rag/answer \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How should an AI agent handle legacy database access?",
    "top_k_per_collection": 3
  }'
```

Response structure:

```json
{
  "question": "How should an AI agent handle legacy database access?",
  "answer": "Based on the retrieved knowledge base, AI agents should not generate arbitrary SQL...",
  "citations": [
    {
      "doc_id": "legacy-db-001",
      "title": "Legacy Database Access Guidelines",
      "source_path": "app/knowledge/tools/legacy-db-access-guideline.md",
      "collection": "tool_catalog",
      "chunk_index": 0,
      "score": 0.95
    }
  ],
  "retrieved_context": {
    "domain_knowledge": [...],
    "agent_policy": [...],
    "tool_catalog": [...]
  },
  "limitations": [
    "The answer is generated only from retrieved local knowledge base context.",
    "No real tool, SQL, or API execution was performed.",
    "For critical decisions, human review is strongly recommended."
  ],
  "model": {
    "provider": "local",
    "name": "qwen2.5:7b-instruct",
    "available": true
  },
  "error": null
}
```

#### Request Parameters

- `question` (required): Question to answer using the knowledge base
- `top_k_per_collection` (optional, default: 3, range: 1-10): Number of results to retrieve per collection
- `model` (optional): Model name override

#### Response Fields

- `answer`: Generated answer from the LLM, or a fallback message if unavailable
- `citations`: List of sources used with similarity scores
- `retrieved_context`: Full retrieved chunks organized by collection
- `limitations`: Important disclaimers about the answer
- `model`: Metadata about the LLM (provider, name, availability)
- `error`: Error message if the model was unavailable

### Grounding & Safety

The system enforces these rules via the system prompt:

1. **Answer only from retrieved context** — Do not invent policies, tools, or database facts
2. **No hidden execution** — Do not claim real tool, SQL, or API calls have been performed
3. **Acknowledge gaps** — If context is insufficient, say so clearly
4. **Cite sources** — Include [source] notation when relevant
5. **Mention policy requirements** — If retrieved policies require human approval, mention it

---

## Tech stack

| Layer | Technology |
|---|---|
| API framework | FastAPI |
| Data validation | Pydantic v2 |
| Agent workflow | LangGraph |
| Database | SQLite + SQLAlchemy |
| RAG engine | ChromaDB + deterministic local hash embeddings |
| Local LLM | Ollama or local OpenAI-compatible API (qwen2.5:7b-instruct) |
| HTTP client | requests |
| Config | python-dotenv |
| Server | Uvicorn |

---

## Project structure

```text
guided-agent-os/
├── app/
│   ├── main.py               # FastAPI application + health check
│   ├── api/
│   │   ├── routes.py         # Generic agent endpoints + template registry
│   │   └── rag_routes.py     # RAG API endpoints
│   ├── agents/
│   │   └── workflow.py       # LangGraph validation workflow + future node skeletons
│   ├── models/
│   │   ├── database.py       # SQLAlchemy engine + session
│   │   └── models.py         # ORM models: agent_runs, intake_templates, action_drafts
│   ├── schemas/
│   │   ├── intake.py         # Freelance intake schema
│   │   └── agent_run.py      # AgentRunResponse + helper schemas
│   ├── services/
│   │   ├── validation.py     # Required-field validation logic
│   │   ├── clarification.py  # Clarification question generation
│   │   ├── normalization.py  # Deterministic normalization helpers
│   │   ├── rag_document_loader.py  # Markdown document discovery and chunking
│   │   ├── rag_embeddings.py # Deterministic local embeddings
│   │   ├── rag_indexer.py    # ChromaDB indexing
│   │   ├── rag_retriever.py  # ChromaDB querying
│   │   ├── local_llm.py      # Local LLM client (local OpenAI-compatible API)
│   │   └── rag_answerer.py   # RAG answer generation with grounding
│   ├── knowledge/            # Local RAG knowledge base
│   │   ├── domain/
│   │   │   ├── internal-operation-manual.md
│   │   │   └── incident-summary-guide.md
│   │   ├── policies/
│   │   │   ├── agent-behavior-policy.md
│   │   │   ├── source-citation-policy.md
│   │   │   └── human-review-policy.md
│   │   └── tools/
│   │       ├── approved-tools.md
│   │       ├── legacy-db-access-guideline.md
│   │       └── query-template-policy.md
│   └── templates/
│       ├── freelance.py              # Freelance agent config
│       └── public_enterprise_ai.py   # Public/enterprise AI-agent config
├── docs/
│   ├── ARCHITECTURE.md              # Architecture overview
│   ├── DECISIONS.md                 # Architectural decision log
│   ├── PRODUCT_DIRECTION.md         # Long-term product vision
│   ├── PROJECT_STATUS.md            # Current implementation status
│   ├── ROADMAP.md                   # Phase-based development roadmap
│   └── public-enterprise-ai-agent.md # Public Enterprise AI Agent details
├── tests/
├── data/                             # ChromaDB persistent storage (generated)
│   └── chroma/
├── requirements.txt
├── AGENTS.md
├── .env.example
└── README.md
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/joeylife94/guided-agent-os.git
cd guided-agent-os
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

For the current phase, the default SQLite database setting is enough:

```dotenv
DATABASE_URL=sqlite:///./agent_os.db
```

`OPENAI_API_KEY` and `LLM_MODEL` in `.env.example` are reserved for future analysis phases and are not required for the current validation/normalization workflow, the Phase 1 RAG engine, or Phase 2 local RAG answer generation. Configure Phase 2 with `LOCAL_LLM_BASE_URL`, `LOCAL_LLM_MODEL`, and `LOCAL_LLM_TIMEOUT`; tests do not require Ollama to be running.

### 5. Start the server

```bash
uvicorn app.main:app --reload
```

The API is now available at `http://localhost:8000`.

Interactive docs: `http://localhost:8000/docs`

---

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `POST` | `/api/agents/{agent_type}/runs` | Start a new agent run |
| `GET` | `/api/agents/runs/{run_id}` | Get run status and results |
| `POST` | `/api/agents/runs/{run_id}/approve` | Reserved for future pending runs |
| `POST` | `/api/agents/runs/{run_id}/reject` | Reserved for future pending runs |

Supported agent types:

| Agent type | Purpose |
|---|---|
| `freelance` | Validate and normalize freelance opportunity intake |
| `public_enterprise_ai` | Validate and normalize public-sector/enterprise AI-agent use-case intake |

---

## Example: public enterprise AI-agent intake

```bash
curl -X POST http://localhost:8000/api/agents/public_enterprise_ai/runs \
  -H "Content-Type: application/json" \
  -d '{
    "use_case_title": "Infrastructure Maintenance Knowledge Agent",
    "business_domain": "Energy and infrastructure operations",
    "target_user_group": "Internal maintenance planners and operations staff",
    "current_workflow_problem": "Maintenance staff need to search manuals, historical incident notes, and facility records across multiple internal systems.",
    "data_sources": "PDF manuals, maintenance reports, Oracle-based legacy facility database, inspection logs",
    "expected_agent_capabilities": "Answer internal policy and maintenance questions, retrieve relevant source documents, summarize historical incidents, and draft recommended next-check items.",
    "legacy_systems": "Oracle facility management system and internal document repository",
    "rag_document_types": "Maintenance manuals, safety guidelines, inspection reports, incident reports",
    "db_access_pattern": "The agent should not generate arbitrary SQL. It should call approved backend APIs or predefined query templates.",
    "llm_environment": "Unknown; must be confirmed against internal-network and security policy.",
    "security_constraints": "Internal network, role-based access, source-level authorization, audit logging",
    "approval_policy": "AI may draft recommendations, but operational actions require human approval.",
    "audit_requirements": "Log user question, retrieved source IDs, tool/API calls, answer metadata, and approval decisions."
  }'
```

Expected status when all required fields are present:

```text
validated
```

If required fields are missing, the run returns:

```text
needs_clarification
```

with clarification questions generated from the selected template.

---

## Example: freelance run

```bash
curl -X POST http://localhost:8000/api/agents/freelance/runs \
  -H "Content-Type: application/json" \
  -d '{
    "opportunity_title": "Build a React dashboard for SaaS startup",
    "client_description": "Early-stage fintech startup, 5 employees",
    "project_description": "Analytics dashboard with MRR and churn charts",
    "budget_range": "$5,000–$8,000",
    "timeline": "6 weeks"
  }'
```

---

## Run statuses

| Status | Meaning |
|---|---|
| `running` | Workflow in progress |
| `needs_clarification` | Required fields were missing; see `clarification_questions` |
| `validated` | All current-phase required fields were present |
| `error` | Unrecoverable workflow error |

Later phases may also use `pending_approval`, `rejected`, and `archived`.

---

## Adding a new agent type

1. Create `app/templates/<your_agent>.py` with:
   - `AGENT_TYPE`, `REQUIRED_FIELDS`, `OPTIONAL_FIELDS`
   - `CLARIFICATION_MAP` for field-level questions
   - Optional future settings such as `ANALYSIS_PROMPT_TEMPLATE` and `DRAFT_ACTION_TEMPLATES`
2. Register the new type in `app/api/routes.py` inside `_TEMPLATE_REGISTRY`.

The LangGraph workflow and all services are generic, so no other current-phase changes are needed.

---

## Design principles

- **Validation first.** The workflow should not analyze or recommend before the minimum context is known.
- **Template-driven.** Agent-specific config lives in `app/templates/`, not in the workflow.
- **Controlled enterprise design.** Internal data access should be mediated by metadata filters, approved APIs, or query templates.
- **No unrestricted autonomous execution.** AI may prepare analysis or drafts, but operational actions should require explicit human approval.
- **Auditable by default.** Intake data, normalized data, missing fields, clarification questions, and future approvals should be persisted.
