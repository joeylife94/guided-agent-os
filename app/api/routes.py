from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.workflow import workflow
from app.models.database import get_db
from app.models.models import ActionDraft as ActionDraftModel
from app.models.models import AgentRun, RunAuditEvent
from app.schemas.agent_run import (
    ActionDraft,
    AgentRunResponse,
    ApproveRequest,
    ClarificationQuestion,
    RejectRequest,
)
from app.services.tool_executor import ToolExecutionError, execute_approved_tool
from app.templates import controlled_rag_agent, freelance, public_enterprise_ai

router = APIRouter(prefix="/api/agents", tags=["agents"])

# ---------------------------------------------------------------------------
# Agent template registry
# ---------------------------------------------------------------------------
# Add new agent types here by importing their template module.

_TEMPLATE_REGISTRY = {
    freelance.AGENT_TYPE: freelance,
    public_enterprise_ai.AGENT_TYPE: public_enterprise_ai,
    controlled_rag_agent.AGENT_TYPE: controlled_rag_agent,
}


def _get_template_config(agent_type: str) -> dict[str, Any]:
    """Return the config dict for a given agent_type, or raise 404."""
    template = _TEMPLATE_REGISTRY.get(agent_type)
    if template:
        return {
            "required_fields": template.REQUIRED_FIELDS,
            "optional_fields": template.OPTIONAL_FIELDS,
            "clarification_map": template.CLARIFICATION_MAP,
            "analysis_prompt_template": getattr(
                template,
                "ANALYSIS_PROMPT_TEMPLATE",
                "",
            ),
            "draft_action_templates": getattr(template, "DRAFT_ACTION_TEMPLATES", []),
        }
    supported_types = ", ".join(sorted(_TEMPLATE_REGISTRY))
    raise HTTPException(
        status_code=404,
        detail=f"Agent type '{agent_type}' is not registered. "
        f"Supported types: {supported_types}",
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_to_response(run: AgentRun) -> AgentRunResponse:
    raw_output = run.raw_llm_output or {}
    clarification_questions = [
        ClarificationQuestion(**q) for q in (run.clarification_questions or [])
    ]
    action_drafts = [
        ActionDraft(
            action_type=d.action_type,
            title=d.title,
            content=d.content,
        )
        for d in run.action_drafts
    ]
    return AgentRunResponse(
        run_id=run.id,
        agent_type=run.agent_type,
        status=run.status,
        intake_data=run.intake_data or {},
        normalized_data=run.normalized_data,
        missing_fields=run.missing_fields or [],
        clarification_questions=clarification_questions,
        analysis_summary=run.analysis_summary,
        score=run.score,
        action_drafts=action_drafts,
        rag_answer=raw_output.get("rag_answer"),
        tool_plan=raw_output.get("tool_plan"),
        human_review_required=raw_output.get("human_review_required"),
        review_status=raw_output.get("review_status"),
        final_status=raw_output.get("final_status"),
        error=run.error_message,
        created_at=run.created_at,
        updated_at=run.updated_at,
        raw_output=run.raw_llm_output,
    )


def _commit_and_refresh(db: Session, run: AgentRun) -> AgentRun:
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(run)
    return run


def _append_audit_event(
    run: AgentRun,
    event_type: str,
    *,
    actor: str = "system",
    payload: dict[str, Any] | None = None,
) -> RunAuditEvent:
    next_sequence = max((event.sequence for event in run.audit_events), default=0) + 1
    event = RunAuditEvent(
        run_id=run.id,
        sequence=next_sequence,
        event_type=event_type,
        actor=actor,
        payload=payload or {},
    )
    run.audit_events.append(event)
    return event


def _audit_event_to_response(event: RunAuditEvent) -> dict[str, Any]:
    return {
        "sequence": event.sequence,
        "event_type": event.event_type,
        "actor": event.actor,
        "payload": event.payload or {},
        "created_at": event.created_at,
    }


def _planned_tool_for_execution(run: AgentRun) -> str | None:
    raw_output = run.raw_llm_output or {}
    tool_plan = raw_output.get("tool_plan") or {}
    if not tool_plan.get("requires_tool_or_api"):
        return None
    recommended = tool_plan.get("recommended_tools") or []
    if not recommended:
        raise ToolExecutionError(
            "Tool execution was required but the persisted plan has no recommended tool"
        )
    tool_name = recommended[0].get("name")
    if not isinstance(tool_name, str) or not tool_name.strip():
        raise ToolExecutionError("Persisted tool plan contains an invalid tool name")
    return tool_name.strip()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/{agent_type}/runs", response_model=AgentRunResponse, status_code=201)
def create_run(
    agent_type: str,
    body: dict[str, Any],
    db: Session = Depends(get_db),
) -> AgentRunResponse:
    """Start a new agent run for the specified agent type."""
    template_config = _get_template_config(agent_type)

    run = AgentRun(
        id=str(uuid.uuid4()),
        agent_type=agent_type,
        status="running",
        intake_data=body,
    )
    db.add(run)
    _append_audit_event(
        run,
        "REQUEST_RECEIVED",
        actor="user",
        payload={"agent_type": agent_type},
    )

    initial_state: dict[str, Any] = {
        "run_id": run.id,
        "agent_type": agent_type,
        "intake_data": body,
        "template_config": template_config,
        "missing_fields": [],
        "clarification_questions": [],
        "action_drafts": [],
        "status": "pending",
    }

    try:
        final_state: dict[str, Any] = workflow.invoke(initial_state)
    except Exception as exc:
        run.status = "error"
        run.error_message = str(exc)
        _append_audit_event(run, "FAILED", payload={"error": str(exc)})
        _commit_and_refresh(db, run)
        return _run_to_response(run)

    run.status = final_state.get("status", "error")
    run.missing_fields = final_state.get("missing_fields", [])
    run.clarification_questions = final_state.get("clarification_questions", [])
    run.normalized_data = final_state.get("normalized_data")
    run.analysis_summary = final_state.get("analysis_summary")
    run.score = final_state.get("score")

    if run.status == "needs_clarification":
        _append_audit_event(
            run,
            "CLARIFICATION_REQUIRED",
            payload={"missing_fields": run.missing_fields},
        )
    else:
        _append_audit_event(run, "VALIDATION_PASSED")
        if run.normalized_data is not None:
            _append_audit_event(run, "NORMALIZED")

    if agent_type == controlled_rag_agent.AGENT_TYPE:
        run.raw_llm_output = {
            "rag_answer": final_state.get("rag_answer"),
            "tool_plan": final_state.get("tool_plan"),
            "human_review_required": final_state.get(
                "human_review_required",
                False,
            ),
            "review_status": final_state.get("review_status"),
            "final_status": final_state.get("final_status"),
        }
        if final_state.get("rag_answer") is not None:
            _append_audit_event(run, "ANSWER_GENERATED")
        if final_state.get("tool_plan") is not None:
            _append_audit_event(run, "TOOL_PLANNED")
        if run.status == "pending_approval":
            _append_audit_event(run, "APPROVAL_REQUESTED")
    else:
        run.raw_llm_output = final_state.get("raw_llm_output")

    if final_state.get("error"):
        run.error_message = final_state["error"]
        _append_audit_event(run, "FAILED", payload={"error": final_state["error"]})

    for draft_data in final_state.get("action_drafts", []):
        db.add(
            ActionDraftModel(
                run_id=run.id,
                action_type=draft_data["action_type"],
                title=draft_data["title"],
                content=draft_data["content"],
            )
        )

    _commit_and_refresh(db, run)
    return _run_to_response(run)


@router.get("/runs/{run_id}", response_model=AgentRunResponse)
def get_run(run_id: str, db: Session = Depends(get_db)) -> AgentRunResponse:
    """Retrieve the current state of an agent run by its ID."""
    run = db.get(AgentRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    return _run_to_response(run)


@router.get("/runs/{run_id}/events")
def get_run_events(run_id: str, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """Return persisted lifecycle events in deterministic run sequence order."""
    run = db.get(AgentRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    return [_audit_event_to_response(event) for event in run.audit_events]


@router.post("/runs/{run_id}/approve", response_model=AgentRunResponse)
def approve_run(
    run_id: str,
    body: ApproveRequest,
    db: Session = Depends(get_db),
) -> AgentRunResponse:
    """Approve a pending run and execute its single controlled read-only tool."""
    run = db.get(AgentRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    if run.status != "pending_approval":
        raise HTTPException(
            status_code=422,
            detail=(
                f"Run '{run_id}' cannot be approved because its status is "
                f"'{run.status}'. Only 'pending_approval' runs can be approved."
            ),
        )

    raw_output = dict(run.raw_llm_output or {})
    try:
        tool_name = _planned_tool_for_execution(run)
        execution_result = None
        if tool_name is not None:
            execution_result = execute_approved_tool(
                tool_name=tool_name,
                parameters=(run.intake_data or {}).get("tool_parameters", {}),
                approved=True,
                allowed_tools=(run.intake_data or {}).get("allowed_tools", []),
            )
    except ToolExecutionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if body.note:
        run.reviewer_note = body.note
    for draft in run.action_drafts:
        draft.is_approved = True

    _append_audit_event(run, "APPROVED", actor="human", payload={"note": body.note or ""})
    raw_output["review_status"] = "approved"
    raw_output["final_status"] = "archived"
    if execution_result is not None:
        raw_output["execution_result"] = execution_result
        _append_audit_event(
            run,
            "TOOL_EXECUTED",
            payload={
                "tool_name": tool_name,
                "status": execution_result.get("status"),
                "read_only": execution_result.get("read_only", True),
            },
        )
    run.raw_llm_output = raw_output
    run.status = "archived"
    _append_audit_event(run, "COMPLETED", payload={"status": run.status})

    _commit_and_refresh(db, run)
    return _run_to_response(run)


@router.post("/runs/{run_id}/reject", response_model=AgentRunResponse)
def reject_run(
    run_id: str,
    body: RejectRequest,
    db: Session = Depends(get_db),
) -> AgentRunResponse:
    """Reject a pending run without executing any tool."""
    run = db.get(AgentRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    if run.status != "pending_approval":
        raise HTTPException(
            status_code=422,
            detail=(
                f"Run '{run_id}' cannot be rejected because its status is "
                f"'{run.status}'. Only 'pending_approval' runs can be rejected."
            ),
        )

    run.status = "rejected"
    run.reviewer_note = body.reason
    for draft in run.action_drafts:
        draft.is_approved = False

    raw_output = dict(run.raw_llm_output or {})
    raw_output["review_status"] = "rejected"
    raw_output["final_status"] = "rejected"
    raw_output.pop("execution_result", None)
    run.raw_llm_output = raw_output
    _append_audit_event(run, "REJECTED", actor="human", payload={"reason": body.reason})
    _append_audit_event(run, "COMPLETED", payload={"status": run.status})

    _commit_and_refresh(db, run)
    return _run_to_response(run)
