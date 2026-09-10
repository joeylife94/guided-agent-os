from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes import router
from app.models.database import Base, get_db
from app.models.models import AgentRun
from app.services.tool_executor import ToolExecutionError, execute_approved_tool, registered_tool_names
from tests.approval_digest_helper import DEFAULT_REVIEWER_ID, approval_body


engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
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


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function() -> None:
    Base.metadata.drop_all(bind=engine)


def _seed_policy_run(*, allowed_tools: list[str] | None = None, parameters: dict | None = None) -> str:
    db = TestingSessionLocal()
    try:
        run = AgentRun(
            id="run-d6-policy-lookup",
            agent_type="controlled_rag_agent",
            status="pending_approval",
            intake_data={
                "user_request": "Look up repository policy POL-READ-001",
                "business_context": "D6 policy isolation acceptance",
                "data_sources": ["tool_catalog"],
                "expected_output": "Approved read-only policy result",
                "risk_level": "internal",
                "allowed_tools": ["policy_lookup"] if allowed_tools is None else allowed_tools,
                "tool_parameters": {"policy_id": "POL-READ-001"} if parameters is None else parameters,
            },
            raw_llm_output={
                "tool_plan": {
                    "requires_tool_or_api": True,
                    "execution_mode": "planned_only",
                    "allowed_to_execute": False,
                    "recommended_tools": [{
                        "name": "policy_lookup",
                        "purpose": "Retrieve repository-owned policy fixture",
                        "requires_approval": True,
                        "reason": "Read-only policy lookup requires explicit review.",
                    }],
                    "blocked_actions": ["direct_database_write"],
                    "approval_required": True,
                    "reason": "Human review required.",
                },
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


def test_two_materially_distinct_read_only_tools_are_registered() -> None:
    assert registered_tool_names() == ("legacy_db_lookup", "policy_lookup")
    legacy = execute_approved_tool(
        tool_name="legacy_db_lookup",
        parameters={"record_id": "LEG-001"},
        approved=True,
        allowed_tools=["legacy_db_lookup"],
    )
    policy = execute_approved_tool(
        tool_name="policy_lookup",
        parameters={"policy_id": "POL-READ-001"},
        approved=True,
        allowed_tools=["policy_lookup"],
    )
    assert legacy["read_only"] is True and policy["read_only"] is True
    assert legacy["parameters"] == {"record_id": "LEG-001"}
    assert policy["parameters"] == {"policy_id": "POL-READ-001"}
    assert policy["result"]["policy"]["decision"] == "read_only_tools_require_explicit_human_approval"


def test_cross_tool_policy_does_not_leak_authority() -> None:
    for tool_name, parameters, allowed_tools in [
        ("policy_lookup", {"policy_id": "POL-READ-001"}, ["legacy_db_lookup"]),
        ("legacy_db_lookup", {"record_id": "LEG-001"}, ["policy_lookup"]),
    ]:
        try:
            execute_approved_tool(
                tool_name=tool_name,
                parameters=parameters,
                approved=True,
                allowed_tools=allowed_tools,
            )
        except ToolExecutionError as exc:
            assert "not explicitly allowed" in str(exc)
        else:
            raise AssertionError("cross-tool policy must fail before handler execution")


def test_policy_tool_parameter_contract_fails_closed() -> None:
    for parameters in [{}, {"record_id": "LEG-001"}, {"policy_id": "   "}, {"policy_id": "POL-READ-001", "extra": "x"}]:
        try:
            execute_approved_tool(
                tool_name="policy_lookup",
                parameters=parameters,
                approved=True,
                allowed_tools=["policy_lookup"],
            )
        except ToolExecutionError:
            pass
        else:
            raise AssertionError(f"invalid policy parameters were accepted: {parameters!r}")


def test_policy_tool_approval_binds_reviewer_digest_and_persists_correlated_execution() -> None:
    run_id = _seed_policy_run()
    response = client.post(
        f"/api/agents/runs/{run_id}/approve",
        json=approval_body(
            "Approved exact policy lookup",
            reviewer_id=DEFAULT_REVIEWER_ID,
            tool_name="policy_lookup",
            tool_parameters={"policy_id": "POL-READ-001"},
            allowed_tools=["policy_lookup"],
        ),
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    execution = payload["raw_output"]["execution_result"]
    assert execution["tool_name"] == "policy_lookup"
    assert execution["parameters"] == {"policy_id": "POL-READ-001"}
    assert execution["result"]["found"] is True

    events = client.get(f"/api/agents/runs/{run_id}/events").json()
    approved = [event for event in events if event["event_type"] == "APPROVED"]
    executed = [event for event in events if event["event_type"] == "TOOL_EXECUTED"]
    assert len(approved) == 1 and len(executed) == 1
    assert approved[0]["actor"] == f"reviewer:{DEFAULT_REVIEWER_ID}"
    assert executed[0]["payload"]["tool_name"] == "policy_lookup"


def test_policy_run_cannot_execute_when_only_legacy_tool_is_allowed() -> None:
    run_id = _seed_policy_run(allowed_tools=["legacy_db_lookup"])
    response = client.post(
        f"/api/agents/runs/{run_id}/approve",
        json=approval_body(
            reviewer_id=DEFAULT_REVIEWER_ID,
            tool_name="policy_lookup",
            tool_parameters={"policy_id": "POL-READ-001"},
            allowed_tools=["legacy_db_lookup"],
        ),
    )
    assert response.status_code == 422
    assert "not explicitly allowed" in response.json()["detail"]
    persisted = client.get(f"/api/agents/runs/{run_id}").json()
    assert persisted["status"] == "pending_approval"
    assert "execution_result" not in persisted["raw_output"]
