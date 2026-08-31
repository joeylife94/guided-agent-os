from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.api.routes as routes_module
from app.api.routes import router
from app.models.database import Base, get_db
from app.models.models import AgentRun


def _client(tmp_path: Path):
    database_path = tmp_path / "interrupted-decision.db"
    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False, "timeout": 5},
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app, raise_server_exceptions=False), SessionLocal


def _seed_transient(SessionLocal, run_id: str, status: str) -> None:
    with SessionLocal() as db:
        db.add(
            AgentRun(
                id=run_id,
                agent_type="controlled_rag_agent",
                status=status,
                intake_data={
                    "user_request": "Look up legacy database record LEG-001",
                    "business_context": "Operations proof flow",
                    "data_sources": ["tool_catalog"],
                    "expected_output": "Approved read-only result",
                    "risk_level": "internal",
                    "allowed_tools": ["legacy_db_lookup"],
                    "tool_parameters": {"record_id": "LEG-001"},
                },
                raw_llm_output={
                    "human_review_required": True,
                    "review_status": "pending_approval",
                    "final_status": "pending_approval",
                },
            )
        )
        db.commit()


def test_quarantine_interrupted_approval_is_non_replaying_and_idempotent(
    tmp_path: Path, monkeypatch
) -> None:
    client, SessionLocal = _client(tmp_path)
    run_id = "run-interrupted-approval"
    _seed_transient(SessionLocal, run_id, "approval_executing")

    execution_count = 0

    def forbidden_execution(**kwargs):
        nonlocal execution_count
        execution_count += 1
        raise AssertionError("quarantine must never execute a tool")

    monkeypatch.setattr(routes_module, "execute_approved_tool", forbidden_execution)

    before = client.get(f"/api/agents/runs/{run_id}/evidence")
    assert before.status_code == 200

    first = client.post(f"/api/agents/runs/{run_id}/recover-decision", json={})
    assert first.status_code == 200
    assert first.json()["status"] == "decision_recovery_required"
    assert execution_count == 0

    second = client.post(f"/api/agents/runs/{run_id}/recover-decision", json={})
    assert second.status_code == 200
    assert second.json()["status"] == "decision_recovery_required"
    assert execution_count == 0

    events = client.get(f"/api/agents/runs/{run_id}/events")
    assert events.status_code == 200
    payloads = events.json()
    recovery_events = [
        event for event in payloads if event["event_type"] == "DECISION_RECOVERY_REQUIRED"
    ]
    assert len(recovery_events) == 1
    assert recovery_events[0]["payload"]["prior_status"] == "approval_executing"

    event_types = [event["event_type"] for event in payloads]
    for terminal_type in ("APPROVED", "REJECTED", "TOOL_EXECUTED", "COMPLETED"):
        assert terminal_type not in event_types

    approve = client.post(f"/api/agents/runs/{run_id}/approve", json={})
    reject = client.post(
        f"/api/agents/runs/{run_id}/reject",
        json={"reason": "must remain quarantined"},
    )
    assert approve.status_code in {409, 422}
    assert reject.status_code in {409, 422}
    assert execution_count == 0

    after = client.get(f"/api/agents/runs/{run_id}/evidence")
    repeat = client.get(f"/api/agents/runs/{run_id}/evidence")
    assert after.status_code == 200
    assert repeat.status_code == 200
    assert before.json()["evidence_digest"] != after.json()["evidence_digest"]
    assert after.json()["evidence_digest"] == repeat.json()["evidence_digest"]


def test_quarantine_interrupted_rejection_records_prior_state(tmp_path: Path) -> None:
    client, SessionLocal = _client(tmp_path)
    run_id = "run-interrupted-rejection"
    _seed_transient(SessionLocal, run_id, "rejection_processing")

    response = client.post(f"/api/agents/runs/{run_id}/recover-decision", json={})
    assert response.status_code == 200
    assert response.json()["status"] == "decision_recovery_required"

    events = client.get(f"/api/agents/runs/{run_id}/events")
    recovery_events = [
        event for event in events.json()
        if event["event_type"] == "DECISION_RECOVERY_REQUIRED"
    ]
    assert len(recovery_events) == 1
    assert recovery_events[0]["payload"]["prior_status"] == "rejection_processing"


def test_quarantine_rejects_unclaimed_non_transient_runs(tmp_path: Path) -> None:
    client, SessionLocal = _client(tmp_path)
    run_id = "run-not-interrupted"
    _seed_transient(SessionLocal, run_id, "pending_approval")

    response = client.post(f"/api/agents/runs/{run_id}/recover-decision", json={})
    assert response.status_code in {409, 422}

    persisted = client.get(f"/api/agents/runs/{run_id}")
    assert persisted.status_code == 200
    assert persisted.json()["status"] == "pending_approval"

    events = client.get(f"/api/agents/runs/{run_id}/events")
    assert all(
        event["event_type"] != "DECISION_RECOVERY_REQUIRED"
        for event in events.json()
    )
