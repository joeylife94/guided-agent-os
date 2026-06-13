# Guided Agent OS

A form-driven AI agent platform that collects structured intake data, validates required fields, generates clarification questions when information is missing, prepares LLM-ready prompts, creates structured analysis output, generates action drafts, and **keeps human approval as a required step**.

The platform is designed as a reusable foundation — agent-specific behaviour lives in `app/templates/` so new agent types can be added without touching the core workflow.

---

## First use-case: Freelance Opportunity Evaluator

Submit a freelance project opportunity via the API. The agent will:

1. Validate that all required fields are present
2. Ask clarification questions if anything is missing
3. Normalise and clean the intake data
4. Analyse the opportunity with an LLM *(requires `OPENAI_API_KEY`)*
5. Score the opportunity from 0–10
6. Draft action items (e.g. initial reply, proposal outline)
7. **Pause for human review** — nothing is sent or submitted automatically
8. Archive the run after the reviewer approves

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
│   │   └── workflow.py       # LangGraph workflow (9 nodes)
│   ├── models/
│   │   ├── database.py       # SQLAlchemy engine + session
│   │   └── models.py         # ORM models: agent_runs, intake_templates, action_drafts
│   ├── schemas/
│   │   ├── intake.py         # FreelanceIntakeRequest Pydantic schema
│   │   └── agent_run.py      # AgentRunResponse + helper schemas
│   ├── services/
│   │   ├── validation.py     # Required-field validation logic
│   │   └── clarification.py  # Clarification question generation
│   └── templates/
│       └── freelance.py      # Freelance agent config (fields, prompts, drafts)
├── requirements.txt
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

Edit `.env` and set at minimum:

```dotenv
DATABASE_URL=sqlite:///./agent_os.db
OPENAI_API_KEY=sk-...          # Required for LLM analysis; omit for stub mode
LLM_MODEL=gpt-4o-mini          # Any OpenAI chat model
```

> **Stub mode** — If `OPENAI_API_KEY` is not set the `analyze_with_llm` node
> returns a labelled stub response so the full workflow can be exercised locally
> without an API key.

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
| `POST` | `/api/agents/runs/{run_id}/approve` | Approve a pending run |
| `POST` | `/api/agents/runs/{run_id}/reject` | Reject a pending run |

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
| `pending_approval` | Workflow complete; awaiting human review |
| `approved` / `archived` | Approved by reviewer |
| `rejected` | Rejected by reviewer |
| `error` | Unrecoverable workflow error |

---

## Adding a new agent type

1. Create `app/templates/<your_agent>.py` with:
   - `AGENT_TYPE`, `REQUIRED_FIELDS`, `OPTIONAL_FIELDS`
   - `CLARIFICATION_MAP` (field → question text)
   - `ANALYSIS_PROMPT_TEMPLATE`
   - `DRAFT_ACTION_TEMPLATES`
2. Register the new type in `app/api/routes.py` inside `_get_template_config()`.

The LangGraph workflow and all services are already generic — no other changes needed.

---

## Design principles

- **Human approval is mandatory.** The workflow always pauses at `human_review`; nothing is published or sent automatically.
- **Template-driven.** Agent-specific config lives in `app/templates/`, not in the workflow.
- **No over-engineering.** No authentication, payments, crawling, automatic email sending, complex RAG, or multi-agent orchestration.
- **Stub-friendly.** The `analyze_with_llm` node degrades gracefully when no LLM API key is configured.
