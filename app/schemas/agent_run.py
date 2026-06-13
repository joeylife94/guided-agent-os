from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ClarificationQuestion(BaseModel):
    field: str = Field(..., description="Name of the missing or unclear field.")
    question: str = Field(..., description="Question to ask the user to fill the gap.")


class ActionDraft(BaseModel):
    action_type: str = Field(..., description="Category of action (e.g. 'reply', 'proposal').")
    title: str = Field(..., description="Short label for this action draft.")
    content: str = Field(..., description="Draft content ready for human review and editing.")


class AgentRunResponse(BaseModel):
    """Response returned for every agent run operation."""

    run_id: str = Field(..., description="Unique identifier for this agent run.")
    agent_type: str = Field(..., description="Type of agent that was run (e.g. 'freelance').")
    status: str = Field(
        ...,
        description=(
            "Current run status. One of: pending, running, needs_clarification, "
            "validated, pending_approval, approved, rejected, archived, error."
        ),
    )
    clarification_questions: list[ClarificationQuestion] = Field(
        default_factory=list,
        description="Questions generated when required fields are missing.",
    )
    analysis_summary: Optional[str] = Field(
        default=None,
        description="High-level summary produced by a future analysis node.",
    )
    score: Optional[float] = Field(
        default=None,
        ge=0,
        le=10,
        description="Future opportunity score from 0 (avoid) to 10 (ideal fit).",
    )
    action_drafts: list[ActionDraft] = Field(
        default_factory=list,
        description="Action drafts ready for human review.",
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if the run failed.",
    )
    created_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the run was created.",
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp of the most recent status change.",
    )
    raw_output: Optional[dict[str, Any]] = Field(
        default=None,
        description="Full structured output from the workflow for debugging.",
    )

    model_config = {"from_attributes": True}


class ApproveRequest(BaseModel):
    """Optional note attached to an approval."""

    note: Optional[str] = Field(default=None, description="Reviewer note for the approval.")


class RejectRequest(BaseModel):
    """Required reason for rejecting a run."""

    reason: str = Field(..., description="Why this run is being rejected.")
