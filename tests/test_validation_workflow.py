from __future__ import annotations

import unittest
from typing import Any

from app.agents.workflow import workflow
from app.templates import freelance


def run_validation_workflow(intake_data: dict[str, Any]) -> dict[str, Any]:
    template_config = {
        "required_fields": freelance.REQUIRED_FIELDS,
        "optional_fields": freelance.OPTIONAL_FIELDS,
        "clarification_map": freelance.CLARIFICATION_MAP,
    }
    return workflow.invoke(
        {
            "run_id": "test-run",
            "agent_type": freelance.AGENT_TYPE,
            "intake_data": intake_data,
            "template_config": template_config,
            "missing_fields": [],
            "clarification_questions": [],
            "action_drafts": [],
            "status": "pending",
        }
    )


class ValidationWorkflowTests(unittest.TestCase):
    def test_complete_required_fields_returns_validated(self) -> None:
        result = run_validation_workflow(
            {
                "opportunity_title": "Build a React dashboard",
                "client_description": "Early-stage fintech startup",
                "project_description": "Dashboard with MRR and churn charts",
            }
        )

        self.assertEqual(result["status"], "validated")
        self.assertEqual(result["missing_fields"], [])
        self.assertEqual(result["clarification_questions"], [])
        self.assertEqual(result["action_drafts"], [])

    def test_missing_required_fields_returns_needs_clarification(self) -> None:
        result = run_validation_workflow(
            {
                "opportunity_title": "Build a React dashboard",
                "client_description": None,
            }
        )

        self.assertEqual(result["status"], "needs_clarification")
        self.assertEqual(
            result["missing_fields"],
            ["client_description", "project_description"],
        )

    def test_whitespace_only_required_field_is_missing(self) -> None:
        result = run_validation_workflow(
            {
                "opportunity_title": "Build a React dashboard",
                "client_description": "Early-stage fintech startup",
                "project_description": "   \t\n",
            }
        )

        self.assertEqual(result["status"], "needs_clarification")
        self.assertEqual(result["missing_fields"], ["project_description"])

    def test_optional_fields_are_not_required(self) -> None:
        result = run_validation_workflow(
            {
                "opportunity_title": "Build a React dashboard",
                "client_description": "Early-stage fintech startup",
                "project_description": "Dashboard with MRR and churn charts",
                "budget_range": "",
                "timeline": None,
                "required_skills": [],
            }
        )

        self.assertEqual(result["status"], "validated")
        self.assertEqual(result["missing_fields"], [])

    def test_missing_fields_have_clear_deterministic_questions(self) -> None:
        result = run_validation_workflow({})

        self.assertEqual(result["status"], "needs_clarification")
        self.assertEqual(result["missing_fields"], freelance.REQUIRED_FIELDS)
        self.assertEqual(
            result["clarification_questions"],
            [
                {
                    "field": field,
                    "question": freelance.CLARIFICATION_MAP[field],
                }
                for field in freelance.REQUIRED_FIELDS
            ],
        )


if __name__ == "__main__":
    unittest.main()
