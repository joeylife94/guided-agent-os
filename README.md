# Guided Agent OS

A reusable **Form-driven AI Agent OS** for turning structured user intake into stateful, traceable AI workflows.

The goal is not to build one freelance agent. The goal is to build a reusable platform where new agents can be added through templates, schemas, prompts, and workflow configuration with minimal new code. Users should be guided through forms instead of needing to write perfect prompts.

See [docs/PRODUCT_DIRECTION.md](docs/PRODUCT_DIRECTION.md) for the long-term product direction.

---

## First use-case: Freelance Opportunity Evaluator

Submit a freelance project opportunity via the API. The current agent will:

1. Validate that all required fields are present
2. Ask clarification questions if anything is missing
3. Persist every run to SQLite
4. Normalize validated intake data into a structured internal shape
5. Return `validated` when the minimal intake is complete

The Freelance Opportunity Agent is the first proof-of-concept for the platform. Later phases will add LLM analysis, scoring, action drafting, human review, and archive/export behavior. Those future phases are not active in the current workflow.

---

## Current implementation status

Completed:

- **Phase 1:** required-field validation and clarification questions
- **Phase 2-A:** SQLite persistence for agent runs
- **Phase 2-B:** deterministic normalization for validated freelance intake

Not implemented yet:

- LLM analysis, structured AI output, or model routing
- Opportunity scoring
- Proposal/action draft generation
- Human approval workflow
- Archive/export
- Authentication, crawling, RAG, or external account actions

---

## Tech stack

| Layer | Technology |
|---|---|
| API framework | FastAPI |
| Data validation | Pydantic v2 |
| Agent workflow | LangGraph |
| Database | SQLite + SQLAlchemy |
| Config | python-dotenv |
| Server | Uvicorn |

---

## Project structure

```
guided-agent-os/
├── app/
│   ├── main.py               # FastAPI application + health check
│   ├── api/
│   │   └── routes.py         # All API endpoints
│   ├── agents/
│   │   └── workflow.py       # LangGraph validation workflow + future node skeletons
│   ├── models/
│   │   ├── database.py       # SQLAlchemy engine + session
│   │   └── models.py         # ORM models: agent_runs, intake_templates, action_drafts
│   ├── schemas/
│   │   ├── intake.py         # FreelanceIntakeRequest Pydantic schema
│   │   └── agent_run.py      # AgentRunResponse + helper schemas
│   ├── services/
│   │   ├── validation.py     # Required-field validation logic
│   │   ├── clarification.py  # Clarification question generation
│   │   └── normalization.py  # Deterministic input normalization
│   └── templates/
│       └── freelance.py      # Freelance agent config (fields, prompts, drafts)
├── requirements.txt
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DECISIONS.md
│   ├── PRODUCT_DIRECTION.md
│   ├── PROJECT_STATUS.md
│   └── ROADMAP.md
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

For the current validation, persistence, and normalization phases, the default SQLite database setting is enough:

```dotenv
DATABASE_URL=sqlite:///./agent_os.db
```

`OPENAI_API_KEY` and `LLM_MODEL`, if present, are reserved for a future analysis/model-routing phase and are not used by the active workflow.

### 5. Start the server

```bash
uvicorn app.main:app --reload
```

The API is now available at **http://localhost:8000**.

Interactive docs: **http://localhost:8000/docs**

---

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `POST` | `/api/agents/{agent_type}/runs` | Start a new agent run |
| `GET` | `/api/agents/runs/{run_id}` | Get run status and results |
| `POST` | `/api/agents/runs/{run_id}/approve` | Reserved for future pending runs |
| `POST` | `/api/agents/runs/{run_id}/reject` | Reserved for future pending runs |

### Example: start a freelance run

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

**Run statuses**

| Status | Meaning |
|---|---|
| `running` | Workflow in progress |
| `needs_clarification` | Required fields were missing; see `clarification_questions` |
| `validated` | Required fields were present and `normalized_data` was produced |
| `error` | Unrecoverable workflow error |

Later phases may also use `pending_approval`, `rejected`, and `archived`.

---

## Adding a new agent type

1. Create `app/templates/<your_agent>.py` with:
   - `AGENT_TYPE`, `REQUIRED_FIELDS`, `OPTIONAL_FIELDS`
   - `CLARIFICATION_MAP` (field -> question text)
   - Optional future settings such as `ANALYSIS_PROMPT_TEMPLATE` and `DRAFT_ACTION_TEMPLATES`
2. Register the new type in `app/api/routes.py` inside `_get_template_config()`.

The validation and clarification workflow is designed for reuse. The current normalization service is freelance-shaped, so future agent types should add template-aware normalization rather than rewriting the whole backend.

Planned future examples include AI Content Agent, Duru SKU & Marketing Agent, Personal Command Center Agent, AI Market Watch Agent, and additional guided intake agents.

---

## Design principles

- **Guided intake first.** Users fill out forms instead of crafting complex prompts.
- **Validation before AI.** Required context is checked before any future LLM call.
- **Template-driven.** Agent-specific config lives in templates, schemas, prompts, and workflow configuration.
- **Stateful and traceable.** Runs preserve original input, normalized data, future analysis output, drafts, approval state, and archive records.
- **Human-in-the-loop.** Real external actions must never execute without explicit human approval.
- **Cost-aware AI development.** Use deterministic validation and normalization before spending model calls.
- **No over-engineering.** No authentication, payments, crawling, automatic email sending, complex RAG, or multi-agent orchestration.
