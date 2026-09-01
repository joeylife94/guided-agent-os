from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
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

_TEMPLATE_REGISTRY = {
    freelance.AGENT_TYPE: freelance,
    public_enterprise_ai.AGENT_TYPE: public_enterprise_ai,
    controlled_rag_agent.AGENT_TYPE: controlled_rag_agent,
}


def _get_template_config(agent_type: str) -> dict[str, Any]:
    template = _TEMPLATE_REGISTRY.get(agent_type)
    if template:
        return {
            "required_fields": template.REQUIRED_FIELDS,
            "optional_fields": template.OPTIONAL_FIELDS,
            "clarification_map": template.CLARIFICATION_MAP,
            "analysis_prompt_template": getattr(template, "ANALYSIS_PROMPT_TEMPLATE", ""),
            "draft_action_templates": getattr(template, "DRAFT_ACTION_TEMPLATES", []),
        }
    supported_types = ", ".join(sorted(_TEMPLATE_REGISTRY))
    raise HTTPException(
        status_code=404,
        detail=f"Agent type '{agent_type}' is not registered. Supported types: {supported_types}",
    )


def _run_to_response(run: AgentRun) -> AgentRunResponse:
    raw_output = run.raw_llm_output or {}
    clarification_questions = [
        ClarificationQuestion(**q) for q in (run.clarification_questions or [])
    ]
    action_drafts = [
        ActionDraft(action_type=d.action_type, title=d.title, content=d.content)
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


def _run_evidence_bundle(run: AgentRun) -> dict[str, Any]:
    evidence = jsonable_encoder(
        {
            "run": _run_to_response(run),
            "events": [
                _audit_event_to_response(event)
                for event in sorted(run.audit_events, key=lambda item: item.sequence)
            ],
        }
    )
    canonical = json.dumps(
        evidence,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return {**evidence, "evidence_digest": hashlib.sha256(canonical).hexdigest()}


def _retrieval_audit_payload(rag_answer: dict[str, Any]) -> dict[str, Any]:
    retrieved_context = rag_answer.get("retrieved_context") or {}
    collection_counts = {
        str(collection): len(results) if isinstance(results, list) else 0
        for collection, results in retrieved_context.items()
    }
    return {
        "collection_counts": collection_counts,
        "retrieved_chunks": sum(collection_counts.values()),
        "citation_count": len(rag_answer.get("citations") or []),
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


def _claim_pending_decision(
    db: Session,
    run_id: str,
    claimed_status: str,
) -> tuple[AgentRun, bool]:
    claimed = (
        db.query(AgentRun)
        .filter(AgentRun.id == run_id, AgentRun.status == "pending_approval")
        .update({AgentRun.status: claimed_status}, synchronize_session=False)
    )
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.expire_all()
    run = db.get(AgentRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    return run, claimed == 1


def _decision_in_progress(run_id: str) -> HTTPException:
    return HTTPException(
        status_code=409,
        detail=f"Run '{run_id}' already has a human decision in progress.",
    )


@router.post("/{agent_type}/runs", response_model=AgentRunResponse, status_code=201)
def create_run(
    agent_type: str,
    body: dict[str, Any],
    db: Session = Depends(get_db),
) -> AgentRunResponse:
    template_config = _get_template_config(agent_type)
    run = AgentRun(
        id=str(uuid.uuid4()),
        agent_type=agent_type,
        status="running",
        intake_data=body,
    )
    db.add(run)
    _append_audit_event(run, "REQUEST_RECEIVED", actor="user", payload={"agent_type": agent_type})
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
        _append_audit_event(run, "CLARIFICATION_REQUIRED", payload={"missing_fields": run.missing_fields})
    else:
        _append_audit_event(run, "VALIDATION_PASSED")
        if run.normalized_data is not None:
            _append_audit_event(run, "NORMALIZED")

    if agent_type == controlled_rag_agent.AGENT_TYPE:
        rag_answer = final_state.get("rag_answer")
        run.raw_llm_output = {
            "rag_answer": rag_answer,
            "tool_plan": final_state.get("tool_plan"),
            "human_review_required": final_state.get("human_review_required", False),
            "review_status": final_state.get("review_status"),
            "final_status": final_state.get("final_status"),
        }
        if rag_answer is not None:
            _append_audit_event(run, "RAG_RETRIEVED", payload=_retrieval_audit_payload(rag_answer))
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


@router.get("/runs/recovery-queue")
def get_recovery_queue(db: Session = Depends(get_db)) -> list[AgentRunResponse]:
    runs = (
        db.query(AgentRun)
        .filter(
            AgentRun.status.in_(
                {"approval_executing", "rejection_processing", "decision_recovery_required"}
            )
        )
        .order_by(AgentRun.created_at.asc(), AgentRun.id.asc())
        .all()
    )
    return [_run_to_response(run) for run in runs]


@router.get("/runs/{run_id}", response_model=AgentRunResponse)
def get_run(run_id: str, db: Session = Depends(get_db)) -> AgentRunResponse:
    run = db.get(AgentRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    return _run_to_response(run)


@router.get("/runs/{run_id}/events")
def get_run_events(run_id: str, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    run = db.get(AgentRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    return [_audit_event_to_response(event) for event in run.audit_events]


@router.get("/runs/{run_id}/evidence")
def get_run_evidence(run_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    run = db.get(AgentRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    return _run_evidence_bundle(run)


@router.post("/runs/{run_id}/recover-decision", response_model=AgentRunResponse)
def recover_interrupted_decision(
    run_id: str,
    db: Session = Depends(get_db),
) -> AgentRunResponse:
    run = db.get(AgentRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    if run.status == "decision_recovery_required":
        return _run_to_response(run)
    if run.status not in {"approval_executing", "rejection_processing"}:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Run '{run_id}' cannot be quarantined because its status is "
                f"'{run.status}'."
            ),
        )
    prior_status = run.status
    run.status = "decision_recovery_required"
    _append_audit_event(
        run,
        "DECISION_RECOVERY_REQUIRED",
        actor="operator",
        payload={"prior_status": prior_status},
    )
    _commit_and_refresh(db, run)
    return _run_to_response(run)


@router.post("/runs/{run_id}/approve", response_model=AgentRunResponse)
def approve_run(
    run_id: str,
    body: ApproveRequest,
    db: Session = Depends(get_db),
) -> AgentRunResponse:
    run = db.get(AgentRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    raw_output = dict(run.raw_llm_output or {})
    review_status = raw_output.get("review_status")
    if run.status != "pending_approval":
        if review_status == "approved":
            return _run_to_response(run)
        if review_status == "rejected":
            raise HTTPException(status_code=409, detail=f"Run '{run_id}' was already rejected and cannot be approved.")
        if run.status in {"approval_executing", "rejection_processing"}:
            raise _decision_in_progress(run_id)
        raise HTTPException(
            status_code=422,
            detail=f"Run '{run_id}' cannot be approved because its status is '{run.status}'. Only 'pending_approval' runs can be approved.",
        )

    run, claimed = _claim_pending_decision(db, run_id, "approval_executing")
    if not claimed:
        raw_output = dict(run.raw_llm_output or {})
        review_status = raw_output.get("review_status")
        if review_status == "approved":
            return _run_to_response(run)
        if review_status == "rejected":
            raise HTTPException(status_code=409, detail=f"Run '{run_id}' was already rejected and cannot be approved.")
        raise _decision_in_progress(run_id)

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
        run.status = "pending_approval"
        _commit_and_refresh(db, run)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception:
        run.status = "pending_approval"
        _commit_and_refresh(db, run)
        raise

    raw_output = dict(run.raw_llm_output or {})
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
    run = db.get(AgentRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    raw_output = dict(run.raw_llm_output or {})
    review_status = raw_output.get("review_status")
    if run.status != "pending_approval":
        if review_status == "rejected":
            return _run_to_response(run)
        if review_status == "approved":
            raise HTTPException(status_code=409, detail=f"Run '{run_id}' was already approved and cannot be rejected.")
        if run.status in {"approval_executing", "rejection_processing"}:
            raise _decision_in_progress(run_id)
        raise HTTPException(
            status_code=422,
            detail=f"Run '{run_id}' cannot be rejected because its status is '{run.status}'. Only 'pending_approval' runs can be rejected.",
        )

    run, claimed = _claim_pending_decision(db, run_id, "rejection_processing")
    if not claimed:
        raw_output = dict(run.raw_llm_output or {})
        review_status = raw_output.get("review_status")
        if review_status == "rejected":
            return _run_to_response(run)
        if review_status == "approved":
            raise HTTPException(status_code=409, detail=f"Run '{run_id}' was already approved and cannot be rejected.")
        raise _decision_in_progress(run_id)

    raw_output = dict(run.raw_llm_output or {})
    run.status = "rejected"
    run.reviewer_note = body.reason
    for draft in run.action_drafts:
        draft.is_approved = False
    raw_output["review_status"] = "rejected"
    raw_output["final_status"] = "rejected"
    raw_output.pop("execution_result", None)
    run.raw_llm_output = raw_output
    _append_audit_event(run, "REJECTED", actor="human", payload={"reason": body.reason})
    _append_audit_event(run, "COMPLETED", payload={"status": run.status})
    _commit_and_refresh(db, run)
    return _run_to_response(run)
