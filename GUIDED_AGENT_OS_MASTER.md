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
| Baseline HEAD | `fae00d67227a8bc496842ceb244845f09c0bfeae` |
| Current Level | **L2 — Integrated Backend Demo** |
| Target Level | **L3 — Usable / Demonstrable Proof** |
| Target Release | **Proof v1.0** |
| Primary Purpose | Wishket AI Agent / RAG / Backend Proof |
| Final Product Goal | **Deployable Controlled AI Agent Proof** |
| Scope Status | **FROZEN** |
| Phase 0 | **CLOSED — Baseline Frozen** |
| Current Phase | **Phase 1 — Real Semantic RAG** |
| Overall Status | **IN PROGRESS** |

---

# 1. Goal

Guided Agent OS를 기업 내부 업무를 가정한 **Controlled AI Agent Backend Proof** 수준까지 완성한다.

최종 Golden Path:

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
- current implementation 확인
- active workflow 확인
- RAG 구현 확인
- tool control 구현 확인
- CI / deployment 구조 확인
- README / PROJECT_STATUS / ROADMAP drift 확인
- open issue 상태 확인
- implemented / missing matrix freeze

### P1 — Real Semantic RAG
- production-grade local semantic embedding
- Korean / English retrieval
- persistent Chroma integration 유지
- retrieval validation

### P2 — Controlled Tool Execution
- Tool Registry / allowlist
- parameter validation
- read-only tool 1개
- approve → execute
- reject → no execute
- unauthorized → blocked
- execution result persistence

### P3 — Operator UI
- request form
- answer / citation
- tool plan
- approve / reject
- result
- audit timeline

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

# 4. Phase 0 Baseline Freeze — CLOSED

## Baseline Date

**2026-08-18**

## Verified Repository State

### Active backend / workflow

- FastAPI API server exists.
- Registered templates include `freelance`, `public_enterprise_ai`, `controlled_rag_agent`.
- Agent runs are persisted through SQLite/SQLAlchemy.
- Active `controlled_rag_agent` LangGraph path is:

```text
intake
→ validate_required_fields
→ [clarify_missing_info OR mark_validated]
→ normalize_input
→ generate_rag_answer
→ generate_tool_plan
→ route_human_review
→ END
```

- Non-controlled templates stop after validation/normalization.
- Controlled RAG outputs are persisted in `raw_llm_output` and exposed in the run response.

### RAG

Implemented:
- local Markdown knowledge base
- ChromaDB persistent index
- multi-collection retrieval
- `domain_knowledge`
- `agent_policy`
- `tool_catalog`
- source metadata / citation output
- optional local OpenAI-compatible LLM path
- model-unavailable retrieval fallback

Known boundary:
- current embedding is a **64-dimensional deterministic hashed bag-of-words test embedding**.
- it is adequate for deterministic integration tests, but does **not** satisfy Proof v1.0 semantic RAG acceptance.

### Tool / control

Implemented:
- deterministic system-access/risk detection
- tool recommendation planning
- `planned_only` execution mode
- `allowed_to_execute = false`
- approval routing
- approve/reject status endpoints
- explicit blocked-action list

Known boundary:
- no actual Tool Registry / Executor exists.
- approve currently updates status only; it does not execute an allowlisted tool.

### Deployment / CI

Repository contains:
- non-root production Docker image path
- Docker Compose Firebat deployment
- persistent SQLite/Chroma volume
- startup bootstrap
- `/health` / `/version`
- PR validation workflow
- Firebat container workflow

Historical PR #6 records successful validation of:
- dependency install
- pytest
- unittest discovery
- compileall
- whitespace check
- production image build
- non-root startup
- DB/RAG bootstrap
- health/docs/version
- non-empty retrieval
- graceful no-model fallback
- run creation
- restart persistence

Important boundary:
- current `main` HEAD contains only Master-document commits after the last implementation commit.
- no fresh test/build/container run was executed during this baseline inspection.

### Documentation drift

`README.md` broadly reflects the controlled RAG Phase 1–3 implementation.

`docs/PROJECT_STATUS.md` is stale (last updated 2026-06-14) and incorrectly says RAG, additional templates, and active approval flow are not implemented.

`docs/ROADMAP.md` is also stale and still describes later workflow capabilities as planned even though parts are active in code.

GitHub Issue #4 remains open and contains unchecked tasks, while major portions such as `controlled_rag_agent`, RAG services, tool planning, workflow extension, persistence, tests, and README updates are already present.

**Decision:** `GUIDED_AGENT_OS_MASTER.md` overrides these stale documents. External documentation synchronization is deferred to Proof Packaging unless it blocks an earlier acceptance check.

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
| Multi-collection RAG | IMPLEMENTED | NEEDS SEMANTIC EMBEDDING |
| Citation metadata | IMPLEMENTED | NEEDS QUALITY VALIDATION |
| Local LLM client | IMPLEMENTED | NEEDS GOLDEN-PATH VERIFICATION |
| LLM unavailable fallback | IMPLEMENTED | ACCEPTABLE, RE-VERIFY LATER |
| Tool planning | IMPLEMENTED | ACCEPTABLE FOUNDATION |
| Human review routing | IMPLEMENTED | ACCEPTABLE FOUNDATION |
| Approve / reject status | IMPLEMENTED | NEEDS REAL EXECUTION PATH |
| Real read-only tool execution | NOT IMPLEMENTED | REQUIRED |
| Tool allowlist / executor | NOT IMPLEMENTED | REQUIRED |
| Operator UI | NOT IMPLEMENTED | REQUIRED |
| Persistent audit timeline | NOT IMPLEMENTED | REQUIRED |
| AI quality eval | NOT IMPLEMENTED | REQUIRED |
| Proof packaging | PARTIAL | REQUIRED |

---

# 6. Current Limitations / Risks

| ID | Risk | Severity | Status |
|---|---|---:|---|
| L-01 | Test-grade hash embedding; semantic retrieval proof 부족 | HIGH | OPEN |
| L-02 | Approval 이후 real controlled execution 없음 | HIGH | OPEN |
| L-03 | Swagger 중심 UX; operator UI 없음 | HIGH | OPEN |
| L-04 | Full lifecycle audit timeline 없음 | MEDIUM | OPEN |
| L-05 | Retrieval/grounding/control evaluation 없음 | MEDIUM | OPEN |
| L-06 | README 외 PROJECT_STATUS/ROADMAP/Issue 상태 drift | MEDIUM | OPEN |
| L-07 | Current main에서 fresh full-suite/container validation 미실행 | MEDIUM | OPEN |

---

# 7. Work Plan / Closure Contracts

## Phase 1 — Real Semantic RAG

### Goal
테스트용 retrieval을 실제 multilingual semantic retrieval로 교체한다.

### Smallest Safe Implementation Slice

**P1-A — Embedding Provider Boundary**

1. 기존 `rag_embeddings.py` 호출 지점을 확인한다.
2. semantic embedding provider를 명시적 interface/config boundary 뒤에 둔다.
3. 기본 Proof provider는 local multilingual model로 고정한다.
4. index/query가 같은 provider와 embedding dimension을 사용하도록 보장한다.
5. model unavailable/configuration error를 명확하게 실패 처리한다. hash fallback으로 조용히 회귀하지 않는다.

Candidate default: **BGE-M3 또는 동급 multilingual embedding model**.

### Phase 1 Acceptance Criteria

- [ ] Real semantic embedding integrated
- [ ] Index rebuild 성공
- [ ] Existing three collections 정상 동작
- [ ] Korean query retrieval verified
- [ ] English query retrieval verified
- [ ] Relevant document Top-K verified
- [ ] Container execution verified
- [ ] Regression tests PASS

### Closure
Golden evaluation set에서 semantic retrieval 결과를 Proof evidence로 제시할 수 있어야 한다.

---

## Phase 2 — Controlled Tool Execution

### Goal
Human Approval 이후 제한된 업무 하나를 실제 수행한다.

### Minimum Deliverable

`legacy_record_lookup` 또는 동등한 local read-only lookup tool 1개.

### Acceptance Criteria

- [ ] Tool Registry
- [ ] Tool Allowlist
- [ ] Read-only Tool 1개
- [ ] Parameters validation
- [ ] No approval → no execution
- [ ] Reject → no execution
- [ ] Unauthorized tool → blocked
- [ ] Approved allowlisted tool → execute
- [ ] Result persisted
- [ ] Tests PASS

---

## Phase 3 — Operator UI

### Acceptance Criteria

- [ ] Request form
- [ ] Run submission
- [ ] Clarification display
- [ ] Grounded Answer
- [ ] Citations
- [ ] Tool Plan
- [ ] Approve / Reject
- [ ] Result
- [ ] Audit Timeline

Closure: Swagger 없이 browser UI만으로 Golden Path 완료.

---

## Phase 4 — Audit Trail

Minimum events:

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
| E-001 | Baseline | `main` baseline inspection at `fae00d67227a8bc496842ceb244845f09c0bfeae` | PRESENT |
| E-002 | Baseline | Active LangGraph controlled-RAG path inspected | PRESENT |
| E-003 | Baseline | Hash embedding implementation inspected | PRESENT |
| E-004 | Baseline | Planned-only tool generator / approval endpoints inspected | PRESENT |
| E-005 | Baseline | PR #6 historical CI/container validation record inspected | PRESENT — HISTORICAL |
| E-006 | Baseline | README / PROJECT_STATUS / ROADMAP / Issue #4 drift identified | PRESENT |
| E-101 | RAG | Real semantic embedding integration | TODO |
| E-102 | RAG | Korean + English retrieval results | TODO |
| E-103 | RAG | Fresh regression/container validation | TODO |
| E-201 | Execution | Approved tool execution | TODO |
| E-202 | Execution | Reject/unauthorized execution blocked | TODO |
| E-301 | UI | Golden Path screenshot/E2E | TODO |
| E-401 | Audit | Complete Run Timeline | TODO |
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
- ChromaDB integration
- Local LLM integration boundary
- Tool planning / human review routing
- Docker deployment structure
- Historical CI / persistence evidence

## Done Enough to Use

**아직 없음.**

## Not Yet Done

- Real semantic RAG
- Real controlled execution
- Operator UI
- Complete audit trail
- AI evaluation
- Final proof packaging

---

# 11. Current Priority

## NOW

**Phase 1 — Real Semantic RAG**

### Next smallest task

**P1-A — inspect embedding call graph and implement a semantic embedding provider boundary without changing unrelated workflow behavior.**

Required before closing P1-A:
- exact changed files recorded
- narrow embedding/index/retrieval tests actually executed
- full regression status recorded if executed
- model/download/runtime requirement recorded
- no silent fallback to hash embeddings

---

# 12. Work Log

## 2026-08-18 — Proof v1.0 Scope Definition

### Decision
Production SaaS가 아닌 **Deployable Controlled AI Agent Proof**로 목표 고정.

### Scope
Real semantic RAG, human-approved read-only execution, minimal UI, audit trail, evaluation, proof packaging.

### Next
Phase 0 baseline freeze.

---

## 2026-08-18 — Phase 0 Baseline Freeze

### Status
**CLOSED**

### Changed
- `GUIDED_AGENT_OS_MASTER.md`만 갱신.
- baseline HEAD, implemented/missing matrix, documentation drift, evidence, risks, Phase 1 next slice를 authoritative하게 기록.
- application code, README, PROJECT_STATUS, ROADMAP, GitHub Issue는 변경하지 않음.

### Executed
실제 repository inspection 수행:
- `main` HEAD 확인
- `README.md` 확인
- `app/agents/workflow.py` active path 확인
- `app/services/rag_embeddings.py` 확인
- `app/services/tool_plan_generator.py` 확인
- `app/api/routes.py` approve/reject/persistence 확인
- `.github/workflows/pr-validation.yml` 확인
- `.github/workflows/firebat-container.yml` 확인
- `docs/PROJECT_STATUS.md` 확인
- `docs/ROADMAP.md` 확인
- GitHub Issue #4 확인
- PR #6 validation record 확인

### Not Verified
- 이번 iteration에서 pytest/unittest를 실제 재실행하지 않음.
- Docker image/build/container를 실제 재실행하지 않음.
- Firebat 실제 host deployment 상태를 확인하지 않음.
- 실제 local LLM inference를 실행하지 않음.
- semantic embedding model은 아직 도입/실행하지 않음.

### Remaining Risks
- hash embedding이 semantic Proof 요건을 충족하지 않음.
- approval 이후 실제 tool execution 없음.
- operator UI/audit/evaluation 없음.
- stale project docs/issues가 남아 있음.
- CI/container evidence는 historical이며 fresh final evidence가 아님.

### Decision
Phase 0 목적은 현재 상태를 정확히 freeze하는 것이므로, 코드 변경/재검증 없이 baseline을 닫는다. Fresh executable verification은 각 구현 Phase와 final proof closure에서 다시 요구한다.

### Next Action
**Phase 1 / P1-A — semantic embedding provider boundary 구현 및 narrow validation.**

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
