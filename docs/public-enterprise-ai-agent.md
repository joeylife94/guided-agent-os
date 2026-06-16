# Public Enterprise AI Agent Use Case

This document explains how **Guided Agent OS** can be adapted to a public-sector or enterprise AI-agent project.

The project is intentionally scoped as a **controlled agent workflow MVP**, not an unrestricted autonomous agent. The goal is to collect structured requirements, validate missing information, normalize intake data, and prepare a safe foundation for later RAG, tool/API integration, and human approval.

---

## Why this use case exists

Public-sector and enterprise AI-agent projects often start with ambiguous requirements:

- The target business workflow is not fully defined.
- Internal data sources are scattered across documents, databases, and legacy systems.
- Security constraints are not negotiable.
- LLM/RAG access must respect user authorization and audit requirements.
- Actual system-changing actions should not be executed without human review.

Guided Agent OS addresses the first step of that problem: converting an ambiguous AI-agent request into a structured, reviewable, and auditable intake record.

---

## Agent type

```text
public_enterprise_ai
```

The template is implemented in:

```text
app/templates/public_enterprise_ai.py
```

It is registered in the FastAPI route registry, so it can be invoked through the existing generic endpoint:

```http
POST /api/agents/public_enterprise_ai/runs
```

---

## Required intake fields

| Field | Purpose |
|---|---|
| `use_case_title` | Short name of the internal AI-agent use case |
| `business_domain` | Domain such as energy, infrastructure, safety, customer service, or internal operations |
| `target_user_group` | Department, role, or user group that will use the agent |
| `current_workflow_problem` | Manual, repetitive, or knowledge-heavy workflow to improve |
| `data_sources` | Internal documents, manuals, databases, logs, or legacy systems to use |
| `expected_agent_capabilities` | What the agent should do: Q&A, retrieval, summarization, analysis, recommendations, etc. |

---

## Optional enterprise fields

| Field | Purpose |
|---|---|
| `legacy_systems` | Existing systems that may need API or database integration |
| `rag_document_types` | Candidate documents for RAG ingestion |
| `db_access_pattern` | Whether the agent should query databases through approved APIs or query templates |
| `llm_environment` | External API, private cloud, on-premise model, or unknown |
| `security_constraints` | Internal network, data protection, access-control, or compliance constraints |
| `approval_policy` | Which outputs or actions require human approval |
| `audit_requirements` | What should be logged for traceability |
| `integration_constraints` | Network, package, deployment, or system-integration constraints |
| `success_metrics` | Practical measures of project success |
| `out_of_scope_actions` | Actions that the AI agent must not perform automatically |

---

## Example request

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

---

## Expected behavior

### Complete intake

When all required fields are provided, the run returns:

```text
validated
```

The normalized intake is persisted in the database and can be retrieved later through:

```http
GET /api/agents/runs/{run_id}
```

### Missing intake fields

When required fields are missing, the run returns:

```text
needs_clarification
```

The response includes clarification questions generated from the enterprise template.

---

## Enterprise design principles

### 1. Validate before analysis

The agent should not analyze or recommend solutions before the minimum business, data, and security context is known.

### 2. Control data access

For enterprise use, RAG retrieval should be filtered by metadata, role, department, and document authorization. Database access should go through approved APIs or query templates rather than unrestricted LLM-generated SQL.

### 3. Keep human approval in the loop

The agent may draft summaries, recommendations, or next actions, but operationally meaningful actions should require explicit human review.

### 4. Make outputs auditable

Enterprise AI systems should preserve the request, normalized data, retrieved sources, tool/API calls, reviewer decisions, and final status.

---

## Relationship to future RAG/tool phases

This use case is intentionally Phase 1 oriented. It does not claim to be a full production RAG implementation.

Instead, it prepares structured inputs for later phases:

1. **RAG scope design** — document types, metadata filters, source citation requirements
2. **Tool/API scope design** — which legacy queries should be exposed as controlled tools
3. **Security design** — role-based access, audit logs, internal-network constraints
4. **Human approval design** — which actions are informational, review-required, or prohibited

---

## Interview positioning

Guided Agent OS should be described as:

> A FastAPI/LangGraph-based controlled agent workflow MVP that demonstrates structured intake, validation, clarification, normalization, persistence, and human-approval-oriented design for enterprise AI-agent use cases.

It should not be described as:

> A fully autonomous production AI agent.
