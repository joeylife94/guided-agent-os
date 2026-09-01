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

    assert 'id="load-run-id"' in html
    assert 'id="load-run-button"' in html
    assert "/api/agents/runs/${runId}`" in html
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


def test_workspace_discovers_recovery_queue_via_read_only_loader() -> None:
    response = client.get("/")
    html = response.text

    assert 'id="recovery-queue"' in html
    assert 'id="refresh-recovery-queue-button"' in html
    assert "function renderRecoveryQueue(runs)" in html
    assert "function refreshRecoveryQueue()" in html
    assert "await api('/api/agents/runs/recovery-queue')" in html
    assert "loadRunIdInput.value = run.run_id" in html
    assert "loadPersistedRun();" in html
    assert "Open persisted run" in html
    assert "automatic retry" not in html.lower()


def test_workspace_surfaces_existing_deterministic_evidence_bundle_read_only() -> None:
    response = client.get("/")
    html = response.text

    assert 'id="run-evidence-panel"' in html
    assert 'id="refresh-run-evidence-button"' in html
    assert 'id="evidence-digest"' in html
    assert 'id="run-evidence-json"' in html
    assert "function renderRunEvidence(evidence)" in html
    assert "function refreshRunEvidence(runId)" in html
    assert "await api(`/api/agents/runs/${runId}/evidence`)" in html
    assert "evidence.evidence_digest" in html
    assert "JSON.stringify(evidence, null, 2)" in html
    assert "refreshRunEvidence(run.run_id)" in html


def test_workspace_surfaces_exact_execution_inputs_before_human_approval() -> None:
    response = client.get("/")
    html = response.text

    assert 'id="execution-input-review"' in html
    assert 'id="execution-tool-parameters"' in html
    assert 'id="execution-allowed-tools"' in html
    assert "run.intake_data && run.intake_data.tool_parameters" in html
    assert "run.intake_data && run.intake_data.allowed_tools" in html
    assert "JSON.stringify(toolParameters, null, 2)" in html
    assert "JSON.stringify(allowedTools, null, 2)" in html
    assert "run.status === 'pending_approval'" in html


def test_swagger_remains_available_for_developer_inspection() -> None:
    response = client.get("/docs")

    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower()
