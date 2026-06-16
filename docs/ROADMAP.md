# Roadmap

Phases are implemented sequentially. A phase must be complete and passing before the next begins.

Planned phases below describe target behavior only. They are not implemented until their code is wired into the active workflow, covered by tests, and documented as current behavior.

The destination is a reusable Form-driven AI Agent OS: users fill out guided forms, the platform validates and normalizes context, the workflow runs structured AI analysis when appropriate, and every run remains traceable. See [PRODUCT_DIRECTION.md](PRODUCT_DIRECTION.md) for the strategic direction.

---

## Phase 1 — Validation and Clarification

**Status:** ✅ Complete

**Goal:** Accept structured intake data, validate required fields, and return clarification questions if any are missing.

**Expected output:**
- `status = "needs_clarification"` with `clarification_questions` if required fields are absent
- `status = "validated"` if all required fields are present

**Non-goals:** No LLM, no persistence, no normalization, no scoring, no drafting.

---

## Phase 2-A — Agent Run Persistence

**Status:** ✅ Complete

**Goal:** Persist every agent run to SQLite so runs can be retrieved after the fact.

**Expected output:**
- `POST /api/agents/{agent_type}/runs` returns a `run_id` and stores the run
- `GET /api/agents/runs/{run_id}` retrieves the stored run

**Non-goals:** No LLM, no normalization, no scoring, no drafting.

---

## Phase 2-B — Deterministic Input Normalization

**Status:** ✅ Complete

**Goal:** After validation passes, normalize intake data using deterministic rules — trim whitespace, detect technology keywords, infer stack/language/category — and persist alongside the original.

**Expected output:**
- `normalized_data` stored in the agent run record for all `validated` runs
- `needs_clarification` runs produce no `normalized_data`
- Original `intake_data` is preserved unchanged

**Non-goals:** No LLM, no scoring, no drafting, no approval workflow, no external actions.

---

## Phase 3-A — LLM Structured Analysis

**Status:** Planned

**Goal:** Feed `normalized_data` into an LLM prompt and store a structured analysis result.

**Expected output:**
- `analysis_summary` (string) stored in the agent run
- `raw_llm_output` (JSON) stored for debugging and auditability
- Run status transitions to `"analyzed"`

**Non-goals:** No scoring, no drafting, no approval workflow, no external actions.

---

## Phase 3-A2 — Model Routing

**Status:** Planned

**Goal:** Choose an appropriate model for analysis based on task complexity, cost, and reliability needs.

**Expected output:**
- Model choice recorded in the run or raw output for auditability
- Low-cost model path available for routine structured analysis
- Clear fallback or error behavior when a configured model is unavailable

**Non-goals:** No scoring, no drafting, no approval workflow, no external actions.

---

## Phase 3-B — Scoring

**Status:** Planned

**Goal:** Derive a numeric opportunity score (0–10) from the LLM analysis output.

**Expected output:**
- `score` (float) stored in the agent run
- Run status transitions to `"scored"`

**Non-goals:** No draft generation, no approval workflow, no external actions.

---

## Phase 3-C — Action Draft Generation

**Status:** Planned

**Goal:** Generate a draft action (e.g. proposal outline, follow-up questions) from the scored analysis.

**Expected output:**
- Draft artifact stored in a related record or field
- Run status transitions to `"draft_ready"`

**Non-goals:** No sending, submitting, posting, crawling, or approval workflow yet.

---

## Phase 4 — Human Approval Workflow

**Status:** Planned

**Goal:** Surface the draft to the user for review and record an internal approve / reject / revise decision.

**Expected output:**
- Run status transitions: `"draft_ready"` → `"pending_approval"` → `"approved"` or `"rejected"`
- Approval records a decision only; it does not send, submit, post, crawl, or contact anyone

**Non-goals:** No automatic sending, submission, posting, crawling, or other external account action.

---

## Phase 5 — Archive / Export

**Status:** Planned

**Goal:** Allow approved or completed runs to be exported or archived for long-term record-keeping.

**Expected output:**
- Export endpoint or file output for completed runs
- Clear audit trail from intake through approval

**Non-goals:** No new analysis or workflow logic.

---

## Future — Additional Agent Templates

**Status:** Planned (no timeline)

**Goal:** Add additional agent templates using the same core platform without restructuring the existing code.

**Expected output:**
- New template registered alongside `freelance`
- Core validation, persistence, normalization, and workflow nodes reused
- Template-specific schemas, prompts, structured outputs, and workflow configuration added with minimal new backend code

**Candidate templates:**
- AI Content Agent
- Duru SKU & Marketing Agent
- Personal Command Center Agent
- AI Market Watch Agent
- Additional guided intake agents

**Non-goals:** Do not redesign the core platform to accommodate a template that does not yet exist.
