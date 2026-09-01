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
| Latest accepted milestone | **P-006 / Issue #28 read-only interrupted-decision recovery queue — CLOSED** |
| Active milestone | **P-007 / Issue #30 Operator deterministic evidence artifact — OPEN** |
| Active branch | `proof-v1.1/30-operator-evidence-artifact` |
| Active PR | **#31 — OPEN / first head RED expected** |
| Latest accepted progression merge | `c405b66d0a91f2924660d049f05390daab20ddaa` |
| P-007 first contract head | `873733a5c61611f5f475348005c39a1328545594` |

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
- no positive final-stack local-LLM inference claim; v1.0 accepted explicit non-claim closure.

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
| L-09 | CPU image resolves large CUDA/NVIDIA Torch dependency footprint | OPEN — deferred until bounded delivery value justifies work |
| L-11 | semantic provider identifier remains legacy `bge_m3` while actual model is MiniLM | OPEN — documented / low |
| L-12 | positive local-LLM final-stack inference not verified | ACCEPTED explicit non-claim |
| L-13 | controlled tool uses local fixture rather than customer system | ACCEPTED frozen-scope boundary |
| L-14 | execution result uses existing run output storage | ACCEPTED for Proof |
| L-17 | browser CI depends on GitHub runner Chrome + Selenium | ACCEPTED for Proof |
| L-20 | concurrency guarantee is current SQLite/SQLAlchemy-runtime scoped | ACCEPTED P-002 boundary |
| L-21 | crash after decision claim can leave ambiguous transient state | CONTAINED by P-004 quarantine; no replay/reconstruction claim |
| L-22 | interrupted/recovery-required run discovery requires a known run id | CLOSED by P-006 read-only recovery queue |
| L-23 | deterministic evidence bundle is API-accessible but not yet surfaced as a compact Operator delivery/review artifact | **ACTIVE — P-007 addresses Operator evidence usability only** |

---

# 4. Progression Registry

## P-001 — Replay-safe human approval finalization
**CLOSED — ACCEPTED**
- Issue #17; PR #18.
- exact head `c927cc83d97f92cd58f8a78c19b28fb67707f204`; merge `fc5f237f78a41ae4c099599445df99ea6d56f1b3`.
- PR Validation #54, Firebat #52, Proof Evaluation #3 PASS.
- sequential duplicate decisions are replay-safe; no distributed exactly-once claim.

## P-002 — Concurrent approval finalization guard
**CLOSED — ACCEPTED**
- Issue #19; PR #20 + corrective test-only PR #21.
- app head `228c6ce30084f22f6b45939643dd24f809c535bf`; PR Validation #59, Firebat #56, Proof Evaluation #4 PASS.
- corrective head `cd21a46db87a824a6c65643cc26d9aa71a813415`; PR Validation #61 PASS.
- latest merge `ad5f9b1a865d1be97ce427cc18760d7de5ca5a2e`.
- approve/approve and approve/reject races cross the bounded finalization boundary at most once.

## P-003 — Deterministic run evidence bundle
**CLOSED — ACCEPTED**
- Issue #22; PR #23.
- exact head `ab1c09a017184285e51d43758bd9f688e81e3a72`; merge `ff70352ba87017654ca5d180d141dc1c8eb1fe75`.
- PR Validation `33425357884` #66, Firebat `33425358523` #61, Proof Evaluation `33425357788` #6 PASS.
- read-only run+event bundle; deterministic sequence and SHA-256 digest; no tool/event mutation from reads.
- digest is not external notarization/non-repudiation.

## P-004 — Quarantine interrupted decisions without replay
**CLOSED — ACCEPTED**
- Issue #24; PR #25.
- exact head `3b99e9aebb9363aea3b1ce2434587839c3c352f0`; merge `b43da1762ed04cee9fa87e295511e3eb5b5d8a03`.
- PR Validation `33441510676` #69, Firebat `33441510318` #63, Proof Evaluation `33441510344` #7 PASS.
- transient decision claims can be explicitly quarantined to `decision_recovery_required` with zero replay and one idempotent recovery event.
- no inference whether an external side effect happened; no auto-resume/retry.

## P-005 — Operator quarantine UX
**CLOSED — ACCEPTED**
- Issue #26; PR #27.
- exact head `db42ce1d86cd578e97743814ce6ac1615ce4b751`; merge `8cf4a2847b527ae3f322dd744f0abec8b30844c8`.
- PR Validation `33450813525` #74, Firebat `33450813435` #68, Proof Evaluation `33450813445` #10 PASS.
- Operator UI surfaces interrupted/quarantined state, calls existing P-004 action, disables approve/reject when recovery is required, and can reopen a persisted run by id.

## P-006 — Read-only interrupted-decision recovery queue
**CLOSED — ACCEPTED**
- Issue #28; PR #29.
- first contract head `2cef6b981a3af7c2fc3a786185a3e8137891a970` established executable RED.
- accepted exact head `e8718b6ae823539be7cee3ffbc36500432a6bbb5`; merge `c405b66d0a91f2924660d049f05390daab20ddaa`.
- PR Validation `33466248162` #81, Firebat `33466248210` #74, Proof Evaluation `33466248142` #13 PASS.
- read-only queue returns only `approval_executing`, `rejection_processing`, `decision_recovery_required`, deterministically oldest-first with run-id tie-breaker.
- repeated reads are non-mutating and execute no tools; Operator queue selection reuses the persisted-run loader.
- limitation: discovery/read UX only; no automatic quarantine, retry, resume, notification, execution, or distributed recovery semantics.

## P-007 — Operator deterministic evidence artifact
**OPEN — CONTRACT HEAD / RED EXPECTED**

### Gate / Value
P-003 already provides a deterministic read-only run+events evidence bundle and SHA-256 digest, but the Operator Workspace does not expose it. Surfacing the existing artifact gives a human reviewer/demo operator a compact inspectable delivery artifact without increasing execution authority.

### Lifecycle
- Issue #30 — OPEN.
- Branch `proof-v1.1/30-operator-evidence-artifact` from reconciled main `d338af13437f3276cfefd7d4c4e37039106b8be0`.
- PR #31 — OPEN.
- first exact head `873733a5c61611f5f475348005c39a1328545594`.

### Acceptance Contract
1. Operator Workspace contains an explicit run-evidence panel/action tied to the currently loaded run.
2. UI reuses only `GET /api/agents/runs/{run_id}/evidence` for the evidence artifact.
3. Rendered artifact includes returned `evidence_digest` and deterministic bundle JSON.
4. Evidence loading adds no approve/reject/recover/tool-execution path.
5. Existing P-003 repeated-read/non-mutation semantics remain green.
6. Existing Golden Path, replay/concurrency/quarantine/recovery-queue semantics and required workflow suites remain green.
7. no signature/notarization/non-repudiation claim is introduced.

### Changed This Run
- accepted and reconciled P-006 after exact-head workflow success and expected-head merge.
- created Issue #30 and linked branch.
- added test-first Operator evidence UI contract.
- opened PR #31 on exact test-only head `873733a5c61611f5f475348005c39a1328545594`.

### Actually Executed
- re-read root Master first.
- verified P-006 exact head `e8718b6ae823539be7cee3ffbc36500432a6bbb5`: PR Validation #81, Firebat #74, Proof Evaluation #13 all success.
- resolved the first-head Codex review thread after implementation evidence.
- merged PR #29 with expected-head protection and closed Issue #28.
- confirmed no open PR/Issue before selecting P-007.

### Verified
- P-006 is repository/executable-evidence accepted.
- P-007 passes the milestone gate: concrete human review/delivery value, read-only scope, executable acceptance, no unresolved security/product decision.

### Not Verified
- P-007 evidence panel/action is not implemented on the first head.
- no P-007 PASS or merge claim exists yet.

### Limitations
P-007 is evidence usability only. The digest remains an integrity checksum, not an external signature, timestamp authority, notarization, or non-repudiation mechanism.

### Exact Next Action
Observe PR #31 first-head CI to establish executable RED. Then, inside the same Issue/PR, add the smallest Operator-only evidence panel that reads the existing P-003 endpoint and re-run exact-head regression before any merge.
