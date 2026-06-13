from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class FreelanceIntakeRequest(BaseModel):
    """Intake form for a freelance opportunity evaluation."""

    opportunity_title: str = Field(
        ...,
        description="Short title or headline of the freelance opportunity.",
        examples=["Build a React dashboard for SaaS startup"],
    )
    client_description: str = Field(
        ...,
        description="Who is the client? Industry, size, and any relevant background.",
        examples=["Early-stage B2B SaaS startup with 5 employees in the fintech space"],
    )
    project_description: str = Field(
        ...,
        description="What work needs to be done? Scope, deliverables, and context.",
        examples=["Build an analytics dashboard with charts showing MRR, churn, and signups"],
    )
    budget_range: Optional[str] = Field(
        default=None,
        description="Estimated budget or rate (e.g. '$5,000–$8,000' or '$150/hr').",
        examples=["$5,000–$8,000"],
    )
    timeline: Optional[str] = Field(
        default=None,
        description="Expected timeline or deadline for the project.",
        examples=["6 weeks starting immediately"],
    )
    required_skills: Optional[list[str]] = Field(
        default=None,
        description="Skills or technologies the client listed as required.",
        examples=[["React", "TypeScript", "Recharts"]],
    )
    client_location: Optional[str] = Field(
        default=None,
        description="Client's location or timezone preferences.",
        examples=["San Francisco, CA (US timezone preferred)"],
    )
    contact_info: Optional[str] = Field(
        default=None,
        description="How/where you found this opportunity or client contact details.",
        examples=["Upwork posting ID 12345"],
    )
    additional_notes: Optional[str] = Field(
        default=None,
        description="Any other relevant context, red flags, or special considerations.",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "opportunity_title": "Build a React dashboard for SaaS startup",
                "client_description": "Early-stage B2B SaaS startup, 5 employees, fintech",
                "project_description": "Analytics dashboard with MRR, churn, and signup charts",
                "budget_range": "$5,000–$8,000",
                "timeline": "6 weeks",
                "required_skills": ["React", "TypeScript"],
                "client_location": "San Francisco, CA",
                "contact_info": "Upwork",
                "additional_notes": None,
            }
        }
    }


class IntakeRequest(BaseModel):
    """Generic wrapper that carries the raw intake payload for any agent type."""

    data: dict[str, Any] = Field(
        ...,
        description="Raw intake fields for the specific agent type.",
    )
