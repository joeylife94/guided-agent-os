from __future__ import annotations

from fastapi.responses import HTMLResponse

from app.operator_evidence_ui import operator_workspace_with_evidence


_REJECTION_RATIONALE_PANEL = r'''
      <label for="rejection-reason">Rejection rationale</label>
      <textarea id="rejection-reason" rows="3" placeholder="Explain why this execution is being rejected." aria-describedby="rejection-reason-help"></textarea>
      <div id="rejection-reason-help" class="muted">Required only for Reject. The trimmed rationale is persisted in the existing REJECTED audit event.</div>
'''

_REJECTION_RATIONALE_SCRIPT = r'''

  const rejectionReason = document.getElementById('rejection-reason');
  const p018SubmitDecision = submitDecision;
  submitDecision = async function(decision) {
    if (decision !== 'reject') return p018SubmitDecision(decision);
    if (!currentRunId) return;

    const rationale = rejectionReason.value.trim();
    if (!rationale) {
      requestError.textContent = 'Rejection rationale is required.';
      requestError.classList.remove('hidden');
      rejectionReason.focus();
      return;
    }

    approveButton.disabled = true;
    rejectButton.disabled = true;
    requestError.classList.add('hidden');
    try {
      const body = { reason: rejectionReason.value.trim() };
      const run = await api(`/api/agents/runs/${currentRunId}/reject`, { method: 'POST', body: JSON.stringify(body) });
      rejectionReason.value = '';
      renderRun(run);
    } catch (error) {
      requestError.textContent = error.message;
      requestError.classList.remove('hidden');
      try {
        const persisted = await api(`/api/agents/runs/${currentRunId}`);
        renderRun(persisted);
      } catch (_) {
        // Preserve the original rejection error. The persisted run can still be loaded explicitly.
      }
    } finally {
      if (!panel.classList.contains('hidden') && document.getElementById('run-status').textContent === 'pending_approval') {
        rejectButton.disabled = false;
        approveButton.disabled = !currentReviewedExecutionInputsDigest;
      }
    }
  };
'''


def operator_workspace_with_rejection_rationale() -> HTMLResponse:
    """Add explicit, fail-closed human rejection rationale capture to the existing Operator workspace."""
    response = operator_workspace_with_evidence()
    html = response.body.decode("utf-8")
    review_copy = '<div class="muted">Execution remains blocked until an operator explicitly approves this run.</div>'
    if review_copy not in html:
        raise RuntimeError("Operator review surface changed; P-018 rationale injection point is unavailable")
    html = html.replace(review_copy, f"{review_copy}\n{_REJECTION_RATIONALE_PANEL}", 1)
    html = html.replace("Rejected from operator workspace.", "", 1)
    close_script = "})();\n</script>"
    if close_script not in html:
        raise RuntimeError("Operator script boundary changed; P-018 rationale guard cannot be installed")
    html = html.replace(close_script, f"{_REJECTION_RATIONALE_SCRIPT}\n}})();\n</script>", 1)
    return HTMLResponse(content=html)
