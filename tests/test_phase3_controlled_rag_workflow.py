"""
Tests for Phase 3: Controlled RAG Agent Workflow Integration

Tests cover:
1. controlled_rag_agent template exists and is registered
2. Missing required fields still produce clarification
3. Valid controlled RAG request runs through workflow nodes
4. RAG answer is generated
5. Tool plan is generated without executing anything
6. Human review routing works correctly
7. Local LLM unavailable fallback works
8. All Phase 3 outputs are persisted
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.agents.workflow import (
    AgentState,
    node_generate_rag_answer,
    node_generate_tool_plan,
    node_route_human_review,
    workflow,
)
from app.models.database import SessionLocal
from app.models.models import AgentRun
from app.services.tool_plan_generator import generate_tool_plan
from app.api.routes import create_run, _get_template_config


class TestControlledRAGAgentTemplate:
    """Test controlled_rag_agent template registration and configuration."""

    def test_template_registered(self):
        """Test that controlled_rag_agent template is registered."""
        config = _get_template_config("controlled_rag_agent")
        assert config is not None
        assert "required_fields" in config
        assert "clarification_map" in config

    def test_required_fields(self):
        """Test that controlled_rag_agent requires correct fields."""
        config = _get_template_config("controlled_rag_agent")
        assert config["required_fields"] == [
            "user_request",
            "business_context",
            "data_sources",
            "expected_output",
            "risk_level",
        ]

    def test_optional_fields(self):
        """Test that controlled_rag_agent has optional fields."""
        config = _get_template_config("controlled_rag_agent")
        optional = config.get("optional_fields", [])
        assert len(optional) > 0
        assert "data_sources" not in optional
        assert "risk_level" not in optional


class TestValidationAndClarification:
    """Test that validation and clarification still work with controlled_rag_agent."""

    def test_missing_required_fields_produces_clarification(self):
        """Test that missing required fields produce clarification questions."""
        incomplete_input = {
            "user_request": "What is the policy?",
            # Missing: business_context, expected_output
        }
        
        initial_state = {
            "agent_type": "controlled_rag_agent",
            "intake_data": incomplete_input,
            "template_config": _get_template_config("controlled_rag_agent"),
            "status": "pending",
        }
        
        result = workflow.invoke(initial_state)
        
        assert result["status"] == "needs_clarification"
        assert result["missing_fields"] == [
            "business_context",
            "data_sources",
            "expected_output",
            "risk_level",
        ]
        assert len(result["clarification_questions"]) > 0
        # Should NOT proceed to RAG/tool plan phases
        assert result.get("rag_answer") is None

    def test_complete_input_proceeds_past_clarification(self):
        """Test that complete input proceeds past clarification."""
        complete_input = {
            "user_request": "What is the policy for legacy database access?",
            "business_context": "Operations team needs guidance.",
            "data_sources": ["domain_knowledge", "agent_policy", "tool_catalog"],
            "expected_output": "Grounded answer with execution plan.",
            "risk_level": "internal",
        }
        
        initial_state = {
            "agent_type": "controlled_rag_agent",
            "intake_data": complete_input,
            "template_config": _get_template_config("controlled_rag_agent"),
            "status": "pending",
        }
        
        result = workflow.invoke(initial_state)
        
        # Should pass validation
        assert result["status"] != "needs_clarification"
        assert len(result["missing_fields"]) == 0


class TestGenerateRAGAnswerNode:
    """Test the RAG answer generation node."""

    def test_rag_answer_node_generates_answer(self):
        """Test that node calls RAG answerer and stores result."""
        state = {
            "intake_data": {
                "user_request": "Test question",
            },
            "normalized_data": {},
        }
        
        result = node_generate_rag_answer(state)
        
        # Should have rag_answer in result
        assert "rag_answer" in result
        assert "question" in result["rag_answer"]
        assert "answer" in result["rag_answer"]

    def test_rag_answer_node_fallback_on_error(self):
        """Test that node gracefully falls back if RAG fails."""
        state = {
            "intake_data": {},  # Missing user_request - will trigger graceful fallback
            "normalized_data": {},
        }
        
        result = node_generate_rag_answer(state)
        
        assert "rag_answer" in result
        # Should have a fallback answer
        assert result["rag_answer"]["answer"] is not None


class TestGenerateToolPlanNode:
    """Test the tool plan generation node."""

    def test_tool_plan_node_generates_plan(self):
        """Test that tool plan node generates a valid plan."""
        state = {
            "intake_data": {
                "user_request": "Query the legacy database",
            },
            "normalized_data": {
                "risk_level": "internal",
            },
            "rag_answer": {
                "answer": "The context is insufficient.",
            },
        }
        
        result = node_generate_tool_plan(state)
        
        assert "tool_plan" in result
        tool_plan = result["tool_plan"]
        assert "requires_tool_or_api" in tool_plan
        assert "execution_mode" in tool_plan
        assert tool_plan["execution_mode"] == "planned_only"
        assert tool_plan["allowed_to_execute"] is False

    def test_tool_plan_blocks_direct_execution(self):
        """Test that tool plan never allows direct execution."""
        state = {
            "intake_data": {
                "user_request": "Query the database",
            },
            "normalized_data": {},
            "rag_answer": {},
        }
        
        result = node_generate_tool_plan(state)
        tool_plan = result["tool_plan"]
        
        assert tool_plan["allowed_to_execute"] is False
        assert "direct_sql_execution" in tool_plan["blocked_actions"]
        assert "direct_database_write" in tool_plan["blocked_actions"]


class TestToolPlanGenerator:
    """Test the tool plan generator service."""

    def test_high_risk_requires_approval(self):
        """Test that high risk level requires approval."""
        plan = generate_tool_plan(
            user_request="Test request",
            normalized_data={"risk_level": "high"},
            rag_answer={},
        )
        
        assert plan["approval_required"] is True

    def test_internal_risk_requires_approval(self):
        """Test that internal risk level requires approval."""
        plan = generate_tool_plan(
            user_request="Test request",
            normalized_data={"risk_level": "internal"},
            rag_answer={},
        )
        
        assert plan["approval_required"] is True

    def test_database_query_detected_as_tool_needed(self):
        """Test that database queries are detected as needing tools."""
        plan = generate_tool_plan(
            user_request="Query the legacy database for records",
            normalized_data={},
            rag_answer={},
        )
        
        assert plan["requires_tool_or_api"] is True

    def test_insufficient_context_requires_approval(self):
        """Test that insufficient context requires approval."""
        plan = generate_tool_plan(
            user_request="Test request",
            normalized_data={},
            rag_answer={"answer": "The context is insufficient."},
        )
        
        assert plan["approval_required"] is True

    def test_informational_request_no_approval(self):
        """Test that simple informational requests may not need approval."""
        plan = generate_tool_plan(
            user_request="What is the general policy?",
            normalized_data={"risk_level": "low"},
            rag_answer={"answer": "Here is the general policy information..."},
        )
        
        assert plan["requires_tool_or_api"] is False
        assert plan["approval_required"] is False
        assert "reason" in plan

    def test_tool_api_db_requests_require_approval(self):
        """Tool, API, and database requests should route to human review."""
        requests = [
            "Call the inventory API for the latest record",
            "Use the approved tool to update the case",
            "Query the database for matching records",
        ]

        for user_request in requests:
            plan = generate_tool_plan(
                user_request=user_request,
                normalized_data={"risk_level": "low"},
                rag_answer={"answer": "Context is available."},
            )

            assert plan["requires_tool_or_api"] is True
            assert plan["approval_required"] is True
            assert plan["execution_mode"] == "planned_only"
            assert plan["allowed_to_execute"] is False

    def test_llm_unavailable_with_context_does_not_force_approval(self):
        """Low-risk informational fallback can complete without approval."""
        plan = generate_tool_plan(
            user_request="Summarize the source citation policy",
            normalized_data={"risk_level": "low"},
            rag_answer={
                "answer": (
                    "Local LLM is unavailable, so no generated answer was "
                    "produced. Retrieved local knowledge base context and "
                    "source metadata are returned for caller inspection."
                )
            },
        )

        assert plan["approval_required"] is False


class TestHumanReviewRouting:
    """Test the human review routing node."""

    def test_approval_required_routes_to_pending_approval(self):
        """Test that high-risk requests are routed to pending_approval."""
        state = {
            "tool_plan": {
                "approval_required": True,
            },
        }
        
        result = node_route_human_review(state)
        
        assert result["human_review_required"] is True
        assert result["review_status"] == "pending_approval"
        assert result["final_status"] == "pending_approval"
        assert result["status"] == "pending_approval"

    def test_no_approval_required_marks_completed(self):
        """Test that low-risk requests are marked as completed."""
        state = {
            "tool_plan": {
                "approval_required": False,
            },
        }
        
        result = node_route_human_review(state)
        
        assert result["human_review_required"] is False
        assert result["review_status"] == "not_required"
        assert result["final_status"] == "completed"
        assert result["status"] == "completed"


class TestWorkflowIntegration:
    """Test full workflow integration for controlled_rag_agent."""

    def test_complete_workflow_with_high_risk_requires_approval(self):
        """Test complete workflow for high-risk request requiring approval."""
        complete_input = {
            "user_request": "What is the legacy database access policy?",
            "business_context": "Operations team needs guidance.",
            "data_sources": ["domain_knowledge", "agent_policy", "tool_catalog"],
            "expected_output": "Policy and execution plan.",
            "risk_level": "internal",
        }
        
        initial_state = {
            "agent_type": "controlled_rag_agent",
            "intake_data": complete_input,
            "template_config": _get_template_config("controlled_rag_agent"),
            "status": "pending",
        }
        
        result = workflow.invoke(initial_state)
        
        # Should reach pending_approval for high-risk internal request
        assert result["status"] == "pending_approval"
        assert result["human_review_required"] is True
        assert "rag_answer" in result
        assert "tool_plan" in result

    def test_complete_workflow_persists_phase3_outputs(self):
        """Test that Phase 3 outputs are persisted in the database."""
        complete_input = {
            "user_request": "Test request",
            "business_context": "Test context",
            "data_sources": ["agent_policy"],
            "expected_output": "Test output",
            "risk_level": "low",
        }
        
        db: Session = SessionLocal()
        try:
            response = create_run("controlled_rag_agent", complete_input, db)
            
            # Check that run was created
            assert response.run_id is not None
            
            # Retrieve the run from DB
            run = db.get(AgentRun, response.run_id)
            assert run is not None
            
            # Check that Phase 3 outputs are in raw_llm_output
            raw_output = run.raw_llm_output or {}
            assert "rag_answer" in raw_output
            assert "tool_plan" in raw_output
            assert "human_review_required" in raw_output
            assert "review_status" in raw_output
            assert "final_status" in raw_output

            assert response.rag_answer == raw_output["rag_answer"]
            assert response.tool_plan == raw_output["tool_plan"]
            assert response.human_review_required == raw_output["human_review_required"]
            assert response.review_status == raw_output["review_status"]
            assert response.final_status == raw_output["final_status"]
        finally:
            db.close()


class TestExistingPhasesStillWork:
    """Test that existing Phase 1 and Phase 2 functionality still works."""

    def test_freelance_agent_still_works(self):
        """Test that existing freelance agent still works."""
        freelance_input = {
            "opportunity_title": "Build a React dashboard",
            "client_description": "SaaS startup",
            "project_description": "Analytics dashboard",
        }
        
        initial_state = {
            "agent_type": "freelance",
            "intake_data": freelance_input,
            "template_config": _get_template_config("freelance"),
            "status": "pending",
        }
        
        result = workflow.invoke(initial_state)
        
        # Should reach validated state
        assert result["status"] == "validated"
        assert len(result["missing_fields"]) == 0

    def test_normalization_still_works(self):
        """Test that input normalization still works."""
        complete_input = {
            "user_request": "Test with React and Python ",  # Note trailing space
            "business_context": "Test context",
            "data_sources": ["domain_knowledge"],
            "expected_output": "Test output",
            "risk_level": "low",
        }
        
        initial_state = {
            "agent_type": "controlled_rag_agent",
            "intake_data": complete_input,
            "template_config": _get_template_config("controlled_rag_agent"),
            "status": "pending",
        }
        
        result = workflow.invoke(initial_state)
        
        # Should have normalized data
        assert result.get("normalized_data") is not None
        assert result["normalized_data"]["user_request"] == "Test with React and Python"
        assert result["normalized_data"]["data_sources"] == ["domain_knowledge"]
        assert result["normalized_data"]["risk_level"] == "low"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
