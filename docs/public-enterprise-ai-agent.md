# Public Enterprise AI Agent Use Case

This document explains how **Guided Agent OS** can be adapted to a public-sector or enterprise AI-agent project.

The project is intentionally scoped as a **controlled agent workflow MVP**, not an unrestricted autonomous agent. The registered `public_enterprise_ai` template uses the shared controlled execution profile: structured intake is validated and normalized, grounded RAG/tool planning can run through the generic controlled workflow, and explicit template policy/security signals can require human review before any allowlisted read-only tool execution.

---

## Why this use case exists

Public-sector and enterprise AI-agent projects often start with ambiguous requirements:

- The target business workflow is not fully defined.
- Internal data sources are scattered across documents, databases, and legacy systems.
- Security constraints are not negotiable.
- LLM/RAG access must respect user authorization and audit requirements.
- Actual system-changing actions should not be executed without human review.

Guided Agent OS uses structured enterprise intake to make those requirements explicit before the request enters the shared bounded controlled-agent path.

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
| `user_request` | The concrete request/question that the shared grounded controlled workflow should process |

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
    "user_request": "Summarize the maintenance guidance relevant to the reported inspection condition and cite the retrieved source.",
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

When all required fields are provided, the request is validated and can traverse the registered shared controlled workflow. The resulting status depends on the grounded/tool plan and bounded policy signals. In particular, an explicit review requirement from `approval_policy` or a restricted/sensitive security constraint keeps the run at the human-review boundary rather than silently completing it.

A run that reaches review is expected to expose the reviewed execution input and remain pending until an explicit approve or reject decision. Rejection must not execute a tool. Approval does not grant arbitrary authority: only the existing allowlisted read-only execution path may proceed, with the reviewed-input digest and correlated result/audit evidence preserved.

The normalized intake and controlled-run evidence are persisted and can be retrieved later through:

```http
GET /api/agents/runs/{run_id}
```

### Missing intake fields

When required fields — including `user_request` — are missing, the run returns:

```text
needs_clarification
```

The response includes clarification questions generated from the enterprise template.

---

## Enterprise design principles

### 1. Validate before analysis

The agent should not analyze or recommend solutions before the minimum business, data, security, and concrete request context is known.

### 2. Control data access

For enterprise use, RAG retrieval should be filtered by metadata, role, department, and document authorization. Database access should go through approved APIs or query templates rather than unrestricted LLM-generated SQL. The repository pilot itself does **not** claim enterprise authorization or customer production-system integration.

### 3. Keep human approval in the loop

The shared planner honors bounded template policy/security signals. An explicit human-review requirement or restricted/sensitive constraint must not be bypassed merely because a request appears innocuous. Human review also does not authorize write/destructive actions; the accepted pilot remains limited to allowlisted read-only tooling.

### 4. Make outputs auditable

The controlled workflow preserves request, normalized data, retrieval/citation provenance, reviewed execution input, approval/rejection decision, allowlisted tool result when executed, and correlated audit evidence within the repository pilot boundary.

---

## Relationship to the shared controlled RAG/tool path

`public_enterprise_ai` is the second registered template used to demonstrate reuse of the same generic controlled architecture as `controlled_rag_agent`. Its enterprise-specific intake and policy semantics remain distinct, but the workflow engine is selected through the template-owned execution profile rather than a new agent-type conditional.

The bounded path is:

1. **Structured intake / validation** — collect enterprise context plus a concrete `user_request`.
2. **Grounded RAG** — retrieve repository-owned public/synthetic-safe context and preserve source/citation provenance.
3. **Tool planning / policy check** — interpret bounded policy/security signals without inventing additional tool authority.
4. **Human review** — explicit approve/reject boundary with reviewed-input digest binding when execution is proposed.
5. **Allowlisted read-only execution / audit** — only the existing bounded read-only tool path may execute after approval, with correlated persistence/audit evidence.

This does not claim production enterprise RAG, customer/private-data access, reviewer authentication/RBAC/SSO, write/destructive authority, unrestricted autonomy, or production/compliance readiness.

---

## Interview positioning

Guided Agent OS should be described as:

> A FastAPI/LangGraph-based controlled agent workflow pilot that demonstrates template-configurable structured intake, grounded retrieval, policy-aware human review, allowlisted read-only execution, and correlated audit evidence across materially distinct registered templates.

It should not be described as:

> A fully autonomous production AI agent or a production enterprise authorization/integration platform.
