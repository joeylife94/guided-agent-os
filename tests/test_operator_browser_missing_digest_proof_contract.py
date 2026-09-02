from pathlib import Path


def test_browser_proof_exercises_missing_reviewed_digest_rejection() -> None:
    script = Path("scripts/verify_operator_browser.py").read_text(encoding="utf-8")

    assert "Intentional missing digest for browser proof." in script
    assert "missing_expected_digest" in script
    assert "approval-rejection-submitted-row" in script
    assert "missing_digest_rejected_409_pending_approval" in script
    assert "missing_digest_notice_hides_submitted_digest" in script
