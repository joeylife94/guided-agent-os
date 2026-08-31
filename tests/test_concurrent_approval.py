from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.api.routes as routes_module
from app.api.routes import router
from app.models.database import Base, get_db
from app.models.models import AgentRun


def _plan() -> dict:
    return {
        "requires_tool_or_api": True,
        "execution_mode": "planned_only",
        "allowed_to_execute": False,
        "recommended_tools": [
            {
                "name": "legacy_db_lookup",
                "purpose": "Controlled fixture lookup",
                "requires_approval": True,
                "reason": "Internal read-only lookup requires human approval.",
            }
        ],
        "blocked_actions": ["direct_sql_execution", "direct_database_write"],
        "approval_required": True,
        "reason": "Human review required.",
    }


def test_concurrent_approvals_execute_tool_at_most_once(tmp_path: Path, monkeypatch) -> None:
    database_path = tmp_path / "concurrent-approval.db"
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
    client = TestClient(app, raise_server_exceptions=False)

    run_id = "run-concurrent-approval"
    with SessionLocal() as db:
        db.add(
            AgentRun(
                id=run_id,
                agent_type="controlled_rag_agent",
                status="pending_approval",
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
                    "tool_plan": _plan(),
                    "human_review_required": True,
                    "review_status": "pending_approval",
                    "final_status": "pending_approval",
                },
            )
        )
        db.commit()

    execution_count = 0
    execution_lock = threading.Lock()

    def slow_execution(**kwargs):
        nonlocal execution_count
        with execution_lock:
            execution_count += 1
        # Keep the first request inside the execution window long enough for the
        # second request to observe the same persisted pending_approval state.
        time.sleep(0.2)
        return {
            "status": "executed",
            "tool_name": kwargs["tool_name"],
            "read_only": True,
            "parameters": kwargs["parameters"],
            "result": {"found": True, "record": {"record_id": "LEG-001"}},
        }

    monkeypatch.setattr(routes_module, "execute_approved_tool", slow_execution)

    start = threading.Barrier(2)

    def approve_once():
        start.wait(timeout=5)
        return client.post(f"/api/agents/runs/{run_id}/approve", json={})

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: approve_once(), range(2)))

    assert execution_count == 1, (
        "Concurrent approvals must not cross the controlled execution boundary more than once"
    )

    statuses = sorted(response.status_code for response in responses)
    assert statuses[0] == 200
    assert statuses[1] in {200, 409}

    persisted = client.get(f"/api/agents/runs/{run_id}")
    assert persisted.status_code == 200
    payload = persisted.json()
    assert payload["status"] == "archived"
    assert payload["review_status"] == "approved"

    events = client.get(f"/api/agents/runs/{run_id}/events")
    assert events.status_code == 200
    event_types = [event["event_type"] for event in events.json()]
    assert event_types.count("APPROVED") == 1
    assert event_types.count("TOOL_EXECUTED") == 1
    assert event_types.count("COMPLETED") == 1


def test_concurrent_approve_reject_has_one_terminal_decision(tmp_path: Path, monkeypatch) -> None:
    database_path = tmp_path / "concurrent-approve-reject.db"
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
    client = TestClient(app, raise_server_exceptions=False)

    run_id = "run-concurrent-approve-reject"
    with SessionLocal() as db:
        db.add(
            AgentRun(
                id=run_id,
                agent_type="controlled_rag_agent",
                status="pending_approval",
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
                    "tool_plan": _plan(),
                    "human_review_required": True,
                    "review_status": "pending_approval",
                    "final_status": "pending_approval",
                },
            )
        )
        db.commit()

    execution_count = 0
    execution_lock = threading.Lock()

    def slow_execution(**kwargs):
        nonlocal execution_count
        with execution_lock:
            execution_count += 1
        time.sleep(0.2)
        return {
            "status": "executed",
            "tool_name": kwargs["tool_name"],
            "read_only": True,
            "parameters": kwargs["parameters"],
            "result": {"found": True, "record": {"record_id": "LEG-001"}},
        }

    monkeypatch.setattr(routes_module, "execute_approved_tool", slow_execution)

    start = threading.Barrier(2)

    def approve_once():
        start.wait(timeout=5)
        return client.post(f"/api/agents/runs/{run_id}/approve", json={})

    def reject_once():
        start.wait(timeout=5)
        return client.post(
            f"/api/agents/runs/{run_id}/reject",
            json={"reason": "Concurrent operator rejection"},
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        approve_future = pool.submit(approve_once)
        reject_future = pool.submit(reject_once)
        approve_response = approve_future.result(timeout=10)
        reject_response = reject_future.result(timeout=10)

    assert sorted([approve_response.status_code, reject_response.status_code]) == [200, 409]

    persisted = client.get(f"/api/agents/runs/{run_id}")
    assert persisted.status_code == 200
    payload = persisted.json()
    assert payload["review_status"] in {"approved", "rejected"}

    events = client.get(f"/api/agents/runs/{run_id}/events")
    assert events.status_code == 200
    event_types = [event["event_type"] for event in events.json()]
    assert event_types.count("COMPLETED") == 1

    if payload["review_status"] == "approved":
        assert payload["status"] == "archived"
        assert execution_count == 1
        assert event_types.count("APPROVED") == 1
        assert event_types.count("REJECTED") == 0
        assert event_types.count("TOOL_EXECUTED") == 1
    else:
        assert payload["status"] == "rejected"
        assert execution_count == 0
        assert event_types.count("APPROVED") == 0
        assert event_types.count("REJECTED") == 1
        assert event_types.count("TOOL_EXECUTED") == 0
