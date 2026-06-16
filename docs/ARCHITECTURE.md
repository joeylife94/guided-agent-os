# Architecture

---

## Overview

Guided Agent OS is a FastAPI application backed by a LangGraph workflow graph and a SQLite persistence layer. It exposes a small HTTP API that accepts structured intake data, runs it through the workflow graph, and returns a persisted agent run.

The platform is template-driven: the same core infrastructure is intended to serve multiple agent types. The Freelance Opportunity Agent is the first and currently only registered template.

The long-term architecture target is a reusable Form-driven AI Agent OS. New agents should be added primarily through templates, schemas, prompts, structured output definitions, and workflow configuration rather than by rewriting the backend.

---

## Directory Structure

```
app/
  main.py              # FastAPI application factory
  agents/
    workflow.py        # LangGraph workflow graph; all nodes defined here
  api/
    routes.py          # HTTP route handlers; thin layer over workflow + DB
  models/
    database.py        # SQLAlchemy engine and session factory
    models.py          # AgentRun ORM model
  schemas/
    agent_run.py       # Pydantic response schemas
    intake.py          # Pydantic intake request schemas (FreelanceIntakeRequest, etc.)
  services/
    validation.py      # Required-field validation logic
    clarification.py   # Clarification question generation
    normalization.py   # Deterministic input normalization (Phase 2-B)
  templates/
    freelance.py       # Freelance-specific field definitions and metadata
```

---

## Workflow Graph

The core processing is a LangGraph `StateGraph`. Each node receives and returns `AgentState` (a typed dict). Routing between nodes is determined by conditional edges.

The workflow is intentionally stateful and phase-based. Each phase should leave behind an inspectable artifact: original intake, missing fields, clarification questions, normalized data, future LLM output, future drafts, future approval state, and future archive records.

### Current active path

```
intake
  └─► validate_required_fields
          │
          ├─ [fields missing] ─► clarify_missing_info ─► END
          │                       status: "needs_clarification"
          │
          └─ [all fields present] ─► mark_validated
                                          └─► normalize_input ─► END
                                               status: "validated"
```

**`validate_required_fields`** — calls `validation.py` to check required fields against the current agent template's definition. Sets `missing_fields` on state.

**`clarify_missing_info`** — calls `clarification.py` to generate human-readable questions for each missing field. Sets `clarification_questions` on state and status to `"needs_clarification"`.

**`mark_validated`** — sets status to `"validated"` when all required fields are present.

**`normalize_input`** — calls `normalization.normalize_intake_data()` to produce `normalized_data` from the raw intake. Runs only for validated runs.

### Future skeleton functions

Python functions for `analyze_with_llm`, `score_result`, `draft_action`, `human_review`, and `archive` may exist as future-phase scaffolding. They are not registered in the compiled graph and their edges are not connected. They must remain inactive until the corresponding phase is explicitly implemented.

---

## Persistence Flow

Routes call the workflow, collect the final `AgentState`, and write a single `AgentRun` record to SQLite:

```
POST /api/agents/{agent_type}/runs
  │
  ├─ Build and run workflow graph with intake payload
  ├─ Collect final AgentState
  └─ Write AgentRun to DB:
       run_id        ← new UUID
       agent_type    ← from path param
       status        ← from final state
       intake_data   ← original payload (unchanged)
       missing_fields
       clarification_questions
       normalized_data  ← present only for "validated" runs
       created_at / updated_at

GET /api/agents/runs/{run_id}
  └─ Read AgentRun from DB by UUID → return AgentRunResponse
```

Database: SQLite file (`agent_os.db` by default, overrideable with `DATABASE_URL`). Tables are created on startup if they do not exist. Each request gets its own SQLAlchemy session via FastAPI dependency injection.

### Reserved future API surfaces

The router currently exposes guarded `approve` and `reject` endpoints for a future approval phase. They only accept runs in `pending_approval`, and the active workflow never produces that status. These endpoints do not send, submit, post, crawl, or otherwise act on external accounts.

---

## Why intake_data and normalized_data Are Separate

`intake_data` is the user's original submission. It must never be modified. It serves as the audit record of exactly what the user provided.

`normalized_data` is a derived artifact produced by deterministic transformation. Storing it separately means:

- The original is always available for debugging and audit.
- Future phases (LLM analysis, scoring) operate on clean, structured input without risk of overwriting source data.
- If normalization logic changes, the original can be re-normalized without data loss.

---

## Supporting Future Agent Templates

The platform is designed for template reuse:

- `FreelanceIntakeRequest` in `schemas/intake.py` is one concrete schema; additional templates add their own schemas.
- `templates/freelance.py` defines the required fields for the freelance agent. New templates register their own required-field definitions in the same pattern.
- The `{agent_type}` path parameter in the API route allows the router to dispatch to the correct template without changing core logic.
- Validation and clarification nodes operate on `AgentState` and receive template-specific required fields and question text through the template configuration.
- `normalize_input` is wired as a generic workflow node, but the current normalization service understands the freelance intake field names. Future templates should add template-aware normalization rather than duplicating the workflow graph.

Future agent templates should be able to define:

- intake schema and required fields
- clarification questions
- normalization rules
- analysis prompt and structured output contract
- scoring rules or rubric
- draft action templates
- workflow configuration for which phases apply
- model-routing preferences once that phase exists

This project should read architecturally as an AI Agent orchestration platform: guided intake, reusable workflow engine, structured output, stateful workflow, model routing, human-in-the-loop review, safety boundaries, template extensibility, and cost-aware AI development.
