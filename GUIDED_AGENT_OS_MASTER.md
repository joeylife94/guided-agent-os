# Guided Agent OS — Proof Master

> [!info] Document Role  
> **Authoritative production document for Guided Agent OS Proof v1.0**
> 
> 이 문서는 Guided Agent OS의 현재 상태, 목표 상태, 작업 범위, 검증 결과, 남은 위험, 다음 작업을 관리하는 기준 문서다.
> 
> 개발 Agent 또는 LLM의 구현 완료 보고는 최종 사실로 취급하지 않는다.  
> 실제 실행 결과와 증거가 확인된 경우에만 상태를 갱신한다.

---

## 0. Project Snapshot

|Item|Status|
|---|---|
|Project|Guided Agent OS|
|Current Level|**L2 — Integrated Backend Demo**|
|Target Level|**L3 — Usable / Demonstrable Proof**|
|Target Release|**Proof v1.0**|
|Primary Purpose|Wishket AI Agent / RAG / Backend Proof|
|Final Product Goal|Production SaaS가 아닌 **Deployable Controlled AI Agent Proof**|
|Scope Status|**FROZEN**|
|Overall Status|**IN PROGRESS**|

---

# 1. Goal

Guided Agent OS를 기업 내부 업무를 가정한 **Controlled AI Agent Backend Proof** 수준까지 완성한다.

최종 시스템은 사용자의 구조화된 요청을 받아:

1. 입력 검증
2. 부족한 정보 확인
3. 입력 정규화
4. 내부 문서 검색
5. 근거 기반 LLM 답변 생성
6. Tool 실행 계획 생성
7. Risk / Policy 판정
8. Human Approval
9. 승인된 Tool 실행
10. 결과 저장
11. 전체 처리 과정 Audit

까지 하나의 workflow로 수행할 수 있어야 한다.

---

# 2. Positioning

## Current Position

**Controlled RAG Agent Backend Prototype**

현재는 AI Agent Backend의 핵심 구조와 workflow를 증명할 수 있는 상태다.

하지만 아직 사용자가 브라우저에서 업무 하나를 처음부터 끝까지 처리할 수 있는 수준은 아니다.

---

## Target Position

**Deployable Controlled AI Agent Proof**

다음 내용을 실제로 시연할 수 있는 상태를 목표로 한다.

```text
Structured Intake
        ↓
Validation
        ↓
Clarification
        ↓
Normalization
        ↓
Semantic RAG
        ↓
Grounded LLM Answer
        ↓
Tool Planning
        ↓
Risk / Policy Check
        ↓
Human Approval
        ↓
Controlled Tool Execution
        ↓
Execution Result
        ↓
Audit Trail
```

---

# 3. Definition of Usable

Guided Agent OS가 **사용 수준**에 도달했다는 의미는 다음 하나의 시나리오를 실제 사용자가 처음부터 끝까지 수행할 수 있다는 것이다.

## Golden Path

### Step 1 — Request
사용자가 브라우저에서 업무 요청과 필요한 업무 맥락을 입력한다.

### Step 2 — Validation
필수 정보가 존재하는지 검증한다.
부족한 정보가 있다면 Agent가 clarification question을 반환한다.

### Step 3 — Normalization
입력 데이터를 Agent workflow가 처리 가능한 구조로 정규화한다.
원본 입력은 별도로 보존한다.

### Step 4 — RAG Retrieval
내부 Knowledge Base에서 의미 기반 검색을 수행한다.
검색 결과는 Source, Document metadata, Retrieved chunk, Relevance / similarity information을 포함한다.

### Step 5 — Grounded Answer
LLM은 검색된 Context를 기반으로 답변을 생성한다.
답변에는 확인 가능한 Citation이 포함되어야 한다.
Context가 충분하지 않을 경우 이를 명시해야 한다.

### Step 6 — Tool Planning
추가 작업이 필요한 경우 Tool Plan을 생성한다.
Tool Plan에는 Tool name, Purpose, Parameters, Risk, Approval requirement, Execution permission이 포함된다.

### Step 7 — Human Review
민감하거나 Tool 실행이 필요한 요청은 사람에게 전달된다.
사용자는 Approve / Reject 중 하나를 선택할 수 있다.

### Step 8 — Controlled Execution
Approve된 경우에만 Allowlist에 등록된 Tool을 Backend Executor가 실행한다.
LLM은 Tool을 직접 실행하지 않는다.

### Step 9 — Result
실행 결과를 Agent Run에 저장하고 사용자에게 반환한다.

### Step 10 — Audit
한 Run의 전체 lifecycle을 시간 순서대로 확인할 수 있다.

---

# 4. Current State

## Implemented

### API / Backend
- FastAPI server
- Health endpoint
- Version endpoint
- Pydantic validation
- SQLite
- SQLAlchemy
- Agent Run persistence

### Agent Workflow
- LangGraph workflow
- Structured intake
- Required field validation
- Clarification question generation
- Deterministic normalization
- Controlled RAG Agent template
- RAG answer node
- Tool planning node
- Human review routing

### RAG
- Markdown Knowledge Base
- ChromaDB
- Persistent RAG index
- Multi-collection retrieval
- Domain Knowledge collection
- Agent Policy collection
- Tool Catalog collection
- Source metadata
- Citation output
- Local LLM integration
- LLM unavailable fallback

### Control
- Risk-aware Tool planning
- `planned_only` execution mode
- Approval required routing
- Approve / Reject API
- Direct SQL execution blocked by design
- Unapproved external action blocked by design

### Deployment / Operations
- Docker image
- Non-root container
- Docker Compose
- Persistent SQLite / Chroma state
- Startup bootstrap
- Health verification
- Restart persistence verification
- GitHub Actions
- Pytest
- Container CI verification

---

# 5. Current Limitations

## L-01 — Test-grade Embedding
현재 RAG embedding은 production-grade semantic embedding model이 아닌 deterministic hash embedding이다.
따라서 ChromaDB integration과 retrieval workflow는 검증되어 있지만 실제 semantic RAG 품질을 충분히 증명하지 못한다.
**Status:** OPEN

## L-02 — Planned-only Tool Execution
현재 Tool Plan은 생성되지만 실제 Tool 실행까지 이어지지 않는다.

```text
Tool Plan
    ↓
Human Approval
    ↓
END
```

현재 상태에서는 Approval 이후 업무 결과를 만들어내지 못한다.
**Status:** OPEN

## L-03 — No Operator UI
현재 주요 사용 인터페이스는 FastAPI Swagger다.
개발 검증에는 충분하지만 실제 클라이언트 또는 비개발자에게 workflow를 시연하기 어렵다.
**Status:** OPEN

## L-04 — Incomplete Audit Timeline
Run persistence는 구현되어 있으나 업무 lifecycle 전체를 Event 단위로 보여주는 Audit Timeline은 없다.
**Status:** OPEN

## L-05 — No AI Quality Evaluation
Software test와 CI는 존재한다.
하지만 Retrieval quality, Grounding, Citation correctness, Unsupported claims, Risk routing, Tool control은 아직 체계적으로 검증하지 않는다.
**Status:** OPEN

## L-06 — Documentation Drift
README, PROJECT_STATUS, ROADMAP, GitHub Issue 사이에 현재 구현 상태가 일치하지 않는 부분이 존재한다.
**Status:** OPEN

---

# 6. Proof v1.0 Scope

## IN SCOPE

### P0 — Baseline / Documentation
- Current implementation 재확인
- 실제 구현 / 미구현 구분
- README 정합성
- PROJECT_STATUS 정합성
- ROADMAP 정합성
- stale GitHub Issue 정리
- Proof Scope Freeze

### P1 — Real Semantic RAG
- production-grade local embedding 도입
- multilingual retrieval 지원
- 기존 Chroma integration 유지
- retrieval quality 검증

Candidate: BGE-M3 또는 동급 multilingual embedding model

### P2 — Controlled Tool Execution
최소 하나의 실제 Read-only Tool을 구현한다.
Candidate: `legacy_record_lookup`
목적: Enterprise legacy system을 가정한 read-only lookup API.

```text
Tool Plan
    ↓
Policy Check
    ↓
Approval
    ↓
Allowlist Check
    ↓
Executor
    ↓
Tool Result
```

### P3 — Operator UI
최소 UI를 구현한다.
필수 기능: Request 입력, Business Context 입력, Risk 선택, Agent 실행, RAG Answer 표시, Citation 표시, Tool Plan 표시, Approve, Reject, Execution Result, Audit Timeline.

### P4 — Audit Trail
Run lifecycle Event를 저장한다.

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

### P5 — Evaluation
고정 Evaluation Dataset 20~30 cases를 만든다.
Retrieval: Top-1, Top-3.
Grounding: Citation presence, Citation correctness, Unsupported claim.
Control: High-risk routing, Reject blocks execution, Approval permits allowlisted execution, Unauthorized Tool block, Restricted action block.

### P6 — Proof Packaging
- README final
- Architecture diagram
- Demo scenario
- Screenshots
- Evaluation result
- Known limitations
- Setup / deployment guide
- clean main branch

---

# 7. NOT NOW

Proof v1.0에서는 다음을 구현하지 않는다.
- Multi-Agent orchestration
- Kubernetes
- Multi-tenancy
- Authentication system
- OAuth / SSO
- Complex RBAC
- Billing
- SaaS commercialization
- Multiple production tools
- Real Oracle integration
- Real customer infrastructure integration
- Destructive/write Tool
- Automatic email sending
- Automatic Slack actions
- External account automation
- High availability
- Horizontal scaling
- Enterprise observability stack
- Complex admin system
- Mobile application

위 항목은 Proof v1.0 Closure 조건에 영향을 주지 않는다.

---

# 8. Work Plan

## Phase 0 — Baseline Freeze
### Goal
현재 구현 상태와 Proof 목표 사이의 차이를 확정한다.
### Deliverable
Authoritative current-state baseline.
### Acceptance Criteria
- 현재 main 코드 확인
- active workflow 확인
- RAG 구현 확인
- Tool control 구현 확인
- CI 확인
- deployment 확인
- README 상태 확인
- PROJECT_STATUS 상태 확인
- ROADMAP 상태 확인
- Open Issue 상태 확인
- 구현 / 미구현 Matrix 확정
### Closure Condition
현재 상태와 Proof v1.0 Scope에 모순이 없어야 한다.

## Phase 1 — Real Semantic RAG
### Goal
테스트용 retrieval을 실제 semantic RAG 수준으로 교체한다.
### Deliverable
Multilingual semantic retrieval engine.
### Acceptance Criteria
- Real embedding model integrated
- Index rebuild 성공
- Existing collections 정상 동작
- Korean query test
- English query test
- Relevant document Top-K 검증
- Container 실행 검증
- Regression tests PASS
### Closure Condition
Golden evaluation set에서 retrieval 결과가 Proof로 제시 가능한 수준이어야 한다.

## Phase 2 — Controlled Tool Execution
### Goal
Human Approval 이후 실제 제한된 업무 하나를 수행한다.
### Deliverable
Allowlisted read-only executor.
### Acceptance Criteria
- Tool Registry 존재
- Tool Allowlist 존재
- Read-only Tool 1개 구현
- Tool parameters validation
- Approval 없이는 실행 불가
- Reject 시 실행 불가
- Unauthorized tool 실행 불가
- Approved tool 정상 실행
- Execution result persistence
- Tests PASS
### Closure Condition
```text
Plan
→ Approval Requested
→ Approve
→ Tool Executed
→ Result Persisted
```

## Phase 3 — Operator UI
### Goal
비개발자도 Golden Path를 수행할 수 있도록 한다.
### Deliverable
Minimal Agent Workspace.
### Acceptance Criteria
- Request form
- Run submission
- Clarification display
- Grounded Answer
- Citations
- Tool Plan
- Approve
- Reject
- Result
- Audit Timeline
### Closure Condition
Swagger를 사용하지 않고 브라우저 UI만으로 Golden Path를 완료할 수 있어야 한다.

## Phase 4 — Audit Trail
### Goal
Agent의 의사결정과 실행 과정을 추적 가능하게 만든다.
### Deliverable
Persistent Run Event Timeline.
### Acceptance Criteria
- Event schema
- timestamps
- actor
- event type
- event payload/reference
- run relationship
- UI timeline
- restart persistence
### Closure Condition
특정 Run 하나를 보고 전체 처리 과정을 재구성할 수 있어야 한다.

## Phase 5 — Evaluation
### Goal
Agent가 단순히 실행되는 것이 아니라 일정 품질을 가진다는 증거를 확보한다.
### Deliverable
Repeatable Agent/RAG Evaluation Suite.
### Acceptance Criteria
- Evaluation cases >= 20
- Retrieval evaluation
- Grounding evaluation
- Citation evaluation
- Risk routing evaluation
- Tool permission evaluation
- Approval / Reject evaluation
- Repeatable command
- Result artifact
### Closure Condition
README 또는 Proof 자료에 실제 Evaluation Result를 제시할 수 있어야 한다.

## Phase 6 — Proof Packaging
### Goal
코드를 열어보지 않아도 프로젝트 가치를 이해할 수 있게 만든다.
### Deliverable
Wishket-ready GitHub Proof.
### Acceptance Criteria
- README updated
- Current architecture diagram
- Golden Path diagram
- Demo screenshots
- Demo scenario
- Evaluation result
- Technology stack
- Safety boundary
- Known limitations
- Reproduction instructions
- Documentation matches implementation
### Closure Condition
외부 검토자가 5~10분 안에 무엇을 해결하는 시스템인지, 어떻게 동작하는지, AI가 어디까지 통제되는지, 실제 구현 기능, 검증 방식, 남은 한계를 이해할 수 있어야 한다.

---

# 9. Proof v1.0 Final Acceptance Criteria

다음 조건이 모두 만족되어야 **Proof v1.0 CLOSED**를 선언한다.

## RAG
- Real semantic embedding
- Persistent vector index
- Korean retrieval verified
- English retrieval verified
- Grounded answer
- Citation
- Missing-context behavior

## Agent Workflow
- Validation
- Clarification
- Normalization
- RAG
- Answer
- Tool Planning
- Risk routing
- Human Approval
- Controlled execution
- Result persistence

## Safety
- No direct LLM tool execution
- Tool allowlist
- Parameter validation
- Reject blocks execution
- Unauthorized action blocked
- Read-only execution boundary documented

## UX
- Browser-based Golden Path
- Answer visible
- Source visible
- Approval controls
- Result visible
- Audit Timeline visible

## Operations
- Docker deployment
- Persistent state
- Restart recovery
- Health check
- Version metadata

## QA
- Unit/integration test suite PASS
- Container test PASS
- Golden Path E2E PASS
- Eval suite PASS
- Known limitations recorded

## Proof
- Architecture diagram
- Demo screenshots
- Evaluation evidence
- README
- Reproduction guide

---

# 10. Evidence Registry

각 Phase를 닫을 때 실제 Evidence를 기록한다.

|ID|Phase|Evidence|Status|
|---|---|---|---|
|E-001|Baseline|Existing pytest / CI|PRESENT|
|E-002|Baseline|Firebat container verification|PRESENT|
|E-003|RAG|Real embedding retrieval result|TODO|
|E-004|Execution|Approved tool execution|TODO|
|E-005|Execution|Rejected execution blocked|TODO|
|E-006|UI|Golden Path screenshot|TODO|
|E-007|Audit|Complete Run Timeline|TODO|
|E-008|Eval|Evaluation result|TODO|
|E-009|Deploy|Fresh deployment verification|TODO|

---

# 11. Validation Rule

어떤 작업도 개발 Agent의 자기 보고만으로 완료 처리하지 않는다.
작업 종료 시 반드시 아래 네 항목을 확인한다.

## Changed
실제로 변경된 코드 / 문서 / 설정.
## Executed
실제로 실행된 Test / Build / API / UI scenario / Deployment.
## Not Verified
이번 작업에서 확인하지 못한 항목.
## Remaining Risks
현재 알려진 위험 또는 불확실성.

---

# 12. Current Risks

|Risk|Severity|Status|
|---|--:|---|
|Hash embedding이 semantic RAG Proof로 부족|HIGH|OPEN|
|Approval 이후 real execution 없음|HIGH|OPEN|
|Swagger 중심 UX|HIGH|OPEN|
|AI quality evaluation 없음|MEDIUM|OPEN|
|Audit lifecycle 부족|MEDIUM|OPEN|
|Documentation drift|MEDIUM|OPEN|

---

# 13. Current Work Status

## Done Enough to Use
현재 없음.

## Done Enough to Show
- Backend architecture
- LangGraph controlled workflow
- Chroma RAG integration
- Local LLM integration structure
- Tool planning
- Human review routing
- Docker deployment
- CI / persistence

## Not Yet Done
- Semantic RAG
- Real controlled execution
- Operator UI
- Complete audit trail
- AI evaluation
- Final proof packaging

---

# 14. Current Priority

## NOW
**Phase 0 — Baseline Freeze**
먼저 현재 repository의 실제 상태를 authoritative하게 확정한다.
그 다음 작업: **Phase 1 — Real Semantic RAG**

---

# 15. Next Action

1. `main` 기준 repository 재검사
2. 현재 active feature matrix 작성
3. stale documentation 식별
4. obsolete/open Issue 확인
5. Proof v1.0 Scope와 실제 상태 비교
6. Phase 0 closure 판정

---

# 16. Work Log

## 2026-08-18 — Proof v1.0 Scope Definition
### Decision
Guided Agent OS의 목표를 Production SaaS가 아닌 **Deployable Controlled AI Agent Proof**로 고정.
### Current Level
**L2 — Integrated Backend Demo**
### Target Level
**L3 — Usable / Demonstrable Proof**
### Scope Added
- Real semantic RAG
- Human-approved read-only Tool execution
- Minimal Operator UI
- Audit Trail
- Agent/RAG Evaluation
- Proof Packaging
### Explicitly Excluded
- Multi-Agent
- Kubernetes
- Authentication / SSO
- SaaS features
- Production customer integrations
- Write/destructive Tools
- Large-scale enterprise infrastructure
### Next
**Phase 0 — Baseline Freeze**

---

# 17. Final Closure Definition

Guided Agent OS Proof v1.0은 다음 질문에 모두 **YES**라고 답할 수 있을 때 종료한다.

> 실제 사용자가 브라우저에서 Agent에게 업무를 요청할 수 있는가?

> Agent가 실제 내부 문서를 semantic search할 수 있는가?

> LLM 답변에 검증 가능한 근거가 존재하는가?

> Tool이 필요할 경우 AI가 직접 실행하지 않고 통제된 Plan을 만드는가?

> 민감한 작업은 사람의 승인을 요구하는가?

> 승인된 제한 Tool 하나가 실제로 실행되는가?

> 거절되거나 허가되지 않은 Tool은 실행되지 않는가?

> 모든 과정이 저장되고 추적 가능한가?

> 이 동작이 자동화된 테스트와 Evaluation으로 검증되어 있는가?

> 외부 사람이 README와 Demo만 보고 이를 확인할 수 있는가?

**모두 YES → `GUIDED AGENT OS PROOF v1.0 CLOSED`**

그 이후 기능은 Proof v1.1 또는 실제 고객 요구사항으로 분리한다.