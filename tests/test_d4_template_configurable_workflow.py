"""D4-01 acceptance contract for template-configurable controlled workflow routing.

These tests intentionally exercise the workflow through template-owned configuration,
not agent-type identity. They define the smallest D4 routing contract while reusing
the existing controlled workflow nodes and preserving intake-only behavior.
"""

from unittest.mock import patch

from app.agents.workflow import workflow
from app.api.routes import _get_template_config


CONTROLLED_PROFILE = {
    "name": "controlled_rag",
    "stages": ["rag_answer", "tool_plan", "human_review"],
}


def _controlled_input() -> dict:
    return {
        "user_request": "What is the legacy database access policy?",
        "business_context": "Operations team needs guidance.",
        "data_sources": ["domain_knowledge", "agent_policy", "tool_catalog"],
        "expected_output": "Grounded answer with execution plan.",
        "risk_level": "internal",
    }


def _fake_rag_answer(*_args, **_kwargs) -> dict:
    return {
        "question": "What is the legacy database access policy?",
        "answer": "Use the reviewed read-only path. SOURCE [agent_policy:test:chunk-0]",
        "citations": [{"source_path": "knowledge/agent_policy.md"}],
        "retrieved_context": {
            "agent_policy": [
                {"doc_id": "test", "chunk_id": "chunk-0", "text": "reviewed read-only path"}
            ]
        },
        "limitations": [],
        "model": {"provider": "local", "name": "test-local", "available": True},
    }


def test_registered_controlled_template_exposes_execution_profile():
    config = _get_template_config("controlled_rag_agent")
    assert config["execution_profile"] == CONTROLLED_PROFILE


def test_distinct_agent_type_can_select_generic_controlled_workflow_by_profile():
    config = _get_template_config("controlled_rag_agent")
    state = {
        "agent_type": "d4_distinct_test_template",
        "intake_data": _controlled_input(),
        "template_config": config,
        "status": "pending",
    }

    with patch("app.services.rag_answerer.generate_rag_answer", side_effect=_fake_rag_answer):
        result = workflow.invoke(state)

    assert result["status"] == "pending_approval"
    assert result["human_review_required"] is True
    assert result["rag_answer"]["model"]["available"] is True
    assert "tool_plan" in result


def test_intake_only_template_remains_intake_only():
    config = _get_template_config("freelance")
    assert config["execution_profile"] == {"name": "intake_only", "stages": []}

    state = {
        "agent_type": "freelance",
        "intake_data": {
            "opportunity_title": "Build a dashboard",
            "client_description": "Synthetic client",
            "project_description": "Synthetic analytics dashboard",
        },
        "template_config": config,
        "status": "pending",
    }
    result = workflow.invoke(state)

    assert result["status"] == "validated"
    assert result.get("rag_answer") is None
    assert result.get("tool_plan") is None


def test_missing_execution_profile_fails_closed():
    state = {
        "agent_type": "d4_missing_profile",
        "intake_data": _controlled_input(),
        "template_config": {
            "required_fields": list(_controlled_input()),
            "optional_fields": [],
            "clarification_map": {},
        },
        "status": "pending",
    }

    result = workflow.invoke(state)

    assert result["status"] == "error"
    assert "execution_profile" in result.get("error", "")
    assert result.get("rag_answer") is None
    assert result.get("tool_plan") is None


def test_invalid_controlled_execution_profile_fails_closed():
    state = {
        "agent_type": "d4_invalid_profile",
        "intake_data": _controlled_input(),
        "template_config": {
            "required_fields": list(_controlled_input()),
            "optional_fields": [],
            "clarification_map": {},
            "execution_profile": {"name": "controlled_rag", "stages": ["rag_answer"]},
        },
        "status": "pending",
    }

    result = workflow.invoke(state)

    assert result["status"] == "error"
    assert "execution_profile" in result.get("error", "")
    assert result.get("tool_plan") is None
