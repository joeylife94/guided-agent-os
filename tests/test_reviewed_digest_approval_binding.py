from __future__ import annotations

import hashlib
import json
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes import router
from app.models.database import Base, get_db
from app.models.models import AgentRun
from app.operator_evidence_ui import operator_workspace_with_evidence


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


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function() -> None:
    Base.metadata.drop_all(bind=engine)


def _seed_pending_run(run_id: str) -> str:
    db = TestingSessionLocal()
    try:
        run = AgentRun(
            id=run_id,
            agent_type="controlled_rag_agent",
            status="pending_approval",
            intake_data={
                "user_request": "Look up LEG-001",
                "business_context": "Reviewed digest binding proof",
                "data_sources": ["tool_catalog"],
                "expected_output": "Approved read-only result",
                "risk_level": "internal",
                "allowed_tools": ["legacy_db_lookup"],
                "tool_parameters": {"record_id": "LEG-001"},
            },
            raw_llm_output={
                "tool_plan": {
                    "requires_tool_or_api": True,
                    "recommended_tools": [{"name": "legacy_db_lookup"}],
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


def _expected_digest() -> str:
    snapshot = {
        "tool_name": "legacy_db_lookup",
        "tool_parameters": {"record_id": "LEG-001"},
        "allowed_tools": ["legacy_db_lookup"],
    }
    canonical = json.dumps(
        snapshot,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _events(run_id: str) -> list[dict]:
    response = client.get(f"/api/agents/runs/{run_id}/events")
    assert response.status_code == 200
    return response.json()


def test_approve_requires_reviewed_execution_input_digest_before_executor() -> None:
    run_id = _seed_pending_run("run-missing-reviewed-digest")

    with patch("app.api.routes.execute_approved_tool") as executor:
        response = client.post(
            f"/api/agents/runs/{run_id}/approve",
            json={"note": "Approve without reviewed digest must fail closed"},
        )

    assert response.status_code == 409
    executor.assert_not_called()
    persisted = client.get(f"/api/agents/runs/{run_id}").json()
    assert persisted["status"] == "pending_approval"
    assert all(event["event_type"] != "TOOL_EXECUTED" for event in _events(run_id))


def test_approve_rejects_mismatched_reviewed_digest_before_executor() -> None:
    run_id = _seed_pending_run("run-mismatched-reviewed-digest")

    with patch("app.api.routes.execute_approved_tool") as executor:
        response = client.post(
            f"/api/agents/runs/{run_id}/approve",
            json={
                "note": "Approve with stale reviewed digest",
                "expected_execution_inputs_digest": "0" * 64,
            },
        )

    assert response.status_code == 409
    executor.assert_not_called()
    persisted = client.get(f"/api/agents/runs/{run_id}").json()
    assert persisted["status"] == "pending_approval"
    assert all(event["event_type"] != "TOOL_EXECUTED" for event in _events(run_id))


def test_approve_accepts_matching_reviewed_digest_and_preserves_audit_correlation() -> None:
    run_id = _seed_pending_run("run-matching-reviewed-digest")
    expected_digest = _expected_digest()

    response = client.post(
        f"/api/agents/runs/{run_id}/approve",
        json={
            "note": "Approve exact reviewed digest",
            "expected_execution_inputs_digest": expected_digest,
        },
    )

    assert response.status_code == 200
    events = _events(run_id)
    approved = next(event for event in events if event["event_type"] == "APPROVED")
    executed = next(event for event in events if event["event_type"] == "TOOL_EXECUTED")
    assert approved["payload"]["execution_inputs_digest"] == expected_digest
    assert executed["payload"]["execution_inputs_digest"] == expected_digest


def test_operator_approval_payload_is_bound_to_displayed_reviewed_digest() -> None:
    html = operator_workspace_with_evidence().body.decode("utf-8")

    assert 'id="execution-inputs-digest"' in html
    assert "currentReviewedExecutionInputsDigest = digest" in html
    assert "expected_execution_inputs_digest: currentReviewedExecutionInputsDigest" in html
    assert "approveButton.disabled = true" in html
