"""
Controlled RAG Agent template.

This template represents an enterprise AI Agent workflow where user requests
are validated, clarified, normalized, processed through multi-collection RAG,
grounded with a local LLM, and checked for tool/API execution planning.

The LLM does not directly execute SQL, APIs, or tools. It generates grounded
answers and planned execution steps, which are routed to human review if needed.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Template configuration
# ---------------------------------------------------------------------------

AGENT_TYPE = "controlled_rag_agent"

DISPLAY_NAME = "Controlled RAG Agent"

DESCRIPTION = (
    "A controlled AI agent workflow for enterprise scenarios. "
    "Validates user requests, retrieves from multi-collection RAG, "
    "generates grounded answers using local LLM, plans tool/API execution, "
    "and routes sensitive actions to human review. The LLM does not directly "
    "execute SQL, tools, or APIs."
)

# Fields the user MUST provide for Phase 1 validation.
REQUIRED_FIELDS: list[str] = [
    "user_request",
    "business_context",
    "data_sources",
    "expected_output",
    "risk_level",
]

# Fields that enrich the analysis but are not strictly required.
OPTIONAL_FIELDS: list[str] = [
    "user_role",
    "allowed_tools",
    "approval_required",
    "security_constraints",
]

# Maps each field name to the clarification question shown to the user when
# that field is missing.
CLARIFICATION_MAP: dict[str, str] = {
    "user_request": (
        "What is your specific request or question? "
        "Please provide context about what you need to accomplish."
    ),
    "business_context": (
        "What is the business context for this request? "
        "Who is making the request and why?"
    ),
    "expected_output": (
        "What output or result do you expect from this request? "
        "Describe the ideal response."
    ),
    "data_sources": (
        "Which data sources should be used? "
        "(e.g., domain_knowledge, agent_policy, tool_catalog)"
    ),
    "risk_level": (
        "What is the risk level? "
        "(e.g., low, medium, internal, restricted, high)"
    ),
    "user_role": (
        "What is the role of the user making this request? "
        "(e.g., analyst, operator, admin)"
    ),
    "allowed_tools": (
        "Which tools or integrations are allowed for this request? "
        "List them or leave blank for auto-detection."
    ),
    "approval_required": (
        "Is human approval required before execution? "
        "(yes/no)"
    ),
    "security_constraints": (
        "Are there any security constraints or compliance requirements?"
    ),
}

# Prompt template for future LLM-based grounding (not used in Phase 3 planning)
ANALYSIS_PROMPT_TEMPLATE = """\
You are a controlled Guided Agent OS assistant for enterprise use. \
Your role is to analyze and respond to user requests using ONLY the \
local retrieved knowledge base context provided to you.

CRITICAL RULES:
1. Answer ONLY using the retrieved knowledge base context.
2. Do NOT invent policies, database facts, APIs, tools, or capabilities.
3. Do NOT execute SQL, call external APIs, or trigger tools directly.
4. If the context is insufficient, clearly state this.
5. If the request suggests tool/API execution, note that a planned execution step \
will be generated, not executed directly.

=== USER REQUEST ===
{intake_text}

=== INSTRUCTION ===
Based ONLY on the retrieved knowledge base context, answer the above request. \
If the context is insufficient, clearly state so.
"""
