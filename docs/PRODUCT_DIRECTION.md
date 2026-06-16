# Product Direction

Guided Agent OS should become a reusable **Form-driven AI Agent OS**.

The final goal is not to build one freelance agent. The final goal is to build a reusable platform where new agents can be added through templates, schemas, prompts, and workflow configuration with minimal new code.

---

## Long-Term Product Direction

Users should not need to know how to write good prompts. Guided Agent OS should guide users through structured forms, validate required information before using AI, ask clarification questions when context is missing, normalize and structure user input, run LLM analysis with structured output, generate practical action drafts, require human approval before any real external action, and archive every run for traceability and reuse.

This is a target direction, not a statement that all capabilities are implemented today. The current active workflow implements validation, clarification, persistence, and deterministic normalization only.

---

## First Use-Case

The **Freelance Opportunity Agent** is the first proof-of-concept.

It will validate the platform by analyzing freelance opportunities, matching them against user strengths, identifying risks, and eventually generating proposal drafts. Today it validates, clarifies, persists, and normalizes freelance intake data; LLM analysis, scoring, and proposal drafts remain planned phases.

---

## Future Use-Cases

- AI Content Agent
- Duru SKU & Marketing Agent
- Personal Command Center Agent
- AI Market Watch Agent
- Additional guided intake agents

Each future use-case should reuse the same intake, validation, workflow, and persistence foundations, plus human-review foundations once that phase exists, instead of requiring a new backend.

---

## Success Criteria

Guided Agent OS is successful if:

1. A non-expert user can produce useful AI outputs by filling out forms instead of writing complex prompts.
2. The platform can add new agent types without rewriting the whole backend.
3. Every agent run is traceable through stored input, normalized data, analysis output, drafts, approval status, and archive records.
4. External actions are never executed without explicit human approval.
5. The system demonstrates real portfolio value as an AI Agent orchestration project, not a simple chatbot.

---

## Strategic Positioning

This project should be documented and developed as an AI Agent orchestration platform. It should emphasize:

- guided intake
- reusable workflow engine
- structured output
- stateful workflow
- model routing
- human-in-the-loop
- safety boundaries
- agent template extensibility
- cost-aware AI development

Model routing, LLM structured output, draft generation, approval state, and archival records are strategic platform capabilities to phase in deliberately. They should not be described as active behavior until they are wired into the workflow and covered by tests.
