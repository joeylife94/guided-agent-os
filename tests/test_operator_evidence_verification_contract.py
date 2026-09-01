from fastapi.testclient import TestClient

from app.main import app


def test_operator_evidence_verification_contract() -> None:
    html = TestClient(app).get("/").text

    assert 'id="evidence-verification-status"' in html
    assert "function canonicalizeEvidence(value)" in html
    assert "async function verifyEvidenceDigest(evidence)" in html
    assert "SHA-256" in html
    assert "evidence_digest" in html
    assert "MATCH" in html
    assert "MISMATCH" in html
    assert "UNAVAILABLE" in html
