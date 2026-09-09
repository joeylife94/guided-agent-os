# Guided Agent OS — Proof Master

> **Authoritative execution contract.** Repository state and executable evidence outrank agent self-report. Proof v1.0 remains CLOSED/FROZEN. Accepted destination evidence is not generalized beyond the explicit boundaries below.

## 0. Project Snapshot

| Item | Status |
|---|---|
| Project | Guided Agent OS |
| Repository | `joeylife94/guided-agent-os` |
| Baseline branch | `main` |
| Proof v1.0 | **CLOSED / FROZEN** |
| D1 | **DESTINATION REACHED — L3 USABLE / DEMONSTRABLE** |
| D2 | **DESTINATION REACHED — L4 CONTROLLED OPERATOR PILOT** |
| D3 | **DESTINATION REACHED — VERIFIED LOCAL-LLM CONTROLLED OPERATOR PILOT** |
| D4 | **SELECTED / IN PROGRESS — REUSABLE CONTROLLED AGENT TEMPLATE PILOT** |
| Latest accepted milestone | **D3-01 / Issue #68 positive real local-LLM inference — CLOSED / ACCEPTED** |
| Accepted D3-01 head | `f7677638d41ac7654b935b559a932b7db1108352` |
| Latest accepted progression merge | `d8962279cd926c073b3b8df1ebc19348fc893823` |
| Active milestone | **D4-01 / Issue #70 — template-configurable controlled workflow** |
| Active PR | **#71** |
| Progression state | **D4 ACTIVE — EXACT-HEAD ACCEPTANCE IN PROGRESS** |

D1, D2, and D3 remain accepted/frozen. Human-approved long-term progression on 2026-09-09 selected D4 and pre-authorized bounded continuation to D5 and D6 only after destination-level acceptance and MASTER reconciliation. D7 or any expansion into write/destructive authority, customer/private production systems, enterprise authorization, production deployment, distributed guarantees, signing/non-repudiation, or security/compliance certification requires Human Review.

---

# 1. Frozen v1.0 Baseline

Accepted bounded workflow:

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
→ Persistent Audit Trail
```

Verified baseline capabilities include FastAPI/Pydantic/SQLite/SQLAlchemy/LangGraph, persistent semantic retrieval with multilingual MiniLM, grounded answer/citation behavior with documented unavailable-local-LLM fallback, deterministic `legacy_db_lookup` read-only execution behind approval/allowlist controls, reject/no-approval/unregistered/unauthorized/invalid-parameter blocking, browser Operator Workspace, persisted run/audit reload, fixed Proof Evaluation 22/22 PASS, and Firebat/browser reproduction.

Frozen non-claims:
- no unrestricted autonomous execution or broad write/destructive tools;
- no customer production database integration;
- no distributed exactly-once/recovery guarantee;
- no production auth/OAuth/RBAC/multi-tenancy claim;
- no signing/non-repudiation or tamper-proof claim;
- no generalized model-quality, benchmark, production-readiness, SLA/SLO, or security/compliance claim from D3 evidence.

Frozen evidence anchors:
- verified app/eval merge `8498183f584332887a38ae5e925e6b810177e99b`;
- closure trigger baseline `35df8902ab22ce5daa13f3120fbdab386c7b21b3`;
- fixed evaluation: 22/22 PASS.

---

# 2. Destination Acceptance

## D1 — L3 Usable / Demonstrable

**DESTINATION REACHED — L3 USABLE / DEMONSTRABLE.**

Accepted evidence spans structured intake and semantic grounding; exact execution-input review; reviewed-digest binding; explicit approve/reject behavior; allowlisted read-only execution; persisted result/audit correlation; deterministic evidence bundle/digest/export; recovery/quarantine visibility; semantic provenance persistence/presentation; and executed browser proof for the bounded Operator surfaces.

## D2 — L4 Controlled Operator Pilot

**DESTINATION REACHED — L4 CONTROLLED OPERATOR PILOT.**

P-025 composes the accepted bounded product into one reviewer-runnable clean-environment pilot path:

```text
setup/start
→ structured intake + RAG grounding
→ exact execution-input review
→ explicit reject boundary with no tool execution
→ separate explicit approval
→ allowlisted read-only `legacy_db_lookup`
→ persisted result/audit/retrieval provenance
→ deterministic evidence export + reload
→ bounded recovery/quarantine visibility
```

Accepted implementation head: `21549a4c2d026d2d1b951ac718e54ff2a7ce4e9c`.

Exact-head executed evidence:
- PR Validation — **SUCCESS**;
- Firebat Container — **SUCCESS**;
- P-025 Controlled Operator Pilot — **SUCCESS**.

PR #67 was merged with expected-head protection to `82c0977c93c0db976fb3138d921b40f91fc9f5ec`; Issue #66 is CLOSED/completed.

## D3 — Verified Local-LLM Controlled Operator Pilot

**DESTINATION REACHED — VERIFIED LOCAL-LLM CONTROLLED OPERATOR PILOT.**

Human Review on 2026-09-07 selected D3 to close the explicit positive final-stack local-inference gap while preserving the accepted D2 authority boundary.

### D3-01 — Issue #68

**CLOSED / ACCEPTED.**

Accepted exact candidate head: `f7677638d41ac7654b935b559a932b7db1108352`.

Accepted progression merge: `d8962279cd926c073b3b8df1ebc19348fc893823` via PR #69 with expected-head protection.

Exact-head executed evidence established:
- a real host-local Ollama OpenAI-compatible endpoint was reachable and invoked from the Firebat container;
- exact acceptance model `qwen2.5:1.5b` was pulled and used for positive inference;
- bounded runtime provenance: Ollama local endpoint on GitHub-hosted Ubuntu 24.04 CPU runtime, without private host details or secrets;
- a grounded request returned non-empty retrieved context and non-empty real model-generated output;
- the generated answer contained an exact `SOURCE [collection:doc_id:chunk-N]` label selected from the same returned retrieved context, while citation metadata remained source-verifiable;
- the intentionally missing-model path remained explicit fallback with `model.available == false`, distinct from positive acceptance;
- the persisted approved controlled run recorded `rag_answer.model.available == true` and exact expected model `qwen2.5:1.5b`;
- explicit rejection still produced no tool execution;
- explicit approval still gated allowlisted read-only `legacy_db_lookup` execution;
- correlated result/audit/retrieval provenance and accepted D2 evidence/reload surfaces remained intact;
- D3 Positive Local LLM Pilot, P-025 Controlled Operator Pilot, PR Validation, Firebat Container, Proof Evaluation, and related browser proof workflows were GREEN on the accepted candidate head;
- all PR #69 review threads, including the two earlier P1 findings and the final P2 workflow-trigger finding, were resolved before merge.

D3 acceptance is bounded to this controlled repository pilot. It does not authorize broader model autonomy, customer data/system access, write/destructive tools, reviewer identity, distributed guarantees, or production/compliance claims.

## D4 — Reusable Controlled Agent Template Pilot

**SELECTED / IN PROGRESS.**

Human direction on 2026-09-09 selected D4 to prove that the accepted controlled workflow is reusable through explicit template/workflow configuration rather than a literal hard-coded agent identity.

### D4-01 — Issue #70 / PR #71

**ACTIVE — exact-head acceptance in progress.**

Bounded implementation contract:
- templates own an explicit `execution_profile`;
- core workflow routing is selected from the validated profile, not from `agent_type == "controlled_rag_agent"`;
- existing `controlled_rag_agent` behavior remains at accepted D2/D3 boundaries;
- intake-only templates remain intake-only unless explicitly configured;
- missing, unknown, or incomplete execution-profile configuration fails closed;
- a distinct test configuration can traverse the same generic controlled path without adding an agent-type conditional;
- controlled result/audit persistence follows the validated execution profile rather than a literal template identity.

Current pre-reconciliation executable candidate `d30ba2eb949cc3a133e85be333cd55b7085fc3ba` was observed GREEN for PR Validation, D3 Positive Local LLM Pilot, P-025 Controlled Operator Pilot, Firebat Container, Proof Evaluation, P-024 Retrieval Provenance, P-019 Rejection Run Binding, and P-018 Rejection Rationale. That evidence is not yet D4-01 acceptance because this branch-side MASTER/docs reconciliation moves the exact head and requires a final exact-head rerun/review.

D4 destination is **not** reached by D4-01 alone. Destination acceptance requires at least two materially distinct registered templates to use the same generic controlled workflow architecture through configuration while their template-specific intake/policy configuration remains distinct and the frozen D3 control/evidence boundary remains preserved.

---

# 3. Progression Registry

P-001 through P-025 remain **CLOSED / ACCEPTED** under their previously recorded merge evidence. Key later milestones:

- **P-020 CLOSED / ACCEPTED** — enforce non-blank rejection rationale server-side; Issue #56 / PR #57; merge `02b310378591e81ca4d26d02fb6c0315d9f4f2b5`.
- **P-021 CLOSED / ACCEPTED** — truthful semantic embedding provenance + MiniLM delivery defaults; Issue #58 / PR #59; merge `1db147e10f630dd0880e636c43849a93874c10b8`.
- **P-022 CLOSED / ACCEPTED** — persist semantic retrieval provenance in run audit evidence; Issue #60 / PR #61; merge `485ad9f218467d6ec3d66e4502e30a0ed972d239`.
- **P-023 CLOSED / ACCEPTED** — surface retrieval provenance in Operator evidence summary; Issue #62 / PR #63; merge `b656e1881c13f40845a463076e0d9fffe786a211`.
- **P-024 CLOSED / ACCEPTED** — browser-verify Operator retrieval provenance summary; Issue #64 / PR #65; merge `7096ae6d1dc9d41d24f895daed56f665736b58fa`.
- **P-025 CLOSED / ACCEPTED** — D2 Controlled Operator Pilot acceptance path; Issue #66 / PR #67; accepted head `21549a4c2d026d2d1b951ac718e54ff2a7ce4e9c`; merge `82c0977c93c0db976fb3138d921b40f91fc9f5ec`.
- **D3-01 CLOSED / ACCEPTED** — positive real local-LLM inference in the controlled operator pilot; Issue #68 / PR #69; accepted head `f7677638d41ac7654b935b559a932b7db1108352`; merge `d8962279cd926c073b3b8df1ebc19348fc893823`.
- **D4-01 ACTIVE** — template-configurable controlled workflow; Issue #70 / PR #71; exact-head acceptance pending after MASTER/docs reconciliation.

Earlier P-001 through P-019 acceptance history remains authoritative in Git/Issue/PR history and is not reopened by this reconciliation.

---

# 4. Current Limitations / Boundaries

- CPU image/model dependency footprint remains an optimization concern, not a D3 acceptance blocker.
- `legacy_db_lookup` remains a deterministic local fixture, not customer-system integration.
- concurrency/recovery evidence remains bounded to the current SQLite/SQLAlchemy runtime and documented quarantine/recovery semantics; no replay/reconstruction or distributed guarantee is claimed.
- browser proof remains bounded to the repository Firebat/GitHub Actions/headless-Chrome environment.
- real local-LLM evidence is bounded to the accepted Ollama + `qwen2.5:1.5b` controlled-pilot path; it is not a model-quality, benchmark, throughput, or production-serving claim.
- D4-01 proves configurable routing architecture only; the D4 product-level reuse claim still requires a second materially distinct registered controlled template if Destination Review confirms that blocker remains.
- reviewer identity/authentication, enterprise RBAC/SSO, customer authorization, write/destructive tooling, unrestricted autonomy, signing/non-repudiation, customer/private data integration, cloud/Kubernetes production deployment, SLA/SLO, and security/compliance certification remain explicitly unaccepted.

---

# 5. Destination Gate

**CURRENT DESTINATION — D4 REUSABLE CONTROLLED AGENT TEMPLATE PILOT.**

Finish active D4-01 before selecting farther work. After D4-01 acceptance, perform Destination Review.

If the D4 product-level claim is still blocked because only one registered template actually uses the generic controlled profile, the smallest allowed follow-on is D4-02: prove a second materially distinct registered template through the same generic controlled workflow, preferably reusing existing `public_enterprise_ai` and repository-owned public/synthetic-safe knowledge/tool fixtures.

Do not add templates merely to increase count and do not create proof-of-proof/UI-only micro-milestones.

After D4 is explicitly reached and this MASTER is reconciled, D5 is pre-authorized. After D5 is reached and reconciled, D6 is pre-authorized. D7 or any write/destructive/customer-production/enterprise-auth/production-deployment/distributed-guarantee/signing/compliance expansion requires Human Review.

---

# 6. Current Run Record

### Current Destination
D4 — `Reusable Controlled Agent Template Pilot`.

### Current Milestone
D4-01 / Issue #70 / PR #71 — `make controlled-agent workflow template-configurable`.

### Changed
- template-owned execution profiles implemented on PR #71;
- core post-normalization routing changed from literal controlled-agent identity to validated execution-profile routing;
- invalid/incomplete profile configuration fails closed;
- controlled persistence follows the validated profile rather than a literal template name;
- stale validation fixture aligned with production registry configuration;
- directly relevant `docs/PRODUCT_DIRECTION.md` and `docs/ARCHITECTURE.md` reconciled with the accepted D1-D3 baseline and active D4 architecture;
- MASTER reconciled to record D4 selected/current and D4-01 active without claiming acceptance.

### Actually Executed
- current root MASTER on `main` read first;
- PR #71 exact head `d30ba2eb949cc3a133e85be333cd55b7085fc3ba` re-fetched;
- eight current exact-head GitHub Actions runs inspected and observed `completed/success` before documentation reconciliation: PR Validation, D3 Positive Local LLM Pilot, P-025 Controlled Operator Pilot, Firebat Container, Proof Evaluation, P-024 Retrieval Provenance, P-019 Rejection Run Binding, and P-018 Rejection Rationale;
- the outstanding P1 implementation review thread was answered with exact-head evidence and resolved;
- branch-side product direction, architecture, and MASTER reconciliation applied in the same PR.

### Verified
- the pre-reconciliation implementation candidate preserved accepted D2/D3 workflow/runtime gates across the observed exact-head workflows;
- generic profile-based workflow routing and fail-closed configuration behavior passed PR Validation on that candidate;
- existing controlled operator/local-LLM/Firebat/evaluation/browser evidence surfaces remained GREEN on that candidate;
- review blocker concerning missing execution-profile implementation is resolved.

### Not Verified
- final post-reconciliation exact head has not yet completed the required executable rerun;
- D4-01 is therefore not yet ACCEPTED;
- the D4 destination-level two-template reuse claim is not yet established;
- D5/D6 are not active and no authority expansion is implied.

### Remaining Risks
- documentation/MASTER reconciliation moves the candidate head and must not inherit PASS from the earlier head;
- a later exact-head review may expose a concrete routing/persistence/configuration regression;
- D4 may still require one coherent D4-02 registered-template reuse milestone after D4-01 closure.

### Exact Next Action
Wait for the new exact PR head produced by this reconciliation. Make no further mutation while required CI is queued/in progress. If all required exact-head gates are GREEN and review is clean, merge PR #71 with expected-head protection where supported, confirm Issue #70 closure, reconcile current `main`, then perform D4 Destination Review. If RED, correct only the first concrete same-gap failure inside PR #71.
