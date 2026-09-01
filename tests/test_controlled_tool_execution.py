from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes import router
from app.models.database import Base, get_db
from app.models.models import AgentRun
from app.services.tool_executor import (
    ToolExecutionError,
    execute_approved_tool,
    registered_tool_names,
)
from tests.approval_digest_helper import approval_body


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


def _plan(tool_name: str = "legacy_db_lookup") -> dict:
    return {
        "requires_tool_or_api": True,
        "execution_mode": "planned_only",
        "allowed_to_execute": False,
        "recommended_tools": [
            {
                "name": tool_name,
                "purpose": "Controlled fixture lookup",
                "requires_approval": True,
                "reason": "Internal read-only lookup requires human approval.",
            }
        ],
        "blocked_actions": ["direct_sql_execution", "direct_database_write"],
        "approval_required": True,
        "reason": "Human review required.",
    }


def _seed_pending_run(
    *,
    tool_name: str = "legacy_db_lookup",
    allowed_tools=None,
    tool_parameters=None,
) -> str:
    db = TestingSessionLocal()
    try:
        run = AgentRun(
            id="run-controlled-tool",
            agent_type="controlled_rag_agent",
            status="pending_approval",
            intake_data={
                "user_request": "Look up legacy database record LEG-001",
                "business_context": "Operations proof flow",
                "data_sources": ["tool_catalog"],
                "expected_output": "Approved read-only result",
                "risk_level": "internal",
                "allowed_tools": (
                    ["legacy_db_lookup"] if allowed_tools is None else allowed_tools
                ),
                "tool_parameters": (
                    {"record_id": "LEG-001"}
                    if tool_parameters is None
                    else tool_parameters
                ),
            },
            raw_llm_output={
                "tool_plan": _plan(tool_name),
                "human_review_required": True,
                "review_status": "pending_approval",
                "final_status": "pending_approval",
            },
        )
        db.add(run)
        db.commit()
        return run.id
    finally:
        db.close()


def _event_types(run_id: str) -> list[str]:
    response = client.get(f"/api/agents/runs/{run_id}/events")
    assert response.status_code == 200
    return [event["event_type"] for event in response.json()]


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function() -> None:
    Base.metadata.drop_all(bind=engine)


def test_registry_contains_only_proof_read_only_tool() -> None:
    assert registered_tool_names() == ("legacy_db_lookup",)


def test_no_approval_blocks_execution() -> None:
    try:
        execute_approved_tool(
            tool_name="legacy_db_lookup",
            parameters={"record_id": "LEG-001"},
            approved=False,
            allowed_tools=["legacy_db_lookup"],
        )
    except ToolExecutionError as exc:
        assert "approval" in str(exc).lower()
    else:
        raise AssertionError("execution must not occur without human approval")


def test_approve_executes_allowlisted_read_only_tool_and_persists_result() -> None:
    run_id = _seed_pending_run()

    response = client.post(
        f"/api/agents/runs/{run_id}/approve",
        json=approval_body("Approved for controlled proof lookup"),
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "archived"
    assert payload["review_status"] == "approved"
    execution = payload["raw_output"]["execution_result"]
    assert execution["status"] == "executed"
    assert execution["tool_name"] == "legacy_db_lookup"
    assert execution["read_only"] is True
    assert execution["parameters"] == {"record_id": "LEG-001"}
    assert execution["result"]["found"] is True
    assert execution["result"]["record"]["record_id"] == "LEG-001"

    persisted = client.get(f"/api/agents/runs/{run_id}")
    assert persisted.status_code == 200
    persisted_execution = persisted.json()["raw_output"]["execution_result"]
    assert persisted_execution == execution


def test_reject_blocks_execution_and_persists_rejection() -> None:
    run_id = _seed_pending_run()

    response = client.post(
        f"/api/agents/runs/{run_id}/reject",
        json={"reason": "Do not access the internal record"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "rejected"
    assert payload["review_status"] == "rejected"
    assert "execution_result" not in payload["raw_output"]

    persisted = client.get(f"/api/agents/runs/{run_id}").json()
    assert persisted["status"] == "rejected"
    assert "execution_result" not in persisted["raw_output"]


def test_duplicate_approval_is_idempotent_and_does_not_repeat_terminal_events() -> None:
    run_id = _seed_pending_run()
    first = client.post(
        f"/api/agents/runs/{run_id}/approve",
        json=approval_body("Approved once"),
    )
    assert first.status_code == 200
    first_execution = first.json()["raw_output"]["execution_result"]

    replay = client.post(
        f"/api/agents/runs/{run_id}/approve",
        json={"note": "Retry of the same decision"},
    )
    assert replay.status_code == 200
    assert replay.json()["status"] == "archived"
    assert replay.json()["review_status"] == "approved"
    assert replay.json()["raw_output"]["execution_result"] == first_execution

    events = _event_types(run_id)
    assert events.count("APPROVED") == 1
    assert events.count("TOOL_EXECUTED") == 1
    assert events.count("COMPLETED") == 1


def test_duplicate_rejection_is_idempotent_and_does_not_repeat_terminal_events() -> None:
    run_id = _seed_pending_run()
    first = client.post(
        f"/api/agents/runs/{run_id}/reject",
        json={"reason": "Reject once"},
    )
    assert first.status_code == 200

    replay = client.post(
        f"/api/agents/runs/{run_id}/reject",
        json={"reason": "Retry of the same decision"},
    )
    assert replay.status_code == 200
    assert replay.json()["status"] == "rejected"
    assert replay.json()["review_status"] == "rejected"
    assert "execution_result" not in replay.json()["raw_output"]

    events = _event_types(run_id)
    assert events.count("REJECTED") == 1
    assert events.count("TOOL_EXECUTED") == 0
    assert events.count("COMPLETED") == 1


def test_reject_after_approval_is_conflict_and_preserves_approved_result() -> None:
    run_id = _seed_pending_run()
    approved = client.post(
        f"/api/agents/runs/{run_id}/approve",
        json=approval_body(),
    )
    assert approved.status_code == 200
    execution = approved.json()["raw_output"]["execution_result"]

    conflict = client.post(
        f"/api/agents/runs/{run_id}/reject",
        json={"reason": "Conflicting later decision"},
    )
    assert conflict.status_code == 409

    persisted = client.get(f"/api/agents/runs/{run_id}").json()
    assert persisted["status"] == "archived"
    assert persisted["review_status"] == "approved"
    assert persisted["raw_output"]["execution_result"] == execution
    events = _event_types(run_id)
    assert events.count("APPROVED") == 1
    assert events.count("REJECTED") == 0
    assert events.count("TOOL_EXECUTED") == 1
    assert events.count("COMPLETED") == 1


def test_approve_after_rejection_is_conflict_and_never_executes_tool() -> None:
    run_id = _seed_pending_run()
    rejected = client.post(
        f"/api/agents/runs/{run_id}/reject",
        json={"reason": "Reject first"},
    )
    assert rejected.status_code == 200

    conflict = client.post(f"/api/agents/runs/{run_id}/approve", json={})
    assert conflict.status_code == 409

    persisted = client.get(f"/api/agents/runs/{run_id}").json()
    assert persisted["status"] == "rejected"
    assert persisted["review_status"] == "rejected"
    assert "execution_result" not in persisted["raw_output"]
    events = _event_types(run_id)
    assert events.count("APPROVED") == 0
    assert events.count("REJECTED") == 1
    assert events.count("TOOL_EXECUTED") == 0
    assert events.count("COMPLETED") == 1


def test_unregistered_planned_tool_is_blocked() -> None:
    run_id = _seed_pending_run(
        tool_name="policy_lookup",
        allowed_tools=["policy_lookup"],
    )

    response = client.post(f"/api/agents/runs/{run_id}/approve", json={})
    assert response.status_code == 422
    assert "not registered" in response.json()["detail"]

    persisted = client.get(f"/api/agents/runs/{run_id}").json()
    assert persisted["status"] == "pending_approval"
    assert "execution_result" not in persisted["raw_output"]


def test_registered_tool_not_explicitly_allowed_for_run_is_blocked() -> None:
    run_id = _seed_pending_run(allowed_tools=[])

    response = client.post(f"/api/agents/runs/{run_id}/approve", json={})
    assert response.status_code == 422
    assert "not explicitly allowed" in response.json()["detail"]

    persisted = client.get(f"/api/agents/runs/{run_id}").json()
    assert persisted["status"] == "pending_approval"
    assert "execution_result" not in persisted["raw_output"]


def test_invalid_parameters_are_blocked() -> None:
    run_id = _seed_pending_run(tool_parameters={"unexpected": "value"})

    response = client.post(f"/api/agents/runs/{run_id}/approve", json={})
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert "required tool parameters" in detail.lower() or "unexpected" in detail.lower()

    persisted = client.get(f"/api/agents/runs/{run_id}").json()
    assert persisted["status"] == "pending_approval"
    assert "execution_result" not in persisted["raw_output"]
