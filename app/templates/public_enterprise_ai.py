"""
Public Enterprise AI Agent template.

This template adapts the generic Guided Intake Agent Platform to public-sector
or enterprise AI-agent discovery work. It focuses on collecting the minimum
structured information needed before designing a safe internal AI agent:

- business/domain context
- user group and workflow target
- data sources and legacy systems
- expected agent capabilities
- security, approval, and audit constraints

The goal is not to let an agent execute actions automatically. The goal is to
turn an ambiguous enterprise AI request into a validated, reviewable intake
record that can later drive RAG design, API/tool scoping, and human approval.
"""

AGENT_TYPE = "public_enterprise_ai"

REQUIRED_FIELDS = [
    "use_case_title",
    "business_domain",
    "target_user_group",
    "current_workflow_problem",
    "data_sources",
    "expected_agent_capabilities",
]

OPTIONAL_FIELDS = [
    "legacy_systems",
    "rag_document_types",
    "db_access_pattern",
    "llm_environment",
    "security_constraints",
    "approval_policy",
    "audit_requirements",
    "integration_constraints",
    "success_metrics",
    "out_of_scope_actions",
]

CLARIFICATION_MAP = {
    "use_case_title": "What is the short name of the internal AI-agent use case?",
    "business_domain": "Which business domain does this agent support, such as energy, infrastructure, safety, customer service, or internal operations?",
    "target_user_group": "Who will use this agent inside the organization? Please specify department, role, or user group.",
    "current_workflow_problem": "What manual, repetitive, or knowledge-heavy workflow should this agent improve?",
    "data_sources": "Which internal data sources should the agent use, such as documents, manuals, databases, logs, or legacy systems?",
    "expected_agent_capabilities": "What should the agent be able to do? For example: answer policy questions, retrieve facility data, summarize reports, analyze incidents, or draft action recommendations.",
}

ANALYSIS_PROMPT_TEMPLATE = """
You are an enterprise AI solution analyst.

Analyze the validated intake for a public-sector or enterprise AI-agent project.
Focus on safe system integration, not unrestricted autonomous execution.

Return a structured analysis covering:
1. Core business workflow
2. Candidate RAG scope
3. Candidate backend API/tool scope
4. Legacy-system and database integration risks
5. Authorization, audit-log, and approval requirements
6. Questions that must be resolved before implementation

Validated intake:
{normalized_data}
""".strip()

DRAFT_ACTION_TEMPLATES = [
    {
        "action_type": "requirements_review",
        "title": "Prepare AI-agent requirements gap review",
        "content": "Summarize missing business, data, security, and integration details before implementation starts.",
    },
    {
        "action_type": "rag_scope_draft",
        "title": "Draft controlled RAG scope",
        "content": "List candidate document collections, metadata filters, citation requirements, and access-control boundaries.",
    },
    {
        "action_type": "tool_scope_draft",
        "title": "Draft backend API/tool scope",
        "content": "Identify which legacy-system queries should be exposed through approved APIs or query templates instead of direct LLM-generated SQL.",
    },
    {
        "action_type": "human_approval_plan",
        "title": "Define human approval checkpoints",
        "content": "Define which outputs are informational only and which actions require explicit human approval before execution.",
    },
]
