# Guided Agent OS

A form-driven AI agent platform that collects structured intake data, validates required fields, and generates clarification questions when information is missing.

The platform is designed as a reusable foundation. Agent-specific behaviour lives in `app/templates/` so new agent types can be added without hard-coding the core workflow.

---

## First use-case: Freelance Opportunity Evaluator

Submit a freelance project opportunity via the API. The agent will:

1. Validate that all required fields are present
2. Ask clarification questions if anything is missing
3. Return `validated` when the minimal intake is complete

Phase 1 stops after validation. Normalization, LLM analysis, scoring, action drafting, human review, and archive are planned for later phases.

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

For Phase 1, the default SQLite database setting is enough:

```dotenv
DATABASE_URL=sqlite:///./agent_os.db
```

`OPENAI_API_KEY` and `LLM_MODEL` in `.env.example` are reserved for a future analysis phase and are not used by the Phase 1 validation flow.

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
| `validated` | All Phase 1 required fields were present |
| `error` | Unrecoverable workflow error |

Later phases may also use `pending_approval`, `rejected`, and `archived`.

---

## Adding a new agent type

1. Create `app/templates/<your_agent>.py` with:
   - `AGENT_TYPE`, `REQUIRED_FIELDS`, `OPTIONAL_FIELDS`
   - `CLARIFICATION_MAP` (field -> question text)
   - Optional future settings such as `ANALYSIS_PROMPT_TEMPLATE` and `DRAFT_ACTION_TEMPLATES`
2. Register the new type in `app/api/routes.py` inside `_get_template_config()`.

The LangGraph workflow and all services are generic, so no other Phase 1 changes are needed.

---

## Design principles

- **Validation first.** Phase 1 stops at `validated` or `needs_clarification`.
- **Template-driven.** Agent-specific config lives in `app/templates/`, not in the workflow.
- **No over-engineering.** No authentication, payments, crawling, automatic email sending, complex RAG, or multi-agent orchestration.
- **Human-controlled future actions.** Later phases may draft or review actions, but nothing should be sent or submitted automatically.
