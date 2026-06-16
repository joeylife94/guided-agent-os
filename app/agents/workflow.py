"""
LangGraph workflow for the Guided Intake Agent Platform.

The workflow is intentionally template-driven: agent-specific behaviour
(required fields, clarification questions, LLM prompts, draft templates)
is passed in via a TemplateConfig dict so the same graph can be reused
for any agent type.

Current execution order for standard intake agents:
  intake -> validate_required_fields -> mark_validated -> normalize_input

If required fields are missing after validate_required_fields, the graph
branches to clarify_missing_info, marks the run as 'needs_clarification',
and terminates. The user must resubmit with the missing data filled in.

The controlled_rag_agent template continues after normalization into a
planned-only Phase 3 path:
  generate_rag_answer -> generate_tool_plan -> route_human_review

LLM analysis, scoring, drafting, and archive nodes remain inactive skeletons
until their corresponding phases are intentionally wired.
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

    # Phase 3: Controlled RAG Agent Workflow
    rag_answer: dict[str, Any]  # Answer generated from RAG + local LLM
    tool_plan: dict[str, Any]  # Planned tool/API execution steps
    human_review_required: bool  # Whether human review is needed
    review_status: str  # 'pending_approval', 'not_required', etc.
    final_status: str  # Final status after review routing

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


def node_mark_validated(state: AgentState) -> AgentState:
    """
    Validation success node — marks the run as 'validated' when all
    required fields are present and complete.

    This implements the minimal validation and clarification flow.
    The workflow stops here; future analysis and approval steps can
    be added in subsequent phases.
    """
    return {**state, "status": "validated"}


def node_normalize_input(state: AgentState) -> AgentState:
    """
    Normalization node — cleans and standardises the intake data.

    Runs only when validation succeeds (after mark_validated).
    Applies deterministic normalization rules:
    - Trims whitespace
    - Extracts specific normalized fields
    - Detects technology keywords and stack
    - Preserves original intake_data

    The normalized data is stored separately and returned to the API
    for persistence in the database.
    """
    from app.services.normalization import normalize_intake_data

    intake = state.get("intake_data", {})
    normalized = normalize_intake_data(intake)

    return {**state, "normalized_data": normalized}


def node_generate_rag_answer(state: AgentState) -> AgentState:
    """
    Phase 3: RAG Answer Generation Node.

    Calls the RAG + local LLM answerer to generate a grounded answer
    based on the user request and normalized data.

    Falls back gracefully if local LLM is unavailable.
    """
    from app.services.rag_answerer import generate_rag_answer

    user_request = state.get("intake_data", {}).get("user_request", "")
    if not user_request:
        # If no direct request field, use the normalized summary
        normalized = state.get("normalized_data", {})
        user_request = str(normalized.get("user_request", ""))

    if not user_request:
        # No valid question found
        return {
            **state,
            "rag_answer": {
                "question": "",
                "answer": "No user request provided.",
                "citations": [],
                "retrieved_context": {},
                "limitations": ["No valid question to process."],
                "model": {"provider": "local", "name": "unknown", "available": False},
            }
        }

    try:
        rag_answer = generate_rag_answer(user_request, top_k_per_collection=3)
        return {**state, "rag_answer": rag_answer}
    except Exception as exc:
        # Fallback if RAG generation fails
        fallback_answer = {
            "question": user_request,
            "answer": f"RAG answer generation failed: {exc}. Please check the logs.",
            "citations": [],
            "retrieved_context": {},
            "limitations": [
                "Answer generation encountered an error.",
                "Local LLM may be unavailable.",
            ],
            "model": {"provider": "local", "name": "unknown", "available": False},
        }
        return {**state, "rag_answer": fallback_answer}


def node_generate_tool_plan(state: AgentState) -> AgentState:
    """
    Phase 3: Tool/API Execution Planning Node.

    Generates a deterministic execution plan based on:
    - Original user request
    - Normalized data (including risk_level)
    - RAG answer (to check if context is sufficient)

    The plan does NOT execute anything. It specifies WHAT WOULD BE
    executed if approved, along with approval requirements.
    """
    from app.services.tool_plan_generator import generate_tool_plan

    user_request = state.get("intake_data", {}).get("user_request", "")
    normalized_data = state.get("normalized_data", {})
    rag_answer = state.get("rag_answer", {})

    try:
        tool_plan = generate_tool_plan(
            user_request=user_request,
            normalized_data=normalized_data,
            rag_answer=rag_answer,
        )
        return {**state, "tool_plan": tool_plan}
    except Exception as exc:
        # Fallback plan if generation fails
        fallback_plan = {
            "requires_tool_or_api": False,
            "execution_mode": "planned_only",
            "allowed_to_execute": False,
            "recommended_tools": [],
            "blocked_actions": [
                "direct_sql_execution",
                "unapproved_external_api_call",
            ],
            "approval_required": True,
            "reason": f"Tool plan generation encountered an error: {exc}. "
                     "Human review is required.",
        }
        return {**state, "tool_plan": fallback_plan}


def node_route_human_review(state: AgentState) -> AgentState:
    """
    Phase 3: Human Review Routing Node.

    Determines whether human review is required based on:
    - tool_plan.approval_required
    - risk_level
    - RAG answer sufficiency

    Sets review_status and final_status accordingly.
    """
    tool_plan = state.get("tool_plan", {})
    approval_required = tool_plan.get("approval_required", False)

    if approval_required:
        return {
            **state,
            "human_review_required": True,
            "review_status": "pending_approval",
            "final_status": "pending_approval",
            "status": "pending_approval",
        }
    else:
        return {
            **state,
            "human_review_required": False,
            "review_status": "not_required",
            "final_status": "completed",
            "status": "completed",
        }


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
    """
    Route after validation: either to clarification (if fields missing)
    or to mark_validated (if all required fields present).
    """
    if state.get("missing_fields"):
        return "clarify_missing_info"
    return "mark_validated"


def node_end_phase2_workflow(state: AgentState) -> AgentState:
    """
    End node for Phase 2 (non-controlled_rag_agent) workflows.

    Ensures the status is "validated" before ending for Phase 1/2 agents.
    """
    # Only change status if not already set to a terminal state
    current_status = state.get("status", "")
    if current_status not in ["validated", "needs_clarification", "error"]:
        return {**state, "status": "validated"}
    return state


def _route_after_normalization(state: AgentState) -> str:
    """
    Route after normalization: controlled_rag_agent goes to Phase 3,
    other agents go to end_phase2_workflow.
    """
    agent_type = state.get("agent_type", "")
    if agent_type == "controlled_rag_agent":
        return "generate_rag_answer"
    # For other agents, stop after normalization
    return "end_phase2_workflow"


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

    Implements Phase 1-3 with conditional routing:
    - Phase 1: Validates required fields, generates clarification questions
    - Phase 2-B: Normalizes input data
    - Phase 3 (controlled_rag_agent only): RAG answer generation, tool planning, human review routing

    Workflow order for controlled_rag_agent:
      intake
      → validate_required_fields
      → [clarify_missing_info OR mark_validated]
      → normalize_input
      → generate_rag_answer
      → generate_tool_plan
      → route_human_review
      → END

    Workflow order for other agents (freelance, public_enterprise_ai):
      intake
      → validate_required_fields
      → [clarify_missing_info OR mark_validated]
      → normalize_input
      → END (status="validated")

    If required fields are missing, workflow stops at clarify_missing_info.
    If all required fields are present, the workflow proceeds through normalization
    and optionally to Phase 3 based on agent type.

    Returns a compiled runnable.  Call `.invoke(initial_state)` to
    execute the full graph.
    """
    graph = StateGraph(AgentState)

    # Register Phase 1 nodes
    graph.add_node("intake", node_intake)
    graph.add_node("validate_required_fields", node_validate_required_fields)
    graph.add_node("clarify_missing_info", node_clarify_missing_info)
    graph.add_node("mark_validated", node_mark_validated)

    # Register Phase 2-B nodes
    graph.add_node("normalize_input", node_normalize_input)
    graph.add_node("end_phase2_workflow", node_end_phase2_workflow)

    # Register Phase 3 nodes (controlled_rag_agent only)
    graph.add_node("generate_rag_answer", node_generate_rag_answer)
    graph.add_node("generate_tool_plan", node_generate_tool_plan)
    graph.add_node("route_human_review", node_route_human_review)

    # Entry point
    graph.set_entry_point("intake")

    # Edges — Phase 1 validation/clarification flow
    graph.add_edge("intake", "validate_required_fields")
    graph.add_conditional_edges(
        "validate_required_fields",
        _route_after_validation,
        {
            "clarify_missing_info": "clarify_missing_info",
            "mark_validated": "mark_validated",
        },
    )
    graph.add_edge("clarify_missing_info", END)

    # Phase 2-B normalization flow (only after validation succeeds)
    graph.add_edge("mark_validated", "normalize_input")

    # Phase 3 conditional routing (controlled_rag_agent only) or end Phase 2
    graph.add_conditional_edges(
        "normalize_input",
        _route_after_normalization,
        {
            "generate_rag_answer": "generate_rag_answer",
            "end_phase2_workflow": "end_phase2_workflow",
        },
    )

    # End Phase 2 workflow
    graph.add_edge("end_phase2_workflow", END)

    # Phase 3 flow (controlled_rag_agent only)
    graph.add_edge("generate_rag_answer", "generate_tool_plan")
    graph.add_edge("generate_tool_plan", "route_human_review")
    graph.add_edge("route_human_review", END)

    return graph.compile()


# Module-level compiled workflow instance
workflow = build_workflow()
