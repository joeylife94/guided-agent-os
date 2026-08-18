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
| Active Proof PR | None — PR #9 merged after required checks passed |
| Current Level | **L2+ — backend Golden Path now reaches verified controlled read-only execution** |
| Target Level | **L3 — Usable / Demonstrable Proof** |
| Target Release | **Proof v1.0** |
| Primary Purpose | Wishket AI Agent / RAG / Backend Proof |
| Final Product Goal | **Deployable Controlled AI Agent Proof** |
| Scope Status | **FROZEN** |
| Phase 0 | **CLOSED — Baseline Frozen** |
| Phase 1 | **CLOSED — Real Semantic RAG runtime + bilingual retrieval proven** |
| Phase 2 | **CLOSED — Human-approved allowlisted read-only execution proven** |
| Phase 3 | **NEXT — Minimal Operator UI** |
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

Verified current controlled path:

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
- FastAPI
- Pydantic
- SQLite / SQLAlchemy run persistence
- LangGraph controlled workflow
- templates: `freelance`, `public_enterprise_ai`, `controlled_rag_agent`

## Semantic RAG — CLOSED

Verified model:
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- dimensions: `384`
- persistent Chroma collections:
  - `domain_knowledge=4`
  - `agent_policy=6`
  - `tool_catalog=7`

Verified P1-B evidence:
- semantic model loaded
- semantic index rebuilt
- Korean query retrieval PASS
- English query retrieval PASS
- intended `tools/legacy-db-access-guideline.md` ranked #1/#2 in captured Top-3 for both languages
- runtime sample after bilingual retrieval: `1.167GiB / 1.5GiB`, CPU `0.30%`
- local-LLM unavailable fallback PASS
- restart persistence PASS
- no hash fallback used for semantic proof

## Controlled Tool Execution — CLOSED

Merged through PR #9 as `0d6ff79834cec1cfe11189dfe95b7d6dd89b4fc8`.

Implemented boundary:
- minimal deterministic Tool Registry
- global read-only allowlist
- one real proof tool: `legacy_db_lookup`
- deterministic local fixture lookup only; no customer/external system
- strict required parameter contract: `record_id`
- explicit human approval gate
- explicit per-run `allowed_tools` gate
- registry membership gate
- read-only allowlist gate
- invalid/unexpected parameters rejected
- approved execution result persisted in existing `raw_llm_output.execution_result`
- approve/reject review state persisted consistently

Approved execution path:

```text
Persisted Tool Plan
→ /approve
→ Human Approval Boundary
→ Registry Check
→ Global Read-only Allowlist Check
→ Per-run allowed_tools Check
→ Parameter Validation
→ legacy_db_lookup
→ Execution Result
→ AgentRun persistence
```

Blocked paths verified:
- no human approval → execution blocked
- reject → no execution result
- unregistered planned tool → blocked
- registered tool not explicitly allowed for run → blocked
- invalid parameters → blocked

Important boundary:
- LLM still does **not** directly invoke tools.
- only the existing server-side approval boundary can reach executor code.
- no SQL, write operation, Oracle, real internal API or external action was added.

## Deployment / CI

Current repository contains:
- non-root production Docker image
- Firebat Docker Compose deployment
- persistent SQLite / Chroma volume
- startup bootstrap
- `/health` / `/version`
- PR Validation workflow
- Firebat Container workflow

Fresh PR #9 validation at head `95e80317c560cc4c4f6e5612434d9b290b8e910e`:

**PR Validation — PASS**
- dependency installation
- full pytest suite, including P2-A controlled execution tests
- unittest discovery
- compileall
- whitespace/diff check

**Firebat Container — PASS**
- production container regression remained green after executor changes
- existing health/docs/version, RAG/runtime and persistence gates remained green

PR #9 squash-merged to `main` as `0d6ff79834cec1cfe11189dfe95b7d6dd89b4fc8`.

## Documentation drift

Still open and intentionally deferred to P6 unless blocking:
- README does not yet describe final P1/P2 proof state
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
| Validation / clarification | IMPLEMENTED | ACCEPTABLE |
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
| Operator UI | NOT IMPLEMENTED | REQUIRED |
| Persistent audit timeline | NOT IMPLEMENTED | REQUIRED |
| AI quality eval | NOT IMPLEMENTED | REQUIRED |
| Proof packaging | PARTIAL | REQUIRED |

---

# 6. Current Limitations / Risks

| ID | Risk | Severity | Status |
|---|---|---:|---|
| L-01 | BGE-M3 unstable under frozen 1536 MiB envelope | HIGH | RESOLVED FOR PROOF WITH MINILM |
| L-02 | Approval 이후 real controlled execution 없음 | HIGH | **CLOSED — P2-A VERIFIED** |
| L-03 | Swagger 중심 UX; operator UI 없음 | HIGH | OPEN |
| L-04 | Full lifecycle persistent audit timeline 없음 | MEDIUM | OPEN |
| L-05 | 20~30 case retrieval/grounding/control evaluation 없음 | MEDIUM | OPEN |
| L-06 | README / PROJECT_STATUS / ROADMAP / Issue drift | MEDIUM | OPEN — P6 |
| L-09 | CPU-oriented image still resolves large CUDA/NVIDIA Torch dependencies | MEDIUM | OPEN — DEFER UNLESS BLOCKING |
| L-11 | Semantic provider identifier remains legacy `bge_m3` while actual model metadata is MiniLM | LOW | OPEN — DEFER UNLESS CONFUSING PROOF |
| L-12 | Positive local-LLM inference not freshly verified with final semantic model | MEDIUM | OPEN — VERIFY BEFORE FINAL CLOSURE |
| L-13 | P2-A execution is deterministic local fixture proof, not a real customer system integration | LOW | ACCEPTED BY FROZEN SCOPE |
| L-14 | Execution result lives in existing `raw_llm_output` JSON rather than a dedicated execution table | MEDIUM | ACCEPTED FOR P2; REVISIT ONLY IF P4 AUDIT REQUIRES |

---

# 7. Work Plan / Closure Contracts

## Phase 1 — Real Semantic RAG

**Status: CLOSED**

Closure evidence:
- explicit semantic provider boundary
- real multilingual model loaded
- persistent semantic index
- Korean/English retrieval
- intended source Top-K
- constrained Firebat runtime fit
- regression/container checks green

---

## Phase 2 — Controlled Tool Execution

**Status: CLOSED**

Acceptance Criteria:
- [x] Tool Registry
- [x] Tool Allowlist
- [x] Read-only Tool 1개
- [x] Parameters validation
- [x] No approval → no execution
- [x] Reject → no execution
- [x] Unauthorized tool → blocked
- [x] Approved allowlisted tool → execute
- [x] Result persisted
- [x] Tests PASS

### P2-A Closure

**CLOSED.**

Reason:
- smallest controlled execution boundary exists and is actually exercised by tests.
- approval, allowlist, read-only and parameter gates are explicit.
- safe success and required failure paths are verified.
- adding more tools/external systems would expand beyond Proof v1.0 need.

---

## Phase 3 — Operator UI

### Goal
Swagger 없이 비개발자가 Golden Path를 수행할 수 있는 최소 UI를 제공한다.

### Acceptance Criteria
- [ ] Request form
- [ ] Run submission
- [ ] Clarification display
- [ ] Grounded Answer
- [ ] Citations
- [ ] Tool Plan
- [ ] Approve / Reject
- [ ] Execution Result
- [ ] Audit Timeline presentation shell

### P3-A — Smallest Next Slice

Do **not** start with a large frontend framework migration or admin system.

Next iteration must first inspect the current static/template/frontend surface and choose the smallest existing-stack-compatible UI path.

Minimum first target:
1. determine whether an existing server-rendered/static surface can host the proof UI without introducing unnecessary infrastructure.
2. render one controlled-agent request form.
3. submit to existing `controlled_rag_agent` API.
4. display returned status, grounded answer/citations and tool plan.
5. expose approve/reject controls only for `pending_approval`.
6. after approval, display persisted `execution_result`.
7. preserve backend API as the source of truth; do not duplicate workflow logic in frontend.

P3 does not close until the Golden Path is browser-usable without Swagger.

---

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

---

## Phase 5 — Evaluation

Target: **20~30 fixed cases**.

Required dimensions:
- retrieval Top-1 / Top-3
- citation presence / correctness
- unsupported claim check
- high-risk routing
- reject blocks execution
- approved allowlisted execution
- unauthorized/restricted action block

Closure: repeatable command + durable result artifact.

---

## Phase 6 — Proof Packaging

Required:
- README sync
- architecture diagram
- Golden Path diagram
- screenshots
- evaluation evidence
- safety boundary
- known limitations
- setup/reproduction guide
- stale docs/issues synchronized or explicitly deprecated

Closure: 외부 검토자가 5~10분 안에 무엇을 만들었고 무엇을 실제 검증했는지 이해 가능.

---

# 8. Evidence Registry

| ID | Phase | Evidence | Status |
|---|---|---|---|
| E-001 | Baseline | Phase 0 baseline inspection at `fae00d67227a8bc496842ceb244845f09c0bfeae` | PRESENT |
| E-002 | Baseline | Active LangGraph controlled-RAG path inspected | PRESENT |
| E-005 | Baseline | PR #6 historical CI/container validation | PRESENT — HISTORICAL |
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
| E-201 | Execution | Approved `legacy_db_lookup` execution test + persisted result retrieval | **PASS** |
| E-202 | Execution | Reject, unregistered tool and per-run unauthorized tool block tests | **PASS** |
| E-203 | Execution | No-approval and invalid-parameter block tests | **PASS** |
| E-204 | Execution | PR #9 PR Validation at `95e80317c560cc4c4f6e5612434d9b290b8e910e` | **PASS** |
| E-205 | Execution | PR #9 Firebat Container regression | **PASS** |
| E-206 | Execution | PR #9 squash merge at `0d6ff79834cec1cfe11189dfe95b7d6dd89b4fc8` | PRESENT |
| E-301 | UI | Browser Golden Path | TODO |
| E-401 | Audit | Complete persistent Run Timeline | TODO |
| E-501 | Eval | Evaluation result | TODO |
| E-601 | Deploy | Fresh final deployment verification | TODO |

---

# 9. Validation Rule

각 iteration 종료 시 아래 네 항목을 반드시 기록한다.

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
- Structured intake / validation / clarification
- LangGraph controlled RAG workflow
- persistent ChromaDB semantic retrieval
- Korean + English intended-source retrieval proof
- Local LLM integration boundary and fallback
- Tool planning / human review routing
- one controlled read-only execution boundary
- explicit registry / allowlists / parameter validation
- approve → execute → persisted result
- reject/no-approval/unauthorized/invalid-param safety evidence
- Docker/Firebat deployment structure and CI regression

## Done Enough to Use
**Backend/API level only.**

The controlled backend workflow can now reach a persisted read-only execution result, but the project is not yet Proof-v1.0 usable because:
- operator UI does not exist.
- persistent lifecycle audit timeline does not exist.
- positive local-LLM Golden Path and final eval remain open.

## Not Yet Done
- Operator UI
- Persistent audit trail
- Positive local-LLM Golden Path verification
- AI quality evaluation
- Final proof packaging

---

# 11. Current Priority

## NOW

**Phase 3 / P3-A — Minimal Operator UI path selection + first browser workflow slice**

Smallest next action:
1. inspect current `app/main.py`, routes, static/template dependencies and Docker serving path.
2. choose the smallest UI implementation compatible with the existing FastAPI deployment.
3. implement a single controlled-agent workspace, not an admin system.
4. connect it to existing run creation and approval APIs.
5. prove at least request → result rendering in browser-oriented integration tests before expanding UI states.

Do not add React/Next.js or a separate frontend service unless repository inspection proves the existing FastAPI/static approach cannot satisfy Proof v1.0.

---

# 12. Work Log

## 2026-08-18 — Proof v1.0 Scope Definition

**Decision:** Production SaaS가 아닌 **Deployable Controlled AI Agent Proof**로 목표 고정.

---

## 2026-08-18 — Phase 0 Baseline Freeze

### Status
**CLOSED**

### Changed
- Master baseline, implemented/missing matrix, drift, evidence, risks, next slice frozen.

### Executed
- repository/main/workflow/RAG/tool/CI/docs/Issue inspection.

### Not Verified
- fresh runtime tests at baseline stage.

### Remaining Risks
- recorded into subsequent phase contracts.

---

## 2026-08-18 — Phase 1 P1-A Embedding Provider Boundary

### Status
**CLOSED**

### Changed
- explicit semantic provider boundary
- test-only hash path
- metadata compatibility checks
- runtime configuration

### Executed
- PR #7 PR Validation PASS
- PR #7 Firebat Container PASS

### Not Verified
- real semantic model runtime at P1-A.

### Remaining Risks
- semantic fit deferred to P1-B and later closed.

---

## 2026-08-18 — Phase 1 P1-B Semantic Runtime

### Status
**CLOSED**

### Changed
- selected multilingual MiniLM model under frozen Firebat envelope
- bilingual retrieval/metadata/runtime proof gates

### Executed
- PR #8 PR Validation PASS
- PR #8 Firebat Container PASS
- Korean/English retrieval PASS
- intended-source Top-K PASS
- restart/persistence PASS

### Not Verified
- broad 20~30 case quality evaluation
- positive local-LLM inference with final semantic model

### Remaining Risks
- CPU image dependency footprint
- legacy provider label
- production capacity not claimed

---

## 2026-08-18 — Phase 2 P2-A Controlled Read-only Execution

### Status
**CLOSED**

### Changed
Application changes merged through PR #9:
- `app/services/tool_executor.py`
  - minimal deterministic Tool Registry
  - one read-only `legacy_db_lookup` tool
  - global read-only allowlist
  - explicit human approval requirement
  - per-run `allowed_tools` requirement
  - strict `record_id` parameter validation
- `app/api/routes.py`
  - existing `/approve` boundary resolves persisted planned tool
  - executes only through controlled executor
  - persists `execution_result` in existing run output
  - approve/reject review status kept consistent
- `app/templates/controlled_rag_agent.py`
  - `tool_parameters` added as optional intake metadata
- `tests/test_controlled_tool_execution.py`
  - approved success + persisted retrieval
  - reject block
  - no-approval block
  - unregistered tool block
  - per-run unauthorized tool block
  - invalid parameter block

No external tool, write operation, auth system or separate frontend was added.

### Executed
Actual GitHub Actions on PR #9 head `95e80317c560cc4c4f6e5612434d9b290b8e910e`:

**PR Validation — PASS**
- full pytest suite, including new P2-A tests
- unittest discovery
- compileall
- whitespace/diff check

**Firebat Container — PASS**
- existing production-style container/RAG/persistence regression remained green after P2-A code changes

PR #9 squash-merged to `main` as `0d6ff79834cec1cfe11189dfe95b7d6dd89b4fc8`.

### Not Verified
- no real customer/Oracle/API integration; intentionally out of scope.
- browser UI has not exercised the approval/execution path.
- dedicated execution-event table does not exist.
- positive local-LLM inference remains unverified.

### Remaining Risks
- execution result currently shares `raw_llm_output`; Phase 4 may require a dedicated event model for durable audit semantics.
- deterministic fixture tool proves control architecture, not customer-system integration performance.

### Decision
P2-A and Phase 2 closure criteria are met. More tools or external integration would be overbuilding.

### Next Action
**Phase 3 / P3-A — inspect the current FastAPI serving surface and implement the smallest single-page operator workflow without introducing a separate frontend stack unless necessary.**

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
