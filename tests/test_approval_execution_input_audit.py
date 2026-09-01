from __future__ import annotations

import hashlib
import json

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes import router
from app.models.database import Base, get_db
from app.models.models import AgentRun
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


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function() -> None:
    Base.metadata.drop_all(bind=engine)


def _seed_pending_run() -> str:
    db = TestingSessionLocal()
    try:
        run = AgentRun(
            id="run-approval-input-audit",
            agent_type="controlled_rag_agent",
            status="pending_approval",
            intake_data={
                "user_request": "Look up LEG-001",
                "business_context": "Audit proof",
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


def _event(run_id: str, event_type: str) -> dict:
    response = client.get(f"/api/agents/runs/{run_id}/events")
    assert response.status_code == 200
    return next(event for event in response.json() if event["event_type"] == event_type)


def test_approval_and_tool_execution_share_deterministic_execution_input_digest() -> None:
    run_id = _seed_pending_run()

    response = client.post(
        f"/api/agents/runs/{run_id}/approve",
        json=approval_body("Approved after reviewing exact execution inputs"),
    )
    assert response.status_code == 200

    approved = _event(run_id, "APPROVED")["payload"]
    executed = _event(run_id, "TOOL_EXECUTED")["payload"]

    expected_snapshot = {
        "tool_name": "legacy_db_lookup",
        "tool_parameters": {"record_id": "LEG-001"},
        "allowed_tools": ["legacy_db_lookup"],
    }
    assert approved["execution_inputs"] == expected_snapshot

    canonical = json.dumps(
        expected_snapshot,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    expected_digest = hashlib.sha256(canonical).hexdigest()

    assert approved["execution_inputs_digest"] == expected_digest
    assert executed["execution_inputs_digest"] == expected_digest


def test_rejection_does_not_emit_execution_input_or_tool_execution_evidence() -> None:
    run_id = _seed_pending_run()

    response = client.post(
        f"/api/agents/runs/{run_id}/reject",
        json={"reason": "Rejected"},
    )
    assert response.status_code == 200

    events = client.get(f"/api/agents/runs/{run_id}/events").json()
    assert all(event["event_type"] != "TOOL_EXECUTED" for event in events)
    rejected = next(event for event in events if event["event_type"] == "REJECTED")
    assert "execution_inputs" not in rejected["payload"]
    assert "execution_inputs_digest" not in rejected["payload"]
