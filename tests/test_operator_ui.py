from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_serves_operator_workspace() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Guided Agent OS" in response.text
    assert 'id="agent-form"' in response.text
    assert 'id="run-panel"' in response.text
    assert 'id="clarification-panel"' in response.text
    assert 'id="clarification-questions"' in response.text
    assert 'id="review-panel"' in response.text
    assert 'id="execution-result"' in response.text
    assert 'id="audit-timeline"' in response.text


def test_workspace_calls_existing_controlled_agent_api_only() -> None:
    response = client.get("/")
    html = response.text

    assert "/api/agents/controlled_rag_agent/runs" in html
    assert "/api/agents/runs/${currentRunId}/${endpoint}" in html
    assert "/api/agents/runs/${runId}/events" in html
    assert "legacy_db_lookup" in html
    assert "renderRun(run)" in html
    assert "renderClarifications(run.clarification_questions || [])" in html
    assert "refreshAuditTimeline(run.run_id)" in html
    assert "run.status === 'pending_approval'" in html
    assert "run.raw_output && run.raw_output.execution_result" in html


def test_workspace_renders_persisted_audit_events() -> None:
    response = client.get("/")
    html = response.text

    assert "function renderAuditEvents(events)" in html
    assert "event.sequence" in html
    assert "event.event_type" in html
    assert "event.actor" in html
    assert "event.created_at" in html
    assert "event.payload" in html
    assert "Persistent lifecycle events arrive in Phase 4" not in html


def test_workspace_allows_backend_validation_to_drive_clarification() -> None:
    response = client.get("/")
    html = response.text

    assert '<textarea id="business_context">' in html
    assert '<input id="expected_output" value=' in html
    assert 'item.question || item.message || JSON.stringify(item)' in html
    assert "clarificationPanel.classList.remove('hidden')" in html


def test_workspace_surfaces_interrupted_decision_quarantine_without_new_execution_path() -> None:
    response = client.get("/")
    html = response.text

    assert 'id="recovery-panel"' in html
    assert 'id="recover-decision-button"' in html
    assert "approval_executing" in html
    assert "rejection_processing" in html
    assert "decision_recovery_required" in html
    assert "/api/agents/runs/${currentRunId}/recover-decision" in html
    assert "DECISION_RECOVERY_REQUIRED" in html
    assert "run.status === 'decision_recovery_required'" in html
    assert "approveButton.disabled = true" in html
    assert "rejectButton.disabled = true" in html


def test_swagger_remains_available_for_developer_inspection() -> None:
    response = client.get("/docs")

    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower()
