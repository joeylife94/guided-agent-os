# Guided Agent OS — Proof Master

> **Authoritative execution contract.** Repository state and executable evidence outrank agent self-report. Proof v1.0 remains CLOSED/FROZEN; post-v1.0 work proceeds only through bounded progression milestones.

## 0. Project Snapshot

| Item | Status |
|---|---|
| Project | Guided Agent OS |
| Repository | `joeylife94/guided-agent-os` |
| Baseline branch | `main` |
| Proof v1.0 | **CLOSED / FROZEN** |
| Current Level | **L3 — Usable / Demonstrable Proof** |
| Progression Mode | **ENABLED — bounded milestones only** |
| Latest accepted milestone | **P-011 / Issue #38 auditable approval execution-input snapshot — CLOSED** |
| Active milestone | **P-012 / Issue #40 bind human approval to reviewed execution-input digest — OPEN** |
| Active branch | `proof-v1.1/40-reviewed-digest-approval-binding` |
| Active PR | **#41 OPEN** |
| Latest accepted progression merge | `3c2a5c58d7735064e9f4132751e003dee8a58da6` |

The v1.0 acceptance baseline is not reopened by later milestones.

---

# 1. Frozen v1.0 Baseline

Accepted workflow:

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

Verified baseline capabilities:
- FastAPI / Pydantic / SQLite / SQLAlchemy / LangGraph.
- persistent Chroma semantic index with multilingual MiniLM; Korean/English retrieval.
- grounded answer/citation path with documented unavailable-local-LLM fallback.
- deterministic `legacy_db_lookup` read-only tool behind human approval and allowlist controls.
- reject/no-approval/unregistered/unauthorized/invalid-parameter blocking.
- browser Operator Workspace, persisted run reload, persisted audit timeline.
- fixed Proof Evaluation **22/22 PASS**, 0 failed.
- Firebat container reproduction and browser Golden Path.

Frozen non-claims:
- no unrestricted autonomous execution or broad write/destructive tools.
- no customer production database integration.
- no distributed exactly-once/recovery guarantee.
- no production auth/OAuth/RBAC/multi-tenancy claim.
- no positive final-stack local-LLM inference claim.

Frozen evidence anchors:
- verified app/eval merge `8498183f584332887a38ae5e925e6b810177e99b`.
- closure trigger baseline `35df8902ab22ce5daa13f3120fbdab386c7b21b3`.
- fixed evaluation: 22/22 PASS.

---

# 2. Validation / Lifecycle Rules

Each iteration records **Changed / Actually Executed / Verified / Not Verified / Limitations / Exact Next Action**.

Lifecycle:

```text
MASTER → one bounded Issue → linked branch → implementation/proof → PR
→ exact-head executed verification/review → merge → Issue close
→ MASTER reconciliation → milestone acceptance → next Progression Review
```

Rules:
- active PR first; one active implementation Issue by default.
- same-gap fixes remain inside the milestone.
- code existence/self-report is not PASS.
- no successful bounded run is generalized into unrestricted safety/autonomy/reliability claims.
- if no candidate has direct use/show/delivery value and bounded executable acceptance, remain ENABLED in HOLD/no-mutation mode.

---

# 3. Current Limitations / Risks

| ID | Risk | Status |
|---|---|---|
| L-09 | CPU image resolves large CUDA/NVIDIA Torch dependency footprint | OPEN — deferred |
| L-11 | semantic provider identifier remains legacy `bge_m3` while actual model is MiniLM | OPEN — documented / low |
| L-12 | positive local-LLM final-stack inference not verified | ACCEPTED explicit non-claim |
| L-13 | controlled tool uses local fixture rather than customer system | ACCEPTED frozen-scope boundary |
| L-17 | browser CI depends on GitHub runner Chrome + Selenium | ACCEPTED for Proof |
| L-20 | concurrency guarantee is current SQLite/SQLAlchemy-runtime scoped | ACCEPTED P-002 boundary |
| L-21 | crash after decision claim can leave ambiguous transient state | CONTAINED by P-004; no replay/reconstruction claim |
| L-22 | interrupted/recovery-required run discovery requires known run id | CLOSED by P-006 |
| L-23 | deterministic evidence bundle was API-only | CLOSED by P-007 |
| L-24 | Operator could not independently check displayed bundle/digest consistency | CLOSED by P-008 |
| L-25 | reviewed deterministic evidence could not be persisted directly from Operator Workspace | CLOSED by P-009 |
| L-26 | exact persisted execution inputs were not surfaced together at the human approval boundary | CLOSED by P-010 |
| L-27 | approval/tool audit events did not correlate the exact execution-input snapshot | CLOSED by P-011 |
| L-28 | browser approval action is not explicitly bound to the exact execution-input digest reviewed by the operator | OPEN — P-012 |

---

# 4. Progression Registry

## P-001 — Replay-safe human approval finalization
**CLOSED — ACCEPTED** — Issue #17, PR #18, merge `fc5f237f78a41ae4c099599445df99ea6d56f1b3`.

## P-002 — Concurrent approval finalization guard
**CLOSED — ACCEPTED** — Issue #19, PR #20 + corrective PR #21, latest merge `ad5f9b1a865d1be97ce427cc18760d7de5ca5a2e`.

## P-003 — Deterministic run evidence bundle
**CLOSED — ACCEPTED** — Issue #22, PR #23, exact head `ab1c09a017184285e51d43758bd9f688e81e3a72`, merge `ff70352ba87017654ca5d180d141dc1c8eb1fe75`.

## P-004 — Quarantine interrupted decisions without replay
**CLOSED — ACCEPTED** — Issue #24, PR #25, exact head `3b99e9aebb9363aea3b1ce2434587839c3c352f0`, merge `b43da1762ed04cee9fa87e295511e3eb5b5d8a03`.

## P-005 — Operator quarantine UX
**CLOSED — ACCEPTED** — Issue #26, PR #27, exact head `db42ce1d86cd578e97743814ce6ac1615ce4b751`, merge `8cf4a2847b527ae3f322dd744f0abec8b30844c8`.

## P-006 — Read-only interrupted-decision recovery queue
**CLOSED — ACCEPTED** — Issue #28, PR #29, exact head `e8718b6ae823539be7cee3ffbc36500432a6bbb5`, merge `c405b66d0a91f2924660d049f05390daab20ddaa`.

## P-007 — Operator deterministic evidence artifact
**CLOSED — ACCEPTED** — Issue #30, PR #31, exact head `bc40adc59cfdc64c4d0a86b188bf9522b7873fc1`, merge `9d5a89b982eef8b3e492aa52a380e7806cd207d5`.

## P-008 — Operator evidence digest local verification
**CLOSED — ACCEPTED** — Issue #32, PR #33, exact head `90652198add41eaaf6f95c182898d3ef530057d6`, merge `a238a9a89e3edb7afa5a00d0290c53483726625e`; exact-head validate / proof-eval / firebat-container SUCCESS.

## P-009 — Portable deterministic evidence download
**CLOSED — ACCEPTED** — Issue #34, PR #35, exact head `f21e2545a8a7417bda71f1b988aed15d7c77ee26`, merge `019f93ebffc9f9b0089e5f16378df8f160f6bcdc`; browser-only deterministic JSON export, no new network/execution authority.

## P-010 — Operator approval execution-input review
**CLOSED — ACCEPTED** — Issue #36, PR #37, exact head `33dcb87a1da90dc0b8cc86a136a37ac9bf807afd`, merge `3e8a653820f48c30bb60743184d2c90416523b26`; browser Golden Path verifies planned tool + persisted `tool_parameters` + per-run `allowed_tools` before approval.

## P-011 — Auditable approval execution-input snapshot
**CLOSED — ACCEPTED**
- Issue #38; PR #39.
- first contract head `ac16e09a6c22ab644007f394e6b7d49229fda1b0` established executable RED: validate run `33525861379` FAILURE.
- accepted exact head `cd3f3d6609772d8c4b74a0955570c9cfbc8808f3`; squash merge `3c2a5c58d7735064e9f4132751e003dee8a58da6`.
- exact-head checks: validate run `33531771136`, Proof Evaluation run `33531771205`, Firebat Container run `33531771324` — all SUCCESS.
- successful approval audits the canonical planned-tool + persisted `tool_parameters` + per-run `allowed_tools` snapshot and SHA-256 digest; `TOOL_EXECUTED` correlates the same digest.
- limitation: correlation in the same evidence store only; no signature, tamper-proof storage, notarization, non-repudiation, production RBAC, or unrestricted tool-safety claim.

## P-012 — Bind human approval to reviewed execution-input digest
**OPEN**
- Issue #40; PR #41.
- branch `proof-v1.1/40-reviewed-digest-approval-binding`.
- first contract head `bb48fb44c6c62c5a96d75af1f0986e0ba18a5255` is test-only and expects executable RED.
- bounded acceptance: Operator approve must carry the digest of the exact execution inputs reviewed in the pending-approval surface; server must recompute the current persisted digest after decision claim and before tool execution, fail closed on missing/mismatch, and preserve the successful matching path plus P-011 audit correlation.
- mismatch/missing precondition must return/revert to `pending_approval` and emit no false `TOOL_EXECUTED` evidence.
- no new endpoint, tool capability, write authority, autonomous execution, permission expansion, signing, or external trust claim.

### Changed This Run
- accepted and merged P-011 after exact-head PR Validation, Proof Evaluation, and Firebat Container all completed SUCCESS.
- closed Issue #38 completed and reconciled P-011 as accepted.
- bounded Progression Review identified a direct human-approval correctness gap: the browser approval action sends only a reviewer note and is not explicitly bound to the exact execution-input digest the operator reviewed.
- opened P-012 Issue #40, linked branch, test-first contract, and PR #41.

### Actually Executed
- root MASTER read first.
- PR #39 exact head `cd3f3d6609772d8c4b74a0955570c9cfbc8808f3` inspected directly; validate, proof-eval, firebat-container all completed SUCCESS.
- prior P1 review was confirmed addressed by the implementation head.
- PR #39 squash merged with expected-head protection; Issue #38 closed completed.
- current approval endpoint and Operator submit path inspected directly: approval execution recomputes/persists P-011 evidence, while browser approve currently submits only a note.
- P-012 test-only head `bb48fb44c6c62c5a96d75af1f0986e0ba18a5255` pushed and PR #41 opened.
- first-head validate run `33537981892` observed queued; no RED/PASS inferred yet.

### Verified
- P-011 acceptance is backed by exact-head executable evidence.
- P-012 has concrete use/security value, bounded executable acceptance, one-Issue/one-PR scope, and does not require product-direction or permission expansion.
- frozen human approval, allowlist, read-only execution, recovery, and non-autonomy boundaries remain explicit.

### Not Verified
- P-012 first-head executable RED has not yet completed.
- P-012 implementation does not yet exist and no P-012 PASS is claimed.
- no cryptographic signature, authenticated reviewer identity, tamper-proof storage, external notarization, production authorization/RBAC, non-repudiation, or unrestricted tool safety is established.

### Limitations
P-012 is an optimistic approval precondition inside the existing bounded workflow. A digest equality check is not an identity/authentication or external integrity guarantee.

### Exact Next Action
Observe PR #41 first-head validate for executable RED. Once RED is confirmed, implement the minimal reviewed-digest precondition inside Issue #40, including fail-closed missing/mismatch behavior before tool execution and browser submission of the exact reviewed digest, then run exact-head PR Validation, Proof Evaluation, and Firebat Container before any merge.