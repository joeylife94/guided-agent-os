from __future__ import annotations

from fastapi.responses import HTMLResponse

from app.operator_ui import operator_workspace


_EVIDENCE_PANEL = r'''

    <section id="run-evidence-panel" class="card">
      <h3>Deterministic run evidence</h3>
      <div class="muted">Read-only delivery artifact for the currently loaded run. The digest is an integrity checksum, not a signature or notarization.</div>
      <div class="actions">
        <button id="refresh-run-evidence-button" class="primary" type="button">Refresh run evidence</button>
      </div>
      <div><span class="pill">SHA-256</span> <code id="evidence-digest">Not loaded.</code></div>
      <pre id="run-evidence-json">Evidence not loaded.</pre>
    </section>
'''

_EVIDENCE_SCRIPT = r'''

  const refreshRunEvidenceButton = document.getElementById('refresh-run-evidence-button');

  function renderRunEvidence(evidence) {
    document.getElementById('evidence-digest').textContent = evidence.evidence_digest || 'Digest unavailable.';
    document.getElementById('run-evidence-json').textContent = JSON.stringify(evidence, null, 2);
  }

  async function refreshRunEvidence(runId) {
    if (!runId) return;
    refreshRunEvidenceButton.disabled = true;
    try {
      const evidence = await api(`/api/agents/runs/${runId}/evidence`);
      if (runId === currentRunId) renderRunEvidence(evidence);
    } catch (error) {
      if (runId === currentRunId) {
        document.getElementById('evidence-digest').textContent = 'Unavailable';
        document.getElementById('run-evidence-json').textContent = `Run evidence unavailable: ${error.message}`;
      }
    } finally {
      refreshRunEvidenceButton.disabled = false;
    }
  }

  const originalRenderRun = renderRun;
  renderRun = function(run) {
    originalRenderRun(run);
    refreshRunEvidence(run.run_id);
  };

  refreshRunEvidenceButton.addEventListener('click', () => refreshRunEvidence(currentRunId));
'''


def operator_workspace_with_evidence() -> HTMLResponse:
    """Return the existing Operator Workspace with a read-only evidence surface."""
    response = operator_workspace()
    html = response.body.decode("utf-8")
    html = html.replace("  </section>\n</main>", f"  </section>{_EVIDENCE_PANEL}\n</main>", 1)
    html = html.replace("})();\n</script>", f"{_EVIDENCE_SCRIPT}\n}})();\n</script>", 1)
    return HTMLResponse(content=html)
