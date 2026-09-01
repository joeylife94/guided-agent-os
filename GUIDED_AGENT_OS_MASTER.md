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
| Latest accepted milestone | **P-005 / Issue #26 Operator interrupted-decision quarantine UX — CLOSED** |
| Active milestone | **P-006 / Issue #28 read-only interrupted-decision recovery queue — OPEN** |
| Active branch | `proof-v1.1/28-recovery-queue` |
| Active PR | **#29 — OPEN / first head RED expected** |
| Latest accepted progression merge | `8cf4a2847b527ae3f322dd744f0abec8b30844c8` |
| P-006 first contract head | `2cef6b981a3af7c2fc3a786185a3e8137891a970` |

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
| L-22 | interrupted/recovery-required run discovery requires a known run id | **ACTIVE — P-006 addresses only discovery/read UX** |

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
- limitation: operator still needs the run id; no recovery queue exists.

## P-006 — Read-only interrupted-decision recovery queue
**OPEN — CONTRACT HEAD / RED EXPECTED**

### Gate / Value
P-004/P-005 made interrupted-decision quarantine safe and usable, but after restart an operator must already know the affected run id. A deterministic read-only recovery queue lets the operator discover affected runs without increasing execution authority.

### Lifecycle
- Issue #28 — OPEN.
- Branch `proof-v1.1/28-recovery-queue` from reconciled main `c8ee49d6af740117984531e886062caf80620da4`.
- PR #29 — OPEN.
- first exact head `2cef6b981a3af7c2fc3a786185a3e8137891a970`.

### Acceptance Contract
1. `GET /api/agents/runs/recovery-queue` returns only `approval_executing`, `rejection_processing`, `decision_recovery_required` runs.
2. empty queue is 200/`[]` and read-only.
3. deterministic ordering: created time ascending, then run id.
4. unchanged repeated reads are identical, append no audit events, execute no tools.
5. pending/archived/rejected runs never appear.
6. Operator UI renders/refreshes queue and selecting an item uses the existing persisted-run loader only.
7. existing replay/concurrency/quarantine/evidence/Golden Path plus applicable PR Validation, Firebat Container, Proof Evaluation remain green.

### Changed This Run
- reconciled stale Master through P-005.
- created Issue #28 and branch.
- added `tests/test_recovery_queue.py` as executable backend contract.
- opened PR #29 on exact test-only head `2cef6b981a3af7c2fc3a786185a3e8137891a970`.

### Actually Executed
- re-read root Master first.
- confirmed no pre-existing open PR/Issue before selecting P-006.
- re-read Issues #22/#24/#26, PRs #23/#25/#27, and exact-head workflow evidence.
- inspected current quarantine route/UI/test implementation.

### Verified
- P-003/P-004/P-005 repository/executable evidence is reconciled.
- P-006 passes the bounded milestone gate: direct operator failure-handling value; read-only scope; concrete executable acceptance; no unresolved security/product decision.

### Not Verified
- recovery-queue endpoint is **not implemented** on the first PR head.
- Operator queue UI is not implemented.
- no PASS/merge claim exists for P-006 yet.

### Limitations
P-006 is discovery/read UX only: no notification/SLA worker, automatic quarantine, retry, resume, execution, or distributed recovery semantics.

### Exact Next Action
Observe PR #29 first-head CI to establish executable RED. Then, inside the same Issue/PR, add the smallest read-only endpoint before wiring the queue to the existing persisted-run loader. Re-run exact-head regression before any merge.
