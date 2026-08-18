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
| Phase 6 | **NEXT — Proof Packaging + final local-LLM closure decision** |
| Current Level | **L2++++ — functional Proof path and fixed quality suite proven; packaging/final closure remain** |
| Target Level | **L3 — Usable / Demonstrable Proof** |
| Target Release | **Proof v1.0** |
| Final Product Goal | **Deployable Controlled AI Agent Proof** |
| Scope Status | **FROZEN** |
| Overall Status | **IN PROGRESS** |
| Latest verified app/eval merge | `8498183f584332887a38ae5e925e6b810177e99b` |

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
- README / architecture / demo / known limitations / reproduction guide
- final local-LLM positive-path verification or explicit closure decision

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

Durable evidence:
- workflow: **Proof Evaluation run #2**
- run id: `32177070127`
- tested PR head: `40033b966994dc06332cf858d1b4a781a1168347`
- artifact: `guided-agent-proof-eval`
- artifact id: `9339491975`
- artifact digest: `sha256:ab24f530331d9e90dda4ff4fad552f8e36a3735dbd924e1365002f7819f3935b`
- retained machine-readable file: `proof-eval-results.json`
- runtime sample: `204.3MiB / 1.5GiB`, CPU `0.12%`

Important history:
- first real fixed-suite execution returned **21/22 PASS**.
- only failure: `R03`, expected `tools/approved-tools.md` Top-3 but observed rank `5` for `Which tools are approved for controlled agent use?`.
- the expectation was **not weakened**.
- the actual approved-tools knowledge document was minimally clarified to state its controlled-agent purpose explicitly.
- rerun produced `R03` rank `1` and **22/22 PASS**.

Grounding boundary observed in the suite:
- citation structure/source checks passed 4/4.
- GitHub Firebat CI had no reachable local LLM; grounding cases exercised the documented unavailable-model fallback (`model_available=false`) rather than positive inference.
- positive local-LLM inference remains a separate final-closure item, not silently counted as P5 evidence.

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
| Positive local-LLM final-stack inference | OPEN | FINAL CLOSURE ITEM |
| Tool planning / routing | **4/4 FIXED EVAL PASS** | ACCEPTABLE |
| Human review routing | VERIFIED | ACCEPTABLE |
| Tool Registry / allowlist | VERIFIED | ACCEPTABLE |
| Read-only execution/control blocks | **6/6 FIXED EVAL PASS** | ACCEPTABLE |
| Operator browser Golden Path | VERIFIED | ACCEPTABLE |
| Persistent audit timeline | VERIFIED | ACCEPTABLE |
| Fixed evaluation evidence | **22/22 PASS** | ACCEPTABLE |
| Proof packaging | PARTIAL | REQUIRED |

---

# 5. Current Limitations / Risks

| ID | Risk | Severity | Status |
|---|---|---:|---|
| L-01 | BGE-M3 unstable under frozen 1536 MiB envelope | HIGH | RESOLVED FOR PROOF WITH MINILM |
| L-02 | Approval 이후 real controlled execution 없음 | HIGH | CLOSED |
| L-03 | Swagger-only UX | HIGH | CLOSED |
| L-04 | Full lifecycle persistent audit timeline 없음 | MEDIUM | CLOSED |
| L-05 | Fixed retrieval/grounding/control quality evidence 없음 | MEDIUM | **CLOSED — 22/22 PASS** |
| L-06 | README / PROJECT_STATUS / ROADMAP / Issue drift | MEDIUM | **OPEN — P6** |
| L-09 | CPU-oriented image still resolves large CUDA/NVIDIA Torch dependencies | MEDIUM | OPEN — DEFER UNLESS BLOCKING |
| L-11 | Semantic provider identifier remains legacy `bge_m3` while model metadata is MiniLM | LOW | OPEN — DEFER UNLESS CONFUSING PROOF |
| L-12 | Positive local-LLM inference not freshly verified with final semantic model | MEDIUM | **OPEN — FINAL CLOSURE ITEM** |
| L-13 | P2 execution uses deterministic local fixture, not customer integration | LOW | ACCEPTED BY FROZEN SCOPE |
| L-14 | Execution result shares `raw_llm_output` instead of dedicated execution table | MEDIUM | ACCEPTED FOR PROOF |
| L-17 | Browser CI depends on GitHub runner Chrome + Selenium | LOW | ACCEPTABLE FOR PROOF |
| L-19 | Audit append helper is API-boundary helper rather than standalone service | LOW | ACCEPTABLE FOR PROOF |
| L-20 | Fixed eval expectations could reveal real retrieval misses | MEDIUM | **RESOLVED — R03 FOUND/FIXED WITHOUT EXPECTATION WEAKENING** |

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
| E-509 | Eval | `proof-eval-results.json`, artifact `9339491975`, digest `sha256:ab24f530331d9e90dda4ff4fad552f8e36a3735dbd924e1365002f7819f3935b` | PRESENT |
| E-510 | Eval | PR #16 PR Validation run #43 | PASS |
| E-511 | Eval | PR #16 Firebat Container run #42 | PASS |
| E-512 | Eval | PR #16 squash merge `8498183f584332887a38ae5e925e6b810177e99b` | PRESENT |
| E-601 | Deploy | fresh final deployment verification after packaging | TODO — P6 |
| E-602 | LLM | positive final-stack local-LLM inference or explicit closure decision | TODO — P6 |

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

## Phase 6 — Proof Packaging
**NEXT**

Required:
- synchronize README with P1–P5 reality
- architecture / Golden Path diagram
- demo screenshots/evidence pointers
- fixed evaluation summary and artifact evidence
- safety boundary
- known limitations
- reproduction guide
- stale `PROJECT_STATUS.md` / `ROADMAP.md` / Issue #4 synchronization or explicit deprecation
- positive final-stack local-LLM inference **or explicit documented closure decision if the environment cannot provide it without expanding frozen scope**
- fresh final deployment/regression check

---

# 9. Current Work Status

## Done Enough to Use

**YES for the frozen Proof path.**

A user can complete the browser Golden Path, approval-gated read-only execution, persisted result, and audit timeline. The fixed quality/control suite is now 22/22 PASS.

## Not Yet Closure-Complete

- P6 external-facing packaging/document synchronization
- positive local-LLM final-stack verification or explicit closure decision
- final deployment/regression evidence after P6 sync

---

# 10. Current Priority

## NOW

**Phase 6 / P6-A — external-facing Proof synchronization**

Smallest next action:
1. inspect `README.md`, `docs/PROJECT_STATUS.md`, `docs/ROADMAP.md`, and Issue #4 against this Master.
2. update/deprecate only stale statements required for Proof consistency.
3. add concise P1–P5 architecture, Golden Path, evaluation result, safety boundary, evidence pointers, limitations, and reproduction guidance to the main external-facing README.
4. do not add new product features.
5. keep positive local-LLM verification as a distinct closure item; do not count fallback evidence as positive inference.

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
Executed: PR #7/#8 validation, Firebat regression, Korean/English intended-source retrieval, restart/persistence.
Not Verified: broad quality eval; positive final local-LLM inference.
Remaining Risks: CPU dependency footprint, legacy provider label.

## 2026-08-18 — Phase 2 Controlled Read-only Execution
**Status:** CLOSED

Changed: registry/allowlist, `legacy_db_lookup`, validation, approval executor, persisted execution result and block-path tests.
Executed: PR #9 validation + Firebat PASS.
Not Verified: real customer systems; positive local-LLM inference.
Remaining Risks: fixture proves control architecture, not customer integration performance.

## 2026-08-18 — Phase 3 Operator UI
**Status:** CLOSED

Changed: FastAPI workspace, clarification rendering, approval/result UX, Chrome proof harness.
Executed: PR #10/#11 checks PASS; Chrome Golden Path and persisted reload PASS.
Not Verified: positive local-LLM final-stack inference.
Remaining Risks: browser test dependency accepted for proof.

## 2026-08-19 — Phase 4 Audit Trail
**Status:** CLOSED

Changed: append-only audit model, frozen event coverage, persisted Operator timeline.
Executed: PR #12/#13/#14 validation, Firebat, Chrome persisted-timeline proof.
Not Verified: P5 at that stage; positive local-LLM inference.
Remaining Risks: deterministic sequence is ordering authority.

## 2026-08-19 — Phase 5 Evaluation
**Status:** CLOSED

### Changed
- added dedicated `.github/workflows/proof-eval.yml` to execute the existing fixed suite in the Firebat proof environment and retain JSON/runtime diagnostics.
- after first execution exposed only `R03`, minimally clarified `app/knowledge/tools/approved-tools.md` so the document explicitly states that it defines tools approved for controlled agent use.
- **did not change `evaluation/cases.json` or relax `R03` Top-3 expectation.**

### Executed
Baseline verified first:
- Master read first.
- `main` before P5-B: `e884f863db39b717ed018d4abbb676adda65298a`.

First real P5-B run:
- Proof Evaluation run #1 / run id `32176549561`.
- result: **21/22 PASS**.
- retrieval: 7/8; grounding: 4/4; routing: 4/4; tool_control: 6/6.
- only failed ID: `R03`.
- `R03`: expected `tools/approved-tools.md` <= rank 3; observed rank `5`.
- evidence artifact uploaded successfully.

Targeted fix rerun on PR head `40033b966994dc06332cf858d1b4a781a1168347`:
- Proof Evaluation run #2 / run id `32177070127`: **PASS**.
- final result: **22/22 PASS**.
- retrieval 8/8; grounding 4/4; routing 4/4; tool_control 6/6.
- `R03` observed rank improved to `1`.
- artifact `9339491975`, digest `sha256:ab24f530331d9e90dda4ff4fad552f8e36a3735dbd924e1365002f7819f3935b`.
- runtime sample: `204.3MiB / 1.5GiB`, CPU `0.12%`.
- PR Validation run #43: **PASS**.
- Firebat Container run #42: **PASS**.
- PR #16 squash-merged to `main`: `8498183f584332887a38ae5e925e6b810177e99b`.

### Not Verified
- positive local-LLM inference was **not** produced in GitHub Firebat CI; grounding cases used the already-documented unavailable-model fallback.
- P6 README/docs synchronization not yet performed.
- no claim of production/customer-system integration.

### Remaining Risks
- positive local-LLM final-stack inference remains open.
- README/status/roadmap/Issue drift remains until P6.
- CPU dependency footprint and legacy provider identifier remain non-blocking proof risks.

### Decision
**Phase 5 CLOSED.** Real fixed-suite evidence exists and the final committed Proof path is 22/22 PASS without expectation weakening.

### Next Action
**P6-A — synchronize external-facing Proof documentation/evidence with the now-proven P1–P5 state; do not add new features.**

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
- positive local-LLM final-stack inference 또는 명시적 closure decision이 있는가? **OPEN — P6**
- 외부 사람이 README/Demo/Evidence만 보고 확인 가능한가? **OPEN — P6**

그 이후 기능은 Proof v1.1 또는 실제 고객 요구사항으로 분리한다.
