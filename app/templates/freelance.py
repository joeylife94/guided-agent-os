"""
Freelance Opportunity Agent template.

This module defines the agent-specific configuration that the generic
Guided Intake Agent Platform uses when running a 'freelance' agent type.
Keeping agent behaviour here (rather than hard-coding it in the workflow)
makes it straightforward to add new agent types in the future.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Template configuration
# ---------------------------------------------------------------------------

AGENT_TYPE = "freelance"

DISPLAY_NAME = "Freelance Opportunity Evaluator"

DESCRIPTION = (
    "Evaluates a freelance project opportunity by analysing the client, "
    "project scope, budget, timeline, and fit with your skills. "
    "Produces a scored analysis and action drafts (e.g. a short reply and "
    "a full proposal) for human review."
)

# Fields the user MUST provide for a meaningful analysis.
REQUIRED_FIELDS: list[str] = [
    "opportunity_title",
    "client_description",
    "project_description",
]

# Fields that enrich the analysis but are not strictly required.
OPTIONAL_FIELDS: list[str] = [
    "budget_range",
    "timeline",
    "required_skills",
    "client_location",
    "contact_info",
    "additional_notes",
]

# Maps each field name to the clarification question shown to the user when
# that field is missing.
CLARIFICATION_MAP: dict[str, str] = {
    "opportunity_title": (
        "What is a short title or headline for this freelance opportunity? "
        "(e.g. 'Build a React dashboard for a SaaS startup')"
    ),
    "client_description": (
        "Can you describe the client? Include their industry, company size, "
        "and any relevant background."
    ),
    "project_description": (
        "What work needs to be done? Please describe the scope, key deliverables, "
        "and any important context."
    ),
    "budget_range": (
        "What is the budget or rate for this project? "
        "(e.g. '$5,000–$8,000 fixed' or '$120/hr')"
    ),
    "timeline": "What is the expected timeline or deadline for this project?",
    "required_skills": (
        "Which skills or technologies does the client require for this project?"
    ),
    "client_location": (
        "Where is the client located, and do they have timezone preferences?"
    ),
    "contact_info": "Where did you find this opportunity or how can the client be contacted?",
}

# Prompt template injected into the analyze_with_llm node.
# {intake_text} is replaced with the normalized intake fields at runtime.
ANALYSIS_PROMPT_TEMPLATE = """\
You are an expert freelance business advisor. Evaluate the following freelance \
opportunity and return a structured JSON response.

=== OPPORTUNITY ===
{intake_text}

=== INSTRUCTIONS ===
Return a JSON object with these fields:
- summary (string): 2-3 sentence overview of the opportunity.
- strengths (list of strings): Why this is a good opportunity.
- risks (list of strings): Red flags or concerns.
- score (number 0-10): Overall fit score (10 = ideal, 0 = avoid).
- recommendation (string): "pursue", "consider", or "pass".
- rationale (string): One paragraph explaining the score and recommendation.
"""

# Draft action templates used by the draft_action node.
# Each entry defines one type of action draft to generate.
DRAFT_ACTION_TEMPLATES: list[dict[str, Any]] = [
    {
        "action_type": "initial_reply",
        "title": "Initial Client Reply",
        "prompt_hint": (
            "Write a short, professional reply expressing interest and asking one "
            "clarifying question. Keep it to 3-4 sentences."
        ),
    },
    {
        "action_type": "proposal_outline",
        "title": "Project Proposal Outline",
        "prompt_hint": (
            "Create a brief proposal outline with: project understanding, proposed approach, "
            "timeline estimate, and a placeholder rate. Keep it under 200 words."
        ),
    },
]


def build_template_record() -> dict[str, Any]:
    """Return a dict suitable for upserting an IntakeTemplate database record."""
    return {
        "agent_type": AGENT_TYPE,
        "display_name": DISPLAY_NAME,
        "description": DESCRIPTION,
        "required_fields": REQUIRED_FIELDS,
        "optional_fields": OPTIONAL_FIELDS,
        "clarification_map": CLARIFICATION_MAP,
    }
