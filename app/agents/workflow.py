"""
LangGraph workflow for the Guided Intake Agent Platform.

Agent-specific behaviour is passed in via template configuration so the same
graph can be reused for multiple agent types. Execution routing is selected by
an explicit template-owned execution profile rather than agent-type identity.

Current execution order for intake-only agents:
  intake -> validate_required_fields -> mark_validated -> normalize_input -> end

A valid controlled_rag profile continues after normalization into:
  generate_rag_answer -> generate_tool_plan -> route_human_review

Missing or incomplete execution-profile configuration fails closed.
"""

from __future__ import annotations

import json
import os
from typing import Any

from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict


CONTROLLED_EXECUTION_PROFILE = {
    "name": "controlled_rag",
    "stages": ["rag_answer", "tool_plan", "human_review"],
}
INTAKE_ONLY_EXECUTION_PROFILE = {"name": "intake_only", "stages": []}


class AgentState(TypedDict, total=False):
    """Shared mutable state threaded through every node."""

    run_id: str
    agent_type: str
    intake_data: dict[str, Any]
    template_config: dict[str, Any]
    missing_fields: list[str]
    clarification_questions: list[dict[str, str]]
    normalized_data: dict[str, Any]
    analysis_summary: str
    score: float
    raw_llm_output: dict[str, Any]
    action_drafts: list[dict[str, Any]]
    rag_answer: dict[str, Any]
    tool_plan: dict[str, Any]
    human_review_required: bool
    review_status: str
    final_status: str
    status: str
    error: str


def node_intake(state: AgentState) -> AgentState:
    return {**state, "status": "running"}


def node_validate_required_fields(state: AgentState) -> AgentState:
    from app.services.validation import find_missing_fields

    config = state.get("template_config", {})
    required = config.get("required_fields", [])
    missing = find_missing_fields(state.get("intake_data", {}), required)
    return {**state, "missing_fields": missing}


def node_clarify_missing_info(state: AgentState) -> AgentState:
    from app.services.clarification import generate_clarification_questions

    config = state.get("template_config", {})
    clarification_map = config.get("clarification_map", {})
    questions = generate_clarification_questions(
        state.get("missing_fields", []), clarification_map
    )
    return {
        **state,
        "clarification_questions": [q.model_dump() for q in questions],
        "status": "needs_clarification",
    }


def node_mark_validated(state: AgentState) -> AgentState:
    return {**state, "status": "validated"}


def node_normalize_input(state: AgentState) -> AgentState:
    from app.services.normalization import normalize_intake_data

    normalized = normalize_intake_data(state.get("intake_data", {}))
    return {**state, "normalized_data": normalized}


def node_generate_rag_answer(state: AgentState) -> AgentState:
    from app.services.rag_answerer import generate_rag_answer

    user_request = state.get("intake_data", {}).get("user_request", "")
    if not user_request:
        normalized = state.get("normalized_data", {})
        user_request = str(normalized.get("user_request", ""))

    if not user_request:
        return {
            **state,
            "rag_answer": {
                "question": "",
                "answer": "No user request provided.",
                "citations": [],
                "retrieved_context": {},
                "limitations": ["No valid question to process."],
                "model": {"provider": "local", "name": "unknown", "available": False},
            },
        }

    try:
        rag_answer = generate_rag_answer(user_request, top_k_per_collection=3)
        return {**state, "rag_answer": rag_answer}
    except Exception as exc:
        return {
            **state,
            "rag_answer": {
                "question": user_request,
                "answer": f"RAG answer generation failed: {exc}. Please check the logs.",
                "citations": [],
                "retrieved_context": {},
                "limitations": [
                    "Answer generation encountered an error.",
                    "Local LLM may be unavailable.",
                ],
                "model": {"provider": "local", "name": "unknown", "available": False},
            },
        }


def node_generate_tool_plan(state: AgentState) -> AgentState:
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
        return {
            **state,
            "tool_plan": {
                "requires_tool_or_api": False,
                "execution_mode": "planned_only",
                "allowed_to_execute": False,
                "recommended_tools": [],
                "blocked_actions": [
                    "direct_sql_execution",
                    "unapproved_external_api_call",
                ],
                "approval_required": True,
                "reason": (
                    f"Tool plan generation encountered an error: {exc}. "
                    "Human review is required."
                ),
            },
        }


def node_route_human_review(state: AgentState) -> AgentState:
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
    return {
        **state,
        "human_review_required": False,
        "review_status": "not_required",
        "final_status": "completed",
        "status": "completed",
    }


def node_analyze_with_llm(state: AgentState) -> AgentState:
    api_key = os.getenv("OPENAI_API_KEY", "")
    config = state.get("template_config", {})
    prompt_template = config.get("analysis_prompt_template", "")
    normalized = state.get("normalized_data", state.get("intake_data", {}))

    if not api_key or api_key == "your-openai-api-key-here":
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

    intake_text = "\n".join(
        f"{k}: {v}" for k, v in normalized.items() if v is not None
    )
    prompt = prompt_template.format(intake_text=intake_text)

    try:
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
    score = max(0.0, min(10.0, float(state.get("score", 0.0))))
    return {**state, "score": score}


def node_draft_action(state: AgentState) -> AgentState:
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
    return {**state, "status": "pending_approval"}


def node_archive(state: AgentState) -> AgentState:
    return {**state, "status": "archived"}


def _route_after_validation(state: AgentState) -> str:
    if state.get("missing_fields"):
        return "clarify_missing_info"
    return "mark_validated"


def node_end_phase2_workflow(state: AgentState) -> AgentState:
    current_status = state.get("status", "")
    if current_status not in ["validated", "needs_clarification", "error"]:
        return {**state, "status": "validated"}
    return state


def node_invalid_execution_profile(state: AgentState) -> AgentState:
    profile = state.get("template_config", {}).get("execution_profile")
    return {
        **state,
        "status": "error",
        "error": f"Invalid or missing execution_profile: {profile!r}",
    }


def is_controlled_execution_profile(profile: Any) -> bool:
    return profile == CONTROLLED_EXECUTION_PROFILE


def is_intake_only_execution_profile(profile: Any) -> bool:
    return profile == INTAKE_ONLY_EXECUTION_PROFILE


def _route_after_normalization(state: AgentState) -> str:
    profile = state.get("template_config", {}).get("execution_profile")
    if is_controlled_execution_profile(profile):
        return "generate_rag_answer"
    if is_intake_only_execution_profile(profile):
        return "end_phase2_workflow"
    return "invalid_execution_profile"


def _route_after_llm(state: AgentState) -> str:
    if state.get("status") == "error":
        return END
    return "score_result"


def build_workflow() -> Any:
    graph = StateGraph(AgentState)

    graph.add_node("intake", node_intake)
    graph.add_node("validate_required_fields", node_validate_required_fields)
    graph.add_node("clarify_missing_info", node_clarify_missing_info)
    graph.add_node("mark_validated", node_mark_validated)
    graph.add_node("normalize_input", node_normalize_input)
    graph.add_node("end_phase2_workflow", node_end_phase2_workflow)
    graph.add_node("invalid_execution_profile", node_invalid_execution_profile)
    graph.add_node("generate_rag_answer", node_generate_rag_answer)
    graph.add_node("generate_tool_plan", node_generate_tool_plan)
    graph.add_node("route_human_review", node_route_human_review)

    graph.set_entry_point("intake")
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
    graph.add_edge("mark_validated", "normalize_input")
    graph.add_conditional_edges(
        "normalize_input",
        _route_after_normalization,
        {
            "generate_rag_answer": "generate_rag_answer",
            "end_phase2_workflow": "end_phase2_workflow",
            "invalid_execution_profile": "invalid_execution_profile",
        },
    )
    graph.add_edge("end_phase2_workflow", END)
    graph.add_edge("invalid_execution_profile", END)
    graph.add_edge("generate_rag_answer", "generate_tool_plan")
    graph.add_edge("generate_tool_plan", "route_human_review")
    graph.add_edge("route_human_review", END)

    return graph.compile()


workflow = build_workflow()
