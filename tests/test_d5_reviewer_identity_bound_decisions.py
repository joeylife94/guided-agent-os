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
                "business_context": "D5 reviewer identity proof",
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


def _seed_recovery_run(run_id: str) -> str:
    db = TestingSessionLocal()
    try:
        run = AgentRun(
            id=run_id,
            agent_type="controlled_rag_agent",
            status="approval_executing",
            intake_data={},
            raw_llm_output={"review_status": "pending_approval"},
        )
        db.add(run)
        db.commit()
        return run.id
    finally:
        db.close()


def _reviewed_digest() -> str:
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


def test_approval_binds_reviewer_identity_and_preserves_digest_correlation() -> None:
    run_id = _seed_pending_run("d5-approve-alice")
    digest = _reviewed_digest()

    response = client.post(
        f"/api/agents/runs/{run_id}/approve",
        json={
            "reviewer_id": "alice.local",
            "note": "Approved after exact-input review",
            "expected_execution_inputs_digest": digest,
        },
    )

    assert response.status_code == 200
    events = _events(run_id)
    approved = next(event for event in events if event["event_type"] == "APPROVED")
    executed = next(event for event in events if event["event_type"] == "TOOL_EXECUTED")
    assert approved["actor"] == "reviewer:alice.local"
    assert approved["payload"]["execution_inputs_digest"] == digest
    assert executed["payload"]["execution_inputs_digest"] == digest


def test_rejection_binds_a_distinct_reviewer_identity_without_tool_execution() -> None:
    run_id = _seed_pending_run("d5-reject-bob")

    response = client.post(
        f"/api/agents/runs/{run_id}/reject",
        json={
            "reviewer_id": "bob.local",
            "reason": "Policy review rejected this request",
        },
    )

    assert response.status_code == 200
    events = _events(run_id)
    rejected = next(event for event in events if event["event_type"] == "REJECTED")
    assert rejected["actor"] == "reviewer:bob.local"
    assert all(event["event_type"] != "TOOL_EXECUTED" for event in events)


def test_recovery_quarantine_binds_reviewer_identity() -> None:
    run_id = _seed_recovery_run("d5-recovery-carol")

    response = client.post(
        f"/api/agents/runs/{run_id}/recover-decision",
        json={"reviewer_id": "carol.local"},
    )

    assert response.status_code == 200
    events = _events(run_id)
    recovery = next(
        event for event in events if event["event_type"] == "DECISION_RECOVERY_REQUIRED"
    )
    assert recovery["actor"] == "reviewer:carol.local"


def test_missing_reviewer_identity_fails_closed_before_approval_execution() -> None:
    run_id = _seed_pending_run("d5-missing-reviewer")

    with patch("app.api.routes.execute_approved_tool") as executor:
        response = client.post(
            f"/api/agents/runs/{run_id}/approve",
            json={
                "note": "Identity missing",
                "expected_execution_inputs_digest": _reviewed_digest(),
            },
        )

    assert response.status_code == 422
    executor.assert_not_called()
    persisted = client.get(f"/api/agents/runs/{run_id}").json()
    assert persisted["status"] == "pending_approval"
    assert all(event["event_type"] != "APPROVED" for event in _events(run_id))


def test_blank_reviewer_identity_fails_closed_for_rejection() -> None:
    run_id = _seed_pending_run("d5-blank-reviewer")

    response = client.post(
        f"/api/agents/runs/{run_id}/reject",
        json={"reviewer_id": "   ", "reason": "Reject with blank identity"},
    )

    assert response.status_code == 422
    persisted = client.get(f"/api/agents/runs/{run_id}").json()
    assert persisted["status"] == "pending_approval"
    assert all(event["event_type"] != "REJECTED" for event in _events(run_id))
