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
| Latest accepted milestone | **P-018 / Issue #52 capture explicit operator rejection rationale — CLOSED** |
| Active milestone | **P-019 — bind rejection rationale to the currently reviewed run — PLANNED** |
| Active branch | not created yet |
| Active PR | none yet |
| Latest accepted progression merge | `c5e2e705c3a9f313c3e7371b4d7499c2bf742883` |

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
| L-34 | Operator rejection used a fixed generic rationale instead of a human-entered audit rationale | CLOSED by P-018 |
| L-35 | typed rejection rationale is not explicitly cleared/bound when the Operator switches to another run, risking cross-run audit misattribution | OPEN — P-019 |

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
- **P-018 CLOSED — ACCEPTED** — capture explicit operator rejection rationale; Issue #52 / PR #53; accepted head `8e189460eb14a707124b95ca7e4de59f99faf03b`; merge `c5e2e705c3a9f313c3e7371b4d7499c2bf742883`. Exact-head PR Validation / Proof Evaluation / Firebat Container / P-018 Browser Rejection Rationale all SUCCESS. Browser proof verifies blank rationale is blocked, trimmed human rationale reaches persisted `REJECTED.payload.reason`, run is rejected, and no `TOOL_EXECUTED` event is emitted.

## P-019 — Bind rejection rationale to the currently reviewed run
**PLANNED — bounded next milestone**

### Gap
P-018 clears the rationale only after a successful reject. The textarea is not explicitly reset when `currentRunId` changes, so an operator can type a reason for run A, load run B, and accidentally reject run B with run A's rationale. That would preserve a technically valid rejection event but weaken audit truthfulness by misattributing the human rationale across runs.

### Bounded acceptance
1. Rejection rationale is cleared whenever the Operator changes from one run ID to another or resets the workspace to no run.
2. Reload/refresh of the same run does not invent or transfer rationale to another run; approval behavior remains unchanged.
3. Browser proof creates two pending-approval runs, types a distinctive rationale on run A, switches to run B, and verifies the rationale field is empty before any reject request can be issued.
4. Browser proof rejects run B only after entering a new B-specific rationale, then verifies `REJECTED.payload.reason` contains only the B rationale and no `TOOL_EXECUTED` event exists.
5. Exact-head PR Validation, Proof Evaluation, Firebat Container, and the dedicated P-019 browser gate are SUCCESS before acceptance.

### Boundaries / non-claims
- no new tool, endpoint, execution authority, write permission, autonomous behavior, authentication/RBAC, signing, or external trust claim.
- this binds ephemeral browser input to the visible run context; it does not create authenticated reviewer identity or tamper-proof/non-repudiable evidence.

---

# 5. Current Run Record

### Changed
- P-018 accepted on exact head `8e189460eb14a707124b95ca7e4de59f99faf03b` after all four required exact-head gates completed SUCCESS.
- PR #53 squash merged with expected-head protection to `c5e2e705c3a9f313c3e7371b4d7499c2bf742883`; Issue #52 closed completed.
- MASTER reconciled through P-018.
- one next bounded milestone selected: P-019 cross-run rejection-rationale binding/reset.

### Actually Executed
- current root MASTER read first.
- PR #53 exact head and mergeability inspected.
- exact-head workflow runs inspected directly: PR Validation, Proof Evaluation, Firebat Container, and P-018 Browser Rejection Rationale all completed SUCCESS.
- PR #53 review threads inspected; none were unresolved.
- PR #53 merged with expected-head protection and Issue #52 closed completed.
- merged P-018 Operator wrapper inspected on `main`; `rejectionReason.value = ''` occurs after successful reject, but no run-change binding/reset is installed by the wrapper.

### Verified
- P-018 executable evidence is green on the accepted exact head and remains inside the frozen human-approval/read-only boundary.
- P-019 satisfies the milestone gate: direct audit-correctness value, one-Issue/one-PR scope, deterministic two-run browser acceptance, and no unresolved product/security direction decision.

### Not Verified
- P-019 has not yet been implemented or executed.
- no authenticated reviewer identity, tamper-proof logging, RBAC, non-repudiation, production authorization, or unrestricted tool-safety claim is established.

### Limitations
P-018/P-019 evidence remains bounded to this repository, its existing Firebat/headless-Chrome proof environment, and its existing controlled read-only tool path.

### Exact Next Action
Create one P-019 Issue and linked branch/PR. Establish executable RED for cross-run rationale carryover, then minimally clear/bind the rationale on run-context change and require exact-head PR Validation / Proof Evaluation / Firebat Container / dedicated P-019 browser SUCCESS before merge.