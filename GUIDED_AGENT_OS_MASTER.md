# Guided Agent OS — Proof Master

> [!info] Document Role
> **Single authoritative execution contract for Guided Agent OS Proof v1.0**
>
> 이 문서만 현재 상태, 목표 범위, 검증 증거, 리스크, 다음 작업의 authoritative source로 사용한다.
> 구현 Agent/LLM의 self-check는 self-report일 뿐이며, 실제 실행/검증 증거가 확인된 경우에만 완료 처리한다.

---

## 0. Project Snapshot

| Item | Status |
|---|---|
| Project | Guided Agent OS |
| Repository | `joeylife94/guided-agent-os` |
| Baseline branch | `main` |
| Phase 0 Baseline HEAD | `fae00d67227a8bc496842ceb244845f09c0bfeae` |
| P1-A Verified App HEAD | `44d9f2965aea0836081e043a1c7e6888f389feb9` |
| P1-B Verified App HEAD | `ebbaafc89363ef31012b235e3c8822920895bbe3` |
| P2-A Verified App HEAD | `0d6ff79834cec1cfe11189dfe95b7d6dd89b4fc8` |
| P3-A Verified App HEAD | `ce85e38f8ae615dc2c61355f54da215d597acd66` |
| P3-B Verified App HEAD | `8a8d8bc3e6431639c8588bce384de7a286540640` |
| P4-A Verified App HEAD | `01122f6faf5b6e517f8bfa16f51c208c62037ec3` |
| Active Proof PR | None — PR #12 squash-merged after required checks passed |
| Current Level | **L2++ — browser Golden Path + persisted audit foundation proven; full audit UI/eval/final packaging still open** |
| Target Level | **L3 — Usable / Demonstrable Proof** |
| Target Release | **Proof v1.0** |
| Primary Purpose | Wishket AI Agent / RAG / Backend Proof |
| Final Product Goal | **Deployable Controlled AI Agent Proof** |
| Scope Status | **FROZEN** |
| Phase 0 | **CLOSED — Baseline Frozen** |
| Phase 1 | **CLOSED — Real Semantic RAG runtime + bilingual retrieval proven** |
| Phase 2 | **CLOSED — Human-approved allowlisted read-only execution proven** |
| Phase 3 | **CLOSED — Operator UI + clarification + real browser Golden Path proven** |
| Phase 4 | **IN PROGRESS — P4-A persistent event foundation CLOSED; P4-B complete timeline/UI NEXT** |
| Overall Status | **IN PROGRESS** |

---

# 1. Goal

Guided Agent OS를 기업 내부 업무를 가정한 **Controlled AI Agent Backend Proof** 수준까지 완성한다.

Final Golden Path:

```text
Structured Intake
        ↓
Validation / Clarification
        ↓
Normalization
        ↓
Semantic RAG
        ↓
Grounded LLM Answer + Citation
        ↓
Tool Planning
        ↓
Risk / Policy Check
        ↓
Human Approval
        ↓
Allowlisted Read-only Tool Execution
        ↓
Execution Result Persistence
        ↓
Persistent Audit Trail
```

Production SaaS 완성이 목표가 아니다. 위 workflow를 실제로 재현·검증·시연할 수 있으면 Proof v1.0을 닫는다.

---

# 2. Definition of Usable

Proof v1.0은 사용자가 브라우저에서 다음 과정을 끝까지 완료할 수 있을 때 usable로 본다.

1. 업무 요청 및 business context 입력
2. 필수 정보 validation
3. 누락 시 clarification
4. input normalization
5. 내부 Knowledge Base semantic retrieval
6. retrieved context 기반 grounded answer + citation
7. 필요 시 structured tool plan 생성
8. risk/policy에 따라 human approval 요청
9. 승인된 allowlisted read-only tool만 실제 실행
10. execution result 저장/표시
11. 전체 Run lifecycle audit timeline 확인

Browser Golden Path의 1~10은 Phase 3에서 실제 Chrome으로 검증되었다.
Phase 4 P4-A에서 lifecycle event persistence/reload 기반은 검증되었고, 11의 Operator UI timeline은 P4-B에서 닫는다.

---

# 3. Frozen Scope

## IN SCOPE

### P0 — Baseline / Documentation
- implementation / missing matrix freeze
- CI/deployment/current-doc drift 확인

### P1 — Real Semantic RAG
- production-grade local semantic embedding
- Korean / English retrieval
- persistent Chroma integration
- intended-source retrieval validation

### P2 — Controlled Tool Execution
- Tool Registry / allowlist
- parameter validation
- read-only tool 1개
- approve → execute
- reject / no approval / unauthorized / invalid params → blocked
- execution result persistence

### P3 — Operator UI
- request form
- run submission
- clarification display
- answer / citation
- tool plan
- approve / reject
- result
- actual browser Golden Path proof

### P4 — Audit Trail
- persistent lifecycle event records
- run-level chronological reconstruction
- UI timeline backed by persisted events

### P5 — Evaluation
- 20~30 fixed cases
- retrieval / grounding / citation / control evaluation

### P6 — Proof Packaging
- README sync
- architecture / Golden Path diagram
- screenshots
- eval evidence
- known limitations
- reproduction guide
- clean main

## NOT NOW

- Multi-Agent orchestration
- Kubernetes
- Multi-tenancy
- Authentication / OAuth / SSO
- Complex RBAC
- Billing / SaaS commercialization
- Multiple production tools
- Real Oracle/customer infrastructure integration
- Destructive/write tools
- Automatic email/Slack/external account actions
- High availability / horizontal scaling
- Enterprise observability stack
- Complex admin system
- Mobile application

---

# 4. Verified Current State

## Backend / workflow

Verified controlled backend path:

```text
intake
→ validate_required_fields
→ [clarify_missing_info OR mark_validated]
→ normalize_input
→ generate_rag_answer
→ generate_tool_plan
→ route_human_review
→ pending_approval
→ approve/reject API boundary
→ [approved allowlisted read-only execution OR blocked/rejected]
→ persisted run result
```

Implemented:
- FastAPI / Pydantic
- SQLite / SQLAlchemy run persistence
- LangGraph controlled workflow
- templates: `freelance`, `public_enterprise_ai`, `controlled_rag_agent`

## Semantic RAG — CLOSED

Verified model:
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- dimensions: `384`
- persistent Chroma collections: `domain_knowledge=4`, `agent_policy=6`, `tool_catalog=7`

Verified:
- semantic model load
- persistent semantic index rebuild
- Korean retrieval PASS
- English retrieval PASS
- intended `tools/legacy-db-access-guideline.md` in captured Top-3
- constrained Firebat runtime sample `1.167GiB / 1.5GiB`, CPU `0.30%`
- local-LLM unavailable fallback PASS
- restart persistence PASS
- no hash fallback used for semantic proof

## Controlled Tool Execution — CLOSED

Merged through PR #9 as `0d6ff79834cec1cfe11189dfe95b7d6dd89b4fc8`.

Verified boundary:
- deterministic Tool Registry
- global read-only allowlist
- one proof tool: `legacy_db_lookup`
- strict `record_id` parameter contract
- human approval gate
- per-run `allowed_tools` gate
- registry/read-only allowlist gates
- approved execution result persisted in `raw_llm_output.execution_result`
- reject/no-approval/unregistered/unauthorized/invalid-param paths blocked

Important boundary:
- LLM does **not** directly invoke tools.
- only the server-side approval boundary reaches executor code.
- no SQL, write operation, Oracle, real internal API or external action was added.

## Operator UI — PHASE 3 CLOSED

P3-A merged through PR #10 as `ce85e38f8ae615dc2c61355f54da215d597acd66`.
P3-B merged through PR #11 as `8a8d8bc3e6431639c8588bce384de7a286540640`.

Verified:
- dependency-free single-page Operator Workspace served by FastAPI `/`
- backend-driven validation/clarification
- grounded answer / citations / tool plan presentation
- approve/reject controls for `pending_approval`
- persisted execution-result presentation
- actual headless Chrome Golden Path
- clarification → pending approval → approve → execution result → persisted reload
- durable screenshot + browser evidence JSON artifact

## Persistent Audit Foundation — P4-A CLOSED

Merged through PR #12 as `01122f6faf5b6e517f8bfa16f51c208c62037ec3`.

Implemented:
- append-only `RunAuditEvent` SQLAlchemy model
- run foreign key + deterministic per-run integer `sequence`
- `(run_id, sequence)` uniqueness contract
- `event_type`, `actor`, JSON `payload`, persisted timestamp
- `AgentRun.audit_events` relationship ordered by sequence
- narrow `_append_audit_event` recording helper at the API persistence boundary
- read-only `GET /api/agents/runs/{run_id}/events`

Persisted event coverage currently wired:

```text
REQUEST_RECEIVED
VALIDATION_PASSED
CLARIFICATION_REQUIRED
NORMALIZED
ANSWER_GENERATED
TOOL_PLANNED
APPROVAL_REQUESTED
APPROVED
REJECTED
TOOL_EXECUTED
COMPLETED
FAILED
```

P4-A focused proof:
- controlled approved run persisted and reloaded as sequence `1..N`
- expected lifecycle order survived fresh API/DB-session retrieval
- human actor captured for approval
- executed tool/read-only status captured in audit payload
- clarification path persisted independently
- existing controlled execution regression remained green

Required frozen event not yet emitted explicitly:
- `RAG_RETRIEVED`

P4-A boundary:
- persistence foundation and chronological reload are proven.
- complete frozen event coverage is not yet proven.
- Operator UI audit timeline is not yet backed by `/events`.
- therefore **Phase 4 remains OPEN**.

## Deployment / CI

Repository contains:
- non-root production Docker image
- Firebat Docker Compose deployment
- persistent SQLite / Chroma volume
- startup bootstrap
- `/health` / `/version`
- PR Validation workflow
- Firebat Container workflow
- browser proof integrated into Firebat Container regression

P4-A PR #12:
- PR Validation run #30: PASS
- Firebat Container run #30: PASS
- production image build/start regression: PASS
- health/docs/version regression: PASS
- semantic RAG bilingual regression: PASS
- graceful LLM fallback regression: PASS
- existing Chrome Operator Golden Path regression: PASS
- persistence/restart regression: PASS

## Documentation drift

Still open and intentionally deferred to P6 unless blocking:
- README does not yet describe final P1/P2/P3/P4 state
- `docs/PROJECT_STATUS.md` stale
- `docs/ROADMAP.md` stale
- Issue #4 stale/open

This Master overrides those sources until P6 synchronization.

---

# 5. Implemented / Missing Matrix

| Capability | Current State | Proof v1.0 State |
|---|---|---|
| FastAPI backend | IMPLEMENTED | ACCEPTABLE |
| Structured intake | IMPLEMENTED | ACCEPTABLE |
| Validation / clarification backend | VERIFIED | ACCEPTABLE |
| Normalization | IMPLEMENTED | ACCEPTABLE |
| Run persistence | IMPLEMENTED | ACCEPTABLE |
| LangGraph controlled path | IMPLEMENTED | ACCEPTABLE |
| ChromaDB persistence | IMPLEMENTED | ACCEPTABLE |
| Real semantic model | VERIFIED | ACCEPTABLE |
| Korean / English retrieval | VERIFIED | ACCEPTABLE |
| Intended-source semantic Top-K | VERIFIED | ACCEPTABLE |
| Citation metadata | IMPLEMENTED | QUALITY EVAL IN P5 |
| Local LLM client | IMPLEMENTED | POSITIVE INFERENCE STILL NEEDS FINAL VERIFICATION |
| LLM unavailable fallback | VERIFIED | ACCEPTABLE |
| Tool planning | IMPLEMENTED | ACCEPTABLE |
| Human review routing | VERIFIED | ACCEPTABLE |
| Tool Registry / allowlist | VERIFIED | ACCEPTABLE |
| Read-only tool execution | VERIFIED | ACCEPTABLE |
| Reject/no-approval block | VERIFIED | ACCEPTABLE |
| Unauthorized/invalid-param block | VERIFIED | ACCEPTABLE |
| Execution result persistence | VERIFIED | ACCEPTABLE |
| Operator UI serving/API wiring | VERIFIED | ACCEPTABLE |
| Clarification UI | **BROWSER VERIFIED** | ACCEPTABLE |
| Browser JS Golden Path | **BROWSER VERIFIED** | ACCEPTABLE |
| Persistent audit event model | **VERIFIED — P4-A** | ACCEPTABLE FOUNDATION |
| Chronological event reload | **VERIFIED — P4-A** | ACCEPTABLE FOUNDATION |
| Frozen event coverage | PARTIAL — `RAG_RETRIEVED` GAP | REQUIRED |
| Persisted audit UI timeline | NOT IMPLEMENTED | REQUIRED |
| AI quality eval | NOT IMPLEMENTED | REQUIRED |
| Proof packaging | PARTIAL | REQUIRED |

---

# 6. Current Limitations / Risks

| ID | Risk | Severity | Status |
|---|---|---:|---|
| L-01 | BGE-M3 unstable under frozen 1536 MiB envelope | HIGH | RESOLVED FOR PROOF WITH MINILM |
| L-02 | Approval 이후 real controlled execution 없음 | HIGH | CLOSED — P2-A VERIFIED |
| L-03 | Swagger-only UX | HIGH | CLOSED — WORKSPACE + REAL BROWSER PROOF |
| L-04 | Full lifecycle persistent audit timeline 없음 | MEDIUM | **PARTIALLY RESOLVED — STORAGE/RELOAD CLOSED; UI + FULL EVENT COVERAGE OPEN** |
| L-05 | 20~30 case retrieval/grounding/control evaluation 없음 | MEDIUM | OPEN — P5 |
| L-06 | README / PROJECT_STATUS / ROADMAP / Issue drift | MEDIUM | OPEN — P6 |
| L-09 | CPU-oriented image still resolves large CUDA/NVIDIA Torch dependencies | MEDIUM | OPEN — DEFER UNLESS BLOCKING |
| L-11 | Semantic provider identifier remains legacy `bge_m3` while actual model metadata is MiniLM | LOW | OPEN — DEFER UNLESS CONFUSING PROOF |
| L-12 | Positive local-LLM inference not freshly verified with final semantic model | MEDIUM | OPEN — VERIFY BEFORE FINAL CLOSURE |
| L-13 | P2 execution uses deterministic local fixture, not customer integration | LOW | ACCEPTED BY FROZEN SCOPE |
| L-14 | Execution result shares `raw_llm_output` instead of dedicated execution table | MEDIUM | ACCEPTED FOR P2/P4; NO CHANGE REQUIRED FOR PROOF |
| L-17 | Browser CI depends on GitHub runner Chrome + test-only Selenium installation | LOW | OPEN — ACCEPTABLE FOR PROOF; WATCH CI REGRESSION |
| L-18 | Frozen audit contract includes `RAG_RETRIEVED`, but P4-A does not yet persist it explicitly | MEDIUM | **OPEN — P4-B** |
| L-19 | `_append_audit_event` is API-boundary helper rather than a standalone audit service | LOW | ACCEPTABLE FOR PROOF UNLESS P4-B CAUSES DUPLICATION |

---

# 7. Work Plan / Closure Contracts

## Phase 1 — Real Semantic RAG

**Status: CLOSED**

Closure evidence: real multilingual semantic model, persistent index, bilingual intended-source retrieval, constrained runtime fit, regression/container checks green.

## Phase 2 — Controlled Tool Execution

**Status: CLOSED**

Closure evidence: registry/allowlist/read-only tool/parameter validation, approval success, reject/no-approval/unauthorized/invalid-param blocks, persisted result, CI/container PASS.

## Phase 3 — Operator UI

**Status: CLOSED**

Closure evidence:
- request/clarification/answer/citation/tool-plan/approval/result UI
- PR #11 validation + Firebat PASS
- actual headless Chrome Golden Path
- persisted execution reload
- screenshot + JSON artifact

## Phase 4 — Audit Trail

**Status: IN PROGRESS**

Frozen minimum persistent events:

```text
REQUEST_RECEIVED
VALIDATION_PASSED
CLARIFICATION_REQUIRED
NORMALIZED
RAG_RETRIEVED
ANSWER_GENERATED
TOOL_PLANNED
APPROVAL_REQUESTED
APPROVED
REJECTED
TOOL_EXECUTED
COMPLETED
FAILED
```

Closure: 특정 run 하나로 전체 처리 과정을 chronological event records만으로 재구성 가능하고, Operator UI timeline이 persisted events를 표시해야 한다.

### P4-A — Persistent Foundation

**Status: CLOSED**

Acceptance:
- [x] SQLAlchemy persistence boundary inspected
- [x] append-only run audit model
- [x] deterministic run sequence
- [x] narrow recording helper
- [x] create/clarification/approval/execution/rejection/failure event wiring
- [x] read-only event retrieval endpoint
- [x] reload/order tests
- [x] PR Validation PASS
- [x] Firebat Container PASS
- [x] squash merge to main

Boundary: full Phase 4 does not close here.

### P4-B — Complete Persisted Timeline + Operator UI

**Status: NEXT**

Smallest next slice:
1. inspect retrieval state/output and add explicit `RAG_RETRIEVED` evidence without duplicating RAG execution.
2. verify every frozen required event has a reachable/tested persistence path.
3. wire the existing Operator Workspace audit shell to `GET /api/agents/runs/{run_id}/events`.
4. render sequence, event type, actor, timestamp and concise payload evidence chronologically.
5. extend real Chrome proof to confirm persisted timeline rendering after approve/execution.
6. verify fresh reload still reconstructs the same event order.
7. do not start Phase 5 until P4 closure is evidence-backed.

## Phase 5 — Evaluation

Target: **20~30 fixed cases** covering retrieval Top-1/Top-3, citation correctness, unsupported claims, risk routing, approval/reject and unauthorized/restricted actions.

Closure: repeatable command + durable result artifact.

## Phase 6 — Proof Packaging

Required: README sync, architecture/Golden Path diagram, screenshots, evaluation evidence, safety boundary, known limitations, reproduction guide, stale docs/issues synchronization/deprecation.

---

# 8. Evidence Registry

| ID | Phase | Evidence | Status |
|---|---|---|---|
| E-001 | Baseline | Phase 0 baseline inspection at `fae00d67227a8bc496842ceb244845f09c0bfeae` | PRESENT |
| E-002 | Baseline | Active LangGraph controlled-RAG path inspected | PRESENT |
| E-006 | Baseline | README / PROJECT_STATUS / ROADMAP / Issue #4 drift identified | PRESENT |
| E-101 | RAG | P1-A provider boundary merged via PR #7 | PRESENT |
| E-102 | RAG | PR #7 PR Validation | PASS |
| E-103 | RAG | PR #7 Firebat regression using explicit test provider | PASS |
| E-107 | RAG | Final PR #8 PR Validation | PASS |
| E-108 | RAG | MiniLM semantic metadata `4 / 6 / 7`, dimensions `384` | PASS |
| E-109 | RAG | Korean intended-source semantic Top-3 | PASS |
| E-110 | RAG | English intended-source semantic Top-3 | PASS |
| E-111 | RAG | Stable semantic runtime sample `1.167GiB / 1.5GiB`, CPU `0.30%` | PRESENT |
| E-112 | RAG | PR #8 Firebat semantic/fallback/persistence/restart workflow | PASS |
| E-113 | RAG | PR #8 merge `ebbaafc89363ef31012b235e3c8822920895bbe3` | PRESENT |
| E-201 | Execution | Approved `legacy_db_lookup` execution + persisted result retrieval | PASS |
| E-202 | Execution | Reject/unregistered/per-run unauthorized block tests | PASS |
| E-203 | Execution | No-approval and invalid-parameter block tests | PASS |
| E-204 | Execution | PR #9 PR Validation | PASS |
| E-205 | Execution | PR #9 Firebat Container regression | PASS |
| E-206 | Execution | PR #9 squash merge `0d6ff79834cec1cfe11189dfe95b7d6dd89b4fc8` | PRESENT |
| E-301 | UI | FastAPI Operator Workspace root contract tests | PASS |
| E-302 | UI | Controlled run/approve/reject API wiring asserted in UI tests | PASS |
| E-303 | UI | PR #10 PR Validation | PASS |
| E-304 | UI | PR #10 Firebat Container regression | PASS |
| E-305 | UI | PR #10 squash merge `ce85e38f8ae615dc2c61355f54da215d597acd66` | PRESENT |
| E-306 | UI | Real Chrome Golden Path | PASS |
| E-307 | UI | Fresh persisted run reload after browser approval | PASS |
| E-308 | UI | PR #11 PR Validation run #27 | PASS |
| E-309 | UI | PR #11 Firebat Container run #27 including Chrome | PASS |
| E-310 | UI | `operator-browser-evidence.json` artifact | PRESENT |
| E-311 | UI | `operator-golden-path.png` artifact | PRESENT |
| E-312 | UI | PR #11 squash merge `8a8d8bc3e6431639c8588bce384de7a286540640` | PRESENT |
| E-401 | Audit | `RunAuditEvent` append-only model + deterministic per-run sequence | **PASS** |
| E-402 | Audit | Controlled approved lifecycle persisted/reloaded chronologically | **PASS** |
| E-403 | Audit | Clarification lifecycle persisted/reloaded | **PASS** |
| E-404 | Audit | PR #12 PR Validation run #30 | **PASS** |
| E-405 | Audit | PR #12 Firebat Container run #30 | **PASS** |
| E-406 | Audit | PR #12 squash merge `01122f6faf5b6e517f8bfa16f51c208c62037ec3` | PRESENT |
| E-407 | Audit | Complete frozen event coverage including `RAG_RETRIEVED` | TODO |
| E-408 | Audit | Persisted Operator UI timeline + browser proof | TODO |
| E-501 | Eval | Evaluation result | TODO |
| E-601 | Deploy | Fresh final deployment verification | TODO |

---

# 9. Validation Rule

각 iteration 종료 시 반드시 기록:

## Changed
실제로 변경된 코드 / 문서 / 설정.

## Executed
실제로 실행한 test/build/API/UI/deployment 또는 repository inspection.

## Not Verified
이번 iteration에서 검증하지 않은 항목.

## Remaining Risks
현재 알려진 위험 / 불확실성.

완료 표시는 self-report가 아니라 Evidence Registry와 위 네 항목을 근거로 한다.

---

# 10. Current Work Status

## Done Enough to Show
- Backend architecture
- Structured intake / validation / clarification backend
- LangGraph controlled RAG workflow
- persistent semantic retrieval + bilingual intended-source proof
- Local LLM integration boundary and fallback
- one human-approved controlled read-only execution boundary
- registry / allowlists / parameter validation
- approve → execute → persisted result backend evidence
- reject/no-approval/unauthorized/invalid-param safety evidence
- dependency-free Operator Workspace served from FastAPI
- browser-proven clarification / approval / execution-result UX
- durable Chrome evidence JSON + screenshot
- append-only persistent run audit foundation
- deterministic chronological audit reload through `/events`
- Docker/Firebat deployment and CI regression

## Done Enough to Use
**Backend/API level: YES. Browser Golden Path: YES for the frozen single-tool Proof path. Audit storage/reload: YES.**

Proof v1.0 is still not closure-complete because:
- explicit `RAG_RETRIEVED` audit event is not yet persisted.
- Operator UI audit timeline is not yet backed by persisted events.
- positive local-LLM inference with the final semantic stack remains open.
- fixed AI quality evaluation remains open.
- final proof packaging/doc synchronization remains open.

## Not Yet Done
- Complete frozen audit-event coverage
- Persisted audit UI timeline + browser proof
- Positive local-LLM final-stack verification
- AI quality evaluation
- Final proof packaging

---

# 11. Current Priority

## NOW

**Phase 4 / P4-B — Complete persisted timeline + Operator UI**

Smallest next action:
1. inspect the actual RAG workflow state to find the narrowest source for `RAG_RETRIEVED` evidence.
2. persist that missing frozen event without re-running retrieval.
3. prove all frozen required event points are reachable in tests.
4. wire the existing audit shell to persisted `/events` data.
5. extend browser proof only enough to verify chronological persisted timeline rendering after execution.

Do not start Phase 5 until Phase 4 closure is proven.

---

# 12. Work Log

## 2026-08-18 — Phase 0 Baseline Freeze

**Status:** CLOSED

**Changed:** authoritative baseline/matrix/scope/evidence/risk contract frozen.

**Executed:** repository/workflow/RAG/tool/CI/docs/Issue inspection.

**Not Verified:** fresh runtime tests at baseline stage.

**Remaining Risks:** carried into phase contracts.

---

## 2026-08-18 — Phase 1 Real Semantic RAG

**Status:** CLOSED

**Changed:** semantic provider boundary + multilingual MiniLM path + persistent semantic index proof gates.

**Executed:** PR #7/#8 validation, Firebat regression, Korean/English intended-source retrieval, restart/persistence.

**Not Verified:** broad quality eval; positive final local-LLM inference.

**Remaining Risks:** CPU dependency footprint, legacy provider label, no production-capacity claim.

---

## 2026-08-18 — Phase 2 P2-A Controlled Read-only Execution

**Status:** CLOSED

**Changed:** registry/allowlist, `legacy_db_lookup`, parameter validation, approval executor, persisted execution result and block-path tests.

**Executed:** PR #9 PR Validation PASS; Firebat Container PASS; squash merge `0d6ff79834cec1cfe11189dfe95b7d6dd89b4fc8`.

**Not Verified:** real customer systems; dedicated audit event model; positive local-LLM inference.

**Remaining Risks:** fixture proves control architecture rather than customer integration performance; execution result shares `raw_llm_output`.

---

## 2026-08-18 — Phase 3 P3-A Minimal Operator Workspace

**Status:** CLOSED AS FIRST UI SLICE

**Changed:** FastAPI-served dependency-free workspace with request form, answer/citation/tool-plan rendering, approval controls, result presentation and audit shell.

**Executed:** PR #10 PR Validation PASS; Firebat Container PASS; squash merge `ce85e38f8ae615dc2c61355f54da215d597acd66`.

**Not Verified:** actual browser JavaScript behavior; clarification rendering; persistent audit events.

**Remaining Risks:** UI contract tests alone could not prove browser runtime behavior.

---

## 2026-08-18 — Phase 3 P3-B Browser Golden Path

**Status:** CLOSED — PHASE 3 CLOSED

**Changed:** clarification rendering + real Chrome proof harness + Firebat browser regression artifact capture.

**Executed:** PR #11 PR Validation PASS; Firebat Container PASS; Chrome Golden Path PASS; persisted execution reload PASS; squash merge `8a8d8bc3e6431639c8588bce384de7a286540640`.

**Not Verified:** persistent audit event storage; positive local-LLM final-stack inference; separate reject screenshot path.

**Remaining Risks:** Chrome test dependency; proof remains frozen deterministic read-only tool scenario.

---

## 2026-08-19 — Phase 4 P4-A Persistent Audit Foundation

### Status
**CLOSED AS PERSISTENCE FOUNDATION — PHASE 4 REMAINS OPEN**

### Changed
Merged through PR #12:
- `app/models/models.py`
  - `RunAuditEvent` append-only persistence model
  - run relationship
  - deterministic per-run integer sequence
  - `(run_id, sequence)` uniqueness
  - actor/payload/timestamp evidence
- `app/api/routes.py`
  - narrow `_append_audit_event` helper
  - persisted lifecycle events at create/clarification/validation/normalization/answer/tool-plan/approval/rejection/execution/completion/failure boundaries
  - read-only `GET /api/agents/runs/{run_id}/events`
- `tests/test_run_audit_events.py`
  - controlled approved lifecycle ordering/reload proof
  - clarification lifecycle persistence proof

No UI timeline, auth, extra tool, new frontend framework, external integration or Not Now item was added.

### Executed
Actual GitHub evidence on PR #12 head `1324f098d11634588af7bac0c2e400eea7a1bd7e`:

**PR Validation — PASS**
- run #30
- dependency installation PASS
- full pytest PASS
- unittest discovery PASS
- compileall PASS
- whitespace/diff check PASS

**Firebat Container — PASS**
- run #30
- production image build/start PASS
- health/docs/version PASS
- semantic RAG bilingual regression PASS
- graceful local-model fallback PASS
- existing headless Chrome workspace regression PASS
- persistent run/restart regression PASS

PR #12 squash-merged to `main` as `01122f6faf5b6e517f8bfa16f51c208c62037ec3`.

### Not Verified
- explicit `RAG_RETRIEVED` event is not yet persisted.
- every frozen event point has not yet been separately exercised in one complete test matrix.
- Operator UI does not yet request/render `/events`.
- browser proof does not yet show a persisted audit timeline.
- positive local-LLM inference with final semantic model remains open.

### Remaining Risks
- Phase 4 cannot close until missing `RAG_RETRIEVED` evidence and persisted UI timeline are proven.
- helper is currently located at the API persistence boundary; extraction to a service is unnecessary unless P4-B creates duplication.
- event timestamps may share wall-clock resolution; ordering authority is the persisted integer `sequence`, not timestamp alone.

### Decision
P4-A closes. Persistent chronological lifecycle evidence now exists and survives retrieval. Full Phase 4 remains open.

### Next Action
**P4-B — close the missing `RAG_RETRIEVED` event coverage, then render persisted `/events` as the Operator UI audit timeline and prove it in Chrome.**

---

# 13. Final Closure Definition

다음 질문에 모두 **YES**일 때만 `GUIDED AGENT OS PROOF v1.0 CLOSED`를 선언한다.

- 실제 사용자가 browser에서 Agent에게 업무를 요청할 수 있는가? **YES — P3-B**
- 실제 내부 문서를 semantic search할 수 있는가? **YES — P1**
- LLM 답변에 검증 가능한 근거/citation이 있는가? **IMPLEMENTED; quality eval remains P5**
- Tool이 필요할 때 AI가 직접 실행하지 않고 controlled plan을 만드는가? **YES — P2**
- 민감 작업은 human approval을 요구하는가? **YES — P2/P3**
- 승인된 제한 read-only tool 하나가 실제 실행되는가? **YES — P2/P3 browser proof**
- reject/unauthorized tool은 실행되지 않는가? **YES — P2 backend safety proof**
- 모든 과정이 저장되고 추적 가능한가? **PARTIAL — P4-A STORAGE/RELOAD YES; FULL EVENT COVERAGE + UI TIMELINE OPEN**
- 이 동작이 automated tests + evaluation으로 검증되는가? **PARTIAL — tests PASS, P5 eval OPEN**
- 외부 사람이 README/Demo/Evidence만 보고 이를 확인할 수 있는가? **PARTIAL — P6 OPEN**

그 이후 기능은 Proof v1.1 또는 실제 고객 요구사항으로 분리한다.
