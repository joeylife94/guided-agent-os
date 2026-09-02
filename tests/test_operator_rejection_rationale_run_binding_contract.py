from app.operator_rejection_rationale_ui import operator_workspace_with_rejection_rationale


def test_rejection_rationale_is_bound_to_current_run_context() -> None:
    html = operator_workspace_with_rejection_rationale().body.decode("utf-8")

    assert "let rejectionRationaleRunId = null" in html
    assert "function bindRejectionRationaleToRun(runId)" in html
    assert "const normalizedRunId = runId || null" in html
    assert "normalizedRunId !== rejectionRationaleRunId" in html
    assert "rejectionReason.value = '';" in html
    assert "rejectionRationaleRunId = normalizedRunId" in html
    assert "bindRejectionRationaleToRun(run.run_id);" in html
