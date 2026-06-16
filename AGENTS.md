# Guided Agent OS — Agent Guidelines

## Project Identity

Guided Agent OS is a **reusable Guided Intake Agent Platform**.

It is not a single hardcoded freelance agent. The first deployed template is the Freelance Opportunity Agent, but the platform is designed so that future agent templates (job search, contract review, RFP evaluation, etc.) can be added without restructuring the core.

The core principle: users should not need to write perfect prompts. The current system collects structured form input, validates required fields, asks clarification questions when information is missing, normalizes validated input, and persists runs. Future phases may add LLM analysis, scoring, action drafting, and human approval without requiring users to write perfect prompts.

Long-term, this project should read as an AI Agent orchestration platform, not a simple chatbot. Emphasize guided intake, reusable workflow engine, structured output, stateful workflow, model routing, human-in-the-loop review, safety boundaries, agent template extensibility, and cost-aware AI development.

Future agents should be added primarily through templates, schemas, prompts, and workflow configuration with minimal new backend code. Candidate future templates include AI Content Agent, Duru SKU & Marketing Agent, Personal Command Center Agent, AI Market Watch Agent, and additional guided intake agents.

---

## Phase-Based Development Policy

Development follows a strict phase-based approach. Each phase has a defined goal and must be fully complete and tested before the next phase begins.

**Do not implement future phases early.** If a phase is listed as planned, its code must not execute. Skeleton functions, nodes, schemas, columns, or routes may exist, but they must not be wired into active behavior.

If a task description requests work that belongs to a future phase, stop and flag it rather than implementing it.

Current active phases as of 2026-06-14:

- **Phase 1:** required-field validation and clarification questions
- **Phase 2-A:** SQLite persistence for agent runs
- **Phase 2-B:** deterministic normalization for validated freelance intake

Future-phase functions, columns, schemas, or guarded routes may exist as scaffolding. Treat them as inactive unless the compiled workflow, route behavior, and tests show that phase is intentionally wired.

---

## Forbidden Actions

The following must never be implemented unless explicitly and specifically requested by the project owner:

- Automatic email sending
- Automatic job applications
- Payments or billing integrations
- Web crawling or scraping
- Authentication or user account management
- Any external account actions (posting, submitting, contacting)
- Destructive file operations (deleting user data, purging records)
- Complex RAG (retrieval-augmented generation) pipelines
- Multi-agent orchestration beyond the current single-agent workflow
- Production deployment automation

---

## Model Workflow

| Role | Responsibility |
|------|----------------|
| **Haiku** | Routine implementation: adding nodes, writing services, extending schemas, writing tests |
| **Codex** | Review and fix must-fix issues: correctness bugs, broken tests, API contract violations |
| **Sonnet** | Architecture decisions, documentation, complex design problems |

Haiku should handle the majority of implementation work. Codex reviews are for catching errors, not rewriting working code.

---

## Testing Expectations

Before any review or merge, all of the following must pass:

```bash
python -m pytest tests
python -m unittest discover -s tests
python -m compileall app tests
git diff --check
```

No test should be skipped or marked xfail without a documented reason.

---

## Review Checklist

Each review comment or PR description must include:

1. **Changes made** — what was added, modified, or removed
2. **Tests run** — which test commands were executed and their results
3. **Remaining concerns** — open questions, known gaps, or items deferred to a future phase
4. **Merge readiness** — explicit statement of whether the change is ready to merge

---

## Scope Discipline

- Do not add dependencies that are not required by the current phase.
- Do not add features that are not required by the current phase.
- Do not modify application code while working on documentation tasks.
- Do not modify documentation while working on application code tasks (unless the task explicitly includes both).
