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
| Latest accepted milestone | **P-007 / Issue #30 Operator deterministic evidence artifact — CLOSED** |
| Active milestone | **P-008 / Issue #32 Operator evidence digest local verification — OPEN** |
| Active branch | `proof-v1.1/32-operator-evidence-digest-verification` |
| Active PR | **#33 — OPEN / first head RED expected** |
| Latest accepted progression merge | `9d5a89b982eef8b3e492aa52a380e7806cd207d5` |
| P-008 first contract head | `a5ba9cd763c1eeff5ff75462aa9fc1279949e6f7` |

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
| L-23 | deterministic evidence bundle was API-only | CLOSED by P-007 Operator evidence surface |
| L-24 | Operator can display server digest but cannot independently check displayed bundle/digest consistency | **ACTIVE — P-008 local integrity verification only** |

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
**CLOSED — ACCEPTED**
- Issue #30; PR #31.
- first contract head `873733a5c61611f5f475348005c39a1328545594` established executable RED.
- accepted exact head `bc40adc59cfdc64c4d0a86b188bf9522b7873fc1`; merge `9d5a89b982eef8b3e492aa52a380e7806cd207d5`.
- exact-head checks: PR Validation run `33473699413`, Firebat Container run `33473699508`, Proof Evaluation run `33473699743` — all SUCCESS.
- Operator Workspace exposes the existing read-only P-003 evidence endpoint, including `evidence_digest` and deterministic bundle JSON, without adding approve/reject/recover/tool-execution authority.
- limitation: evidence digest remains an integrity checksum, not a signature, timestamp authority, notarization, or non-repudiation mechanism.

## P-008 — Operator evidence digest local verification
**OPEN — CONTRACT HEAD / RED EXPECTED**

### Gate / Value
P-007 exposes the deterministic evidence bundle and server digest in the Operator Workspace. A reviewer still cannot independently check whether the visible bundle canonicalizes to that digest. Local browser verification gives concrete review/demo value while remaining read-only and bounded.

### Lifecycle
- Issue #32 — OPEN.
- Branch `proof-v1.1/32-operator-evidence-digest-verification` from reconciled main `39cc053d216d5bea338d08429805999ffe69a3cd`.
- PR #33 — OPEN.
- first exact head `a5ba9cd763c1eeff5ff75462aa9fc1279949e6f7`.

### Acceptance Contract
1. Operator evidence panel exposes an explicit verification status for the currently rendered artifact.
2. Browser recomputes SHA-256 from deterministic canonical evidence content, excluding `evidence_digest`, and valid unchanged evidence renders MATCH.
3. deterministic tampered fixture renders MISMATCH.
4. unavailable browser crypto or digest renders UNAVAILABLE rather than PASS.
5. verification creates no additional approve/reject/recover/tool-execution request and performs no server mutation.
6. existing P-003/P-007 evidence behavior plus Golden Path, replay/concurrency/quarantine/recovery-queue semantics and required workflow suites remain green.
7. no signature/notarization/non-repudiation or hostile-client security claim is introduced.

### Changed This Run
- accepted and reconciled P-007 after exact-head workflow success and expected-head merge.
- confirmed no open Issue/PR before Progression Review.
- created Issue #32, linked branch, test-first contract, and PR #33.

### Actually Executed
- root MASTER read first.
- exact P-007 head check-runs inspected directly: validate, proof-eval, firebat-container all success.
- PR #31 merged with expected-head protection; Issue #30 closed completed.
- P-008 branch created from reconciled main and first contract commit pushed.

### Verified
- P-007 is repository/executable-evidence accepted.
- P-008 passes the milestone gate: concrete human review value, read-only scope, executable acceptance, no unresolved product/security decision.

### Not Verified
- P-008 local digest verification is not implemented on the first head.
- no P-008 PASS or merge claim exists yet.

### Limitations
P-008 checks local consistency only. It does not authenticate the server/operator or establish any external chain of trust.

### Exact Next Action
Observe PR #33 first-head CI to establish executable RED. Then, inside the same Issue/PR, implement the smallest client-side canonicalization + SHA-256 verification surface and rerun exact-head regression before any merge.
