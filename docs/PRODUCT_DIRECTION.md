# Product Direction

Guided Agent OS is a reusable **Form-driven AI Agent OS** built around guided intake, grounded retrieval, explicit human review, bounded tool execution, and persisted evidence.

The product goal is not one hard-coded agent. New agents should be added primarily through templates, schemas, prompts, policy/workflow configuration, and reusable services without rewriting the core workflow engine.

---

## Accepted Product Baseline

The following destinations are accepted and frozen unless later work exposes a real regression:

- **D1 — L3 Usable / Demonstrable**
- **D2 — L4 Controlled Operator Pilot**
- **D3 — Verified Local-LLM Controlled Operator Pilot**

The accepted controlled path includes structured intake, validation/clarification, normalization, semantic RAG, grounded answer/citation behavior, tool planning, policy/risk checks, explicit human approve/reject, reviewed execution-input digest binding, allowlisted read-only execution, persisted result/audit/retrieval provenance, and truthful unavailable-model fallback. D3 additionally proved bounded positive local inference through a real Ollama OpenAI-compatible endpoint with `qwen2.5:1.5b`.

These are bounded repository-pilot claims, not authorization for customer/private systems, write/destructive actions, unrestricted autonomy, enterprise auth/RBAC/SSO, distributed guarantees, production deployment, model benchmarking, SLA/SLO, or compliance claims.

---

## Current Destination — D4 Reusable Controlled Agent Template Pilot

D4 asks whether the accepted controlled workflow is genuinely reusable as a platform capability rather than being coupled to one literal agent type.

### D4-01 — template-configurable controlled workflow

The active milestone is Issue #70 / PR #71.

The intended product contract is:

- each registered template owns an explicit `execution_profile`;
- the workflow engine routes from that profile rather than from a hard-coded agent-type identity;
- `controlled_rag_agent` preserves the accepted D2/D3 controlled behavior;
- intake-only templates remain intake-only unless explicitly configured otherwise;
- missing, unknown, or incomplete controlled execution profiles fail closed;
- a future controlled template can reuse the same grounded-RAG → tool-plan → human-review architecture without adding another agent-type conditional in the core workflow engine;
- controlled result/audit persistence follows the validated execution profile rather than a literal template name.

D4-01 by itself does **not** establish the full D4 destination claim. D4 is reached only when at least two materially distinct registered templates use the same generic controlled workflow through configuration while preserving their own intake/policy distinctions and all accepted D3 safety/evidence boundaries.

The likely next proof, only if still needed after D4-01 acceptance, is a second real registered template using the same controlled profile. Prefer existing repository assets such as `public_enterprise_ai` rather than adding templates for count.

---

## Pre-authorized Farther Destinations

After D4 is reached and the MASTER is reconciled, the current human-approved envelope allows progression to:

- **D5 — Reviewer Identity-bound Decision Pilot**: bind approve/reject/recovery decisions to a bounded truthful reviewer identity while preserving run and reviewed-input digest correlation. This does not authorize OAuth/OIDC, Keycloak, enterprise SSO, broad RBAC, or production account lifecycle.
- **D6 — Policy-scoped Multi-tool Read-only Pilot**: prove that at least two materially distinct repository-owned read-only tools can traverse the same registry/policy/parameter/approval/execution/audit architecture without cross-tool authority leakage.

Anything beyond D6, including write/destructive authority, customer/private production integration, enterprise authorization, production deployment, distributed guarantees, signing/non-repudiation, or security/compliance certification, requires Human Review.

---

## Product Success Criteria

Guided Agent OS should continue to be judged by product-level reuse and trustworthy operation rather than activity count:

1. Non-expert users can provide structured input instead of engineering prompts.
2. Template configuration can select reusable workflow capabilities without hard-coded agent branches.
3. Grounding, review, policy, execution, and evidence boundaries remain explicit and inspectable.
4. No allowlisted tool executes without the accepted human-approval and reviewed-input binding.
5. New controlled templates reuse the same core architecture instead of duplicating a backend.
6. Progression is demonstrated by executable exact-head evidence, not by code existence or self-report.

---

## Explicit Non-goals in the Current Envelope

Do not expand the project merely to keep scheduled work active. In particular, avoid model/prompt variants, citation-display variants, cosmetic UI, arbitrary templates, proof-of-proof chains, broad refactors, write/destructive tools, customer/private data, enterprise auth, cloud/Kubernetes production deployment, SLA/SLO, or compliance claims unless a later authorized destination specifically requires them.
