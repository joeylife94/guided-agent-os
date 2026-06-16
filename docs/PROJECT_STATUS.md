# Project Status

Last updated: 2026-06-14

---

## Current State

Three phases are complete. The system accepts structured intake data, validates required fields, generates clarification questions for missing fields, normalizes validated input, and persists every run to SQLite.

No LLM analysis, scoring, drafting, approval workflow, RAG, crawling, authentication, or external account action executes in the active workflow. Future-phase scaffolding may exist in code, but it is not wired into run creation.

## Product Destination

Guided Agent OS is intended to become a reusable Form-driven AI Agent OS, not a one-off freelance agent. The platform should let new guided intake agents be added through templates, schemas, prompts, structured output contracts, and workflow configuration with minimal new backend code.

The Freelance Opportunity Agent is the first proof-of-concept. Future candidates include AI Content Agent, Duru SKU & Marketing Agent, Personal Command Center Agent, AI Market Watch Agent, and other guided intake agents.

See [PRODUCT_DIRECTION.md](PRODUCT_DIRECTION.md) for success criteria and strategic positioning.

---

## Completed Phases

| Phase | Description |
|-------|-------------|
| **Phase 1** | Required-field validation and clarification question generation |
| **Phase 2-A** | Agent run persistence to SQLite |
| **Phase 2-B** | Deterministic input normalization (rule-based, no LLM) |

---

## Current API Surface

### Active endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/agents/{agent_type}/runs` | Create a new agent run; validates input, normalizes if valid, persists to DB |
| `GET` | `/api/agents/runs/{run_id}` | Retrieve a saved agent run by UUID |

### Reserved future-phase endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/agents/runs/{run_id}/approve` | Guarded future endpoint; active runs never reach `pending_approval` |
| `POST` | `/api/agents/runs/{run_id}/reject` | Guarded future endpoint; active runs never reach `pending_approval` |

These reserved endpoints do not make external calls and do not mean the approval workflow is implemented.

### Freelance agent required fields

`opportunity_title`, `client_description`, `project_description`

### Run status values

| Status | Meaning |
|--------|---------|
| `validated` | All required fields present; normalized_data populated |
| `needs_clarification` | One or more required fields missing; clarification_questions populated |
| `error` | Workflow raised an unhandled exception |

---

## Stored Artifacts (per AgentRun record)

| Field | Type | Notes |
|-------|------|-------|
| `run_id` | UUID | Unique identifier |
| `agent_type` | string | e.g. `"freelance"` |
| `status` | string | `validated` / `needs_clarification` / `error` |
| `intake_data` | JSON | Original, unmodified input payload |
| `missing_fields` | JSON array | Fields absent from intake |
| `clarification_questions` | JSON array | Questions to surface for the user |
| `normalized_data` | JSON | Cleaned fields + detected keywords, stack, language, category (validated runs only) |
| `created_at` | datetime | Set on creation |
| `updated_at` | datetime | Updated on any change |

Additional future-phase columns and relations are present but not populated by the active workflow:

- `analysis_summary`, `score`, `raw_llm_output`: null unless future LLM/scoring phases are wired
- `action_drafts`: empty because draft generation is inactive
- `reviewer_note`: only used by guarded future approval endpoints
- `error_message`: populated only when the workflow raises an exception

---

## Not Implemented Yet

- LLM analysis (`analysis_summary`, `raw_llm_output`)
- Structured AI output and model routing
- Opportunity scoring (`score`)
- Action / proposal draft generation
- Human approval workflow (approve/reject endpoints are reserved and unreachable from active runs)
- Archive or export
- Authentication
- Email, job application automation, or any external account actions
- Web crawling or scraping
- RAG pipelines
- Multi-agent orchestration
- Additional agent templates beyond freelance

---

## Next Recommended Phase

**Phase 3-A — LLM Structured Analysis**

Feed `normalized_data` into an LLM prompt and store a structured analysis in `analysis_summary` and `raw_llm_output`. No scoring or drafting yet. See [ROADMAP.md](ROADMAP.md) for details.
