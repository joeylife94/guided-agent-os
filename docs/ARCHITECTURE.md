# Architecture

---

## Overview

Guided Agent OS is a FastAPI application backed by a LangGraph workflow graph, reusable template configuration, and SQLite/SQLAlchemy persistence. The current accepted platform can run structured intake through grounded semantic retrieval, local-LLM answer generation, tool planning, explicit human review, bounded read-only execution, and correlated persisted audit/provenance evidence.

The architecture is intentionally template-driven. A registered template supplies its intake contract and an explicit `execution_profile`; the core workflow selects capabilities from that profile instead of special-casing a literal agent type.

Proof v1.0 and destinations D1/D2/D3 remain accepted/frozen. D4 is the current reuse destination and must preserve all accepted approval, digest-binding, allowlist, provenance, persistence, and fallback boundaries.

---

## Core Structure

```text
app/
  agents/
    workflow.py          # shared LangGraph nodes and profile-based routing
  api/
    routes.py            # HTTP API, template lookup, persistence and operator surfaces
  models/                # SQLAlchemy persistence models/session
  schemas/               # request/response contracts
  services/
    validation.py
    clarification.py
    normalization.py
    rag_answerer.py
    local_llm.py
    tool_registry.py
    tool_executor.py
    policy.py
  templates/
    freelance.py
    public_enterprise_ai.py
    controlled_rag_agent.py
```

The exact file set evolves, but the architectural rule is stable: template-specific identity/configuration belongs in the template registry; reusable execution behavior belongs in shared workflow/services.

---

## Template Configuration Contract

A registered template provides the fields needed for intake/clarification plus an explicit `execution_profile`.

Two bounded execution modes are currently relevant:

- `intake_only`: validation/clarification/normalization only;
- controlled RAG profile: shared semantic RAG → grounded answer → tool plan/policy → human review → allowlisted read-only execution/persistence path.

The workflow engine must not decide controlled behavior by testing for `agent_type == "controlled_rag_agent"` or another literal template name. A future registered template can select the same controlled architecture by providing the validated profile contract.

Missing, unknown, or incomplete execution-profile configuration fails closed rather than silently escalating an intake-only template into a controlled workflow.

---

## Shared Workflow

Conceptually, the accepted controlled path is:

```text
Structured Intake
→ Validation / Clarification
→ Normalization
→ Semantic RAG
→ Grounded Answer + Citation
→ Tool Planning
→ Risk / Policy Check
→ Human Approval
→ Allowlisted Read-only Tool Execution
→ Execution Result Persistence
→ Persistent Audit / Retrieval Provenance
```

Conditional LangGraph routing uses the validated execution profile after normalization:

- intake-only profile → bounded validated/intake completion;
- controlled profile → reusable controlled RAG path;
- invalid/incomplete profile → fail closed with an error/bounded terminal state.

The same generic controlled nodes are reused regardless of the template name. D4-01 acceptance requires a distinct test configuration to traverse that route without another hard-coded agent-type branch.

---

## Human Review and Execution Boundary

Generation does not execute tools directly. The accepted control boundary remains:

1. RAG/model output informs a proposed tool plan.
2. Policy and allowlist checks bound the proposed tool/parameters.
3. The exact reviewed execution input is digest-bound.
4. Explicit rejection produces no tool execution.
5. Explicit approval gates the executor.
6. Only registered, allowed, read-only tools are executable in the current envelope.
7. Result, decision, audit, and retrieval/model provenance are persisted and correlated to the run.

D4 changes routing/configuration reuse; it does not broaden authority.

---

## Local LLM and Grounding Boundary

The accepted D3 path uses the existing OpenAI-compatible `LocalLLMClient` and semantic RAG services. Exact accepted positive evidence used host-local Ollama with `qwen2.5:1.5b` in the bounded Firebat/GitHub Actions CPU environment.

The runtime preserves:

- non-empty retrieved context for the grounded path;
- source-verifiable citation/retrieval provenance;
- non-empty real model-generated output for positive local inference;
- a clearly distinguishable unavailable-model fallback;
- no cloud-model or HTTP-stub substitution presented as local positive inference.

D4 must preserve these semantics for the existing controlled template. Reusability does not generalize the D3 model-quality or production-serving claim.

---

## Persistence

Routes invoke the shared workflow and persist the resulting `AgentRun` plus the accepted controlled evidence surfaces. Controlled persistence must follow the validated execution profile, not a literal template identity, so another configured controlled template cannot traverse the workflow while silently losing its result/audit/provenance evidence.

The original intake remains distinct from derived normalized, retrieval, model, review, execution, and audit artifacts. This supports traceability without claiming signing, tamper-proofing, distributed exactly-once behavior, or production-grade recovery.

---

## D4 Reuse Boundary

D4-01 proves that workflow capability selection is configuration-owned and fail-closed. Full D4 destination acceptance requires at least two materially distinct **registered** templates to use the same generic controlled architecture through configuration while their template-specific intake/policy configuration remains distinct.

A second template should reuse existing repository-owned public/synthetic-safe knowledge and deterministic read-only fixtures wherever possible. Adding another template merely to increase count is not an architectural goal.

---

## Explicitly Outside the Current Architecture Claim

The current human-approved progression envelope does not authorize write/destructive tools, customer/private production systems, enterprise RBAC/SSO/multi-tenancy, unrestricted autonomy, distributed exactly-once/recovery guarantees, signing/non-repudiation, cloud/Kubernetes production deployment, SLA/SLO, security/compliance certification, or broad model benchmarking/tuning.
