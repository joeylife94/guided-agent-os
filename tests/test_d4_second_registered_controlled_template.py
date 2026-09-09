from __future__ import annotations

from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.agents.workflow import workflow
from app.api.routes import _get_template_config, router
from app.models.database import Base, get_db
from app.models.models import AgentRun
from tests.approval_digest_helper import DEFAULT_REVIEWER_ID, approval_body


CONTROLLED_PROFILE = {
    "name": "controlled_rag",
    "stages": ["rag_answer", "tool_plan", "human_review"],
}


def _public_enterprise_input() -> dict:
    return {
        "user_request": "What is the reviewed legacy database access policy?",
        "use_case_title": "Operations policy assistant",
        "business_domain": "infrastructure operations",
        "target_user_group": "operations analysts",
        "current_workflow_problem": "Analysts manually search policy and legacy-system guidance.",
        "data_sources": ["domain_knowledge", "agent_policy", "tool_catalog"],
        "expected_agent_capabilities": "Grounded policy answer and reviewed read-only lookup plan.",
        "allowed_tools": ["legacy_db_lookup"],
        "tool_parameters": {"record_id": "LEG-001"},
    }


def _fake_rag_answer(*_args, **_kwargs) -> dict:
    return {
        "question": "What is the reviewed legacy database access policy?",
        "answer": "Use only the approved read-only lookup path. SOURCE [agent_policy:d4-public:chunk-0]",
        "citations": [{"source_path": "knowledge/agent_policy.md"}],
        "retrieved_context": {
            "agent_policy": [
                {
                    "doc_id": "d4-public",
                    "chunk_id": "chunk-0",
                    "text": "Legacy lookup is read-only and requires explicit human approval.",
                }
            ]
        },
        "limitations": [],
        "model": {"provider": "local", "name": "test-local", "available": True},
    }


def _fake_guidance_rag_answer(*_args, **_kwargs) -> dict:
    return {
        "question": "Summarize the maintenance guidance.",
        "answer": "Follow the documented maintenance interval. SOURCE [manuals:d4-public:chunk-0]",
        "citations": [{"source_path": "knowledge/manuals.md"}],
        "retrieved_context": {
            "manuals": [
                {
                    "doc_id": "d4-public",
                    "chunk_id": "chunk-0",
                    "text": "Follow the documented maintenance interval.",
                }
            ]
        },
        "limitations": [],
        "model": {"provider": "local", "name": "test-local", "available": True},
    }


def test_second_registered_template_uses_same_generic_controlled_profile() -> None:
    controlled = _get_template_config("controlled_rag_agent")
    public = _get_template_config("public_enterprise_ai")

    assert controlled["execution_profile"] == CONTROLLED_PROFILE
    assert public["execution_profile"] == CONTROLLED_PROFILE
    assert public["required_fields"] != controlled["required_fields"]
    assert "use_case_title" in public["required_fields"]
    assert "business_domain" in public["required_fields"]

    state = {
        "agent_type": "public_enterprise_ai",
        "intake_data": _public_enterprise_input(),
        "template_config": public,
        "status": "pending",
    }
    with patch("app.services.rag_answerer.generate_rag_answer", side_effect=_fake_rag_answer):
        result = workflow.invoke(state)

    assert result["status"] == "pending_approval"
    assert result["human_review_required"] is True
    assert result["rag_answer"]["retrieved_context"]["agent_policy"]
    assert result["rag_answer"]["citations"][0]["source_path"] == "knowledge/agent_policy.md"
    assert "SOURCE [agent_policy:d4-public:chunk-0]" in result["rag_answer"]["answer"]
    assert result["tool_plan"]["approval_required"] is True


def test_second_template_explicit_policy_constraints_cannot_bypass_review() -> None:
    public = _get_template_config("public_enterprise_ai")
    cases = [
        {"approval_policy": "human review required"},
        {"security_constraints": "restricted"},
    ]

    for policy_fields in cases:
        intake = _public_enterprise_input()
        intake.update(
            {
                "user_request": "Summarize the maintenance guidance.",
                "data_sources": ["manuals"],
                "allowed_tools": [],
                "tool_parameters": {},
                **policy_fields,
            }
        )
        state = {
            "agent_type": "public_enterprise_ai",
            "intake_data": intake,
            "template_config": public,
            "status": "pending",
        }
        with patch(
            "app.services.rag_answerer.generate_rag_answer",
            side_effect=_fake_guidance_rag_answer,
        ):
            result = workflow.invoke(state)

        assert result["tool_plan"]["requires_tool_or_api"] is False
        assert result["tool_plan"]["approval_required"] is True
        assert result["human_review_required"] is True
        assert result["review_status"] == "pending_approval"
        assert result["status"] == "pending_approval"


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app_under_test = FastAPI()
app_under_test.include_router(router)
app_under_test.dependency_overrides[get_db] = override_get_db
client = TestClient(app_under_test)


def _tool_plan() -> dict:
    return {
        "requires_tool_or_api": True,
        "execution_mode": "planned_only",
        "allowed_to_execute": False,
        "recommended_tools": [
            {
                "name": "legacy_db_lookup",
                "purpose": "Controlled read-only legacy lookup",
                "requires_approval": True,
                "reason": "Explicit reviewer approval is required.",
            }
        ],
        "blocked_actions": ["direct_sql_execution", "direct_database_write"],
        "approval_required": True,
        "reason": "Human review required.",
    }


def _seed_public_enterprise_run(run_id: str) -> None:
    db = TestingSessionLocal()
    try:
        intake = _public_enterprise_input()
        run = AgentRun(
            id=run_id,
            agent_type="public_enterprise_ai",
            status="pending_approval",
            intake_data=intake,
            raw_llm_output={
                "rag_answer": _fake_rag_answer(),
                "tool_plan": _tool_plan(),
                "human_review_required": True,
                "review_status": "pending_approval",
                "final_status": "pending_approval",
            },
        )
        db.add(run)
        db.commit()
    finally:
        db.close()


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function() -> None:
    Base.metadata.drop_all(bind=engine)


def test_second_template_reject_still_executes_no_tool() -> None:
    _seed_public_enterprise_run("run-d4-public-reject")

    response = client.post(
        "/api/agents/runs/run-d4-public-reject/reject",
        json={"reviewer_id": DEFAULT_REVIEWER_ID, "reason": "Reviewer rejects this lookup"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "rejected"
    assert payload["review_status"] == "rejected"
    assert "execution_result" not in payload["raw_output"]

    events = client.get("/api/agents/runs/run-d4-public-reject/events").json()
    event_types = [event["event_type"] for event in events]
    assert "REJECTED" in event_types
    assert "TOOL_EXECUTED" not in event_types


def test_second_template_approval_preserves_digest_gate_and_read_only_execution() -> None:
    _seed_public_enterprise_run("run-d4-public-approve")

    missing_digest = client.post(
        "/api/agents/runs/run-d4-public-approve/approve",
        json={"reviewer_id": DEFAULT_REVIEWER_ID, "note": "No reviewed digest"},
    )
    assert missing_digest.status_code == 409

    approved = client.post(
        "/api/agents/runs/run-d4-public-approve/approve",
        json=approval_body("Approved after reviewing public enterprise execution inputs"),
    )
    assert approved.status_code == 200
    payload = approved.json()
    assert payload["status"] == "archived"
    assert payload["review_status"] == "approved"

    execution = payload["raw_output"]["execution_result"]
    assert execution["status"] == "executed"
    assert execution["tool_name"] == "legacy_db_lookup"
    assert execution["read_only"] is True
    assert execution["parameters"] == {"record_id": "LEG-001"}

    persisted = client.get("/api/agents/runs/run-d4-public-approve").json()
    assert persisted["raw_output"]["execution_result"] == execution
    assert persisted["raw_output"]["rag_answer"]["retrieved_context"]["agent_policy"]

    events = client.get("/api/agents/runs/run-d4-public-approve/events").json()
    event_types = [event["event_type"] for event in events]
    assert "APPROVED" in event_types
    assert "TOOL_EXECUTED" in event_types
