from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.workflow import workflow
from app.models.database import get_db
from app.models.models import ActionDraft as ActionDraftModel
from app.models.models import AgentRun
from app.schemas.agent_run import (
    ActionDraft,
    AgentRunResponse,
    ApproveRequest,
    ClarificationQuestion,
    RejectRequest,
)
from app.templates import freelance, public_enterprise_ai

router = APIRouter(prefix="/api/agents", tags=["agents"])

# ---------------------------------------------------------------------------
# Agent template registry
# ---------------------------------------------------------------------------
# Add new agent types here by importing their template module.

_TEMPLATE_REGISTRY = {
    freelance.AGENT_TYPE: freelance,
    public_enterprise_ai.AGENT_TYPE: public_enterprise_ai,
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


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/{agent_type}/runs", response_model=AgentRunResponse, status_code=201)
def create_run(
    agent_type: str,
    body: dict[str, Any],
    db: Session = Depends(get_db),
) -> AgentRunResponse:
    """
    Start a new agent run for the specified agent type.

    The request body is the raw intake form payload for that agent type.
    Supported agent types are registered in `_TEMPLATE_REGISTRY`.

    Returns the newly created run, which will be in one of these states:
    - **needs_clarification** — required fields were missing; check
      `clarification_questions` in the response.
    - **validated** — all required fields were present. Phase 1 stops here.
    - **error** — the workflow encountered an unrecoverable error.
    """
    template_config = _get_template_config(agent_type)

    # Create the DB record first so we have an ID
    run = AgentRun(
        id=str(uuid.uuid4()),
        agent_type=agent_type,
        status="running",
        intake_data=body,
    )
    db.add(run)

    # Execute the LangGraph workflow
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
        _commit_and_refresh(db, run)
        return _run_to_response(run)

    # Persist workflow results
    run.status = final_state.get("status", "error")
    run.missing_fields = final_state.get("missing_fields", [])
    run.clarification_questions = final_state.get("clarification_questions", [])
    run.normalized_data = final_state.get("normalized_data")
    run.analysis_summary = final_state.get("analysis_summary")
    run.score = final_state.get("score")
    run.raw_llm_output = final_state.get("raw_llm_output")
    if final_state.get("error"):
        run.error_message = final_state["error"]

    # Persist action drafts
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


@router.post("/runs/{run_id}/approve", response_model=AgentRunResponse)
def approve_run(
    run_id: str,
    body: ApproveRequest,
    db: Session = Depends(get_db),
) -> AgentRunResponse:
    """
    Approve a future-phase run that is in 'pending_approval' status.

    Phase 1 validation runs stop at 'validated' and cannot be approved.
    """
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

    run.status = "archived"
    if body.note:
        run.reviewer_note = body.note
    # Mark all action drafts as approved
    for draft in run.action_drafts:
        draft.is_approved = True

    _commit_and_refresh(db, run)
    return _run_to_response(run)


@router.post("/runs/{run_id}/reject", response_model=AgentRunResponse)
def reject_run(
    run_id: str,
    body: RejectRequest,
    db: Session = Depends(get_db),
) -> AgentRunResponse:
    """
    Reject a future-phase run that is in 'pending_approval' status.

    Phase 1 validation runs stop at 'validated' and cannot be rejected.
    """
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

    _commit_and_refresh(db, run)
    return _run_to_response(run)
