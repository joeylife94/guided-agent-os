# Guided Agent OS — Proof Master

> **Authoritative execution contract.** Repository state and executable evidence outrank agent self-report. Proof v1.0 remains CLOSED/FROZEN; post-v1.0 work proceeds only through bounded progression milestones.

---

## 0. Project Snapshot

| Item | Status |
|---|---|
| Project | Guided Agent OS |
| Repository | `joeylife94/guided-agent-os` |
| Baseline branch | `main` |
| Proof v1.0 | **CLOSED / FROZEN** |
| Current Level | **L3 — Usable / Demonstrable Proof** |
| Progression Mode | **ENABLED — bounded milestones only** |
| Latest accepted milestone | **P-005 / Issue #26 Operator interrupted-decision quarantine UX — CLOSED** |
| Active milestone | **NONE — Progression Review required** |
| Active branch | none |
| Latest progression merge | `8cf4a2847b527ae3f322dd744f0abec8b30844c8` |

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
- persistent Chroma semantic index using multilingual MiniLM.
- Korean/English intended-source retrieval.
- grounded answer/citation path and documented unavailable-local-LLM fallback.
- deterministic `legacy_db_lookup` read-only tool behind human approval and allowlist controls.
- reject/no-approval/unregistered/unauthorized/invalid-parameter blocking.
- browser Operator Workspace, persisted run reload, and persisted audit timeline.
- fixed Proof Evaluation: **22/22 PASS**, 0 failed.
- Firebat container reproduction and browser Golden Path.

Explicit frozen non-claims:
- no unrestricted autonomous execution.
- no destructive/write tools.
- no customer production database integration.
- no distributed exactly-once guarantee.
- no auth/OAuth/RBAC/multi-tenancy production system.
- no positive final-stack local-LLM inference claim; v1.0 accepted the explicit non-claim closure decision.

---

# 2. Validation Rule

Every milestone/run records:

## Changed
Only code/docs/config actually changed.

## Actually Executed
Only tests/build/API/browser/CI/repository checks actually run.

## Verified
Claims directly supported by executable/repository evidence.

## Not Verified
Anything not exercised on the relevant exact head.

## Limitations / Remaining Risks
Scope boundaries and unresolved uncertainty.

## Exact Next Action
One concrete next lifecycle action.

A successful run is never generalized into unrestricted safety, reliability, autonomy, or production-readiness claims.

---

# 3. Lifecycle Contract

```text
MASTER
→ one bounded Issue
→ linked branch
→ implementation/proof
→ PR
→ exact-head executed verification/review
→ merge
→ Issue close
→ MASTER reconciliation
→ milestone acceptance
→ next Progression Review
```

Rules:
- active PR first.
- one active implementation Issue by default.
- same-gap fixes stay inside the milestone.
- no state-only churn.
- new milestones require concrete use/show/delivery value, executable acceptance, bounded one-Issue/one-PR scope, and no unresolved product/security-direction decision.
- if no milestone passes the gate, remain ENABLED in lightweight HOLD/no-mutation mode.

---

# 4. Current Limitations / Risks

| ID | Risk | Status |
|---|---|---|
| L-09 | CPU image still resolves large CUDA/NVIDIA Torch dependency footprint | OPEN — deferred until bounded delivery value justifies work |
| L-11 | semantic provider identifier remains legacy `bge_m3` while actual model is MiniLM | OPEN — documented / low severity |
| L-12 | positive local-LLM final-stack inference not verified | ACCEPTED explicit non-claim |
| L-13 | controlled tool uses deterministic local fixture rather than customer system | ACCEPTED frozen-scope boundary |
| L-14 | execution result shares existing run output storage rather than dedicated execution table | ACCEPTED for Proof |
| L-17 | browser CI depends on GitHub runner Chrome + Selenium | ACCEPTED for Proof |
| L-19 | audit append helper remains API-boundary oriented | ACCEPTED for Proof |
| L-20 | concurrent finalization guarantee is current SQLite/SQLAlchemy-runtime scoped | ACCEPTED P-002 boundary |
| L-21 | crash after decision claim can leave ambiguous transient state | **CONTAINED by P-004 quarantine; no replay/reconstruction claim** |
| L-22 | operator must know a persisted run id to reopen/review an interrupted decision; no recovery work queue/discovery surface exists | OPEN — candidate only, not yet selected |

---

# 5. Frozen v1.0 Evidence Anchors

- final fixed evaluation artifact: 22/22 PASS, 0 failed.
- v1.0 verified app/eval merge: `8498183f584332887a38ae5e925e6b810177e99b`.
- final closure trigger baseline: `35df8902ab22ce5daa13f3120fbdab386c7b21b3`.
- final Firebat/browser reproduction and persisted audit evidence were accepted before v1.0 freeze.

These anchors remain historical acceptance evidence; later progression does not rewrite them.

---

# 6. Progression Registry

## P-001 — Replay-safe human approval finalization

**Status: CLOSED — ACCEPTED**

- Issue #17 — completed.
- PR #18 — merged.
- exact verified head `c927cc83d97f92cd58f8a78c19b28fb67707f204`.
- squash merge `fc5f237f78a41ae4c099599445df99ea6d56f1b3`.
- PR Validation #54 PASS; Firebat Container #52 PASS; Proof Evaluation #3 PASS.
- verified sequential duplicate approve/reject idempotency and conflicting later-decision blocking.
- no distributed exactly-once claim.

## P-002 — Concurrent approval finalization guard

**Status: CLOSED — ACCEPTED**

- Issue #19 — completed after corrective acceptance proof.
- PR #20 exact implementation head `228c6ce30084f22f6b45939643dd24f809c535bf`.
- PR Validation #59 PASS; Firebat Container #56 PASS; Proof Evaluation #4 PASS.
- implementation squash merge `2597109c845ca612d999928b6337e6c5e86c8811`.
- corrective test-only PR #21 exact head `cd21a46db87a824a6c65643cc26d9aa71a813415`; PR Validation #61 PASS.
- latest P-002 merge `ad5f9b1a865d1be97ce427cc18760d7de5ca5a2e`.
- verified approve/approve and approve/reject races cross the bounded finalization boundary at most once.
- no arbitrary distributed/external-side-effect exactly-once claim.

## P-003 — Deterministic run evidence bundle

**Status: CLOSED — ACCEPTED**

### Value
Expose one read-only deterministic representation of persisted run + audit evidence so reviewers do not manually correlate endpoints.

### Lifecycle / Evidence
- Issue #22 — closed / completed.
- PR #23 — merged.
- exact verified head `ab1c09a017184285e51d43758bd9f688e81e3a72`.
- squash merge `ff70352ba87017654ca5d180d141dc1c8eb1fe75`.
- PR Validation run `33425357884` #66 — PASS.
- Firebat Container run `33425358523` #61 — PASS.
- Proof Evaluation run `33425357788` #6 — PASS.

### Verified
- `GET /api/agents/runs/{run_id}/evidence` is read-only.
- persisted audit ordering is preserved.
- unchanged persisted state has stable canonical SHA-256 digest.
- legitimate lifecycle mutation changes evidence/digest.
- evidence reads do not execute tools or append audit events.

### Limitations
Digest is an integrity comparison inside the current application/database trust boundary; no non-repudiation, external notarization, or tamper-proof-storage claim.

## P-004 — Quarantine interrupted approval decisions without replay

**Status: CLOSED — ACCEPTED**

### Value
Contain an interrupted `approval_executing` / `rejection_processing` decision without blind retry or manufactured terminal history.

### Lifecycle / Evidence
- Issue #24 — closed / completed.
- PR #25 — merged.
- exact verified head `3b99e9aebb9363aea3b1ce2434587839c3c352f0`.
- squash merge `b43da1762ed04cee9fa87e295511e3eb5b5d8a03`.
- PR Validation run `33441510676` #69 — PASS.
- Firebat Container run `33441510318` #63 — PASS.
- Proof Evaluation run `33441510344` #7 — PASS.

### Verified
- explicit operator action moves only transient decision claims to `decision_recovery_required`.
- zero tool replay/execution from recovery action.
- no manufactured `APPROVED`, `REJECTED`, `TOOL_EXECUTED`, or `COMPLETED` event.
- one recovery audit event; repeat action is idempotent.
- normal approve/reject cannot execute from recovery-required state.
- P-003 evidence reflects quarantine deterministically.

### Limitations
No inference whether an external side effect occurred; no automatic resume/retry or distributed recovery semantics.

## P-005 — Surface interrupted-decision quarantine in Operator UI

**Status: CLOSED — ACCEPTED**

### Value
Make the P-004 safety control usable from the existing Operator Workspace without expanding execution authority.

### Lifecycle / Evidence
- Issue #26 — closed / completed.
- PR #27 — merged.
- exact verified head `db42ce1d86cd578e97743814ce6ac1615ce4b751`.
- squash merge `8cf4a2847b527ae3f322dd744f0abec8b30844c8`.
- PR Validation run `33450813525` #74 — PASS.
- Firebat Container run `33450813435` #68 — PASS.
- Proof Evaluation run `33450813445` #10 — PASS.

### Verified
- Operator UI renders interrupted decision states and explicit quarantine action.
- action calls the existing P-004 recovery endpoint, not approve/reject/tool execution.
- `decision_recovery_required` disables normal decision execution controls.
- persisted run can be reopened by run id for recovery review.
- existing pending-approval Golden Path/regressions remained green on exact head.

### Not Verified / Limitation
P-005's deterministic UI tests and full regression prove the UI/API contract, but no new claim is made that a real browser can discover an unknown interrupted run without already knowing its run id. There is currently no recovery queue/discovery surface.

---

# 7. Current Progression Review State

P-003, P-004, and P-005 are now reconciled against merged repository state and exact-head CI evidence.

There is no active PR or Issue at this reconciliation point. The next action is one bounded Progression Review. Candidate gaps must be judged against the milestone gate; the Master does not pre-authorize implementation merely because a limitation exists.

## Changed
- reconciled stale P-003 OPEN registry to actual P-003/P-004/P-005 accepted state.
- added exact merge SHAs and exact-head workflow evidence for P-003~P-005.
- recorded L-22 as a candidate observability/UX gap, not an accepted milestone.

## Actually Executed
- re-read current root Master on `main` first.
- confirmed no open PR and no open Issue.
- re-read Issues #22/#24/#26 and PRs #23/#25/#27.
- re-fetched exact-head workflow runs for P-003/P-004/P-005; all three required workflows are completed/success on each accepted head.

## Verified
- repository/executable evidence shows P-003/P-004/P-005 are closed and accepted.
- v1.0 remains CLOSED/FROZEN.

## Not Verified
- no new milestone implementation has been executed by this reconciliation commit.

## Exact Next Action
Perform one bounded Progression Review from this reconciled state. Select exactly one milestone only if it has direct use/show/delivery value and bounded executable acceptance; otherwise remain HOLD/no-mutation.
