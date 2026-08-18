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
| Phase 0 | **CLOSED — Baseline Frozen** |
| Phase 1 | **CLOSED — Real Semantic RAG runtime + bilingual retrieval proven** |
| Phase 2 | **CLOSED — Human-approved allowlisted read-only execution proven** |
| Phase 3 | **CLOSED — Operator UI + clarification + real browser Golden Path proven** |
| Phase 4 | **CLOSED — persisted lifecycle events + persisted Operator audit timeline browser-proven** |
| Phase 5 | **CLOSED — fixed 22-case suite executed 22/22 PASS with durable JSON evidence** |
| Phase 6 | **IN PROGRESS — P6-A CLOSED; P6-B explicit closure decision CLOSED; P6-C final deployment/regression NEXT** |
| Current Level | **L2++++ — usable Proof path + fixed quality suite + external documentation synchronized** |
| Target Level | **L3 — Usable / Demonstrable Proof** |
| Target Release | **Proof v1.0** |
| Final Product Goal | **Deployable Controlled AI Agent Proof** |
| Scope Status | **FROZEN** |
| Overall Status | **IN PROGRESS** |
| Latest verified app/eval merge | `8498183f584332887a38ae5e925e6b810177e99b` |
| P6-A documentation baseline | `cb0cf3b4109531a8f01c612511b11434464621f9` |

---

# 1. Goal

Guided Agent OS를 기업 내부 업무를 가정한 **Controlled AI Agent Proof** 수준까지 완성한다.

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

Production SaaS 완성이 목표가 아니다. 위 workflow를 실제로 재현·검증·시연하고 외부 검토자가 Evidence로 확인할 수 있으면 Proof v1.0을 닫는다.

---

# 2. Frozen Scope

## IN SCOPE

- baseline/current-state freeze
- real local semantic embedding + Korean/English retrieval
- grounded answer + citation
- controlled tool plan
- human approval
- one allowlisted deterministic read-only tool
- reject/no-approval/unauthorized/invalid-parameter block paths
- browser Operator Workspace
- persisted audit timeline
- 20~30 fixed evaluation cases
- machine-readable evaluation evidence
- README / architecture / Golden Path / known limitations / reproduction guide
- stale external status/roadmap/Issue synchronization or explicit deprecation
- final local-LLM positive-path verification **or explicit closure decision**
- fresh final deployment/regression evidence

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
- adding a new cloud/provider dependency solely to obtain final positive LLM evidence
- provisioning a new CI-hosted local-LLM runtime solely for Proof v1.0 closure

---

# 3. Verified Current State

## Backend / Workflow — ACCEPTABLE

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

Verified foundation:
- FastAPI / Pydantic
- SQLite / SQLAlchemy persistence
- LangGraph controlled workflow
- Docker/Firebat runtime
- GitHub PR Validation + Firebat Container regression

## Semantic RAG — CLOSED

Verified model:
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- dimensions: `384`
- persistent Chroma collections

Verified:
- semantic model load
- persistent semantic index
- Korean retrieval
- English retrieval
- intended-source Top-K
- constrained Firebat runtime
- graceful local-LLM unavailable fallback
- restart persistence

## Controlled Tool Execution — CLOSED

Verified:
- deterministic Tool Registry
- read-only allowlist
- proof tool `legacy_db_lookup`
- strict `record_id` contract
- approval gate
- per-run allowed-tools gate
- approved execution persistence
- reject / no approval / unregistered / unauthorized / invalid-parameter blocking

Boundary:
- LLM does **not** directly invoke tools.
- no SQL/write/customer production integration was added.

## Operator UI — CLOSED

Verified:
- dependency-free FastAPI-served Operator Workspace
- clarification rendering
- answer/citations/tool plan
- approve/reject controls
- execution result
- actual headless Chrome Golden Path
- persisted run reload

## Audit Trail — CLOSED

Verified:
- append-only `RunAuditEvent`
- deterministic per-run sequence
- lifecycle coverage including `RAG_RETRIEVED`
- `GET /api/agents/runs/{run_id}/events`
- persisted Operator audit timeline
- Chrome rendered-order == fresh persisted reload order

## Evaluation — CLOSED

Fixed suite:
- **22 cases total**
- retrieval: **8/8 PASS**
- grounding/citation: **4/4 PASS**
- routing/policy: **4/4 PASS**
- tool control: **6/6 PASS**
- aggregate: **22/22 PASS**

Important evidence:
- Proof Evaluation run id `32177070127`
- tested PR head `40033b966994dc06332cf858d1b4a781a1168347`
- artifact `guided-agent-proof-eval`
- artifact id `9339491975`
- artifact digest `sha256:ab24f530331d9e90dda4ff4fad552f8e36a3735dbd924e1365002f7819f3935b`
- machine-readable result `proof-eval-results.json`
- runtime sample `204.3MiB / 1.5GiB`, CPU `0.12%`

The first real suite execution was 21/22. `R03` exposed a real retrieval miss (rank 5). The expectation was not weakened; the approved-tools knowledge document was clarified, and the rerun placed it rank 1 for final 22/22 PASS.

Grounding boundary:
- citation/source checks passed 4/4.
- GitHub Firebat CI had no reachable local LLM, so these cases exercised the documented unavailable-model fallback.
- no positive local-LLM inference is claimed from this evidence.

## External Proof Packaging — P6-A CLOSED

Verified on `main`:
- `README.md` reflects the proven P1–P5 architecture.
- README includes Golden Path, architecture, safety boundary, 22/22 evaluation summary/evidence, known limitations, API surface, and Docker Compose reproduction guidance.
- `docs/PROJECT_STATUS.md` and `docs/ROADMAP.md` delegate authority to this Master.
- GitHub Issue #4 is closed for the frozen Proof scope.

## Local LLM Closure Decision — P6-B CLOSED

Existing runtime contract inspected:
- `app/services/local_llm.py` uses an OpenAI-compatible HTTP client with default `http://localhost:11434/v1` and `qwen2.5:7b-instruct`.
- `.env.firebat.example` configures the container to use `http://host.docker.internal:11434/v1` with no cloud API key.
- `compose.firebat.yml` only forwards that existing host endpoint into the app; it does **not** provision an LLM service.
- GitHub `Firebat Container` runs on `ubuntu-24.04`, copies `.env.firebat.example`, and explicitly validates `model.available is False` as the graceful fallback path.

Closure decision:
- the current execution/CI environment does not provide a reachable local OpenAI-compatible LLM endpoint.
- bringing up Ollama/Qwen or adding a cloud provider solely for this final evidence would introduce a new runtime/provider dependency and expand the frozen Proof scope.
- therefore P6-B uses the Master-authorized **explicit closure decision** path.
- positive final-stack local-LLM inference remains **NOT VERIFIED / NOT CLAIMED**.
- this is accepted for Proof v1.0 because the positive path is optional against an explicit closure decision, while semantic retrieval, grounding/citation structure, fallback behavior, control boundaries, browser flow, and fixed evaluation evidence are already proven independently.

---

# 4. Implemented / Missing Matrix

| Capability | State | Proof v1.0 |
|---|---|---|
| FastAPI backend | VERIFIED | ACCEPTABLE |
| Validation / clarification | VERIFIED | ACCEPTABLE |
| Normalization | VERIFIED | ACCEPTABLE |
| Run persistence | VERIFIED | ACCEPTABLE |
| LangGraph controlled path | VERIFIED | ACCEPTABLE |
| Chroma persistence | VERIFIED | ACCEPTABLE |
| Real semantic model | VERIFIED | ACCEPTABLE |
| Korean / English retrieval | VERIFIED | ACCEPTABLE |
| Intended-source Top-K | **8/8 FIXED EVAL PASS** | ACCEPTABLE |
| Citation metadata/source | **4/4 FIXED EVAL PASS** | ACCEPTABLE |
| Local LLM unavailable fallback | VERIFIED | ACCEPTABLE |
| Positive local-LLM final-stack inference | **NOT VERIFIED — EXPLICIT P6-B CLOSURE DECISION** | ACCEPTABLE WITH NON-CLAIM |
| Tool planning / routing | **4/4 FIXED EVAL PASS** | ACCEPTABLE |
| Human review routing | VERIFIED | ACCEPTABLE |
| Tool Registry / allowlist | VERIFIED | ACCEPTABLE |
| Read-only execution/control blocks | **6/6 FIXED EVAL PASS** | ACCEPTABLE |
| Operator browser Golden Path | VERIFIED | ACCEPTABLE |
| Persistent audit timeline | VERIFIED | ACCEPTABLE |
| Fixed evaluation evidence | **22/22 PASS** | ACCEPTABLE |
| External-facing Proof docs | **SYNCHRONIZED** | ACCEPTABLE |
| Final deployment/regression after P6 | OPEN | REQUIRED |

---

# 5. Current Limitations / Risks

| ID | Risk | Severity | Status |
|---|---|---:|---|
| L-01 | BGE-M3 unstable under frozen 1536 MiB envelope | HIGH | RESOLVED FOR PROOF WITH MINILM |
| L-02 | Approval 이후 real controlled execution 없음 | HIGH | CLOSED |
| L-03 | Swagger-only UX | HIGH | CLOSED |
| L-04 | Full lifecycle persistent audit timeline 없음 | MEDIUM | CLOSED |
| L-05 | Fixed retrieval/grounding/control quality evidence 없음 | MEDIUM | CLOSED — 22/22 PASS |
| L-06 | README / PROJECT_STATUS / ROADMAP / Issue drift | MEDIUM | CLOSED — P6-A |
| L-09 | CPU-oriented image still resolves large CUDA/NVIDIA Torch dependencies | MEDIUM | OPEN — DEFER UNLESS BLOCKING |
| L-11 | Semantic provider identifier remains legacy `bge_m3` while model metadata is MiniLM | LOW | OPEN — DOCUMENTED IN README |
| L-12 | Positive local-LLM inference not freshly verified with final semantic model | MEDIUM | **ACCEPTED — P6-B EXPLICIT CLOSURE DECISION; DO NOT CLAIM POSITIVE INFERENCE** |
| L-13 | P2 execution uses deterministic local fixture, not customer integration | LOW | ACCEPTED BY FROZEN SCOPE |
| L-14 | Execution result shares `raw_llm_output` instead of dedicated execution table | MEDIUM | ACCEPTED FOR PROOF |
| L-17 | Browser CI depends on GitHub runner Chrome + Selenium | LOW | ACCEPTABLE FOR PROOF |
| L-19 | Audit append helper is API-boundary helper rather than standalone service | LOW | ACCEPTABLE FOR PROOF |

---

# 6. Evidence Registry

| ID | Phase | Evidence | Status |
|---|---|---|---|
| E-001 | Baseline | authoritative baseline inspection | PASS |
| E-101 | RAG | semantic provider + MiniLM metadata | PASS |
| E-109 | RAG | Korean intended-source semantic Top-K | PASS |
| E-110 | RAG | English intended-source semantic Top-K | PASS |
| E-112 | RAG | semantic/fallback/persistence/restart workflow | PASS |
| E-201 | Execution | approved `legacy_db_lookup` + persisted result | PASS |
| E-202 | Execution | reject/unregistered/unauthorized blocks | PASS |
| E-203 | Execution | no-approval/invalid-parameter blocks | PASS |
| E-306 | UI | real Chrome Golden Path | PASS |
| E-307 | UI | persisted run reload after browser approval | PASS |
| E-401 | Audit | append-only event model + deterministic sequence | PASS |
| E-408 | Audit | persisted Operator timeline + Chrome proof | PASS |
| E-501 | Eval | fixed 22-case dataset | PASS |
| E-502 | Eval | deterministic evaluator + JSON schema | PASS |
| E-506 | Eval | first real suite execution: 21/22, `R03` rank 5 | PRESENT — FAILURE DISCOVERED |
| E-507 | Eval | targeted approved-tools corpus clarification; expectations unchanged | PRESENT |
| E-508 | Eval | Proof Evaluation run #2: **22/22 PASS** | PASS |
| E-509 | Eval | `proof-eval-results.json`, artifact `9339491975`, fixed digest | PRESENT |
| E-510 | Eval | PR #16 PR Validation run #43 | PASS |
| E-511 | Eval | PR #16 Firebat Container run #42 | PASS |
| E-512 | Eval | PR #16 squash merge `8498183f584332887a38ae5e925e6b810177e99b` | PRESENT |
| E-601 | Packaging | README re-read after Proof synchronization | PASS — P6-A |
| E-602 | Packaging | PROJECT_STATUS / ROADMAP deprecated to Master | PASS — P6-A |
| E-603 | Packaging | Issue #4 closed `completed` with frozen-scope boundary | PASS — P6-A |
| E-604 | LLM | existing local-LLM client/env/compose/CI path inspected; no reachable endpoint in current execution/CI environment; explicit non-claim closure decision recorded | **PASS — P6-B DECISION** |
| E-605 | Deploy | fresh final deployment/regression after packaging | TODO — P6-C |

---

# 7. Validation Rule

각 iteration 종료 시 반드시 기록한다.

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

# 8. Phase Status / Closure Contracts

## Phase 1 — Real Semantic RAG
**CLOSED**

## Phase 2 — Controlled Tool Execution
**CLOSED**

## Phase 3 — Operator UI
**CLOSED**

## Phase 4 — Audit Trail
**CLOSED**

## Phase 5 — Evaluation
**CLOSED**

Closure basis:
- fixed 22-case dataset
- repeatable evaluator
- machine-readable artifact
- actual constrained-runtime execution
- first failure reviewed rather than hidden
- implementation/content defect fixed without weakening case contract
- final 22/22 PASS

## Phase 6 — Proof Packaging / Final Closure
**IN PROGRESS**

### P6-A — External-facing Proof synchronization
**CLOSED**

### P6-B — Positive local-LLM closure decision
**CLOSED — EXPLICIT CLOSURE DECISION**

Decision basis:
1. existing app contract expects an already-running OpenAI-compatible local endpoint.
2. Firebat config uses `host.docker.internal:11434/v1`; the compose stack does not provision Ollama/Qwen.
3. GitHub CI has no such reachable service and intentionally proves graceful fallback instead.
4. adding a new LLM runtime/provider solely for closure would expand frozen Proof scope.
5. therefore positive inference is not claimed; the missing positive runtime evidence is accepted as a documented Proof limitation.

### P6-C — Final deployment/regression
**NEXT**

Required:
- fresh final container/deployment regression on current `main`
- health/database/RAG ready
- semantic model/index + bilingual retrieval remain intact
- browser Golden Path remains intact
- restart/persistence remains intact
- fixed evaluation remains green where applicable
- no documentation-to-runtime contradiction found

---

# 9. Current Work Status

## Done Enough to Use

**YES for the frozen Proof path.**

A user can complete the browser Golden Path, approval-gated read-only execution, persisted result, and audit timeline. The fixed quality/control suite is 22/22 PASS and the external README describes that state accurately.

## Not Yet Closure-Complete

- **P6-C fresh final deployment/regression evidence only**

---

# 10. Current Priority

## NOW

**Phase 6 / P6-C — final deployment/regression**

Smallest next action:
1. read this Master first and re-check `main`.
2. run the existing final Firebat/container regression path without adding new product scope.
3. verify health/database/RAG ready, semantic index/model metadata, bilingual retrieval, Operator browser Golden Path, and restart/persistence.
4. rerun or inspect the fixed evaluation gate as appropriate for the final current `main` state.
5. record exact executed evidence and any failures.
6. if all required final gates pass, synchronize final closure status in this Master and declare `GUIDED AGENT OS PROOF v1.0 CLOSED`.

---

# 11. Work Log

## 2026-08-18 — Phase 0 Baseline Freeze
**Status:** CLOSED

Changed: authoritative baseline/matrix/scope/evidence/risk contract frozen.
Executed: repository/workflow/RAG/tool/CI/docs/Issue inspection.
Not Verified: fresh runtime tests at baseline stage.
Remaining Risks: carried into phase contracts.

## 2026-08-18 — Phase 1 Real Semantic RAG
**Status:** CLOSED

Changed: semantic provider boundary + multilingual MiniLM path + persistent semantic index proof gates.
Executed: PR validation, Firebat regression, Korean/English intended-source retrieval, restart/persistence.
Not Verified: positive final local-LLM inference.
Remaining Risks: CPU dependency footprint, legacy provider label.

## 2026-08-18 — Phase 2 Controlled Read-only Execution
**Status:** CLOSED

Changed: registry/allowlist, `legacy_db_lookup`, validation, approval executor, persisted execution result and block-path tests.
Executed: PR validation + Firebat PASS.
Not Verified: real customer systems; positive local-LLM inference.
Remaining Risks: fixture proves control architecture, not customer integration performance.

## 2026-08-18 — Phase 3 Operator UI
**Status:** CLOSED

Changed: FastAPI workspace, clarification rendering, approval/result UX, Chrome proof harness.
Executed: PR checks PASS; Chrome Golden Path and persisted reload PASS.
Not Verified: positive local-LLM final-stack inference.
Remaining Risks: browser test dependency accepted for proof.

## 2026-08-19 — Phase 4 Audit Trail
**Status:** CLOSED

Changed: append-only audit model, frozen event coverage, persisted Operator timeline.
Executed: validation, Firebat, Chrome persisted-timeline proof.
Not Verified: positive local-LLM inference.
Remaining Risks: deterministic sequence is ordering authority.

## 2026-08-19 — Phase 5 Evaluation
**Status:** CLOSED

Changed: fixed Proof Evaluation workflow and targeted approved-tools corpus clarification after real `R03` failure.
Executed: first suite 21/22; rerun 22/22; PR Validation PASS; Firebat Container PASS.
Not Verified: positive local-LLM inference.
Remaining Risks: fallback-only grounding environment remains explicitly separated from positive inference.

## 2026-08-19 — Phase 6 / P6-A External Proof Synchronization
**Status:** CLOSED

### Changed
- synchronized README to verified P1–P5 Proof state.
- deprecated stale PROJECT_STATUS / ROADMAP authority to this Master.
- closed Issue #4 for frozen Proof scope.
- no application code/runtime configuration changed.

### Executed
- Master-first repository inspection.
- README / stale docs / Issue / compose / env re-read and synchronization verification.

### Not Verified
- no new runtime regression in this documentation-only iteration.
- positive local-LLM inference remained unverified.

### Remaining Risks
- P6-B decision and P6-C final regression remained.

## 2026-08-19 — Phase 6 / P6-B Local LLM Closure Decision
**Status:** CLOSED — EXPLICIT DECISION

### Changed
- updated this Master only.
- converted L-12 from an open final blocker to an accepted explicit non-claim limitation.
- unblocked P6-C final deployment/regression.
- no application code, dependency, compose configuration, workflow, or README changed.

### Executed
- read this Master first from `main`.
- verified pre-change `main` head `cb0cf3b4109531a8f01c612511b11434464621f9`.
- inspected `app/services/local_llm.py` and confirmed the existing OpenAI-compatible HTTP client contract.
- inspected `.env.firebat.example` and confirmed `LOCAL_LLM_BASE_URL=http://host.docker.internal:11434/v1`, `LOCAL_LLM_MODEL=qwen2.5:7b-instruct`, and no cloud API key dependency.
- inspected `compose.firebat.yml` and confirmed the application container references the host endpoint but does not provision an LLM runtime.
- inspected `.github/workflows/firebat-container.yml` and confirmed the GitHub-hosted `ubuntu-24.04` workflow intentionally verifies graceful unavailability (`model.available is False`) rather than positive inference.

### Not Verified
- positive local-LLM final-stack inference was **not** executed because no reachable local endpoint exists in the current execution/CI path.
- no pytest, image build, container runtime, browser execution, or deployment regression was executed in this decision-only iteration.
- no claim is made that `qwen2.5:7b-instruct` has produced a final-stack answer.

### Remaining Risks
- L-12 remains a documented non-claim: positive local-LLM inference has not been freshly proven.
- L-09 large Torch/CUDA dependency footprint remains deferred unless it blocks P6-C.
- L-11 legacy `bge_m3` provider label remains documented.
- P6-C fresh final deployment/regression is the sole remaining closure task.

### Decision
**P6-B CLOSED via explicit closure decision.** Provisioning a new Ollama/Qwen service or cloud provider only to manufacture final positive inference evidence would expand the frozen Proof scope. Existing fallback evidence remains distinct from positive inference.

### Next Action
**P6-C — run the existing final deployment/regression path on current `main`; if required gates pass, close Proof v1.0.**

---

# 12. Final Closure Definition

다음 질문에 모두 **YES**일 때만 `GUIDED AGENT OS PROOF v1.0 CLOSED`를 선언한다.

- 실제 사용자가 browser에서 Agent에게 업무를 요청할 수 있는가? **YES**
- 실제 내부 문서를 semantic search할 수 있는가? **YES**
- 근거/citation이 검증되는가? **YES — fixed suite 4/4 citation checks**
- Tool이 필요할 때 controlled plan을 만드는가? **YES**
- 민감 작업은 human approval을 요구하는가? **YES**
- 승인된 제한 read-only tool이 실제 실행되는가? **YES**
- reject/unauthorized/invalid action은 차단되는가? **YES**
- 과정이 저장되고 UI에서 추적 가능한가? **YES**
- automated tests + fixed evaluation으로 검증되는가? **YES — 22/22 PASS**
- 외부 사람이 README/Evidence만 보고 현재 Proof를 이해할 수 있는가? **YES — P6-A**
- positive local-LLM final-stack inference 또는 명시적 closure decision이 있는가? **YES — P6-B explicit closure decision; positive inference NOT CLAIMED**
- final deployment/regression evidence가 있는가? **OPEN — P6-C**

그 이후 기능은 Proof v1.1 또는 실제 고객 요구사항으로 분리한다.
