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
    .recover { background: #ffd166; color: #241900; }
    button:disabled { opacity: .5; cursor: not-allowed; }
    pre { white-space: pre-wrap; word-break: break-word; background: #0c1325; padding: 12px; border-radius: 9px; border: 1px solid #263452; }
    .pill { display: inline-block; padding: 4px 9px; border-radius: 999px; background: #263452; margin-right: 6px; font-size: 12px; }
    .hidden { display: none; }
    .actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 12px; }
    .error { color: #ff9aa5; }
    .warning { border-left: 3px solid #ffd166; padding: 10px 12px; background: #2a2110; border-radius: 6px; }
    .source { border-top: 1px solid #293553; padding-top: 10px; margin-top: 10px; }
    .clarification { border-left: 3px solid #7c9cff; padding: 8px 12px; margin: 8px 0; background: #10192e; border-radius: 6px; }
    .queue-item { display: flex; justify-content: space-between; gap: 12px; align-items: center; border-top: 1px solid #293553; padding: 10px 0; }
    .queue-item:first-child { border-top: 0; }
    .queue-meta { min-width: 0; }
    .queue-run { font-weight: 700; word-break: break-all; }
    .audit-event { display: grid; grid-template-columns: 56px minmax(180px, .8fr) minmax(160px, .7fr) minmax(260px, 1.5fr); gap: 10px; align-items: start; padding: 10px 0; border-top: 1px solid #293553; font-size: 13px; }
    .audit-event:first-child { border-top: 0; }
    .audit-sequence { font-weight: 700; color: #7c9cff; }
    .audit-type { font-weight: 700; }
    .audit-payload { white-space: pre-wrap; word-break: break-word; color: #cbd4ed; }
    @media (max-width: 760px) { .audit-event { grid-template-columns: 48px 1fr; } .audit-payload { grid-column: 1 / -1; } .queue-item { align-items: flex-start; flex-direction: column; } }
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
      <textarea id="user_request">Look up legacy database record LEG-001 and summarize the access constraints.</textarea>

      <label for="business_context">Business context</label>
      <textarea id="business_context">Internal maintenance operator needs a controlled lookup before reviewing a historical facility record.</textarea>

      <div class="grid">
        <div>
          <label for="data_sources">Data sources (comma separated)</label>
          <input id="data_sources" value="domain_knowledge,agent_policy,tool_catalog" />
        </div>
        <div>
          <label for="expected_output">Expected output</label>
          <input id="expected_output" value="Grounded answer, sources, and controlled execution result" />
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

    <h3>Load persisted run</h3>
    <div class="muted">Use an existing run ID after a browser/server interruption to inspect persisted state before taking any recovery action.</div>
    <div class="grid">
      <div>
        <label for="load-run-id">Run ID</label>
        <input id="load-run-id" placeholder="Existing run ID" />
      </div>
    </div>
    <div class="actions"><button id="load-run-button" class="primary" type="button">Load persisted run</button></div>

    <h3>Interrupted-decision recovery queue</h3>
    <div class="muted">Read-only discovery of persisted approval/rejection claims that require operator attention. Selecting a run only uses the existing persisted-run loader.</div>
    <div class="actions"><button id="refresh-recovery-queue-button" class="primary" type="button">Refresh recovery queue</button></div>
    <div id="recovery-queue" class="muted" aria-live="polite">Queue not loaded.</div>

    <p id="request-error" class="error hidden" role="alert"></p>
  </section>

  <section id="run-panel" class="card hidden" aria-live="polite">
    <h2>2. Run result</h2>
    <div><span class="pill" id="run-status">status</span><span class="pill" id="run-id">run</span></div>

    <div id="clarification-panel" class="hidden">
      <h3>Clarification required</h3>
      <div class="muted">Complete the missing context in the request form, then run the agent again.</div>
      <div id="clarification-questions"></div>
    </div>

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

    <div id="recovery-panel" class="hidden">
      <h3>Interrupted decision requires quarantine</h3>
      <div id="recovery-message" class="warning">An approval/rejection claim was interrupted. Do not replay execution. Quarantine the decision for explicit follow-up.</div>
      <div class="actions">
        <button id="recover-decision-button" class="recover" type="button">Quarantine interrupted decision</button>
      </div>
      <div class="muted">Successful quarantine persists DECISION_RECOVERY_REQUIRED and transitions the run to decision_recovery_required.</div>
    </div>

    <h3>Execution result</h3>
    <pre id="execution-result">Not executed.</pre>

    <h3>Audit timeline</h3>
    <div id="audit-timeline" class="muted" aria-live="polite">Loading persisted lifecycle events…</div>
  </section>
</main>
<script>
(() => {
  const form = document.getElementById('agent-form');
  const panel = document.getElementById('run-panel');
  const requestError = document.getElementById('request-error');
  const approveButton = document.getElementById('approve-button');
  const rejectButton = document.getElementById('reject-button');
  const loadRunIdInput = document.getElementById('load-run-id');
  const loadRunButton = document.getElementById('load-run-button');
  const recoveryQueue = document.getElementById('recovery-queue');
  const refreshRecoveryQueueButton = document.getElementById('refresh-recovery-queue-button');
  const recoveryPanel = document.getElementById('recovery-panel');
  const recoveryMessage = document.getElementById('recovery-message');
  const recoverDecisionButton = document.getElementById('recover-decision-button');
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

  function renderClarifications(questions) {
    const clarificationPanel = document.getElementById('clarification-panel');
    const container = document.getElementById('clarification-questions');
    container.innerHTML = '';
    if (!Array.isArray(questions) || questions.length === 0) {
      clarificationPanel.classList.add('hidden');
      return;
    }
    questions.forEach(item => {
      const div = document.createElement('div');
      div.className = 'clarification';
      div.textContent = item.question || item.message || JSON.stringify(item);
      container.appendChild(div);
    });
    clarificationPanel.classList.remove('hidden');
  }

  function renderAuditEvents(events) {
    const container = document.getElementById('audit-timeline');
    container.innerHTML = '';
    if (!Array.isArray(events) || events.length === 0) {
      container.className = 'muted';
      container.textContent = 'No persisted lifecycle events returned.';
      return;
    }
    container.className = '';
    events.forEach(event => {
      const row = document.createElement('div');
      row.className = 'audit-event';

      const sequence = document.createElement('div');
      sequence.className = 'audit-sequence';
      sequence.textContent = `#${event.sequence}`;

      const type = document.createElement('div');
      type.className = 'audit-type';
      type.textContent = event.event_type || 'UNKNOWN';

      const actor = document.createElement('div');
      actor.textContent = `${event.actor || 'system'} · ${event.created_at || 'time unavailable'}`;

      const payload = document.createElement('div');
      payload.className = 'audit-payload';
      payload.textContent = JSON.stringify(event.payload || {}, null, 2);

      row.append(sequence, type, actor, payload);
      container.appendChild(row);
    });
  }

  function renderRecoveryQueue(runs) {
    recoveryQueue.innerHTML = '';
    if (!Array.isArray(runs) || runs.length === 0) {
      recoveryQueue.className = 'muted';
      recoveryQueue.textContent = 'No interrupted or recovery-required runs.';
      return;
    }
    recoveryQueue.className = '';
    runs.forEach(run => {
      const row = document.createElement('div');
      row.className = 'queue-item';

      const meta = document.createElement('div');
      meta.className = 'queue-meta';
      const runId = document.createElement('div');
      runId.className = 'queue-run';
      runId.textContent = run.run_id;
      const status = document.createElement('div');
      status.className = 'muted';
      status.textContent = `${run.status} · ${run.created_at || 'created time unavailable'}`;
      meta.append(runId, status);

      const openButton = document.createElement('button');
      openButton.type = 'button';
      openButton.className = 'primary';
      openButton.textContent = 'Open persisted run';
      openButton.addEventListener('click', () => {
        loadRunIdInput.value = run.run_id;
        loadPersistedRun();
      });

      row.append(meta, openButton);
      recoveryQueue.appendChild(row);
    });
  }

  async function refreshRecoveryQueue() {
    refreshRecoveryQueueButton.disabled = true;
    recoveryQueue.className = 'muted';
    recoveryQueue.textContent = 'Loading recovery queue…';
    requestError.classList.add('hidden');
    try {
      const runs = await api('/api/agents/runs/recovery-queue');
      renderRecoveryQueue(runs);
    } catch (error) {
      recoveryQueue.className = 'error';
      recoveryQueue.textContent = `Recovery queue unavailable: ${error.message}`;
    } finally {
      refreshRecoveryQueueButton.disabled = false;
    }
  }

  async function refreshAuditTimeline(runId) {
    const container = document.getElementById('audit-timeline');
    container.className = 'muted';
    container.textContent = 'Loading persisted lifecycle events…';
    try {
      const events = await api(`/api/agents/runs/${runId}/events`);
      if (runId === currentRunId) renderAuditEvents(events);
    } catch (error) {
      if (runId === currentRunId) {
        container.className = 'error';
        container.textContent = `Audit timeline unavailable: ${error.message}`;
      }
    }
  }

  function renderRun(run) {
    currentRunId = run.run_id;
    loadRunIdInput.value = run.run_id || '';
    panel.classList.remove('hidden');
    document.getElementById('run-status').textContent = run.status || 'unknown';
    document.getElementById('run-id').textContent = run.run_id || 'no run id';
    renderClarifications(run.clarification_questions || []);

    const rag = run.rag_answer || {};
    document.getElementById('answer').textContent = rag.answer || 'No grounded answer returned.';
    renderCitations(rag.citations || []);
    document.getElementById('tool-plan').textContent = JSON.stringify(run.tool_plan || {}, null, 2);

    const reviewPanel = document.getElementById('review-panel');
    if (run.status === 'pending_approval') reviewPanel.classList.remove('hidden');
    else reviewPanel.classList.add('hidden');

    const interruptedDecision = run.status === 'approval_executing' || run.status === 'rejection_processing';
    if (interruptedDecision) {
      recoveryPanel.classList.remove('hidden');
      recoveryMessage.textContent = `Interrupted ${run.status} claim detected. Quarantine without replay before any further decision action.`;
      recoverDecisionButton.disabled = false;
    } else if (run.status === 'decision_recovery_required') {
      recoveryPanel.classList.remove('hidden');
      recoveryMessage.textContent = 'Decision is quarantined as decision_recovery_required. Automatic replay/resume is intentionally unavailable.';
      recoverDecisionButton.disabled = true;
    } else {
      recoveryPanel.classList.add('hidden');
      recoverDecisionButton.disabled = true;
    }

    if (run.status === 'decision_recovery_required') {
      approveButton.disabled = true;
      rejectButton.disabled = true;
    } else if (run.status === 'pending_approval') {
      approveButton.disabled = false;
      rejectButton.disabled = false;
    }

    const execution = run.raw_output && run.raw_output.execution_result;
    document.getElementById('execution-result').textContent = execution ? JSON.stringify(execution, null, 2) : 'Not executed.';
    refreshAuditTimeline(run.run_id);
  }

  async function loadPersistedRun() {
    const runId = loadRunIdInput.value.trim();
    if (!runId) return;
    loadRunButton.disabled = true;
    requestError.classList.add('hidden');
    try {
      const run = await api(`/api/agents/runs/${runId}`);
      renderRun(run);
    } catch (error) {
      requestError.textContent = error.message;
      requestError.classList.remove('hidden');
    } finally {
      loadRunButton.disabled = false;
    }
  }

  async function recoverInterruptedDecision() {
    if (!currentRunId) return;
    recoverDecisionButton.disabled = true;
    approveButton.disabled = true;
    rejectButton.disabled = true;
    requestError.classList.add('hidden');
    try {
      const run = await api(`/api/agents/runs/${currentRunId}/recover-decision`, { method: 'POST' });
      renderRun(run);
      refreshRecoveryQueue();
    } catch (error) {
      requestError.textContent = error.message;
      requestError.classList.remove('hidden');
      recoverDecisionButton.disabled = false;
    }
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
      try {
        const persisted = await api(`/api/agents/runs/${currentRunId}`);
        renderRun(persisted);
      } catch (_) {
        // Keep the original decision error visible; persisted run can be loaded explicitly after restart.
      }
    } finally {
      if (!panel.classList.contains('hidden') && document.getElementById('run-status').textContent === 'pending_approval') {
        approveButton.disabled = false;
        rejectButton.disabled = false;
      }
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
  loadRunButton.addEventListener('click', loadPersistedRun);
  refreshRecoveryQueueButton.addEventListener('click', refreshRecoveryQueue);
  recoverDecisionButton.addEventListener('click', recoverInterruptedDecision);
})();
</script>
</body>
</html>'''


def operator_workspace() -> HTMLResponse:
    """Return the dependency-free Proof v1.0 operator workspace."""
    return HTMLResponse(content=_OPERATOR_HTML)