from __future__ import annotations

from fastapi.responses import HTMLResponse

from app.operator_ui import operator_workspace


_EXECUTION_INPUT_REVIEW = r'''

    <div id="execution-input-review" class="hidden">
      <h3>Execution inputs for approval</h3>
      <div class="muted">Read-only persisted inputs consumed by the existing approved execution path. Review these values before approving.</div>
      <div><span class="pill">Planned tool</span> <code id="execution-planned-tool">Not available.</code></div>
      <h4>Tool parameters</h4>
      <pre id="execution-tool-parameters">Not available.</pre>
      <h4>Per-run allowed tools</h4>
      <pre id="execution-allowed-tools">Not available.</pre>
    </div>
'''

_EVIDENCE_PANEL = r'''

    <section id="run-evidence-panel" class="card">
      <h3>Deterministic run evidence</h3>
      <div class="muted">Read-only delivery artifact for the currently loaded run. The digest is an integrity checksum, not a signature or notarization.</div>
      <div class="actions">
        <button id="refresh-run-evidence-button" class="primary" type="button">Refresh run evidence</button>
        <button id="download-run-evidence-button" type="button" disabled>Download evidence</button>
      </div>
      <div><span class="pill">SHA-256</span> <code id="evidence-digest">Not loaded.</code></div>
      <div><span class="pill">Local verification</span> <strong id="evidence-verification-status">UNAVAILABLE</strong></div>
      <pre id="run-evidence-json">Evidence not loaded.</pre>
    </section>
'''

_EVIDENCE_SCRIPT = r'''

  const refreshRunEvidenceButton = document.getElementById('refresh-run-evidence-button');
  const downloadRunEvidenceButton = document.getElementById('download-run-evidence-button');
  const evidenceVerificationStatus = document.getElementById('evidence-verification-status');
  const executionInputReview = document.getElementById('execution-input-review');
  let currentEvidence = null;

  function canonicalizeEvidence(value) {
    if (Array.isArray(value)) return value.map(canonicalizeEvidence);
    if (value !== null && typeof value === 'object') {
      const canonical = {};
      Object.keys(value).sort().forEach((key) => {
        if (key !== 'evidence_digest') canonical[key] = canonicalizeEvidence(value[key]);
      });
      return canonical;
    }
    return value;
  }

  async function verifyEvidenceDigest(evidence) {
    if (!evidence || !evidence.evidence_digest || !globalThis.crypto || !globalThis.crypto.subtle) {
      return 'UNAVAILABLE';
    }
    try {
      const canonical = JSON.stringify(canonicalizeEvidence(evidence));
      const bytes = new TextEncoder().encode(canonical);
      const digestBuffer = await globalThis.crypto.subtle.digest('SHA-256', bytes);
      const localDigest = Array.from(new Uint8Array(digestBuffer))
        .map((byte) => byte.toString(16).padStart(2, '0'))
        .join('');
      return localDigest === String(evidence.evidence_digest).toLowerCase() ? 'MATCH' : 'MISMATCH';
    } catch (error) {
      return 'UNAVAILABLE';
    }
  }

  function renderExecutionInputReview(run) {
    const toolParameters = run.intake_data && run.intake_data.tool_parameters;
    const allowedTools = run.intake_data && run.intake_data.allowed_tools;
    const plannedTool = run.tool_plan && (run.tool_plan.tool_name || run.tool_plan.tool);
    const isPendingApproval = run.status === 'pending_approval';

    executionInputReview.classList.toggle('hidden', !isPendingApproval);
    document.getElementById('execution-planned-tool').textContent = plannedTool || 'Not available.';
    document.getElementById('execution-tool-parameters').textContent = JSON.stringify(toolParameters, null, 2);
    document.getElementById('execution-allowed-tools').textContent = JSON.stringify(allowedTools, null, 2);
  }

  async function renderRunEvidence(evidence) {
    currentEvidence = evidence;
    downloadRunEvidenceButton.disabled = false;
    document.getElementById('evidence-digest').textContent = evidence.evidence_digest || 'Digest unavailable.';
    document.getElementById('run-evidence-json').textContent = JSON.stringify(evidence, null, 2);
    evidenceVerificationStatus.textContent = 'UNAVAILABLE';
    evidenceVerificationStatus.textContent = await verifyEvidenceDigest(evidence);
  }

  function clearCurrentEvidence(message = 'Evidence not loaded.') {
    currentEvidence = null;
    downloadRunEvidenceButton.disabled = true;
    document.getElementById('evidence-digest').textContent = 'Not loaded.';
    evidenceVerificationStatus.textContent = 'UNAVAILABLE';
    document.getElementById('run-evidence-json').textContent = message;
  }

  function downloadRunEvidence() {
    if (!currentEvidence || !currentRunId || !currentEvidence.evidence_digest) return;

    const evidenceRunId = currentEvidence.run && currentEvidence.run.run_id;
    if (evidenceRunId && evidenceRunId !== currentRunId) {
      clearCurrentEvidence('Evidence changed with the active run. Refresh before downloading.');
      return;
    }

    const digestPrefix = String(currentEvidence.evidence_digest).slice(0, 12).toLowerCase();
    const filename = `guided-agent-os-${currentRunId}-${digestPrefix}.json`;
    const payload = JSON.stringify(currentEvidence, null, 2);
    const blob = new Blob([payload], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  }

  async function refreshRunEvidence(runId) {
    if (!runId) {
      clearCurrentEvidence();
      return;
    }
    currentEvidence = null;
    downloadRunEvidenceButton.disabled = true;
    refreshRunEvidenceButton.disabled = true;
    evidenceVerificationStatus.textContent = 'UNAVAILABLE';
    try {
      const evidence = await api(`/api/agents/runs/${runId}/evidence`);
      if (runId === currentRunId) await renderRunEvidence(evidence);
    } catch (error) {
      if (runId === currentRunId) {
        clearCurrentEvidence(`Run evidence unavailable: ${error.message}`);
        document.getElementById('evidence-digest').textContent = 'Unavailable';
      }
    } finally {
      refreshRunEvidenceButton.disabled = false;
    }
  }

  const originalRenderRun = renderRun;
  renderRun = function(run) {
    clearCurrentEvidence('Loading evidence for the current run...');
    originalRenderRun(run);
    renderExecutionInputReview(run);
    refreshRunEvidence(run.run_id);
  };

  refreshRunEvidenceButton.addEventListener('click', () => refreshRunEvidence(currentRunId));
  downloadRunEvidenceButton.addEventListener('click', downloadRunEvidence);
'''


def operator_workspace_with_evidence() -> HTMLResponse:
    """Return the existing Operator Workspace with read-only evidence and approval-input surfaces."""
    response = operator_workspace()
    html = response.body.decode("utf-8")
    html = html.replace('    <div id="review-panel" class="hidden">', f'{_EXECUTION_INPUT_REVIEW}\n    <div id="review-panel" class="hidden">', 1)
    html = html.replace("  </section>\n</main>", f"  </section>{_EVIDENCE_PANEL}\n</main>", 1)
    html = html.replace("})();\n</script>", f"{_EVIDENCE_SCRIPT}\n}})();\n</script>", 1)
    return HTMLResponse(content=html)
