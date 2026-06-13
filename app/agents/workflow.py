"""
LangGraph workflow for the Guided Intake Agent Platform.

The workflow is intentionally template-driven: agent-specific behaviour
(required fields, clarification questions, LLM prompts, draft templates)
is passed in via a TemplateConfig dict so the same graph can be reused
for any agent type.

Node execution order (happy path):
  intake → validate_required_fields → normalize_input
         → analyze_with_llm → score_result → draft_action
         → human_review → archive

If required fields are missing after validate_required_fields the graph
branches to clarify_missing_info which marks the run as
'needs_clarification' and terminates — the user must resubmit with the
missing data filled in.
"""

from __future__ import annotations

import json
import os
from typing import Any

from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict


# ---------------------------------------------------------------------------
# Workflow state
# ---------------------------------------------------------------------------

class AgentState(TypedDict, total=False):
    """Shared mutable state threaded through every node."""

    # Inputs
    run_id: str
    agent_type: str
    intake_data: dict[str, Any]
    template_config: dict[str, Any]  # agent-specific config from templates/

    # Validation
    missing_fields: list[str]
    clarification_questions: list[dict[str, str]]

    # Processing
    normalized_data: dict[str, Any]
    analysis_summary: str
    score: float
    raw_llm_output: dict[str, Any]

    # Output
    action_drafts: list[dict[str, Any]]

    # Control
    status: str   # mirrors AgentRun.status
    error: str


# ---------------------------------------------------------------------------
# Node implementations
# ---------------------------------------------------------------------------

def node_intake(state: AgentState) -> AgentState:
    """
    Intake node — accepts the raw data and marks the run as running.

    In a fuller implementation this would also persist the initial run
    record; here the API layer handles persistence so this node just
    confirms receipt.
    """
    return {**state, "status": "running"}


def node_validate_required_fields(state: AgentState) -> AgentState:
    """
    Validation node — checks that all required fields are present and
    non-empty. Populates missing_fields for the routing decision.
    """
    from app.services.validation import find_missing_fields

    config = state.get("template_config", {})
    required = config.get("required_fields", [])
    missing = find_missing_fields(state.get("intake_data", {}), required)
    return {**state, "missing_fields": missing}


def node_clarify_missing_info(state: AgentState) -> AgentState:
    """
    Clarification node — builds human-readable questions for every
    missing field and sets status to 'needs_clarification'.

    After this node the graph terminates; the API response will contain
    the clarification_questions list for the client to act on.
    """
    from app.services.clarification import generate_clarification_questions

    config = state.get("template_config", {})
    clarification_map = config.get("clarification_map", {})
    questions = generate_clarification_questions(
        state.get("missing_fields", []),
        clarification_map,
    )
    return {
        **state,
        "clarification_questions": [q.model_dump() for q in questions],
        "status": "needs_clarification",
    }


def node_normalize_input(state: AgentState) -> AgentState:
    """
    Normalization node — cleans and standardises the intake data.

    Currently applies lightweight rules (strip whitespace, lowercase list
    items). Extend this node as normalisation requirements grow.
    """
    raw = state.get("intake_data", {})
    normalized: dict[str, Any] = {}

    for key, value in raw.items():
        if isinstance(value, str):
            normalized[key] = value.strip()
        elif isinstance(value, list):
            normalized[key] = [
                item.strip().lower() if isinstance(item, str) else item
                for item in value
            ]
        else:
            normalized[key] = value

    return {**state, "normalized_data": normalized}


def node_analyze_with_llm(state: AgentState) -> AgentState:
    """
    LLM analysis node — sends the normalized intake data to an LLM and
    parses the structured response.

    The OPENAI_API_KEY environment variable must be set for live calls.
    When the key is absent the node returns a clearly-labelled stub so
    the rest of the workflow can still be exercised locally.
    """
    api_key = os.getenv("OPENAI_API_KEY", "")
    config = state.get("template_config", {})
    prompt_template = config.get("analysis_prompt_template", "")
    normalized = state.get("normalized_data", state.get("intake_data", {}))

    if not api_key or api_key == "your-openai-api-key-here":
        # Stub response for local development / testing
        stub_output = {
            "summary": "[STUB] LLM analysis not available — set OPENAI_API_KEY to enable.",
            "strengths": [],
            "risks": [],
            "score": 0.0,
            "recommendation": "pending",
            "rationale": "LLM analysis skipped (no API key configured).",
        }
        return {
            **state,
            "analysis_summary": stub_output["summary"],
            "score": stub_output["score"],
            "raw_llm_output": stub_output,
        }

    # Build the prompt
    intake_text = "\n".join(
        f"{k}: {v}" for k, v in normalized.items() if v is not None
    )
    prompt = prompt_template.format(intake_text=intake_text)

    try:
        # Lazy import so the app starts without openai installed during dev
        from openai import OpenAI  # type: ignore[import]

        client = OpenAI(api_key=api_key)
        llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        response = client.chat.completions.create(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        raw_text = response.choices[0].message.content or "{}"
        output: dict[str, Any] = json.loads(raw_text)
    except Exception as exc:
        return {**state, "error": f"LLM call failed: {exc}", "status": "error"}

    return {
        **state,
        "analysis_summary": output.get("summary", ""),
        "score": float(output.get("score", 0)),
        "raw_llm_output": output,
    }


def node_score_result(state: AgentState) -> AgentState:
    """
    Scoring node — finalises the numeric score.

    The score is already set by the LLM node; this node exists as a
    dedicated step so custom scoring logic (rules-based overrides,
    weighted criteria) can be added without touching the LLM node.
    """
    score = state.get("score", 0.0)
    # Clamp to [0, 10]
    score = max(0.0, min(10.0, float(score)))
    return {**state, "score": score}


def node_draft_action(state: AgentState) -> AgentState:
    """
    Action drafting node — produces draft actions based on the analysis.

    Uses the draft_action_templates from the template config.  Each
    template entry provides a title, action_type, and prompt_hint; in
    this skeleton the content is populated with a labelled stub.  Wire
    in an LLM call here to generate real drafts.
    """
    config = state.get("template_config", {})
    draft_templates = config.get("draft_action_templates", [])
    llm_output = state.get("raw_llm_output", {})
    recommendation = llm_output.get("recommendation", "pending")

    drafts: list[dict[str, Any]] = []
    for tpl in draft_templates:
        drafts.append(
            {
                "action_type": tpl.get("action_type", "draft"),
                "title": tpl.get("title", "Draft"),
                "content": (
                    f"[DRAFT — {tpl.get('title', 'Action')}]\n"
                    f"Recommendation: {recommendation}\n"
                    f"Hint: {tpl.get('prompt_hint', '')}\n\n"
                    "Replace this placeholder with an LLM-generated draft."
                ),
            }
        )

    return {**state, "action_drafts": drafts}


def node_human_review(state: AgentState) -> AgentState:
    """
    Human review node — marks the run as pending_approval.

    Execution stops here.  The approve/reject API endpoints are
    responsible for persisting the reviewer decision and triggering the
    archive node.
    """
    return {**state, "status": "pending_approval"}


def node_archive(state: AgentState) -> AgentState:
    """
    Archive node — marks the run as archived after approval.

    Extend this node to move data to long-term storage, send
    notifications, or trigger downstream systems.
    """
    return {**state, "status": "archived"}


# ---------------------------------------------------------------------------
# Routing helpers
# ---------------------------------------------------------------------------

def _route_after_validation(state: AgentState) -> str:
    """Branch to clarification if fields are missing, else continue."""
    if state.get("missing_fields"):
        return "clarify_missing_info"
    return "normalize_input"


def _route_after_llm(state: AgentState) -> str:
    """Stop the graph on LLM errors, else continue to scoring."""
    if state.get("status") == "error":
        return END
    return "score_result"


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_workflow() -> Any:
    """
    Construct and compile the LangGraph StateGraph.

    Returns a compiled runnable.  Call `.invoke(initial_state)` to
    execute the full graph.
    """
    graph = StateGraph(AgentState)

    # Register nodes
    graph.add_node("intake", node_intake)
    graph.add_node("validate_required_fields", node_validate_required_fields)
    graph.add_node("clarify_missing_info", node_clarify_missing_info)
    graph.add_node("normalize_input", node_normalize_input)
    graph.add_node("analyze_with_llm", node_analyze_with_llm)
    graph.add_node("score_result", node_score_result)
    graph.add_node("draft_action", node_draft_action)
    graph.add_node("human_review", node_human_review)
    graph.add_node("archive", node_archive)

    # Entry point
    graph.set_entry_point("intake")

    # Edges
    graph.add_edge("intake", "validate_required_fields")
    graph.add_conditional_edges(
        "validate_required_fields",
        _route_after_validation,
        {
            "clarify_missing_info": "clarify_missing_info",
            "normalize_input": "normalize_input",
        },
    )
    graph.add_edge("clarify_missing_info", END)
    graph.add_edge("normalize_input", "analyze_with_llm")
    graph.add_conditional_edges(
        "analyze_with_llm",
        _route_after_llm,
        {
            "score_result": "score_result",
            END: END,
        },
    )
    graph.add_edge("score_result", "draft_action")
    graph.add_edge("draft_action", "human_review")
    graph.add_edge("human_review", END)

    # archive is invoked directly by the approve endpoint, not via this graph
    graph.add_edge("archive", END)

    return graph.compile()


# Module-level compiled workflow instance
workflow = build_workflow()
