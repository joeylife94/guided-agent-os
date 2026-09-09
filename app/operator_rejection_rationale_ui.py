from __future__ import annotations

from fastapi.responses import HTMLResponse

from app.operator_evidence_ui import operator_workspace_with_evidence


_REVIEWER_IDENTITY_PANEL = r'''
    <div id="reviewer-identity-panel">
      <h3>Reviewer identity</h3>
      <div class="muted">Repository-local reviewer identifier for this decision. This is attribution only; it is not SSO, RBAC, or an authenticated production account.</div>
      <label for="reviewer-id">Reviewer ID</label>
      <input id="reviewer-id" type="text" placeholder="e.g. alice.local" autocomplete="off" />
    </div>
'''

_REJECTION_RATIONALE_PANEL = r'''
      <label for="rejection-reason">Rejection rationale</label>
      <textarea id="rejection-reason" rows="3" placeholder="Explain why this execution is being rejected." aria-describedby="rejection-reason-help"></textarea>
      <div id="rejection-reason-help" class="muted">Required only for Reject. The trimmed rationale is persisted in the existing REJECTED audit event.</div>
'''

_REJECTION_RATIONALE_SCRIPT = r'''

  const reviewerId = document.getElementById('reviewer-id');
  const rejectionReason = document.getElementById('rejection-reason');
  let rejectionRationaleRunId = null;

  function bindRejectionRationaleToRun(runId) {
    const normalizedRunId = runId || null;
    if (normalizedRunId !== rejectionRationaleRunId) {
      rejectionReason.value = '';
      rejectionRationaleRunId = normalizedRunId;
    }
  }

  function currentReviewerId() {
    const value = reviewerId.value.trim();
    if (!value) {
      requestError.textContent = 'Reviewer ID is required before a human decision.';
      requestError.classList.remove('hidden');
      reviewerId.focus();
      return null;
    }
    return value;
  }

  const p019RenderRun = renderRun;
  renderRun = function(run) {
    bindRejectionRationaleToRun(run.run_id);
    return p019RenderRun(run);
  };

  const p018SubmitDecision = submitDecision;
  submitDecision = async function(decision) {
    if (!currentRunId) return;
    const reviewer = currentReviewerId();
    if (!reviewer) return;

    if (decision === 'approve') {
      if (!currentReviewedExecutionInputsDigest) {
        requestError.textContent = 'Approval blocked until the reviewed execution-input digest is available.';
        requestError.classList.remove('hidden');
        approveButton.disabled = true;
        return;
      }
      approveButton.disabled = true;
      rejectButton.disabled = true;
      requestError.classList.add('hidden');
      try {
        const body = {
          reviewer_id: reviewer,
          note: 'Approved from operator workspace.',
          expected_execution_inputs_digest: currentReviewedExecutionInputsDigest,
        };
        const run = await api(`/api/agents/runs/${currentRunId}/approve`, { method: 'POST', body: JSON.stringify(body) });
        renderRun(run);
      } catch (error) {
        requestError.textContent = error.message;
        requestError.classList.remove('hidden');
        try {
          const persisted = await api(`/api/agents/runs/${currentRunId}`);
          renderRun(persisted);
        } catch (_) {
          // Preserve the original approval error. The persisted run can still be loaded explicitly.
        }
      } finally {
        if (!panel.classList.contains('hidden') && document.getElementById('run-status').textContent === 'pending_approval') {
          rejectButton.disabled = false;
          approveButton.disabled = !currentReviewedExecutionInputsDigest;
        }
      }
      return;
    }

    if (decision !== 'reject') return p018SubmitDecision(decision);

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
      const body = { reviewer_id: reviewer, reason: rationale };
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

  recoverInterruptedDecision = async function() {
    if (!currentRunId) return;
    const reviewer = currentReviewerId();
    if (!reviewer) return;
    recoverDecisionButton.disabled = true;
    approveButton.disabled = true;
    rejectButton.disabled = true;
    requestError.classList.add('hidden');
    try {
      const run = await api(`/api/agents/runs/${currentRunId}/recover-decision`, {
        method: 'POST',
        body: JSON.stringify({ reviewer_id: reviewer }),
      });
      renderRun(run);
      refreshRecoveryQueue();
    } catch (error) {
      requestError.textContent = error.message;
      requestError.classList.remove('hidden');
      recoverDecisionButton.disabled = false;
    }
  };
'''


def operator_workspace_with_rejection_rationale() -> HTMLResponse:
    """Add bounded reviewer attribution and fail-closed rejection rationale capture."""
    response = operator_workspace_with_evidence()
    html = response.body.decode("utf-8")

    run_header = '<div><span class="pill" id="run-status">status</span><span class="pill" id="run-id">run</span></div>'
    if run_header not in html:
        raise RuntimeError("Operator run surface changed; reviewer identity injection point is unavailable")
    html = html.replace(run_header, f"{run_header}\n{_REVIEWER_IDENTITY_PANEL}", 1)

    review_copy = '<div class="muted">Execution remains blocked until an operator explicitly approves this run.</div>'
    if review_copy not in html:
        raise RuntimeError("Operator review surface changed; P-018 rationale injection point is unavailable")
    html = html.replace(review_copy, f"{review_copy}\n{_REJECTION_RATIONALE_PANEL}", 1)
    html = html.replace("Rejected from operator workspace.", "", 1)

    close_script = "})();\n</script>"
    if close_script not in html:
        raise RuntimeError("Operator script boundary changed; reviewer/rationale guard cannot be installed")
    html = html.replace(close_script, f"{_REJECTION_RATIONALE_SCRIPT}\n}})();\n</script>", 1)
    return HTMLResponse(content=html)
