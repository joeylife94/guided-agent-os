from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.api.routes as routes_module
from app.api.routes import router
from app.models.database import Base, get_db


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


def _final_state() -> dict:
    return {
        "status": "pending_approval",
        "missing_fields": [],
        "clarification_questions": [],
        "normalized_data": {
            "user_request": "Look up LEG-001",
            "business_context": "Audit proof",
        },
        "analysis_summary": None,
        "score": None,
        "action_drafts": [],
        "rag_answer": {
            "answer": "Use the controlled legacy lookup path.",
            "citations": [{"source": "tools/legacy-db-access-guideline.md"}],
        },
        "tool_plan": {
            "requires_tool_or_api": True,
            "recommended_tools": [
                {
                    "name": "legacy_db_lookup",
                    "purpose": "Controlled fixture lookup",
                    "requires_approval": True,
                }
            ],
        },
        "human_review_required": True,
        "review_status": "pending_approval",
        "final_status": "pending_approval",
    }


def test_full_controlled_run_events_persist_and_reload_in_sequence(monkeypatch) -> None:
    class FakeWorkflow:
        @staticmethod
        def invoke(_state):
            return _final_state()

    monkeypatch.setattr(routes_module, "workflow", FakeWorkflow())

    create_response = client.post(
        "/api/agents/controlled_rag_agent/runs",
        json={
            "user_request": "Look up LEG-001",
            "business_context": "Audit proof",
            "data_sources": ["tool_catalog"],
            "expected_output": "Approved read-only result",
            "risk_level": "internal",
            "allowed_tools": ["legacy_db_lookup"],
            "tool_parameters": {"record_id": "LEG-001"},
        },
    )
    assert create_response.status_code == 201
    run_id = create_response.json()["run_id"]

    before_approval = client.get(f"/api/agents/runs/{run_id}/events")
    assert before_approval.status_code == 200
    before_types = [event["event_type"] for event in before_approval.json()]
    assert before_types == [
        "REQUEST_RECEIVED",
        "VALIDATION_PASSED",
        "NORMALIZED",
        "ANSWER_GENERATED",
        "TOOL_PLANNED",
        "APPROVAL_REQUESTED",
    ]

    approve_response = client.post(
        f"/api/agents/runs/{run_id}/approve",
        json={"note": "Approved for audit proof"},
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "archived"

    reloaded = client.get(f"/api/agents/runs/{run_id}/events")
    assert reloaded.status_code == 200
    events = reloaded.json()
    assert [event["sequence"] for event in events] == list(range(1, len(events) + 1))
    assert [event["event_type"] for event in events] == [
        "REQUEST_RECEIVED",
        "VALIDATION_PASSED",
        "NORMALIZED",
        "ANSWER_GENERATED",
        "TOOL_PLANNED",
        "APPROVAL_REQUESTED",
        "APPROVED",
        "TOOL_EXECUTED",
        "COMPLETED",
    ]
    assert events[0]["actor"] == "user"
    assert events[6]["actor"] == "human"
    assert events[7]["payload"]["tool_name"] == "legacy_db_lookup"
    assert events[7]["payload"]["read_only"] is True
    assert events[-1]["payload"]["status"] == "archived"
    assert all(event["created_at"] for event in events)


def test_clarification_path_persists_minimal_audit_sequence(monkeypatch) -> None:
    class FakeWorkflow:
        @staticmethod
        def invoke(_state):
            return {
                "status": "needs_clarification",
                "missing_fields": ["business_context"],
                "clarification_questions": [
                    {
                        "field": "business_context",
                        "question": "What is the business context?",
                    }
                ],
                "action_drafts": [],
            }

    monkeypatch.setattr(routes_module, "workflow", FakeWorkflow())

    response = client.post(
        "/api/agents/controlled_rag_agent/runs",
        json={"user_request": "Look up LEG-001"},
    )
    assert response.status_code == 201
    run_id = response.json()["run_id"]

    events = client.get(f"/api/agents/runs/{run_id}/events").json()
    assert [event["event_type"] for event in events] == [
        "REQUEST_RECEIVED",
        "CLARIFICATION_REQUIRED",
    ]
    assert events[1]["payload"]["missing_fields"] == ["business_context"]
