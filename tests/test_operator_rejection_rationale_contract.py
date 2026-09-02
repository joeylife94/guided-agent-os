from app.operator_rejection_rationale_ui import operator_workspace_with_rejection_rationale


def test_operator_requires_explicit_rejection_rationale() -> None:
    html = operator_workspace_with_rejection_rationale().body.decode("utf-8")

    assert 'id="rejection-reason"' in html
    assert "const rejectionReason" in html
    assert "rejectionReason.value.trim()" in html
    assert "Rejection rationale is required." in html
    assert "{ reason: rejectionReason.value.trim() }" in html
    assert "Rejected from operator workspace." not in html
