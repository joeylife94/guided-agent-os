from __future__ import annotations

from datetime import datetime, timedelta, timezone
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
    database_path = tmp_path / "recovery-queue.db"
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


def _seed(SessionLocal, run_id: str, status: str, created_at: datetime) -> None:
    with SessionLocal() as db:
        db.add(
            AgentRun(
                id=run_id,
                agent_type="controlled_rag_agent",
                status=status,
                intake_data={"user_request": "bounded recovery queue proof"},
                raw_llm_output={"review_status": "pending_approval"},
                created_at=created_at,
                updated_at=created_at,
            )
        )
        db.commit()


def test_recovery_queue_is_read_only_filtered_and_deterministic(tmp_path: Path, monkeypatch) -> None:
    client, SessionLocal = _client(tmp_path)
    now = datetime.now(timezone.utc)

    _seed(SessionLocal, "b-transient", "approval_executing", now)
    _seed(SessionLocal, "a-transient", "rejection_processing", now)
    _seed(SessionLocal, "older-quarantined", "decision_recovery_required", now - timedelta(minutes=1))
    _seed(SessionLocal, "pending", "pending_approval", now - timedelta(minutes=2))
    _seed(SessionLocal, "archived", "archived", now - timedelta(minutes=3))
    _seed(SessionLocal, "rejected", "rejected", now - timedelta(minutes=4))

    execution_count = 0

    def forbidden_execution(**kwargs):
        nonlocal execution_count
        execution_count += 1
        raise AssertionError("recovery queue reads must never execute a tool")

    monkeypatch.setattr(routes_module, "execute_approved_tool", forbidden_execution)

    before_events = {
        run_id: client.get(f"/api/agents/runs/{run_id}/events").json()
        for run_id in ("older-quarantined", "a-transient", "b-transient")
    }

    first = client.get("/api/agents/runs/recovery-queue")
    second = client.get("/api/agents/runs/recovery-queue")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()
    assert [item["run_id"] for item in first.json()] == [
        "older-quarantined",
        "a-transient",
        "b-transient",
    ]
    assert {item["status"] for item in first.json()} == {
        "approval_executing",
        "rejection_processing",
        "decision_recovery_required",
    }
    assert execution_count == 0

    after_events = {
        run_id: client.get(f"/api/agents/runs/{run_id}/events").json()
        for run_id in ("older-quarantined", "a-transient", "b-transient")
    }
    assert after_events == before_events


def test_recovery_queue_empty_is_200_and_non_mutating(tmp_path: Path) -> None:
    client, SessionLocal = _client(tmp_path)
    now = datetime.now(timezone.utc)
    _seed(SessionLocal, "normal-pending", "pending_approval", now)

    before = client.get("/api/agents/runs/normal-pending/evidence")
    response = client.get("/api/agents/runs/recovery-queue")
    after = client.get("/api/agents/runs/normal-pending/evidence")

    assert response.status_code == 200
    assert response.json() == []
    assert before.status_code == 200
    assert after.status_code == 200
    assert before.json()["evidence_digest"] == after.json()["evidence_digest"]
