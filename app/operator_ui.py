from __future__ import annotations

from fastapi.responses import HTMLResponse


_OPERATOR_HTML = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Guided Agent OS — Operator Workspace</title>
  <style>
    :root { color-scheme: light dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
    body { margin: 0; background: #0b1020; color: #edf2ff; }
    main { max-width: 1040px; margin: 0 auto; padding: 32px 20px 56px; }
    h1 { margin: 0 0 8px; font-size: 30px; }
    .muted { color: #aeb8d4; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
    .card { background: #141b31; border: 1px solid #293553; border-radius: 14px; padding: 18px; margin-top: 18px; }
    label { display: block; font-size: 13px; color: #cbd4ed; margin: 12px 0 6px; }
    input, textarea, select, button { font: inherit; }
    input, textarea, select { width: 100%; box-sizing: border-box; border: 1px solid #374464; border-radius: 9px; background: #0f1629; color: #f7f9ff; padding: 10px 11px; }
    textarea { min-height: 92px; resize: vertical; }
    button { border: 0; border-radius: 9px; padding: 10px 14px; cursor: pointer; font-weight: 700; }
    .primary { background: #7c9cff; color: #071023; }
    .approve { background: #43d19e; color: #07150f; }
    .reject { background: #ff7b88; color: #20080b; }
    button:disabled { opacity: .5; cursor: not-allowed; }
    pre { white-space: pre-wrap; word-break: break-word; background: #0c1325; padding: 12px; border-radius: 9px; border: 1px solid #263452; }
    .pill { display: inline-block; padding: 4px 9px; border-radius: 999px; background: #263452; margin-right: 6px; font-size: 12px; }
    .hidden { display: none; }
    .actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 12px; }
    .error { color: #ff9aa5; }
    .source { border-top: 1px solid #293553; padding-top: 10px; margin-top: 10px; }
  </style>
</head>
<body>
<main>
  <h1>Guided Agent OS</h1>
  <div class="muted">Controlled enterprise AI workflow proof. Backend API remains the source of truth.</div>

  <section class="card" aria-labelledby="request-heading">
    <h2 id="request-heading">1. Controlled request</h2>
    <form id="agent-form">
      <label for="user_request">User request</label>
      <textarea id="user_request" required>Look up legacy database record LEG-001 and summarize the access constraints.</textarea>

      <label for="business_context">Business context</label>
      <textarea id="business_context" required>Internal maintenance operator needs a controlled lookup before reviewing a historical facility record.</textarea>

      <div class="grid">
        <div>
          <label for="data_sources">Data sources (comma separated)</label>
          <input id="data_sources" value="domain_knowledge,agent_policy,tool_catalog" required />
        </div>
        <div>
          <label for="expected_output">Expected output</label>
          <input id="expected_output" value="Grounded answer, sources, and controlled execution result" required />
        </div>
        <div>
          <label for="risk_level">Risk level</label>
          <select id="risk_level"><option>internal</option><option>medium</option><option>low</option><option>restricted</option><option>high</option></select>
        </div>
        <div>
          <label for="record_id">Legacy record ID</label>
          <input id="record_id" value="LEG-001" required />
        </div>
      </div>
      <div class="actions"><button id="run-button" class="primary" type="submit">Run controlled agent</button></div>
    </form>
    <p id="request-error" class="error hidden" role="alert"></p>
  </section>

  <section id="run-panel" class="card hidden" aria-live="polite">
    <h2>2. Run result</h2>
    <div><span class="pill" id="run-status">status</span><span class="pill" id="run-id">run</span></div>

    <h3>Grounded answer</h3>
    <pre id="answer">—</pre>

    <h3>Citations</h3>
    <div id="citations" class="muted">No citations returned.</div>

    <h3>Tool plan</h3>
    <pre id="tool-plan">—</pre>

    <div id="review-panel" class="hidden">
      <h3>Human review</h3>
      <div class="muted">Execution remains blocked until an operator explicitly approves this run.</div>
      <div class="actions">
        <button id="approve-button" class="approve" type="button">Approve read-only execution</button>
        <button id="reject-button" class="reject" type="button">Reject</button>
      </div>
    </div>

    <h3>Execution result</h3>
    <pre id="execution-result">Not executed.</pre>

    <h3>Audit timeline</h3>
    <div id="audit-shell" class="muted">Persistent lifecycle events arrive in Phase 4. Current shell shows observable run state transitions only.</div>
  </section>
</main>
<script>
(() => {
  const form = document.getElementById('agent-form');
  const panel = document.getElementById('run-panel');
  const requestError = document.getElementById('request-error');
  const approveButton = document.getElementById('approve-button');
  const rejectButton = document.getElementById('reject-button');
  let currentRunId = null;

  function csv(value) {
    return value.split(',').map(item => item.trim()).filter(Boolean);
  }

  async function api(path, options = {}) {
    const response = await fetch(path, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    });
    const payload = await response.json();
    if (!response.ok) {
      const detail = payload && payload.detail ? payload.detail : `HTTP ${response.status}`;
      throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
    }
    return payload;
  }

  function renderCitations(citations) {
    const container = document.getElementById('citations');
    container.innerHTML = '';
    if (!Array.isArray(citations) || citations.length === 0) {
      container.textContent = 'No citations returned.';
      return;
    }
    citations.forEach((citation, index) => {
      const div = document.createElement('div');
      div.className = 'source';
      const title = citation.title || citation.source_path || citation.doc_id || `Source ${index + 1}`;
      const score = citation.score === undefined ? '' : ` — score ${citation.score}`;
      div.textContent = `${index + 1}. ${title}${score}`;
      container.appendChild(div);
    });
  }

  function renderRun(run) {
    currentRunId = run.run_id;
    panel.classList.remove('hidden');
    document.getElementById('run-status').textContent = run.status || 'unknown';
    document.getElementById('run-id').textContent = run.run_id || 'no run id';

    const rag = run.rag_answer || {};
    document.getElementById('answer').textContent = rag.answer || 'No grounded answer returned.';
    renderCitations(rag.citations || []);
    document.getElementById('tool-plan').textContent = JSON.stringify(run.tool_plan || {}, null, 2);

    const reviewPanel = document.getElementById('review-panel');
    if (run.status === 'pending_approval') reviewPanel.classList.remove('hidden');
    else reviewPanel.classList.add('hidden');

    const execution = run.raw_output && run.raw_output.execution_result;
    document.getElementById('execution-result').textContent = execution ? JSON.stringify(execution, null, 2) : 'Not executed.';
    document.getElementById('audit-shell').textContent = `Observed state: ${run.status || 'unknown'} · persistent lifecycle event history is Phase 4.`;
  }

  async function submitDecision(decision) {
    if (!currentRunId) return;
    approveButton.disabled = true;
    rejectButton.disabled = true;
    try {
      const endpoint = decision === 'approve' ? 'approve' : 'reject';
      const body = decision === 'approve' ? { note: 'Approved from operator workspace.' } : { reason: 'Rejected from operator workspace.' };
      const run = await api(`/api/agents/runs/${currentRunId}/${endpoint}`, { method: 'POST', body: JSON.stringify(body) });
      renderRun(run);
    } catch (error) {
      requestError.textContent = error.message;
      requestError.classList.remove('hidden');
    } finally {
      approveButton.disabled = false;
      rejectButton.disabled = false;
    }
  }

  form.addEventListener('submit', async event => {
    event.preventDefault();
    requestError.classList.add('hidden');
    const runButton = document.getElementById('run-button');
    runButton.disabled = true;
    try {
      const payload = {
        user_request: document.getElementById('user_request').value.trim(),
        business_context: document.getElementById('business_context').value.trim(),
        data_sources: csv(document.getElementById('data_sources').value),
        expected_output: document.getElementById('expected_output').value.trim(),
        risk_level: document.getElementById('risk_level').value,
        allowed_tools: ['legacy_db_lookup'],
        tool_parameters: { record_id: document.getElementById('record_id').value.trim() },
      };
      const run = await api('/api/agents/controlled_rag_agent/runs', { method: 'POST', body: JSON.stringify(payload) });
      renderRun(run);
    } catch (error) {
      requestError.textContent = error.message;
      requestError.classList.remove('hidden');
    } finally {
      runButton.disabled = false;
    }
  });

  approveButton.addEventListener('click', () => submitDecision('approve'));
  rejectButton.addEventListener('click', () => submitDecision('reject'));
})();
</script>
</body>
</html>'''


def operator_workspace() -> HTMLResponse:
    """Return the dependency-free Proof v1.0 operator workspace."""
    return HTMLResponse(content=_OPERATOR_HTML)
