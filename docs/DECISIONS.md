# Architectural Decisions

Key decisions recorded here. Each entry states what was decided, why, and what it rules out.

---

## One repo, multiple agent templates

**Decision:** All agent templates share a single repository and core codebase.

**Why:** Avoids duplication of infrastructure (routing, persistence, workflow engine, testing harness). New templates add schemas and template config files; they do not fork the repo.

**Rules out:** Separate repos per agent type.

---

## Guided forms over prompt-first UX

**Decision:** Users should provide context through structured forms rather than being expected to write high-quality prompts.

**Why:** The product value is in guiding non-expert users toward useful AI outputs through validation, clarification, normalization, and structured workflow steps.

**Rules out:** Treating the project as a generic chatbot where output quality depends mainly on user prompt skill.

---

## Template configuration over backend rewrites

**Decision:** New agents should be added primarily through templates, schemas, prompts, structured output contracts, and workflow configuration.

**Why:** The platform should prove reusable orchestration value. A new use-case should not require rebuilding the backend or duplicating the workflow engine.

**Rules out:** Hardcoding each new agent as a separate bespoke service.

---

## Phase-based implementation

**Decision:** Phases are implemented sequentially; no phase starts until the previous is complete and tested.

**Why:** Keeps blast radius small, prevents untested code from accumulating, and ensures each layer of the system is solid before the next is built on top of it.

**Rules out:** Implementing scoring or LLM analysis before validation and persistence are stable.

---

## Validation before LLM

**Decision:** The workflow validates required fields and returns early (`needs_clarification`) before any LLM call is made.

**Why:** LLM calls cost money and time. Running them on incomplete or malformed input wastes resources and produces poor results. Users should be asked for missing fields first.

**Rules out:** Calling the LLM optimistically and discarding results if input was incomplete.

---

## Persistence before LLM

**Decision:** Agent runs are persisted to SQLite before LLM analysis is added.

**Why:** Ensures a reliable audit trail exists before adding the most complex and failure-prone component. Also allows runs to be inspected and debugged independently of LLM availability.

**Rules out:** Storing only LLM-completed runs.

---

## Normalization before LLM

**Decision:** Deterministic normalization runs before LLM analysis. The LLM receives clean, structured input.

**Why:** Trimmed whitespace, detected keywords, and inferred categories reduce prompt noise and improve analysis consistency. Normalization is cheap, deterministic, and testable without an LLM.

**Rules out:** Passing raw user input directly to the LLM without preprocessing.

---

## Original intake_data must be preserved

**Decision:** `intake_data` stored in the database is the unmodified original payload. Normalization writes to `normalized_data` only.

**Why:** The original submission is the source of truth. If normalization logic changes or produces incorrect output, the original is always available to reprocess. Required for audit.

**Rules out:** Overwriting or mutating `intake_data` with cleaned values.

---

## Derived artifacts stored separately

**Decision:** Every artifact derived from intake (`normalized_data`, `analysis_summary`, `score`, etc.) is stored in its own named column, not merged back into `intake_data`.

**Why:** Separation makes provenance clear. Each field can be updated, regenerated, or debugged independently without touching the source.

**Rules out:** Accumulating all data into a single JSON blob column.

---

## Traceability is a product requirement

**Decision:** Every run should preserve a trace from original intake through normalized data, future analysis output, future drafts, approval state, and archive records.

**Why:** Traceability supports debugging, user trust, reuse, and portfolio value as an agent orchestration system.

**Rules out:** Ephemeral AI outputs that cannot be inspected or tied back to their source intake.

---

## Cost-aware model routing is planned, not current

**Decision:** Model routing should eventually choose models based on task complexity, cost, and reliability needs.

**Why:** A reusable agent OS should avoid spending expensive model calls on routine steps that deterministic logic or lower-cost models can handle.

**Rules out:** Treating every future AI step as requiring the most expensive available model.

---

## No external actions in the current roadmap

**Decision:** The system must not send emails, submit applications, post to external services, or take any irreversible external action. The planned approval phase records an internal human decision only unless the project owner explicitly scopes a later external-action phase.

**Why:** Automated external actions on behalf of a user without confirmation are a critical trust and safety boundary.

**Rules out:** Automatically sending a draft proposal after generation, or treating approval as permission to contact external accounts.

---

## Haiku writes, Codex reviews and fixes

**Decision:** Haiku handles routine implementation. Codex reviews and fixes correctness bugs. Sonnet is used for architecture and documentation decisions.

**Why:** Matches model cost to task complexity. Avoids over-engineering by reserving expensive models for genuinely hard problems.

**Rules out:** Using Sonnet for adding a new validation rule or writing a test.

---

## Full Copilot access acceptable when blast radius is low

**Decision:** Full Copilot (e.g. Sonnet in agent mode) may be used directly for low-risk tasks where the worst case is a bad file edit that can be reverted.

**Why:** Pragmatic tradeoff. Overhead of review pipelines is not justified for trivial or easily reversible changes.

**Rules out:** Requiring multi-step review for a one-line documentation fix.

---

## Docs-only changes may go to main; code changes use branch + PR

**Decision:** In early solo development, documentation-only commits may be pushed directly to `main`. Any change to application code or tests must use a branch and go through review.

**Why:** Reduces friction for documentation work while protecting the executable codebase from unreviewed changes.

**Rules out:** Pushing code changes directly to `main`.
