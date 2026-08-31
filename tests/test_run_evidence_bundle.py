from __future__ import annotations

import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes import router
from app.models.database import Base, get_db
from app.models.models import AgentRun, RunAuditEvent


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


def _counts() -> tuple[int, int]:
    db = TestingSessionLocal()
    try:
        return db.query(AgentRun).count(), db.query(RunAuditEvent).count()
    finally:
        db.close()


def _seed_pending_run() -> str:
    db = TestingSessionLocal()
    try:
        run = AgentRun(
            id="run-evidence-controlled",
            agent_type="controlled_rag_agent",
            status="pending_approval",
            intake_data={
                "user_request": "Look up legacy database record LEG-001",
                "business_context": "Evidence bundle proof",
                "data_sources": ["tool_catalog"],
                "expected_output": "Approved read-only result",
                "risk_level": "internal",
                "allowed_tools": ["legacy_db_lookup"],
                "tool_parameters": {"record_id": "LEG-001"},
            },
            raw_llm_output={
                "tool_plan": {
                    "requires_tool_or_api": True,
                    "execution_mode": "planned_only",
                    "allowed_to_execute": False,
                    "recommended_tools": [
                        {
                            "name": "legacy_db_lookup",
                            "purpose": "Controlled fixture lookup",
                            "requires_approval": True,
                            "reason": "Human approval required.",
                        }
                    ],
                    "blocked_actions": ["direct_sql_execution", "direct_database_write"],
                    "approval_required": True,
                    "reason": "Human review required.",
                },
                "human_review_required": True,
                "review_status": "pending_approval",
                "final_status": "pending_approval",
            },
        )
        run.audit_events.append(
            RunAuditEvent(
                sequence=1,
                event_type="APPROVAL_REQUESTED",
                actor="system",
                payload={},
            )
        )
        db.add(run)
        db.commit()
        return run.id
    finally:
        db.close()


def test_evidence_bundle_is_stable_and_read_only() -> None:
    create = client.post(
        "/api/agents/freelance/runs",
        json={
            "opportunity_title": "Evidence review",
            "client_description": "Internal reviewer",
            "project_description": "Inspect a deterministic run bundle",
        },
    )
    assert create.status_code == 201
    run_id = create.json()["run_id"]
    before_counts = _counts()

    first = client.get(f"/api/agents/runs/{run_id}/evidence")
    second = client.get(f"/api/agents/runs/{run_id}/evidence")

    assert first.status_code == 200
    assert second.status_code == 200
    first_body = first.json()
    second_body = second.json()
    assert first_body == second_body
    assert first_body["run"]["run_id"] == run_id
    assert [event["sequence"] for event in first_body["events"]] == sorted(
        event["sequence"] for event in first_body["events"]
    )
    assert len(first_body["evidence_digest"]) == 64
    assert first_body["evidence_digest"] == second_body["evidence_digest"]
    assert _counts() == before_counts


def test_missing_evidence_bundle_is_404_and_no_mutation() -> None:
    before_counts = _counts()
    response = client.get(f"/api/agents/runs/{uuid.uuid4()}/evidence")
    assert response.status_code == 404
    assert _counts() == before_counts


def test_evidence_digest_changes_after_approved_lifecycle_mutation() -> None:
    run_id = _seed_pending_run()

    before = client.get(f"/api/agents/runs/{run_id}/evidence")
    assert before.status_code == 200
    before_body = before.json()

    approved = client.post(
        f"/api/agents/runs/{run_id}/approve",
        json={"note": "Approved for deterministic evidence test"},
    )
    assert approved.status_code == 200

    after = client.get(f"/api/agents/runs/{run_id}/evidence")
    assert after.status_code == 200
    after_body = after.json()

    assert after_body["evidence_digest"] != before_body["evidence_digest"]
    assert after_body["run"]["status"] == "archived"
    assert after_body["run"]["raw_output"]["execution_result"]["status"] == "executed"
    event_types = [event["event_type"] for event in after_body["events"]]
    assert event_types[-3:] == ["APPROVED", "TOOL_EXECUTED", "COMPLETED"]
