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
| Latest accepted milestone | **P-008 / Issue #32 Operator evidence digest local verification — CLOSED** |
| Active milestone | **NONE — progression review required** |
| Active branch | none |
| Active PR | none |
| Latest accepted progression merge | `a238a9a89e3edb7afa5a00d0290c53483726625e` |

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
| L-24 | Operator could not independently check displayed bundle/digest consistency | CLOSED by P-008 local verification |

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
**CLOSED — ACCEPTED**
- Issue #32; PR #33.
- first contract head `a5ba9cd763c1eeff5ff75462aa9fc1279949e6f7` established executable RED.
- accepted exact head `90652198add41eaaf6f95c182898d3ef530057d6`; merge `a238a9a89e3edb7afa5a00d0290c53483726625e`.
- exact-head checks: PR Validation run `33481981742`, Firebat Container run `33481981750`, Proof Evaluation run `33481981737` — all SUCCESS.
- Operator browser recomputes SHA-256 from canonical evidence content excluding `evidence_digest` and renders MATCH / MISMATCH / UNAVAILABLE.
- verification is client-side/read-only; no approve/reject/recover/tool execution or server mutation added.
- limitation: local consistency only; no signature, notarization, timestamp authority, external chain of trust, hostile-client security, or non-repudiation claim.

### Changed
- implemented local digest verification in P-008 and accepted exact-head regression evidence.
- merged PR #33 with expected-head protection and closed Issue #32 completed.
- reconciled MASTER to accepted repository state.

### Actually Executed
- root MASTER read first.
- exact head `90652198add41eaaf6f95c182898d3ef530057d6` check-runs inspected directly.
- validate, proof-eval, and firebat-container all completed SUCCESS.

### Verified
- P-008 executable acceptance and frozen baseline compatibility.

### Not Verified
- no external trust/authenticity or hostile-client guarantee.

### Limitations
P-008 proves only browser-side consistency between the rendered deterministic evidence content and the server-provided checksum.

### Exact Next Action
Perform one bounded Progression Review. If a milestone passes the gate, create exactly one Issue/branch/PR; otherwise remain ENABLED in HOLD/no-mutation mode.
