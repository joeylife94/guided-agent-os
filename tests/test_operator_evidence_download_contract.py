from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_operator_evidence_surface_exposes_bounded_download_contract() -> None:
    response = client.get("/operator")
    assert response.status_code == 200
    html = response.text

    assert 'id="download-run-evidence-button"' in html
    assert "downloadRunEvidence" in html
    assert "currentEvidence" in html
    assert "URL.createObjectURL" in html
    assert "Blob" in html
    assert ".json" in html
    assert "evidence_digest" in html
