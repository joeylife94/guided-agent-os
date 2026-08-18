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
| Current Verified App HEAD | `ebbaafc89363ef31012b235e3c8822920895bbe3` |
| Active Proof PR | None — PR #8 merged after passing P1-B evidence |
| Current Level | **L2+ — Integrated Backend Demo with verified semantic RAG runtime** |
| Target Level | **L3 — Usable / Demonstrable Proof** |
| Target Release | **Proof v1.0** |
| Primary Purpose | Wishket AI Agent / RAG / Backend Proof |
| Final Product Goal | **Deployable Controlled AI Agent Proof** |
| Scope Status | **FROZEN** |
| Phase 0 | **CLOSED — Baseline Frozen** |
| Phase 1 | **CLOSED — Real Semantic RAG runtime + bilingual retrieval proven** |
| Phase 2 | **NEXT — Controlled Tool Execution** |
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

Implemented and inspected:
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

### P1-A embedding boundary — CLOSED

Merged through PR #7 at `44d9f2965aea0836081e043a1c7e6888f389feb9`.

Implemented behavior:
- explicit `EmbeddingProvider` boundary
- configurable SentenceTransformers semantic provider
- explicit `RAG_EMBEDDING_PROVIDER` / `RAG_EMBEDDING_MODEL` configuration
- deterministic hash embedding retained only as explicit `hash_test`
- no silent semantic → hash fallback
- index metadata records provider, model, dimensions
- index rebuild uses one provider instance for all document embeddings
- retrieval uses the same configured provider and validates collection provider/model/dimension metadata
- incompatible/stale embedding index produces an explicit rebuild error instead of silent empty retrieval
- Firebat runtime receives embedding provider/model configuration
- CI can explicitly select `hash_test` for deterministic regression without claiming semantic proof

### P1-B semantic runtime + bilingual retrieval — CLOSED

PR #8 was completed and squash-merged to `main` as `ebbaafc89363ef31012b235e3c8822920895bbe3`.

Selected proof model:
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- SentenceTransformers runtime path
- embedding dimension observed from actual collection metadata: `384`
- existing provider identifier remains `bge_m3` for compatibility with the P1-A provider contract; **the actual model identity is the `embedding_model` metadata field above**.

Why the model changed:
- BGE-M3 successfully loaded and rebuilt the semantic index but was unstable under the frozen `1536m` Firebat memory envelope.
- the smaller multilingual MiniLM model was selected rather than increasing the memory envelope or restoring hash fallback.

Fresh successful P1-B runtime evidence:
- production image build: PASS
- container startup: PASS
- semantic bootstrap: PASS
- stable health before semantic retrieval: PASS
- semantic collections: `domain_knowledge=4`, `agent_policy=6`, `tool_catalog=7`
- collection metadata: model `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, dimensions `384`
- Korean semantic query: PASS
- English semantic query: PASS
- intended source `tools/legacy-db-access-guideline.md`: ranked #1 and #2 for both Korean and English global Top-3 checks
- Korean top results:
  - `tools/legacy-db-access-guideline.md` — `0.6741865873336792`
  - `tools/legacy-db-access-guideline.md` — `0.5557947158813477`
  - `tools/approved-tools.md` — `0.4243924617767334`
- English top results:
  - `tools/legacy-db-access-guideline.md` — `0.8019968271255493`
  - `tools/legacy-db-access-guideline.md` — `0.7076278328895569`
  - `tools/approved-tools.md` — `0.39176106452941895`
- runtime sample after bilingual retrieval: `1.167GiB / 1.5GiB`, CPU `0.30%`
- graceful local-LLM unavailable fallback: PASS
- persistent agent run creation: PASS
- container recreation: PASS
- post-restart health: PASS
- persisted run retrieval after recreation: PASS
- no hash fallback used for the P1-B semantic proof

P1-B CI history note:
- first smaller-model run reached healthy semantic retrieval but failed only because CI expected `app/knowledge/tools/...` while actual persisted metadata uses `tools/...`.
- the assertion was corrected to the actual source-path contract.
- the rerun passed all P1-B gates.

Remaining semantic-runtime risk:
- current dependency resolution still installs a large GPU/CUDA-oriented Torch dependency set in a CPU-oriented image.
- this did **not** block the successful MiniLM semantic proof, but remains a footprint/maintainability concern to defer unless it blocks later Proof work.

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

Fresh final P1-B validation on PR #8 head `f07046a7c8eb282714ab73ff722fc428f62fd406`:

**PR Validation — PASS**
- dependency install: PASS
- pytest suite: PASS
- unittest discovery: PASS
- compileall: PASS
- whitespace check: PASS

**Firebat Container — PASS**
- production image build: PASS
- Firebat start: PASS
- health/docs/version: PASS
- real semantic model/index metadata check: PASS
- Korean retrieval + intended Top-K source: PASS
- English retrieval + intended Top-K source: PASS
- semantic runtime stats capture: PASS
- local-LLM unavailable fallback: PASS
- persistent run creation: PASS
- image metadata: PASS
- container recreation: PASS
- post-restart semantic health: PASS
- persisted run retrieval: PASS
- persistent volume inspection: PASS

PR #8 merged after all required P1-B gates were green.

## Documentation drift

Still open:
- `README.md` broadly reflects controlled RAG but does not yet describe final P1 semantic model/runtime state.
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
| Embedding provider boundary | IMPLEMENTED | ACCEPTABLE |
| Real semantic provider config | IMPLEMENTED | ACCEPTABLE |
| Real semantic model load | VERIFIED | ACCEPTABLE |
| Semantic index rebuild | VERIFIED | ACCEPTABLE |
| Multi-collection semantic RAG | VERIFIED | KOREAN + ENGLISH SMOKE PASS |
| Intended-source semantic Top-K | VERIFIED | PASS |
| Citation metadata | IMPLEMENTED | NEEDS QUALITY EVALUATION IN P5 |
| Local LLM client | IMPLEMENTED | POSITIVE INFERENCE PATH STILL NEEDS GOLDEN-PATH VERIFICATION |
| LLM unavailable fallback | IMPLEMENTED | FRESHLY VERIFIED |
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
| L-01 | Original BGE-M3 path was unstable under frozen 1536 MiB Firebat cap | HIGH | RESOLVED FOR PROOF BY SMALLER MODEL |
| L-02 | Approval 이후 real controlled execution 없음 | HIGH | OPEN |
| L-03 | Swagger 중심 UX; operator UI 없음 | HIGH | OPEN |
| L-04 | Full lifecycle audit timeline 없음 | MEDIUM | OPEN |
| L-05 | Retrieval/grounding/control evaluation 없음 | MEDIUM | OPEN |
| L-06 | README 외 PROJECT_STATUS/ROADMAP/Issue 상태 drift | MEDIUM | OPEN |
| L-07 | Selected MiniLM semantic runtime fit under current 1536m envelope | HIGH | VERIFIED / CLOSED FOR P1 |
| L-08 | Korean/English semantic retrieval + intended-source Top-K | HIGH | VERIFIED / CLOSED FOR P1 |
| L-09 | Current unconstrained Torch/SentenceTransformers dependency resolution pulls large CUDA/NVIDIA packages into a CPU-oriented image | MEDIUM | OPEN — DEFER UNLESS BLOCKING |
| L-10 | Exact reason for historical BGE-M3 `Killed` event was not directly verified as Docker OOMKilled | LOW | HISTORICAL / ACCEPTED |
| L-11 | Provider identifier remains `bge_m3` while configured semantic model is MiniLM; actual model metadata is accurate but provider label is legacy/misleading | LOW | OPEN — DEFER UNLESS CONFUSING PROOF |
| L-12 | Positive local-LLM inference path has not been freshly verified with the final P1 semantic model | MEDIUM | OPEN — VERIFY IN GOLDEN PATH BEFORE FINAL CLOSURE |

---

# 7. Work Plan / Closure Contracts

## Phase 1 — Real Semantic RAG

### Goal
테스트용 retrieval을 실제 multilingual semantic retrieval로 교체한다.

### P1-A — Embedding Provider Boundary

**Status: CLOSED**

Closure evidence:
- explicit provider/config boundary implemented
- semantic provider configured
- index/query provider metadata compatibility enforced
- no silent hash fallback
- explicit test-only hash provider
- full PR Validation PASS
- Firebat Container regression PASS with explicit test provider

### P1-B — Semantic Runtime + Bilingual Retrieval Smoke

**Status: CLOSED**

Closure evidence:
1. selected real semantic model `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` loaded successfully.
2. semantic index rebuild executed successfully.
3. all three collections were non-empty: `4 / 6 / 7`.
4. Korean retrieval executed successfully.
5. English retrieval executed successfully.
6. intended legacy DB source ranked in global Top-3 for both queries; in the captured run it ranked #1 and #2 for both languages.
7. production-style Firebat container remained healthy under the frozen `1536m` envelope.
8. observed runtime sample after bilingual retrieval: `1.167GiB / 1.5GiB`, CPU `0.30%`.
9. graceful LLM-unavailable fallback and restart persistence remained green.
10. no hash fallback was used for semantic proof.
11. PR Validation and Firebat Container workflows both passed on final PR #8 head.
12. PR #8 squash-merged to `main` as `ebbaafc89363ef31012b235e3c8822920895bbe3`.

### Phase 1 Acceptance Criteria

- [x] Real semantic embedding model loaded
- [x] Semantic index rebuilt
- [x] Existing three collections proven under stable runtime
- [x] Korean query retrieval verified
- [x] English query retrieval verified
- [x] Relevant intended document Top-K verified
- [x] Semantic container/runtime execution verified stable
- [x] Runtime memory/CPU sample recorded
- [x] Regression tests PASS
- [x] No hash fallback in semantic proof

### Closure
**CLOSED.** Semantic retrieval evidence is sufficient to move to controlled execution. Broader RAG quality evaluation remains Phase 5, not a reason to keep P1 open.

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

### P2-A — Smallest Next Slice

**Goal:** create the controlled execution boundary without overbuilding external integrations.

Smallest safe implementation target:
1. inspect current approve/reject endpoint and `AgentRun` persistence contract.
2. define a minimal local Tool Registry with one allowlisted read-only tool: `legacy_record_lookup` (or an equivalent deterministic local fixture lookup).
3. define explicit parameter validation for the single tool.
4. add an Executor that refuses execution unless:
   - run is in an approval-eligible state,
   - human approval has been recorded,
   - tool exists in registry,
   - tool is allowlisted/read-only,
   - parameters validate.
5. persist execution result on the existing run/result structure using the smallest schema extension that preserves auditability.
6. add narrow tests for approve → execute, reject → block, no approval → block, unauthorized tool → block, invalid parameters → block.
7. do **not** add real Oracle/customer systems, multiple tools, write operations, authentication, or external actions.

P2-A closes only with actual test execution evidence, not code presence alone.

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
| E-104 | RAG | Historical PR #8 BGE-M3 weights loaded after writable HF cache fix | PRESENT — HISTORICAL PARTIAL |
| E-105 | RAG | Historical BGE-M3 semantic bootstrap rebuilt `4 / 6 / 7` collections | PRESENT — HISTORICAL PARTIAL |
| E-106 | RAG | Historical BGE-M3 process reported `Killed` / unstable under `1536m` | FAIL — SUPERSEDED MODEL |
| E-107 | RAG | Final PR #8 PR Validation on head `f07046a7c8eb282714ab73ff722fc428f62fd406` | PASS |
| E-108 | RAG | MiniLM semantic index metadata: `4 / 6 / 7`, model exact, dimensions `384` | PASS |
| E-109 | RAG | Korean semantic retrieval intended source global Top-3 (#1/#2) | PASS |
| E-110 | RAG | English semantic retrieval intended source global Top-3 (#1/#2) | PASS |
| E-111 | RAG | Stable semantic runtime sample after bilingual retrieval: `1.167GiB / 1.5GiB`, CPU `0.30%` | PRESENT |
| E-112 | RAG | Final PR #8 Firebat Container workflow including fallback + persistence + restart | PASS |
| E-113 | RAG | PR #8 squash merge to `main` at `ebbaafc89363ef31012b235e3c8822920895bbe3` | PRESENT |
| E-201 | Execution | Approved allowlisted tool execution | TODO |
| E-202 | Execution | Reject/unauthorized execution blocked | TODO |
| E-203 | Execution | Invalid/no-approval execution blocked | TODO |
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
- real multilingual semantic model runtime
- Korean + English semantic retrieval
- intended-source Top-K evidence
- semantic runtime resource sample under the frozen Firebat envelope
- Local LLM integration boundary
- Tool planning / human review routing
- Docker deployment structure
- fresh P1-A regression/container evidence
- fresh P1-B production-style semantic evidence

## Done Enough to Use
**아직 없음.**

Reason:
- approval 이후 실제 controlled read-only execution이 아직 없다.
- operator UI / complete audit path도 아직 없다.

## Not Yet Done
- Real controlled execution
- Operator UI
- Complete audit trail
- Positive local-LLM Golden Path verification
- AI quality evaluation
- Final proof packaging

---

# 11. Current Priority

## NOW

**Phase 2 / P2-A — Minimal Controlled Read-only Execution Boundary**

Smallest next action:
1. inspect `AgentRun`, approve/reject endpoints, current tool-plan output and persistence path.
2. implement one deterministic local read-only tool (`legacy_record_lookup` or equivalent) behind a minimal registry/allowlist.
3. make execution impossible without recorded approval, allowlist membership, read-only classification and valid parameters.
4. persist result with the smallest auditable schema change.
5. run narrow tests for approved success and every required block path.

Required before closing P2-A:
- one actual tool execution path exists
- approval required and verified
- reject/no approval blocks execution
- unauthorized tool blocks execution
- invalid parameters block execution
- result persists
- relevant tests actually execute and pass

Do not expand into additional tools, external systems, write operations, auth, Oracle, email, Slack, SaaS or admin features.

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
  - configurable semantic model
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
- real semantic model runtime
- Korean semantic query
- English semantic query
- semantic model memory/container fit
- local LLM positive inference path

### Remaining Risks
- semantic runtime fit and quality not yet proven at P1-A closure.
- later Proof phases remain open.

### Decision
P1-A's purpose was to create a safe, explicit semantic provider boundary. Real semantic execution remained P1-B.

### Next Action
P1-B.

---

## 2026-08-18 — Phase 1 P1-B Historical BGE-M3 Runtime Attempt

### Status
**FAILED MODEL FIT — RETAINED AS DIAGNOSTIC EVIDENCE**

### Changed
On PR #8:
- semantic Firebat proof path added
- writable Hugging Face cache routed through existing `/app/data` volume without weakening `read_only: true`
- bilingual query and runtime-stat checks prepared

### Executed
- production image build
- actual BGE-M3 model load
- semantic index rebuild
- non-empty counts `4 / 6 / 7`

### Not Verified
- stable BGE-M3 health
- bilingual retrieval
- Top-K quality
- runtime sample

### Remaining Risks
- historical BGE-M3 kill mechanism was not proven as explicit Docker OOMKilled.
- GPU-heavy Torch dependency footprint remained.

### Decision
Do not increase memory or fall back to hash. Select a smaller multilingual semantic model within the same frozen `1536m` proof envelope.

---

## 2026-08-18 — Phase 1 P1-B Smaller Multilingual Semantic Runtime

### Status
**CLOSED**

### Changed
Changes completed on PR #8 and merged:
- `.env.firebat.example`
  - semantic model changed from `BAAI/bge-m3` to `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
  - frozen semantic provider boundary retained
- `.github/workflows/firebat-container.yml`
  - semantic metadata assertion updated for MiniLM + `384` dimensions
  - Korean query retained
  - English query retained
  - intended legacy DB guideline Top-3 assertion retained
  - runtime resource capture retained
  - source-path assertion corrected from `app/knowledge/tools/...` to actual metadata contract `tools/...`

No separate Markdown artifact created. This Master is the authoritative result.

### Executed
Actual GitHub Actions on final PR #8 head `f07046a7c8eb282714ab73ff722fc428f62fd406`:

**PR Validation — PASS**
- dependency installation
- pytest
- unittest discovery
- compileall
- whitespace check

**Firebat Container — PASS**
- production image built
- container started
- `/health`, `/docs`, `/version` passed
- semantic index metadata confirmed:
  - `domain_knowledge=4`
  - `agent_policy=6`
  - `tool_catalog=7`
  - model `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
  - dimensions `384`
- Korean retrieval passed:
  - intended `tools/legacy-db-access-guideline.md` ranked #1 and #2 globally
- English retrieval passed:
  - intended `tools/legacy-db-access-guideline.md` ranked #1 and #2 globally
- runtime sample captured:
  - memory `1.167GiB / 1.5GiB`
  - CPU `0.30%`
- graceful local-LLM unavailable fallback passed
- persistent agent run creation passed
- image version/revision metadata passed
- container recreation passed
- post-restart health passed
- persisted run retrieval passed
- persistent volume inspection passed

PR #8 squash-merged to `main` as `ebbaafc89363ef31012b235e3c8822920895bbe3`.

### Not Verified
- broader retrieval quality across a 20~30 case set is not verified; this belongs to Phase 5.
- positive local-LLM inference with the final semantic model is not freshly verified.
- CPU-only dependency slimming is not implemented.
- exact historical BGE-M3 kill cause remains unproven and no longer blocks Proof progression.

### Remaining Risks
- current image still resolves large CUDA/NVIDIA Torch dependencies despite CPU-oriented execution.
- provider identifier `bge_m3` is a legacy label while actual model metadata correctly names MiniLM.
- one captured runtime sample proves fit for this proof path, not production capacity planning or sustained-load behavior.

### Decision
P1-B closure criteria are met. The semantic Proof goal is bilingual controlled retrieval evidence under the existing constrained Firebat envelope, not load testing or broad quality benchmarking. Those later concerns remain explicitly scoped to Phase 5/final validation as appropriate.

### Next Action
**Phase 2 / P2-A — implement the smallest human-approved allowlisted read-only execution path with one deterministic local tool and hard block-path tests.**

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
