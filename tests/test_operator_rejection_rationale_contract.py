from app.operator_ui import _OPERATOR_HTML


def test_operator_requires_explicit_rejection_rationale() -> None:
    assert 'id="rejection-reason"' in _OPERATOR_HTML
    assert "const rejectionReason" in _OPERATOR_HTML
    assert "rejectionReason.value.trim()" in _OPERATOR_HTML
    assert "Rejection rationale is required." in _OPERATOR_HTML
    assert "{ reason: rejectionReason.value.trim() }" in _OPERATOR_HTML
    assert "Rejected from operator workspace." not in _OPERATOR_HTML
