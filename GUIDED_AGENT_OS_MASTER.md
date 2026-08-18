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
| Current Verified HEAD | `44d9f2965aea0836081e043a1c7e6888f389feb9` |
| Current Level | **L2 — Integrated Backend Demo** |
| Target Level | **L3 — Usable / Demonstrable Proof** |
| Target Release | **Proof v1.0** |
| Primary Purpose | Wishket AI Agent / RAG / Backend Proof |
| Final Product Goal | **Deployable Controlled AI Agent Proof** |
| Scope Status | **FROZEN** |
| Phase 0 | **CLOSED — Baseline Frozen** |
| Phase 1 | **IN PROGRESS — P1-A CLOSED** |
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

# 4. Verified Current State

## Backend / workflow

Implemented and previously inspected:
- FastAPI API server
- templates: `freelance`, `public_enterprise_ai`, `controlled_rag_agent`
- SQLite/SQLAlchemy Agent Run persistence
- active `controlled_rag_agent` path:

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

- controlled RAG outputs persisted/exposed through the current run response path

## RAG foundation

Implemented:
- local Markdown knowledge base
- persistent ChromaDB
- `domain_knowledge`
- `agent_policy`
- `tool_catalog`
- source metadata / citation output
- optional local OpenAI-compatible LLM answer path
- retrieval-only fallback when the LLM is unavailable

### P1-A embedding boundary — IMPLEMENTED

Merged through PR #7 at `44d9f2965aea0836081e043a1c7e6888f389feb9`.

Implemented behavior:
- explicit `EmbeddingProvider` boundary
- default runtime semantic provider: SentenceTransformers + `BAAI/bge-m3`
- explicit `RAG_EMBEDDING_PROVIDER` / `RAG_EMBEDDING_MODEL` configuration
- deterministic hash embedding retained only as explicit `hash_test`
- no silent semantic → hash fallback
- index metadata records provider, model, dimensions
- index rebuild uses one provider instance for all document embeddings
- retrieval uses the same configured provider and validates collection provider/model/dimension metadata
- incompatible/stale embedding index produces an explicit rebuild error instead of silent empty retrieval
- Firebat runtime receives embedding provider/model configuration
- CI explicitly selects `hash_test` to keep CI deterministic and avoid claiming semantic model runtime verification

Important boundary:
- **real BGE-M3 model load/inference has not yet been executed as evidence.**
- Korean/English semantic retrieval quality has not yet been verified.
- therefore Phase 1 is not closed.

## Tool / control

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

## Deployment / CI

Repository contains:
- non-root production Docker image path
- Docker Compose Firebat deployment
- persistent SQLite/Chroma volume
- startup bootstrap
- `/health` / `/version`
- PR Validation workflow
- Firebat Container workflow

Fresh P1-A validation on PR #7:
- dependency installation: PASS
- pytest suite: PASS
- unittest discovery: PASS
- compileall: PASS
- whitespace check: PASS
- production container build: PASS
- Firebat start: PASS
- health/docs/version: PASS
- RAG retrieval smoke with explicit `hash_test`: PASS
- graceful local-LLM fallback: PASS
- persistent agent run: PASS
- restart persistence: PASS

This fresh container evidence validates the provider boundary and regression path, **not** real semantic-model inference.

## Documentation drift

Still open:
- `README.md` broadly reflects controlled RAG but does not yet describe P1-A final state.
- `docs/PROJECT_STATUS.md` is stale.
- `docs/ROADMAP.md` is stale.
- GitHub Issue #4 remains stale/open.

Decision: Master overrides stale docs. External documentation synchronization remains deferred to Proof Packaging unless it blocks earlier acceptance.

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
| Embedding provider boundary | IMPLEMENTED | ACCEPTABLE FOUNDATION |
| Real semantic provider config | IMPLEMENTED | NEEDS RUNTIME EVIDENCE |
| Multi-collection RAG | IMPLEMENTED | NEEDS SEMANTIC RETRIEVAL PROOF |
| Citation metadata | IMPLEMENTED | NEEDS QUALITY VALIDATION |
| Local LLM client | IMPLEMENTED | NEEDS GOLDEN-PATH VERIFICATION |
| LLM unavailable fallback | IMPLEMENTED | FRESHLY REGRESSION-VERIFIED |
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
| L-01 | Semantic provider boundary는 존재하지만 real BGE-M3 runtime/retrieval 품질 미검증 | HIGH | OPEN |
| L-02 | Approval 이후 real controlled execution 없음 | HIGH | OPEN |
| L-03 | Swagger 중심 UX; operator UI 없음 | HIGH | OPEN |
| L-04 | Full lifecycle audit timeline 없음 | MEDIUM | OPEN |
| L-05 | Retrieval/grounding/control evaluation 없음 | MEDIUM | OPEN |
| L-06 | README 외 PROJECT_STATUS/ROADMAP/Issue 상태 drift | MEDIUM | OPEN |
| L-07 | BGE-M3 model download/runtime memory/latency requirement 미검증 | MEDIUM | OPEN |
| L-08 | Fresh container PASS는 explicit `hash_test` 경로이며 semantic container proof가 아님 | MEDIUM | OPEN |

---

# 7. Work Plan / Closure Contracts

## Phase 1 — Real Semantic RAG

### Goal
테스트용 retrieval을 실제 multilingual semantic retrieval로 교체한다.

### P1-A — Embedding Provider Boundary

**Status: CLOSED**

Closure evidence:
- explicit provider/config boundary implemented
- default semantic provider configured
- index/query provider metadata compatibility enforced
- no silent hash fallback
- explicit test-only hash provider
- full PR Validation PASS
- Firebat Container regression PASS with explicit test provider

### P1-B — Semantic Runtime + Bilingual Retrieval Smoke

**Status: NEXT**

Smallest safe slice:
1. 실제 semantic provider를 로드한다.
2. current knowledge base index를 semantic provider로 rebuild한다.
3. collection metadata의 provider/model/dimension을 확인한다.
4. 최소 Korean query 1개 + English query 1개를 실행한다.
5. 각 query에서 의도한 source가 Top-K에 들어오는지 기록한다.
6. runtime/download/resource failure가 있으면 provider/model 선택을 재평가하되 hash fallback은 사용하지 않는다.

P1-B closure requires:
- actual semantic model load evidence
- actual semantic index rebuild evidence
- three collections non-empty
- Korean retrieval evidence
- English retrieval evidence
- expected source Top-K evidence
- actual runtime/resource requirement recorded

### Phase 1 Acceptance Criteria

- [ ] Real semantic embedding executed
- [ ] Index rebuild 성공
- [ ] Existing three collections 정상 동작
- [ ] Korean query retrieval verified
- [ ] English query retrieval verified
- [ ] Relevant document Top-K verified
- [ ] Semantic container/runtime execution verified
- [x] Regression tests PASS for P1-A boundary

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
| E-001 | Baseline | Phase 0 baseline inspection at `fae00d67227a8bc496842ceb244845f09c0bfeae` | PRESENT |
| E-002 | Baseline | Active LangGraph controlled-RAG path inspected | PRESENT |
| E-003 | Baseline | Original hash embedding implementation inspected | PRESENT |
| E-004 | Baseline | Planned-only tool generator / approval endpoints inspected | PRESENT |
| E-005 | Baseline | PR #6 historical CI/container validation record inspected | PRESENT — HISTORICAL |
| E-006 | Baseline | README / PROJECT_STATUS / ROADMAP / Issue #4 drift identified | PRESENT |
| E-101 | RAG | P1-A provider boundary merged via PR #7 at `44d9f2965aea0836081e043a1c7e6888f389feb9` | PRESENT |
| E-102 | RAG | PR #7 PR Validation — pytest/unittest/compileall/diff check | PASS |
| E-103 | RAG | PR #7 Firebat Container regression with explicit `hash_test` | PASS — TEST PROVIDER |
| E-104 | RAG | Real semantic model load + index rebuild | TODO |
| E-105 | RAG | Korean + English semantic retrieval result | TODO |
| E-106 | RAG | Semantic runtime/container resource verification | TODO |
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
- explicit semantic embedding provider boundary
- Local LLM integration boundary
- Tool planning / human review routing
- Docker deployment structure
- fresh P1-A regression/container evidence

## Done Enough to Use
**아직 없음.**

## Not Yet Done
- Real semantic RAG runtime/retrieval proof
- Real controlled execution
- Operator UI
- Complete audit trail
- AI evaluation
- Final proof packaging

---

# 11. Current Priority

## NOW

**Phase 1 / P1-B — Semantic Runtime + Bilingual Retrieval Smoke**

Required before closing P1-B:
- actual semantic model loaded
- semantic index rebuilt
- three collections non-empty
- Korean query executed
- English query executed
- intended source verified in Top-K
- actual model/runtime/download/resource constraints recorded
- no hash fallback

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

### Executed
Repository inspection 수행:
- `main` HEAD
- README
- active LangGraph workflow
- RAG embedding/index/retrieval implementation
- tool planning / approve/reject
- CI workflows
- PROJECT_STATUS / ROADMAP
- Issue #4
- PR #6 validation record

### Not Verified
- fresh pytest/container
- actual Firebat host
- local LLM inference
- semantic model execution

### Remaining Risks
- hash-only semantic gap
- no real tool execution
- no UI/audit/eval
- stale docs

### Next Action
Phase 1 / P1-A.

---

## 2026-08-18 — Phase 1 P1-A Embedding Provider Boundary

### Status
**CLOSED**

### Changed
Application/runtime changes merged through PR #7:
- `app/services/rag_embeddings.py`
  - explicit provider protocol
  - SentenceTransformers semantic provider
  - default `BAAI/bge-m3`
  - explicit `hash_test`
  - no silent fallback
- `app/services/rag_indexer.py`
  - one provider per rebuild
  - provider/model/dimension collection metadata
- `app/services/rag_retriever.py`
  - same configured provider for query
  - stale/incompatible index detection
- `requirements.txt`
  - `sentence-transformers` runtime dependency
- `tests/conftest.py`
  - explicit `hash_test` selection
- `tests/test_rag_embeddings.py`
  - provider/config/no-fallback tests
- `.env.firebat.example`
  - semantic provider/model config
- `compose.firebat.yml`
  - provider/model runtime propagation
- `.github/workflows/firebat-container.yml`
  - explicit CI `hash_test` selection

Master updated after merge; no separate Markdown artifact created.

### Executed
Actual GitHub validation on PR #7:

**PR Validation — PASS**
- dependency install
- pytest suite
- unittest discovery
- compileall
- whitespace/diff check

**Firebat Container — PASS**
- image build
- container startup
- health/docs/version
- RAG retrieval smoke
- local-LLM unavailable fallback
- run creation
- container recreation
- persisted run retrieval

PR #7 squash-merged to `main` as `44d9f2965aea0836081e043a1c7e6888f389feb9`.

### Not Verified
- BGE-M3 actual model download/load not executed.
- BGE-M3 actual embedding inference not executed.
- semantic Chroma index rebuild not executed.
- Korean semantic query not executed.
- English semantic query not executed.
- semantic model memory/latency/container fit not measured.
- local LLM positive inference path not re-verified.

### Remaining Risks
- configured default model may have runtime/download/resource constraints not yet measured.
- semantic retrieval quality remains unproven.
- CI/container PASS used explicit `hash_test`; it is regression evidence, not semantic quality evidence.
- later Proof phases remain open: controlled execution, UI, audit, evaluation, packaging.

### Decision
P1-A's purpose was to create a safe, explicit semantic provider boundary without silently preserving the test hash path. That contract is implemented and regression-validated. Real semantic execution remains P1-B and is not claimed complete.

### Next Action
**Phase 1 / P1-B — load the semantic provider, rebuild the index, execute Korean + English retrieval smoke cases, and record runtime constraints.**

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
