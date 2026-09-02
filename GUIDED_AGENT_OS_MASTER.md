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
| Latest accepted milestone | **P-017 / Issue #50 browser-verify missing reviewed digest rejection notice — CLOSED** |
| Active milestone | **P-018 — capture explicit operator rejection rationale — PLANNED** |
| Active branch | not created yet |
| Active PR | none yet |
| Latest accepted progression merge | `6afa4d909703497309cc6396d8548545a4b421e1` |

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
| L-28 | browser approval action was not explicitly bound to the exact execution-input digest reviewed by the operator | CLOSED by P-012 |
| L-29 | rejected missing/mismatched approval-digest attempts were not explicit persisted audit evidence | CLOSED by P-013 |
| L-30 | mismatch rejection did not preserve submitted stale digest | CLOSED by P-014 |
| L-31 | Operator did not directly surface stale reviewed digest vs current digest | CLOSED by P-015 |
| L-32 | Firebat browser proof did not verify stale-digest rejection notice | CLOSED by P-016 |
| L-33 | Firebat browser proof did not verify missing-digest rejection notice | CLOSED by P-017 |
| L-34 | Operator rejection uses a fixed generic rationale instead of a human-entered audit rationale | OPEN — P-018 |

---

# 4. Progression Registry

- **P-001 CLOSED — ACCEPTED** — replay-safe human approval finalization; Issue #17 / PR #18; merge `fc5f237f78a41ae4c099599445df99ea6d56f1b3`.
- **P-002 CLOSED — ACCEPTED** — concurrent approval finalization guard; Issue #19 / PR #20 + #21; merge `ad5f9b1a865d1be97ce427cc18760d7de5ca5a2e`.
- **P-003 CLOSED — ACCEPTED** — deterministic run evidence bundle; Issue #22 / PR #23; merge `ff70352ba87017654ca5d180d141dc1c8eb1fe75`.
- **P-004 CLOSED — ACCEPTED** — quarantine interrupted decisions without replay; Issue #24 / PR #25; merge `b43da1762ed04cee9fa87e295511e3eb5b5d8a03`.
- **P-005 CLOSED — ACCEPTED** — Operator quarantine UX; Issue #26 / PR #27; merge `8cf4a2847b527ae3f322dd744f0abec8b30844c8`.
- **P-006 CLOSED — ACCEPTED** — read-only interrupted-decision recovery queue; Issue #28 / PR #29; merge `c405b66d0a91f2924660d049f05390daab20ddaa`.
- **P-007 CLOSED — ACCEPTED** — Operator deterministic evidence artifact; Issue #30 / PR #31; merge `9d5a89b982eef8b3e492aa52a380e7806cd207d5`.
- **P-008 CLOSED — ACCEPTED** — Operator evidence digest local verification; Issue #32 / PR #33; merge `a238a9a89e3edb7afa5a00d0290c53483726625e`.
- **P-009 CLOSED — ACCEPTED** — portable deterministic evidence download; Issue #34 / PR #35; merge `019f93ebffc9f9b0089e5f16378df8f160f6bcdc`.
- **P-010 CLOSED — ACCEPTED** — Operator approval execution-input review; Issue #36 / PR #37; merge `3e8a653820f48c30bb60743184d2c90416523b26`.
- **P-011 CLOSED — ACCEPTED** — auditable approval execution-input snapshot; Issue #38 / PR #39; merge `3c2a5c58d7735064e9f4132751e003dee8a58da6`.
- **P-012 CLOSED — ACCEPTED** — bind human approval to reviewed execution-input digest; Issue #40 / PR #41; merge `48137e552784af2f18c9220a846a57efad9012b7`.
- **P-013 CLOSED — ACCEPTED** — audit rejected approval digest preconditions; Issue #42 / PR #43; merge `1b36d26f68da46e86915991e31fa73d67af1566a`.
- **P-014 CLOSED — ACCEPTED** — correlate rejected approval attempt digest; Issue #44 / PR #45; merge `422352d9292584e5a238b1f37acadcc11e462124`.
- **P-015 CLOSED — ACCEPTED** — surface rejected approval digest mismatch in Operator; Issue #46 / PR #47; accepted head `24de68835b4fa0cbd296f6d10e32b539a7238881`; merge `edd8564ec2eff9fa3971ede0192417b7dd5f8551`.
- **P-016 CLOSED — ACCEPTED** — browser-verify rejected approval digest mismatch notice; Issue #48 / PR #49; accepted head `b7cf9312cd342dab5e5b3a617169854dece9b506`; merge `4a1ae3167d082fb8bc3b7356119550fa8098a39e`. Exact-head validate / proof-eval / firebat-container SUCCESS.
- **P-017 CLOSED — ACCEPTED** — browser-verify missing reviewed digest rejection notice; Issue #50 / PR #51; accepted head `96f393c4c4f3b267b16443215959daebfc6b3952`; merge `6afa4d909703497309cc6396d8548545a4b421e1`. Exact-head validate / proof-eval / firebat-container SUCCESS. Browser proof verifies actual omitted-digest 409, persisted `pending_approval`, `missing_expected_digest`, hidden/empty submitted digest, current server digest, no false `APPROVED`/`TOOL_EXECUTED`, then successful fresh-digest human-approved read-only execution.

## P-018 — Capture explicit operator rejection rationale
**PLANNED — bounded next milestone**

### Gap
The rejection endpoint already persists `REJECTED` with `payload.reason`, but the browser Operator sends the fixed string `Rejected from operator workspace.` rather than a human-entered rationale. This weakens audit usefulness at the explicit human-denial boundary.

### Bounded acceptance
1. Operator provides a small rejection-rationale input associated only with the Reject action.
2. Reject is blocked client-side when the rationale is blank after trimming; approval behavior is unchanged.
3. Existing reject endpoint receives the entered rationale and persists it unchanged in the `REJECTED` audit event.
4. Firebat/browser proof performs one actual human rejection and verifies the persisted rationale plus no `TOOL_EXECUTED` event.
5. Exact-head PR Validation, Proof Evaluation, and Firebat Container are all SUCCESS before acceptance.

### Boundaries / non-claims
- no new tool, endpoint, write authority, autonomous execution, replay, authentication/RBAC, signing, or external trust claim.
- rationale is audit metadata entered by the operator; it is not authenticated identity, non-repudiation, or tamper-proof evidence.

---

# 5. Current Run Record

### Changed
- P-017 accepted on exact head `96f393c4c4f3b267b16443215959daebfc6b3952` after validate / proof-eval / firebat-container all completed SUCCESS.
- PR #51 squash merged with expected-head protection to `6afa4d909703497309cc6396d8548545a4b421e1`; Issue #50 closed completed.
- MASTER reconciled through P-017.
- one next bounded milestone selected: P-018 explicit operator rejection rationale.

### Actually Executed
- current root MASTER read first.
- PR #51 metadata and exact head inspected.
- exact-head check runs inspected directly; all three acceptance gates completed SUCCESS.
- PR #51 discussion inspected; no unresolved comments were present.
- PR #51 merged with expected-head protection and Issue #50 closed.
- Operator rejection implementation inspected: current browser body uses a fixed generic reason while server-side rejection already persists `payload.reason`.

### Verified
- P-017 is reproducible on the accepted exact head and does not broaden approval/execution authority.
- P-018 satisfies the milestone gate: direct audit/use value, one-Issue/one-PR scope, executable browser acceptance, and no unresolved product-direction/security decision.

### Not Verified
- P-018 has not yet been implemented or executed.
- no authenticated reviewer identity, tamper-proof logging, RBAC, non-repudiation, production authorization, or unrestricted tool-safety claim is established.

### Limitations
P-017/P-018 evidence remains bounded to this repository, its existing Firebat/headless-Chrome proof environment, and its existing read-only controlled tool path.

### Exact Next Action
Create one P-018 Issue and linked branch/PR. Establish test-first executable RED for human-entered rejection rationale, then implement minimally inside that same milestone and require exact-head validate / proof-eval / firebat-container SUCCESS before merge.