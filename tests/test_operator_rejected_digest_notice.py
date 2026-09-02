from app.operator_evidence_ui import operator_workspace_with_evidence


def test_operator_contains_rejected_digest_mismatch_rendering_contract() -> None:
    html = operator_workspace_with_evidence().body.decode("utf-8")

    assert 'id="approval-precondition-rejection"' in html
    assert "APPROVAL_PRECONDITION_REJECTED" in html
    assert "digest_mismatch" in html
    assert "submitted_execution_inputs_digest" in html
    assert "current_execution_inputs_digest" in html
    assert "Reviewed approval inputs changed before execution" in html


def test_operator_missing_digest_contract_hides_submitted_digest_row() -> None:
    html = operator_workspace_with_evidence().body.decode("utf-8")

    assert 'id="approval-rejection-submitted-row"' in html
    assert "missing_expected_digest" in html
    assert "No reviewed digest was submitted" in html
    assert "approvalRejectionSubmittedRow.classList.add('hidden')" in html
    assert "document.getElementById('approval-rejection-submitted-digest').textContent = ''" in html
