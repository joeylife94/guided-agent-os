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
| Active Proof PR | None — PR #10 merged after required checks passed |
| Current Level | **L2+ — browser workspace exists; full browser Golden Path not yet proven** |
| Target Level | **L3 — Usable / Demonstrable Proof** |
| Target Release | **Proof v1.0** |
| Primary Purpose | Wishket AI Agent / RAG / Backend Proof |
| Final Product Goal | **Deployable Controlled AI Agent Proof** |
| Scope Status | **FROZEN** |
| Phase 0 | **CLOSED — Baseline Frozen** |
| Phase 1 | **CLOSED — Real Semantic RAG runtime + bilingual retrieval proven** |
| Phase 2 | **CLOSED — Human-approved allowlisted read-only execution proven** |
| Phase 3 | **IN PROGRESS — P3-A workspace slice merged; browser E2E still open** |
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
Audit Trail
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
- audit timeline presentation shell

### P4 — Audit Trail
- persistent lifecycle event records

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
- intended `tools/legacy-db-access-guideline.md` #1/#2 in captured Top-3
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

## Operator UI — P3-A MERGED, PHASE STILL OPEN

Merged through PR #10 as `ce85e38f8ae615dc2c61355f54da215d597acd66`.

Implemented:
- dependency-free single-page Operator Workspace served by FastAPI `/`
- no React/Next.js or separate frontend service
- `/docs` remains available
- controlled-agent request form
- request submission through existing `POST /api/agents/controlled_rag_agent/runs`
- grounded answer presentation
- citation presentation
- tool-plan presentation
- approve/reject controls visible only for `pending_approval`
- approve/reject calls use existing server-side API boundaries
- persisted `raw_output.execution_result` presentation after approval
- audit presentation shell explicitly labels persistent event history as Phase 4 work
- backend API remains the source of truth; workflow logic is not duplicated in the UI

Fresh PR #10 validation at head `26c440c67128c6bcfd7b7006493a98a276b7d9d3`:

**PR Validation — PASS**
- dependency installation
- full pytest suite including `tests/test_operator_ui.py`
- unittest discovery
- compileall
- whitespace/diff check

**Firebat Container — PASS**
- production image build/start
- health/docs/version regression
- semantic RAG bilingual retrieval regression
- local-LLM fallback regression
- persistence/restart regression

Verification boundary:
- FastAPI root HTML serving and existing API wiring are verified.
- actual browser JavaScript execution of request → approval → execution-result Golden Path was **not** executed in this iteration.
- clarification questions are not yet explicitly rendered by the workspace.
- persistent lifecycle audit events do not exist yet; the current UI only provides the Phase 4 presentation shell.

## Deployment / CI

Repository contains:
- non-root production Docker image
- Firebat Docker Compose deployment
- persistent SQLite / Chroma volume
- startup bootstrap
- `/health` / `/version`
- PR Validation workflow
- Firebat Container workflow

## Documentation drift

Still open and intentionally deferred to P6 unless blocking:
- README does not yet describe final P1/P2/P3 state
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
| Validation / clarification backend | IMPLEMENTED | ACCEPTABLE |
| Normalization | IMPLEMENTED | ACCEPTABLE |
| Run persistence | IMPLEMENTED | ACCEPTABLE |
| LangGraph controlled path | IMPLEMENTED | ACCEPTABLE |
| ChromaDB persistence | IMPLEMENTED | ACCEPTABLE |
| Real semantic model | VERIFIED | ACCEPTABLE |
| Korean / English retrieval | VERIFIED | ACCEPTABLE |
| Intended-source semantic Top-K | VERIFIED | ACCEPTABLE |
| Citation metadata | IMPLEMENTED | QUALITY EVAL IN P5 |
| Local LLM client | IMPLEMENTED | POSITIVE INFERENCE STILL NEEDS GOLDEN-PATH VERIFICATION |
| LLM unavailable fallback | VERIFIED | ACCEPTABLE |
| Tool planning | IMPLEMENTED | ACCEPTABLE |
| Human review routing | IMPLEMENTED | ACCEPTABLE |
| Tool Registry / allowlist | VERIFIED | ACCEPTABLE |
| Read-only tool execution | VERIFIED | ACCEPTABLE |
| Reject/no-approval block | VERIFIED | ACCEPTABLE |
| Unauthorized/invalid-param block | VERIFIED | ACCEPTABLE |
| Execution result persistence | VERIFIED | ACCEPTABLE |
| Operator UI serving/API wiring | VERIFIED | ACCEPTABLE SLICE |
| Clarification UI | NOT IMPLEMENTED | REQUIRED |
| Browser JS Golden Path | NOT VERIFIED | REQUIRED |
| Persistent audit timeline | NOT IMPLEMENTED | REQUIRED |
| AI quality eval | NOT IMPLEMENTED | REQUIRED |
| Proof packaging | PARTIAL | REQUIRED |

---

# 6. Current Limitations / Risks

| ID | Risk | Severity | Status |
|---|---|---:|---|
| L-01 | BGE-M3 unstable under frozen 1536 MiB envelope | HIGH | RESOLVED FOR PROOF WITH MINILM |
| L-02 | Approval 이후 real controlled execution 없음 | HIGH | CLOSED — P2-A VERIFIED |
| L-03 | Swagger-only UX | HIGH | **REDUCED — WORKSPACE EXISTS; BROWSER E2E OPEN** |
| L-04 | Full lifecycle persistent audit timeline 없음 | MEDIUM | OPEN |
| L-05 | 20~30 case retrieval/grounding/control evaluation 없음 | MEDIUM | OPEN |
| L-06 | README / PROJECT_STATUS / ROADMAP / Issue drift | MEDIUM | OPEN — P6 |
| L-09 | CPU-oriented image still resolves large CUDA/NVIDIA Torch dependencies | MEDIUM | OPEN — DEFER UNLESS BLOCKING |
| L-11 | Semantic provider identifier remains legacy `bge_m3` while actual model metadata is MiniLM | LOW | OPEN — DEFER UNLESS CONFUSING PROOF |
| L-12 | Positive local-LLM inference not freshly verified with final semantic model | MEDIUM | OPEN — VERIFY BEFORE FINAL CLOSURE |
| L-13 | P2 execution uses deterministic local fixture, not customer integration | LOW | ACCEPTED BY FROZEN SCOPE |
| L-14 | Execution result shares `raw_llm_output` instead of dedicated execution table | MEDIUM | ACCEPTED FOR P2; REVISIT ONLY IF P4 REQUIRES |
| L-15 | Operator UI JavaScript Golden Path not browser-executed yet | HIGH | OPEN — P3-B |
| L-16 | Clarification questions are not rendered in Operator UI | MEDIUM | OPEN — P3-B |

---

# 7. Work Plan / Closure Contracts

## Phase 1 — Real Semantic RAG

**Status: CLOSED**

Closure evidence: real multilingual semantic model, persistent index, bilingual intended-source retrieval, constrained runtime fit, regression/container checks green.

## Phase 2 — Controlled Tool Execution

**Status: CLOSED**

Closure evidence: registry/allowlist/read-only tool/parameter validation, approval success, reject/no-approval/unauthorized/invalid-param blocks, persisted result, CI/container PASS.

## Phase 3 — Operator UI

**Status: IN PROGRESS**

Acceptance Criteria:
- [x] Request form
- [x] Run submission wiring
- [ ] Clarification display
- [x] Grounded Answer presentation
- [x] Citations presentation
- [x] Tool Plan presentation
- [x] Approve / Reject controls
- [x] Execution Result presentation
- [x] Audit Timeline presentation shell
- [ ] Actual browser Golden Path execution evidence

### P3-A — Existing-stack Operator Workspace

**Status: CLOSED AS A SLICE, NOT PHASE CLOSURE**

Decision:
- FastAPI single-service HTML/JS is sufficient for Proof v1.0.
- separate frontend infrastructure would be overbuilding.
- UI consumes existing APIs only.

### P3-B — Smallest Next Slice

1. render `clarification_questions` when a run returns `needs_clarification`.
2. execute the workspace in an actual browser-capable verification path.
3. prove request → pending approval → approve → persisted execution result rendering.
4. capture reject rendering if the same browser harness makes it cheap; do not expand scope solely for visual polish.
5. do not begin persistent audit implementation until the browser Golden Path is actually proven.

P3 closes only when browser usage no longer depends on Swagger and the Golden Path has execution evidence.

## Phase 4 — Audit Trail

Minimum persistent events:

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

Closure: 특정 run 하나로 전체 처리 과정을 재구성 가능.

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
| E-113 | RAG | PR #8 merge at `ebbaafc89363ef31012b235e3c8822920895bbe3` | PRESENT |
| E-201 | Execution | Approved `legacy_db_lookup` execution test + persisted result retrieval | PASS |
| E-202 | Execution | Reject/unregistered/per-run unauthorized block tests | PASS |
| E-203 | Execution | No-approval and invalid-parameter block tests | PASS |
| E-204 | Execution | PR #9 PR Validation | PASS |
| E-205 | Execution | PR #9 Firebat Container regression | PASS |
| E-206 | Execution | PR #9 squash merge `0d6ff79834cec1cfe11189dfe95b7d6dd89b4fc8` | PRESENT |
| E-301 | UI | FastAPI Operator Workspace root HTML contract tests | **PASS** |
| E-302 | UI | Existing controlled run/approve/reject API wiring asserted in UI contract tests | **PASS** |
| E-303 | UI | PR #10 PR Validation at `26c440c67128c6bcfd7b7006493a98a276b7d9d3` | **PASS** |
| E-304 | UI | PR #10 Firebat Container regression | **PASS** |
| E-305 | UI | PR #10 squash merge `ce85e38f8ae615dc2c61355f54da215d597acd66` | PRESENT |
| E-306 | UI | Actual browser request → approval → execution-result rendering | TODO |
| E-401 | Audit | Complete persistent Run Timeline | TODO |
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
- UI wiring for grounded answer/citations/tool plan/approval/result
- Docker/Firebat deployment and CI regression

## Done Enough to Use
**Backend/API level: YES. Browser level: NOT YET VERIFIED.**

Proof v1.0 is not usable-closed because:
- actual browser Golden Path execution has not been captured.
- clarification UI is incomplete.
- persistent lifecycle audit timeline does not exist.
- positive local-LLM Golden Path and final eval remain open.

## Not Yet Done
- Browser-executed Operator Golden Path
- Clarification display in Operator UI
- Persistent audit trail
- Positive local-LLM Golden Path verification
- AI quality evaluation
- Final proof packaging

---

# 11. Current Priority

## NOW

**Phase 3 / P3-B — Clarification rendering + actual browser Golden Path verification**

Smallest next action:
1. add explicit clarification-question rendering without changing backend schemas.
2. choose the lightest browser-capable verification available for the current FastAPI/container path.
3. run the operator workspace through request → pending approval → approve → persisted execution result.
4. record exact browser evidence and any unverified behavior.

Do not begin Phase 4 until P3 browser usability is proven.

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

**Not Verified:** real customer systems; browser execution; dedicated audit event model; positive local-LLM inference.

**Remaining Risks:** fixture proves control architecture rather than customer integration performance; execution result shares `raw_llm_output`.

---

## 2026-08-18 — Phase 3 P3-A Minimal Operator Workspace

### Status
**CLOSED AS FIRST UI SLICE — PHASE 3 REMAINS OPEN**

### Changed
Application changes merged through PR #10:
- `app/operator_ui.py`
  - dependency-free single-page workspace
  - controlled request form
  - grounded answer/citation/tool-plan presentation
  - pending-approval-only approve/reject controls
  - existing approve/reject API calls
  - persisted execution-result presentation
  - explicit Phase 4 audit shell
- `app/main.py`
  - `/` now serves Operator Workspace instead of redirecting to Swagger
  - `/docs` retained
  - API description aligned with the existing controlled read-only execution boundary
- `tests/test_operator_ui.py`
  - root HTML serving contract
  - required workspace elements
  - existing controlled-agent/run decision API wiring contract
  - `/docs` availability

No frontend framework, auth, admin system, additional tool or workflow duplication was added.

### Executed
Actual GitHub Actions on PR #10 head `26c440c67128c6bcfd7b7006493a98a276b7d9d3`:

**PR Validation — PASS**
- dependency installation
- full pytest suite including new UI contract tests
- unittest discovery
- compileall
- whitespace/diff check

**Firebat Container — PASS**
- production image build/start
- existing health/docs/version checks
- semantic RAG bilingual retrieval regression
- local-model fallback regression
- persistent-run/restart regression

PR #10 squash-merged to `main` as `ce85e38f8ae615dc2c61355f54da215d597acd66`.

### Not Verified
- no actual browser JavaScript Golden Path execution was run.
- clarification question rendering is absent.
- approve/reject visual behavior was not browser-executed.
- persistent audit lifecycle events are not implemented.
- positive local-LLM inference remains open.

### Remaining Risks
- UI contract tests can prove serving/wiring but not browser runtime behavior.
- a browser-only defect could still block the Golden Path despite green backend/container CI.
- current audit section is intentionally a presentation shell, not audit evidence.

### Decision
FastAPI single-service UI path is accepted. Phase 3 stays open until P3-B produces actual browser Golden Path evidence and closes clarification display.

### Next Action
**Phase 3 / P3-B — add clarification rendering and execute the Golden Path in a real browser-capable verification path.**

---

# 13. Final Closure Definition

다음 질문에 모두 **YES**일 때만 `GUIDED AGENT OS PROOF v1.0 CLOSED`를 선언한다.

- 실제 사용자가 browser에서 Agent에게 업무를 요청할 수 있는가?
- 실제 내부 문서를 semantic search할 수 있는가?
- LLM 답변에 검증 가능한 근거/citation이 있는가?
- Tool이 필요할 때 AI가 직접 실행하지 않고 controlled plan을 만드는가?
- 민감 작업은 human approval을 요구하는가?
- 승인된 제한 read-only tool 하나가 실제 실행되는가?
- reject/unauthorized tool은 실행되지 않는가?
- 모든 과정이 저장되고 추적 가능한가?
- 이 동작이 automated tests + evaluation으로 검증되는가?
- 외부 사람이 README/Demo/Evidence만 보고 이를 확인할 수 있는가?

그 이후 기능은 Proof v1.1 또는 실제 고객 요구사항으로 분리한다.
