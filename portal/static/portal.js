const token = localStorage.getItem('refinery_token');
const user  = localStorage.getItem('refinery_user');

let _auditRecords = [];

if (!token && !window.location.pathname.includes('/login')) {
  window.location.href = '/login';
}

if (user) {
  const el = document.getElementById('nav-user');
  if (el) el.textContent = user;
}

async function apiFetch(path) {
  const resp = await fetch(path, { headers: { Authorization: `Bearer ${token}` } });
  if (resp.status === 401) { localStorage.clear(); window.location.href = '/login'; }
  return resp.json();
}

async function loadDashboard() {
  const kpis = await apiFetch('/api/dashboard');
  const sub = document.getElementById('page-sub');
  if (sub) sub.textContent = `${kpis.total_audits} audits · ${kpis.flagged_count} flagged · £${(kpis.monthly_saving_usd / 1.27).toLocaleString()} risk avoided`;

  const grid = document.getElementById('kpi-grid');
  if (grid) grid.innerHTML = `
    <div class="kpi-card"><div class="kpi-num">${kpis.total_audits}</div><div class="kpi-label">Audits This Month</div></div>
    <div class="kpi-card"><div class="kpi-num" style="color:#C0392B">${kpis.flagged_count}</div><div class="kpi-label">Changes Flagged</div></div>
    <div class="kpi-card"><div class="kpi-num" style="color:#00A854">£${(kpis.monthly_saving_usd / 1.27).toLocaleString()}</div><div class="kpi-label">Risk Avoided</div></div>
    <div class="kpi-card"><div class="kpi-num">${kpis.pass_count}</div><div class="kpi-label">Signed Certificates</div></div>
  `;
  loadAudits();
}

async function loadAudits(verdict = null) {
  const url = verdict ? `/api/audits?verdict=${verdict}` : '/api/audits';
  const records = await apiFetch(url);
  _auditRecords = records;

  const tbody = document.getElementById('audit-table-body');
  if (!tbody) return;
  tbody.innerHTML = records.map(r => `
    <tr style="cursor:pointer;" onclick="openReviewModal('${r.ref_id}')">
      <td class="mono">${r.program}</td>
      <td class="dim">${r.date}</td>
      <td>
        <span class="${r.verdict === 'FLAGGED' ? 'verdict-flag' : 'verdict-pass'}">${r.verdict}</span>
        ${(r.correction_count || 0) > 0 ? `<span class="badge-corrected">Self-corrected ${r.correction_count}×</span>` : ''}
      </td>
      <td style="font-weight:700;color:${r.risk_score > 50 ? '#C0392B' : '#6E6B64'}">${r.risk_score}</td>
      <td style="font-weight:700;color:${(r.blast_radius_score||0) > 30 ? '#C0392B' : (r.blast_radius_score||0) > 0 ? '#E67E22' : '#6E6B64'}">
        ${r.blast_radius_score || 0}/100
      </td>
      <td>
        ${r.signed_at
          ? `<span style="color:#00A854;font-size:11px;font-family:monospace;">✓ ${_esc(r.signed_by)}</span>`
          : r.rejected_at
            ? `<span style="color:var(--amber,#C47B00);font-size:11px;font-family:monospace;">✗ Rejected</span><span class="rejection-label">"${_esc(r.rejection_reason)}"</span>`
            : ((r.blast_radius_score||0) > 30
                ? `<button onclick="event.stopPropagation();signContract('${r.ref_id}')" style="background:#C0392B;color:#fff;border:none;padding:4px 10px;cursor:pointer;font-size:11px;border-radius:2px;font-family:monospace;">Sign →</button>`
                : '<span style="color:#aaa;font-size:11px;">n/a</span>')
        }
      </td>
      <td><span style="color:#00A854;font-size:11px;font-family:monospace;">Click to review →</span></td>
    </tr>
  `).join('');
}

async function downloadCert(refId) {
  window.open(`/api/certificates/${refId}?token=${token}`, '_blank');
}

function filterAudits(verdict) { loadAudits(verdict); }

function _esc(s) {
  if (s == null) return '—';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function _buildSystemTags(affectedJson) {
  let systems = [];
  try { systems = JSON.parse(affectedJson || '[]'); } catch { systems = []; }
  const MAX = 9;
  const visible = systems.slice(0, MAX);
  const rest = systems.length - MAX;
  const tags = visible.map(s => {
    const isJob = /\.(jcl|JCL)$/.test(s);
    return `<span class="signoff-tag${isJob ? ' signoff-tag-job' : ''}">${_esc(s)}</span>`;
  }).join('');
  const more = rest > 0 ? `<span class="signoff-tag">+${rest} more</span>` : '';
  return tags + more;
}

function _removeModal() {
  const el = document.getElementById('signoff-overlay');
  if (el) el.remove();
  document.removeEventListener('keydown', _escHandler);
}

function _escHandler(e) {
  if (e.key === 'Escape') _removeModal();
}

async function signContract(refId) {
  const r = _auditRecords.find(rec => rec.ref_id === refId);
  if (!r) return;

  const blastScore = r.blast_radius_score || 0;
  const affectedCount = (() => {
    try { return JSON.parse(r.affected_systems_json || '[]').length; } catch { return 0; }
  })();
  const now = new Date().toISOString().replace('T', '  ').slice(0, 19) + ' UTC';

  const overlay = document.createElement('div');
  overlay.id = 'signoff-overlay';
  overlay.className = 'signoff-overlay';
  overlay.innerHTML = `
    <div class="signoff-modal" role="dialog" aria-modal="true" aria-labelledby="signoff-title">
      <div class="signoff-header">
        <h2 id="signoff-title">CRO Sign-off Required</h2>
        <span class="signoff-ref">${_esc(r.ref_id)}</span>
      </div>

      <div class="signoff-context">
        <div class="signoff-blast">
          <div class="signoff-blast-score">${blastScore}</div>
          <div>
            <div class="signoff-blast-label">Blast Radius Score</div>
            <div class="signoff-blast-sub">High — CRO sign-off mandatory</div>
          </div>
          <div class="signoff-blast-count">
            <span class="count">${affectedCount}</span>
            <span class="count-lbl">systems affected</span>
          </div>
        </div>

        <div class="signoff-info">
          <span class="signoff-info-label">Program Changed</span>
          <span class="signoff-info-value" style="font-family:var(--ff-mono);font-size:12px">${_esc(r.program)}</span>
        </div>
        <div class="signoff-info">
          <span class="signoff-info-label">Risk Score</span>
          <span class="signoff-info-value" style="font-family:var(--ff-mono)">${r.risk_score} / 100</span>
        </div>

        <div class="signoff-info signoff-narrative">
          <span class="signoff-info-label">Risk Assessment</span>
          <span class="signoff-info-value">${_esc(r.bob_headline)}</span>
        </div>

        <div class="signoff-info signoff-systems">
          <span class="signoff-info-label">Affected Systems</span>
          <div class="signoff-tags">${_buildSystemTags(r.affected_systems_json)}</div>
        </div>
      </div>

      <div class="signoff-form">
        <div class="signoff-form-row">
          <div class="signoff-field">
            <label for="signoff-name">CRO Name</label>
            <input id="signoff-name" type="text" placeholder="Full name" autocomplete="name">
          </div>
          <div class="signoff-field">
            <label>Date &amp; Time</label>
            <input type="text" value="${now}" disabled style="color:#999;background:#F5F5F0">
          </div>
        </div>
        <div class="signoff-field signoff-field-full" id="signoff-approval-field">
          <label for="signoff-reason">Approval Reason</label>
          <textarea id="signoff-reason" placeholder="State the basis for approval — e.g. 'Reviewed with risk team. Change is non-functional and scoped to packed decimal arithmetic only.'"></textarea>
        </div>
        <div class="signoff-field signoff-field-full" id="signoff-reject-field" style="display:none;">
          <label for="signoff-reject-reason">Rejection Reason <span style="color:var(--red);font-size:10px;">required</span></label>
          <textarea id="signoff-reject-reason" placeholder="State the compliance basis for rejection — e.g. 'Violates audit readability standard — preserve named PERFORM paragraphs'"></textarea>
        </div>
        <div class="signoff-warning" id="signoff-warning-text">This signature is immutable. The record will be locked once submitted.</div>
      </div>

      <div class="signoff-footer">
        <button class="btn-cancel-modal" id="signoff-cancel">Cancel</button>
        <div style="display:flex;gap:8px;margin-left:auto;">
          <button class="btn-reject-modal" id="signoff-reject-toggle">Reject instead</button>
          <button class="btn-sign-modal" id="signoff-confirm" disabled>Confirm Sign-off</button>
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(overlay);
  document.addEventListener('keydown', _escHandler);
  overlay.querySelector('#signoff-cancel').addEventListener('click', _removeModal);

  const nameInput = overlay.querySelector('#signoff-name');
  const reasonInput = overlay.querySelector('#signoff-reason');
  const confirmBtn = overlay.querySelector('#signoff-confirm');

  function _updateDisabled() {
    if (_mode === 'sign') {
      confirmBtn.disabled = !nameInput.value.trim() || !reasonInput.value.trim();
    } else {
      confirmBtn.disabled = !nameInput.value.trim() || !rejectReasonInput.value.trim();
    }
  }
  nameInput.addEventListener('input', _updateDisabled);
  reasonInput.addEventListener('input', _updateDisabled);
  nameInput.focus();

  let _mode = 'sign'; // 'sign' | 'reject'
  const approvalField = overlay.querySelector('#signoff-approval-field');
  const rejectField = overlay.querySelector('#signoff-reject-field');
  const rejectReasonInput = overlay.querySelector('#signoff-reject-reason');
  const rejectToggle = overlay.querySelector('#signoff-reject-toggle');
  const warningEl = overlay.querySelector('#signoff-warning-text');

  function _switchMode(mode) {
    _mode = mode;
    if (mode === 'reject') {
      approvalField.style.display = 'none';
      rejectField.style.display = '';
      confirmBtn.textContent = 'Confirm Rejection';
      confirmBtn.style.background = 'var(--amber, #C47B00)';
      rejectToggle.textContent = 'Sign instead';
      warningEl.textContent = 'This rejection is immutable. The record will be locked once submitted.';
      rejectReasonInput.focus();
    } else {
      approvalField.style.display = '';
      rejectField.style.display = 'none';
      confirmBtn.textContent = 'Confirm Sign-off';
      confirmBtn.style.background = '';
      rejectToggle.textContent = 'Reject instead';
      warningEl.textContent = 'This signature is immutable. The record will be locked once submitted.';
      nameInput.focus();
    }
    _updateDisabled();
  }

  rejectToggle.addEventListener('click', () => _switchMode(_mode === 'sign' ? 'reject' : 'sign'));
  rejectReasonInput.addEventListener('input', _updateDisabled);

  confirmBtn.addEventListener('click', async () => {
    confirmBtn.disabled = true;
    const isReject = _mode === 'reject';
    confirmBtn.textContent = isReject ? 'Rejecting…' : 'Signing…';

    const endpoint = isReject
      ? `/api/audits/${refId}/reject`
      : `/api/audits/${refId}/sign`;
    const body = isReject
      ? { cro_name: nameInput.value.trim(), rejection_reason: rejectReasonInput.value.trim() }
      : { cro_name: nameInput.value.trim(), approval_reason: reasonInput.value.trim() };

    try {
      const resp = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (resp.ok) {
        _removeModal();
        await loadAudits();
      } else {
        confirmBtn.textContent = isReject ? 'Confirm Rejection' : 'Confirm Sign-off';
        confirmBtn.disabled = false;
        const errMsg = overlay.querySelector('#signoff-warning-text');
        errMsg.textContent = (isReject ? 'Rejection' : 'Signature') + ' failed — server returned ' + resp.status + '. Try again.';
        errMsg.style.color = 'var(--red)';
      }
    } catch (e) {
      confirmBtn.textContent = isReject ? 'Confirm Rejection' : 'Confirm Sign-off';
      confirmBtn.disabled = false;
      const errMsg = overlay.querySelector('#signoff-warning-text');
      errMsg.textContent = 'Network error — check connection and try again.';
      errMsg.style.color = 'var(--red)';
    }
  });
}

function exportCsv() {
  window.open(`/api/audits?format=csv&token=${token}`, '_blank');
}

function openReviewModal(refId) {
  const r = _auditRecords.find(rec => rec.ref_id === refId);
  if (!r) return;

  let affected = [];
  try { affected = JSON.parse(r.affected_systems_json || '[]'); } catch {}

  const existing = document.getElementById('review-overlay');
  if (existing) existing.remove();

  const overlay = document.createElement('div');
  overlay.id = 'review-overlay';
  overlay.className = 'review-overlay';
  const accentColor = r.verdict === 'FLAGGED' ? 'var(--red)' : 'var(--green)';
  const pdfUrl = r.pdf_path ? `/api/certificates/${r.ref_id}?token=${token}` : '';

  overlay.innerHTML = `
    <div class="review-modal">

      <div class="review-left">
        <div class="review-accent-bar" style="background:${accentColor};"></div>
        <div class="review-left-inner">
          <div class="review-close" id="review-close">✕</div>

          <div class="review-program">${_esc(r.program)}</div>
          <div class="review-ref">${_esc(r.ref_id)}</div>
          <div class="review-date" style="font-size:11px;color:var(--text-3);font-family:var(--ff-mono);margin-bottom:16px;">${_esc(r.date)}</div>

          <span class="${r.verdict === 'FLAGGED' ? 'verdict-flag' : 'verdict-pass'}" style="margin-bottom:20px;display:inline-block;">${r.verdict}</span>

          <div class="review-scores">
            <div class="review-score-box">
              <div class="review-score-num" style="color:${r.risk_score > 50 ? 'var(--red)' : 'var(--text)'}">${r.risk_score}</div>
              <div class="review-score-lbl">Risk Score</div>
            </div>
            <div class="review-score-box">
              <div class="review-score-num" style="color:${(r.blast_radius_score||0) > 30 ? 'var(--red)' : 'var(--text)'}">${r.blast_radius_score || 0}</div>
              <div class="review-score-lbl">Blast Radius</div>
            </div>
          </div>

          ${affected.length ? `
          <div class="review-divider"></div>
          <div class="review-section-label">Affected Systems</div>
          <div class="review-tags">${affected.map(s => {
            const isJob = /\.(jcl|JCL)$/.test(s);
            return `<span class="signoff-tag${isJob ? ' signoff-tag-job' : ''}">${_esc(s)}</span>`;
          }).join('')}</div>
          ` : ''}

          <div class="review-divider"></div>
          <div class="review-section-label">Signature</div>
          <div style="font-size:12px;color:${r.signed_at ? 'var(--green)' : 'var(--text-2)'};margin-bottom:4px;">
            ${r.signed_at ? `✓ ${_esc(r.signed_by)}` : 'Not yet signed'}
          </div>
          ${r.signed_at ? `<div style="font-size:10px;color:var(--text-3);font-family:var(--ff-mono);">${r.signed_at.slice(0,19)} UTC</div>` : ''}

          <div class="review-actions">
            ${!r.signed_at && (r.blast_radius_score||0) > 30
              ? `<button class="review-btn-sign" onclick="_removeReviewModal();signContract('${r.ref_id}')">Sign off →</button>`
              : ''}
          </div>
        </div>
      </div>

      <div class="review-right">
        <div class="review-tabs">
          <button class="review-tab review-tab-active" id="tab-chat" onclick="switchReviewTab('chat')">Chat</button>
          ${pdfUrl ? `<button class="review-tab" id="tab-pdf" onclick="switchReviewTab('pdf')">Certificate PDF</button>` : ''}
          <div style="flex:1;"></div>
          <span style="font-size:10px;color:var(--text-3);font-family:var(--ff-mono);padding-right:16px;align-self:center;">Refinery AI · RAG · qwen2.5</span>
        </div>

        <div id="review-panel-chat" style="display:flex;flex-direction:column;flex:1;overflow:hidden;">
          <div class="review-chat-messages" id="review-chat-messages">
            <div class="chat-msg chat-msg-bob">
              <span class="chat-msg-label">Analyst</span>
              <span class="chat-msg-text">I've loaded the audit record for <strong>${_esc(r.program)}</strong>. Ask me anything — blast radius, DORA compliance, sign-off requirements, or what this change means for downstream systems.</span>
            </div>
          </div>
          <div class="review-chat-input-row">
            <input id="review-chat-input" class="review-chat-input" type="text" placeholder="Ask a question…" autocomplete="off">
            <button class="review-chat-send" id="review-chat-send">Send</button>
          </div>
        </div>

        <div id="review-panel-pdf" style="display:none;flex:1;overflow:hidden;">
          ${pdfUrl
            ? `<iframe src="${pdfUrl}" style="width:100%;height:100%;border:none;" title="Audit Certificate"></iframe>`
            : `<div style="padding:40px;color:var(--text-3);font-family:var(--ff-mono);font-size:12px;">No certificate available for this record.</div>`
          }
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(overlay);
  document.addEventListener('keydown', _reviewEscHandler);
  document.getElementById('review-close').onclick = _removeReviewModal;
  overlay.addEventListener('click', e => { if (e.target === overlay) _removeReviewModal(); });

  const input = document.getElementById('review-chat-input');
  const sendBtn = document.getElementById('review-chat-send');
  let _chatHistory = [];
  let _streaming = false;

  async function sendMessage() {
    const msg = input.value.trim();
    if (!msg || _streaming) return;
    input.value = '';
    _streaming = true;
    sendBtn.disabled = true;

    const messages = document.getElementById('review-chat-messages');

    const userDiv = document.createElement('div');
    userDiv.className = 'chat-msg chat-msg-user';
    userDiv.innerHTML = `<span class="chat-msg-label">CRO</span><span class="chat-msg-text">${_esc(msg)}</span>`;
    messages.appendChild(userDiv);

    const bobDiv = document.createElement('div');
    bobDiv.className = 'chat-msg chat-msg-bob';
    bobDiv.innerHTML = `<span class="chat-msg-label">Analyst</span><span class="chat-msg-text" id="bob-streaming-text"><span class="chat-cursor"></span></span>`;
    messages.appendChild(bobDiv);
    messages.scrollTop = messages.scrollHeight;

    const textEl = document.getElementById('bob-streaming-text');
    let fullText = '';

    try {
      const resp = await fetch('/api/audits/' + refId + '/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, history: _chatHistory, token }),
      });

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buf = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        const lines = buf.split('\n');
        buf = lines.pop();
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          try {
            const data = JSON.parse(line.slice(6));
            if (data.thinking) {
              textEl.innerHTML = '<span class="chat-thinking">Thinking<span class="chat-dots"><span>.</span><span>.</span><span>.</span></span></span>';
            }
            if (data.token) {
              fullText += data.token;
              textEl.innerHTML = fullText.replace(/\n/g, '<br>') + '<span class="chat-cursor"></span>';
              messages.scrollTop = messages.scrollHeight;
            }
            if (data.done) {
              textEl.innerHTML = fullText.replace(/\n/g, '<br>');
            }
            if (data.error) {
              textEl.innerHTML = '<span style="color:var(--amber)">&#9888; Model unavailable — ' + _esc(data.error) + '</span>';
            }
          } catch {}
        }
      }
    } catch (e) {
      textEl.textContent = 'Network error — ' + e.message;
    }

    _chatHistory.push({ role: 'user', content: msg });
    _chatHistory.push({ role: 'assistant', content: fullText });
    _streaming = false;
    sendBtn.disabled = false;
    input.focus();
  }

  sendBtn.onclick = sendMessage;
  input.addEventListener('keydown', e => { if (e.key === 'Enter') sendMessage(); });
  input.focus();
}

function switchReviewTab(tab) {
  document.getElementById('review-panel-chat').style.display = tab === 'chat' ? 'flex' : 'none';
  document.getElementById('review-panel-pdf').style.display  = tab === 'pdf'  ? 'flex' : 'none';
  document.getElementById('tab-chat').classList.toggle('review-tab-active', tab === 'chat');
  const pdfTab = document.getElementById('tab-pdf');
  if (pdfTab) pdfTab.classList.toggle('review-tab-active', tab === 'pdf');
}

function _removeReviewModal() {
  const el = document.getElementById('review-overlay');
  if (el) el.remove();
  document.removeEventListener('keydown', _reviewEscHandler);
}

function _reviewEscHandler(e) {
  if (e.key === 'Escape') _removeReviewModal();
}

if (document.getElementById('kpi-grid')) loadDashboard();
