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
    assert 'id="review-panel"' in response.text
    assert 'id="execution-result"' in response.text
    assert 'id="audit-shell"' in response.text


def test_workspace_calls_existing_controlled_agent_api_only() -> None:
    response = client.get("/")
    html = response.text

    assert "/api/agents/controlled_rag_agent/runs" in html
    assert "/api/agents/runs/${currentRunId}/${endpoint}" in html
    assert "legacy_db_lookup" in html
    assert "renderRun(run)" in html
    assert "run.status === 'pending_approval'" in html
    assert "run.raw_output && run.raw_output.execution_result" in html


def test_swagger_remains_available_for_developer_inspection() -> None:
    response = client.get("/docs")

    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower()
