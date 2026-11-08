'use strict';

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const ui = {view: 'overview', summary: null, checkpoint: null, selected: null, searchRequest: null, searchNext: null, searchQuery: '', decisionsNext: null, conversation: null, loaded: new Set(), model: 'wheels'};
const viewLabels = {overview: 'Overview', evidence: 'Source explorer', decisions: 'Decisions & continuity', geometry: 'Geometry workspace', comparison: 'Structural comparison', artifacts: 'Archive files', capabilities: 'Jev & capabilities'};

function node(tag, className, content) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (content !== undefined && content !== null) element.textContent = String(content);
  return element;
}
function readable(value) {
  if (typeof value === 'string' || typeof value === 'number') return String(value);
  if (value == null) return '';
  if (Array.isArray(value)) return value.map(readable).filter(Boolean).join('; ');
  return readable(value.text ?? value.statement ?? value.description ?? value.question ?? value.action ?? value.title ?? value.name ?? value.content) || JSON.stringify(value);
}
function listFrom(data, keys = ['results', 'items', 'records']) {
  if (Array.isArray(data)) return data;
  for (const key of keys) if (Array.isArray(data?.[key])) return data[key];
  return [];
}
function firstValue(object, keys) {
  for (const key of keys) if (object?.[key] !== undefined && object?.[key] !== null) return object[key];
  return undefined;
}
function count(value) {
  return Number.isFinite(Number(value)) && value !== null && value !== '' ? new Intl.NumberFormat().format(Number(value)) : '—';
}
function formatDate(value) {
  if (!value) return 'Date not recorded';
  const date = new Date(typeof value === 'number' && value < 1e12 ? value * 1000 : value);
  return Number.isNaN(date.getTime()) ? String(value) : new Intl.DateTimeFormat('en', {year: 'numeric', month: 'short', day: 'numeric', timeZone: 'America/Phoenix'}).format(date);
}
function formatBytes(value) {
  const size = Number(value);
  if (!Number.isFinite(size)) return '—';
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}
async function api(path, options = {}) {
  const response = await fetch(path, {headers: {Accept: 'application/json'}, ...options});
  if (!response.ok) throw new Error(`The local service returned ${response.status}.`);
  return response.json();
}
function displayError(container, message) {
  container.replaceChildren(node('div', 'error-state', message));
}
function notice(message = '') {
  $('#app-notice').textContent = message;
  $('#app-notice').hidden = !message;
}
function roleOf(message) { return message.role ?? message.author?.role ?? 'unrecorded'; }
function textOf(message) {
  if (typeof message.text === 'string') return message.text;
  if (typeof message.content === 'string') return message.content;
  return readable(message.content?.parts ?? message.parts ?? message.snippet ?? message.excerpt ?? 'No text content is available for this record.');
}
function metaRow(label, value) {
  return [node('dt', '', label), node('dd', '', readable(value) || 'Not recorded')];
}
function roleBadge(role) {
  return node('span', `role-badge ${['user', 'assistant'].includes(role) ? role : ''}`, role);
}
function setView(view, updateLocation = true) {
  if (!(view in viewLabels)) view = 'overview';
  ui.view = view;
  for (const panel of $$('[data-panel]')) panel.hidden = panel.dataset.panel !== view;
  for (const button of $$('[data-view]')) {
    const selected = button.dataset.view === view;
    button.classList.toggle('active', selected);
    if (selected) button.setAttribute('aria-current', 'page');
    else button.removeAttribute('aria-current');
  }
  $('#breadcrumb-view').textContent = viewLabels[view];
  document.title = `SUNNY · ${viewLabels[view]}`;
  if (updateLocation) {
    const query = view === 'evidence' && $('#source-search').value ? `?q=${encodeURIComponent($('#source-search').value)}` : '';
    history.replaceState(null, '', `#${view}${query}`);
  }
  if (view === 'artifacts' && !ui.loaded.has(view)) loadArtifacts();
  if (view === 'decisions' && !ui.loaded.has(view)) loadDecisions();
  if (view === 'capabilities' && !ui.loaded.has(view)) { loadCapabilities(); loadJevHistory(); }
  if (view === 'comparison' && !ui.loaded.has(view)) { loadComparisonExample(); loadComparisonHistory(); }
  requestAnimationFrame(drawCanvases);
}

function renderSummary(data) {
  ui.summary = data;
  const counts = data.counts ?? data.stats ?? data;
  $('#stat-conversations').textContent = count(firstValue(counts, ['conversations', 'conversation_count', 'total_conversations']));
  const messages = firstValue(counts, ['messages', 'message_count', 'total_messages', 'nodes']);
  $('#stat-messages').textContent = count(messages);
  $('#nav-message-count').textContent = count(messages);
  $('#stat-artifacts').textContent = count(firstValue(counts, ['artifacts', 'files', 'artifact_count', 'source_files', 'archive_members']));
  const scope = data.scope ?? data.coverage ?? {};
  const description = typeof scope === 'string' ? scope : scope.description ?? scope.summary ?? scope.statement;
  $('#scope-description').textContent = readable(description) || 'This workspace indexes the supplied archive and the additional sources named in its provenance ledger. A bounded import cannot establish that every account conversation or attachment was recovered.';
  const details = $('#scope-details');
  details.replaceChildren();
  const values = [
    ['Import status', data.status ?? scope.status],
    ['Earliest source', firstValue(scope, ['earliest', 'start', 'date_start']) ?? data.earliest_message],
    ['Latest source', firstValue(scope, ['latest', 'end', 'date_end']) ?? data.latest_message],
    ['Unresolved gaps', firstValue(counts, ['gaps', 'unresolved_gaps'])]
  ];
  for (const [label, value] of values) {
    if (value === undefined || value === null) continue;
    const detail = node('div', 'scope-detail');
    detail.append(node('span', 'small-dot'), node('span', '', `${label}: ${label.includes('source') ? formatDate(value) : readable(value)}`));
    details.append(detail);
  }
  $('#footer-scope').textContent = data.account_complete === true ? 'Coverage reported by the source ledger; inspect scope for boundaries.' : 'Account completeness is not assumed.';
}
function checkpointPayload(data) { return data.payload ?? data.state ?? data.checkpoint?.payload ?? data.checkpoint ?? data; }
function checkpointList(value, fallback) {
  if (Array.isArray(value) && value.length) return value.map(readable);
  if (value) return [readable(value)];
  return [fallback];
}
function renderCheckpoint(data) {
  const state = checkpointPayload(data);
  ui.checkpoint = state;
  $('#overview-goal').textContent = readable(state.goal ?? state.objective) || 'No current goal was returned by the checkpoint. Inspect the source-linked requirements before assigning new work.';
  const actions = checkpointList(state.next_actions ?? state.nextActions, 'No next action is recorded.');
  $('#overview-next').replaceChildren(...actions.slice(0, 3).map(value => node('li', '', value)));
  const questions = checkpointList(state.open_questions ?? state.openQuestions ?? state.unresolved, 'No unresolved question was returned. This does not establish that the research is complete.');
  $('#overview-questions').replaceChildren(...questions.slice(0, 3).map(value => node('li', '', value)));
  const target = $('#checkpoint-content');
  target.replaceChildren(node('h3', '', 'Current goal'), node('p', '', readable(state.goal ?? state.objective) || 'Not recorded'));
  for (const [label, values, fallback] of [
    ['Retained constraints', state.constraints, 'No constraints returned.'],
    ['Open questions', state.open_questions ?? state.openQuestions ?? state.unresolved, 'No questions returned.'],
    ['Next actions', state.next_actions ?? state.nextActions, 'No actions returned.']
  ]) {
    const list = node('ul');
    list.append(...checkpointList(values, fallback).map(value => node('li', '', value)));
    target.append(node('h3', '', label), list);
  }
}
async function loadOverview() {
  const results = await Promise.allSettled([api('/api/summary'), api('/api/state')]);
  if (results[0].status === 'fulfilled') {
    renderSummary(results[0].value);
    $('#connection-state').textContent = 'Local service connected';
    $('#connection-state').className = 'connection-state connected';
  } else {
    $('#connection-state').textContent = 'Local service unavailable';
    $('#connection-state').className = 'connection-state error';
    $('#scope-description').textContent = 'The source inventory could not be loaded. Start the local SUNNY service and refresh this workspace.';
    notice('The local source service could not be reached. No collection counts or coverage claims have been inferred.');
  }
  if (results[1].status === 'fulfilled') renderCheckpoint(results[1].value);
  else {
    $('#overview-goal').textContent = 'The checkpoint could not be loaded. Existing source records have not been altered.';
    $('#overview-next').replaceChildren(node('li', '', 'Recover the current checkpoint before continuing the research.'));
    $('#overview-questions').replaceChildren(node('li', '', 'Checkpoint unavailable; unresolved questions are not yet shown.'));
    displayError($('#checkpoint-content'), 'The checkpoint could not be loaded.');
  }
}

async function searchSources(query, {offset = 0, append = false} = {}) {
  ui.searchRequest?.abort();
  const controller = new AbortController();
  ui.searchRequest = controller;
  $('#source-search').value = query;
  setView('evidence');
  const target = $('#search-results');
  target.setAttribute('aria-busy', 'true');
  if (!append) {
    target.replaceChildren(node('div', 'loading-state', 'Searching preserved source text…'));
    ui.searchQuery = query;
    ui.searchNext = null;
    $('#search-more').hidden = true;
  }
  $('#search-more').disabled = true;
  $('#search-status').textContent = 'Searching…';
  try {
    const data = await api(`/api/search?q=${encodeURIComponent(query)}&limit=40&offset=${offset}`, {signal: controller.signal});
    if (controller.signal.aborted) return;
    const records = listFrom(data, ['results', 'messages', 'items']);
    const total = data.total ?? data.count ?? records.length;
    if (!records.length && !append) {
      $('#search-status').textContent = `0 shown of ${count(total)}${query ? ` for “${query}”` : ''}`;
      const empty = node('div', 'empty-state');
      empty.append(node('span', '', '⌕'), node('h3', '', 'No matches in the indexed text'), node('p', '', 'Try a shorter phrase or another spelling. An empty search result does not establish that the original account lacks this material.'));
      target.replaceChildren(empty);
      return;
    }
    const buttons = records.map(record => {
      const button = node('button', 'source-result');
      button.type = 'button';
      button.dataset.sourceId = record.id;
      const meta = node('div', 'result-meta');
      meta.append(roleBadge(roleOf(record)), node('span', '', formatDate(record.create_time ?? record.created_at)));
      if (record.is_current_path === false || record.branch === 'alternate') meta.append(node('span', '', 'Alternate branch'));
      button.append(meta, node('h3', '', record.title ?? record.conversation_title ?? 'Untitled conversation'), node('p', '', textOf(record).slice(0, 310) + (textOf(record).length > 310 ? '…' : '')));
      button.addEventListener('click', () => selectSource(record, button));
      return button;
    });
    if (append) target.append(...buttons); else target.replaceChildren(...buttons);
    const shown = $$('.source-result', target).length;
    $('#search-status').textContent = `${count(shown)} shown of ${count(total)}${query ? ` for “${query}”` : ''}`;
    ui.searchNext = data.next_offset ?? null;
    $('#search-more').hidden = ui.searchNext === null;
  } catch (error) {
    if (error.name === 'AbortError') return;
    $('#search-status').textContent = 'Search could not complete';
    if (append) notice(`${error.message} Existing results remain visible; the next page was not loaded.`);
    else displayError(target, `${error.message} The original sources have not been changed.`);
  } finally { if (!controller.signal.aborted) { target.removeAttribute('aria-busy'); $('#search-more').disabled = false; } }
}
async function selectSource(record, button) {
  ui.selected = record;
  for (const result of $$('.source-result')) result.classList.remove('selected');
  button?.classList.add('selected');
  renderInspector({...record, view_status: record.id ? 'Search text; retrieving full message' : 'Search text; no message ID returned'});
  if (!record.id) return;
  try {
    const data = await api(`/api/message?id=${encodeURIComponent(record.id)}`);
    if (ui.selected === record) renderInspector({...record, ...(data.message ?? data.result ?? data), view_status: 'Retrieved message text'});
  } catch {
    if (ui.selected === record) renderInspector({...record, view_status: 'Search text only; full-message lookup failed'});
  }
}
function renderInspector(record) {
  const target = $('#source-inspector');
  const heading = node('div', 'panel-heading');
  const headingText = node('div');
  headingText.append(node('span', 'eyebrow', 'ORIGINAL RECORD'), node('h2', '', record.title ?? record.conversation_title ?? 'Source record'));
  heading.append(headingText, roleBadge(roleOf(record)));
  const metadata = node('dl', 'inspector-meta');
  const branch = record.is_current_path === true ? 'Current path' : record.is_current_path === false ? 'Alternate / off-path node' : record.branch ?? 'Not reported';
  for (const [label, value] of [
    ['Date', formatDate(record.create_time ?? record.created_at)],
    ['Source', record.source_path ?? record.path ?? record.source_id],
    ['Locator', record.locator ?? record.id],
    ['Branch', branch],
    ['Order basis', record.sequence_semantics ?? record.parent_semantics],
    ['Legacy locator', record.legacy_locator],
    ['Authority', record.authority ?? record.review_status ?? 'Original speaker; no automatic promotion'],
    ['Text view', record.view_status]
  ]) metadata.append(...metaRow(label, value));
  const text = node('pre', 'source-text', textOf(record));
  const actions = node('div', 'inspector-actions');
  const conversationId = record.conversation_id ?? record.conversationId;
  if (conversationId) {
    const button = node('button', 'secondary-button', 'Open conversation context');
    button.addEventListener('click', () => openConversation(conversationId, record.id));
    actions.append(button);
  }
  if (record.id) {
    const link = node('a', 'text-button', 'View source record ↗');
    link.href = `/api/message?id=${encodeURIComponent(record.id)}`;
    link.target = '_blank';
    link.rel = 'noopener';
    actions.append(link);
  }
  target.replaceChildren(heading, metadata, text, actions);
}
async function openConversation(id, selectedMessage, offset = 0) {
  const dialog = $('#conversation-dialog');
  const append = offset > 0 && ui.conversation?.id === id;
  if (!append) {
    ui.conversation = {id, selectedMessage, nextOffset: null};
    $('#conversation-title').textContent = 'Loading conversation…';
    $('#conversation-metadata').textContent = `Native conversation ID: ${id}`;
    $('#conversation-messages').replaceChildren(node('div', 'loading-state', 'Recovering the conversation and its branch context…'));
    $('#conversation-more').hidden = true;
  }
  const current = ui.conversation;
  $('#conversation-more').disabled = true;
  if (!dialog.open) dialog.showModal();
  try {
    const data = await api(`/api/conversation?id=${encodeURIComponent(id)}&offset=${offset}`);
    if (ui.conversation !== current) return;
    const conversation = data.conversation ?? data;
    const messages = listFrom(data, ['messages', 'results', 'nodes']);
    $('#conversation-title').textContent = conversation.title ?? 'Conversation';
    const articles = messages.map(message => {
      const article = node('article', `conversation-message${message.id === selectedMessage ? ' target-message' : ''}`);
      article.dataset.messageId = message.id;
      const meta = node('div', 'result-meta');
      const branch = message.is_current_path === true ? 'Current path' : message.is_current_path === false ? 'Alternate branch' : message.branch ?? message.branch_status ?? 'Branch not reported';
      meta.append(roleBadge(roleOf(message)), node('span', '', formatDate(message.create_time)), node('span', '', branch), node('span', '', message.id ?? ''));
      article.append(meta, node('pre', '', textOf(message)));
      return article;
    });
    if (append) $('#conversation-messages').append(...articles); else $('#conversation-messages').replaceChildren(...articles);
    const shown = $$('.conversation-message').length;
    $('#conversation-metadata').textContent = `Native ID: ${id}${conversation.current_node ? ` · Current node: ${conversation.current_node}` : ''} · ${count(shown)} of ${count(data.total ?? shown)} nodes shown · ${data.message_order ?? 'Order basis not reported'}`;
    current.nextOffset = data.next_offset ?? null;
    $('#conversation-more').hidden = current.nextOffset === null;
    if (!messages.length) $('#conversation-messages').append(node('p', 'quiet-note', 'No message text was returned for this conversation.'));
    if (!append || messages.some(message => message.id === selectedMessage)) requestAnimationFrame(() => $('.target-message', dialog)?.scrollIntoView({block: 'center'}));
  } catch (error) {
    if (append) $('#conversation-metadata').textContent += ` · Next page failed: ${error.message}`;
    else displayError($('#conversation-messages'), error.message);
  } finally { $('#conversation-more').disabled = false; }
}

async function loadArtifacts() {
  $('#artifact-status').textContent = 'Loading inventory';
  try {
    const data = await api('/api/artifacts');
    const records = listFrom(data, ['results', 'artifacts', 'files', 'items']);
    $('#artifact-list').replaceChildren(...records.map(record => {
      const row = node('tr');
      const path = String(record.path ?? record.source_path ?? record.name ?? record.id ?? 'Unnamed artifact');
      const parts = path.split(/[\\/]/);
      const name = parts.pop();
      const cell = node('td', '', name);
      if (parts.length) cell.append(node('span', 'path-part', parts.join('/')));
      const hashCell = node('td');
      hashCell.append(node('code', 'hash-value', record.sha256 ?? record.hash ?? 'Not recorded'));
      row.append(cell, node('td', '', formatBytes(record.bytes ?? record.size ?? record.file_size)), node('td', '', readable(record.status ?? record.extraction_status) || 'Inventoried'), hashCell);
      return row;
    }));
    $('#artifact-status').textContent = `${count(records.length)} files shown`;
    $('#artifact-note').textContent = data.truncated || Number(data.total) > records.length ? `This view shows ${count(records.length)} of ${count(data.total)} inventory records. Consult the full local ledger for all records.` : 'Checksums identify retained bytes. Extraction status records what was read; it does not establish semantic completeness.';
    if (!records.length) $('#artifact-note').textContent = 'No inventory records were returned. This is not evidence that the archive is empty.';
    ui.loaded.add('artifacts');
  } catch (error) {
    $('#artifact-status').textContent = 'Inventory unavailable';
    $('#artifact-note').textContent = error.message;
  }
}
async function loadDecisions(offset = 0, append = false) {
  $('#decisions-more').disabled = true;
  try {
    const data = await api(`/api/decisions?offset=${offset}`);
    const records = listFrom(data, ['results', 'decisions', 'items']);
    const target = $('#decision-list');
    const items = records.map(record => {
      const item = node('article', 'decision-item');
      item.dataset.decisionId = record.id;
      const meta = node('div', 'result-meta');
      meta.append(roleBadge(record.role ?? record.speaker ?? 'record'), node('span', '', record.status ?? record.authority ?? record.review_status ?? 'Extracted candidate'));
      item.append(meta, node('h3', '', readable(record.title ?? 'Source decision candidate')));
      // Actual Jev receipt000023 selected a visible, exact source excerpt alongside its title.
      const excerpt = readable(record.statement ?? record.decision ?? record.text ?? record.content);
      if (excerpt) item.append(node('p', 'subtle', 'Extracted source excerpt'), node('p', 'decision-quote', excerpt));
      const context = readable(record.rationale ?? record.context ?? record.description);
      if (context) item.append(node('p', '', context));
      const refs = readable(record.locator ?? record.source_ref ?? record.source_path ?? record.source_id ?? record.message_id);
      if (refs) item.append(node('p', 'subtle', `Source: ${refs}`));
      if (record.conversation_id) {
        const button = node('button', 'text-button', 'Inspect conversation →');
        button.addEventListener('click', () => openConversation(record.conversation_id, record.message_id));
        item.append(button);
      }
      return item;
    });
    if (append) target.append(...items); else target.replaceChildren(...items);
    const shown = $$('.decision-item', target).length;
    $('#decision-status').textContent = `${count(shown)} shown of ${count(data.total ?? shown)}`;
    ui.decisionsNext = data.next_offset ?? null;
    $('#decisions-more').hidden = ui.decisionsNext === null;
    if (!records.length) target.append(node('p', 'quiet-note', 'No decision candidates were returned. Original conversations remain the authority for recovery.'));
    ui.loaded.add('decisions');
  } catch (error) {
    $('#decision-status').textContent = 'Unavailable';
    if (append) notice(`${error.message} Existing decision candidates remain visible.`);
    else displayError($('#decision-list'), error.message);
  } finally { $('#decisions-more').disabled = false; }
}
async function loadCapabilities() {
  try {
    const data = await api('/api/capabilities');
    const records = listFrom(data, ['plugins', 'results', 'capabilities', 'items']);
    const target = $('#capability-list');
    target.replaceChildren(...records.map(record => {
      const item = node('article', 'panel capability-item');
      const heading = node('div', 'panel-heading');
      heading.append(node('h2', '', record.name ?? record.plugin ?? record.id ?? 'Capability'), node('span', 'status-pill', record.status ?? record.runtime_status ?? 'Status not recorded'));
      item.append(heading, node('p', '', readable(record.contribution ?? record.applied_to ?? record.description ?? record.use ?? record.purpose)));
      if (record.boundary ?? record.limitation ?? record.limitations) item.append(node('p', '', readable(record.boundary ?? record.limitation ?? record.limitations)));
      if (record.evidence ?? record.skills ?? record.skill_path ?? record.output) item.append(node('p', 'capability-evidence', `Evidence: ${readable(record.evidence ?? record.skills ?? record.skill_path ?? record.output)}`));
      return item;
    }));
    if (!records.length) target.append(node('div', 'empty-state', 'The capability ledger has not returned any records. No plugin use is inferred.'));
    ui.loaded.add('capabilities');
  } catch (error) { displayError($('#capability-list'), error.message); }
}

// Jev receipt000006 selected this visible structured input surface and the max-two bridge.
let candidateSequence = 0;
function addJevCandidate() {
  const container = $('#jev-candidates');
  if (container.children.length >= 255) return;
  const sequence = ++candidateSequence;
  const row = node('div', 'jev-candidate');
  const idLabel = node('label', '', 'Candidate ID');
  const idInput = node('input', 'candidate-id');
  idInput.id = `jev-candidate-id-${sequence}`;
  idInput.value = `candidate_${sequence}`;
  idInput.required = true;
  idLabel.htmlFor = idInput.id;
  const meaningLabel = node('label', '', 'Meaning / proposed action');
  const meaning = node('textarea', 'candidate-meaning');
  meaning.id = `jev-candidate-meaning-${sequence}`;
  meaning.rows = 2;
  meaning.required = true;
  meaningLabel.htmlFor = meaning.id;
  const remove = node('button', 'text-button remove-candidate', 'Remove');
  remove.type = 'button';
  remove.setAttribute('aria-label', `Remove candidate ${sequence}`);
  remove.addEventListener('click', () => { if (container.children.length > 2) { row.remove(); updateJevPreview(); } });
  row.append(idLabel, idInput, meaningLabel, meaning, remove);
  container.append(row);
  updateJevPreview();
}
function jevRequest() {
  const entries = $$('.jev-candidate').map(row => [$('.candidate-id', row).value.trim(), $('.candidate-meaning', row).value]);
  if (new Set(entries.map(entry => entry[0])).size !== entries.length) throw new Error('Candidate IDs must be unique.');
  if (entries.some(([id]) => !id)) throw new Error('Each candidate needs a nonempty ID.');
  return {state: $('#jev-state').value, questions: [{id: 'decision', type: 'choice', question: $('#jev-question').value, options: Object.fromEntries(entries)}]};
}
function updateJevPreview() {
  try { $('#jev-request-preview').textContent = JSON.stringify(jevRequest(), null, 2); }
  catch (error) { $('#jev-request-preview').textContent = error.message; }
  for (const button of $$('.remove-candidate')) button.disabled = $$('.jev-candidate').length <= 2;
}
function receiptLink(sha, label = 'Inspect full receipt ↗') {
  const link = node('a', 'text-button', label);
  link.href = `/api/jev/receipt?sha256=${encodeURIComponent(sha)}`;
  link.target = '_blank';
  link.rel = 'noopener';
  return link;
}
function renderJevAssessment(result, target = $('#jev-result')) {
  target.replaceChildren();
  if (result.status !== 'judged') {
    target.append(node('div', 'error-state', readable(result.error) || 'No live assessment was returned.'), node('p', 'quiet-note', 'No fallback decision was substituted. Inspect actual receipt history before retrying an uncertain result.'));
    return;
  }
  const model = result.model_info ?? {};
  target.append(node('p', 'assessment-model', `${model.model ?? 'Model identity not returned'} · ${model.checkpoint ?? 'checkpoint unreported'}`));
  if (model.checkpoint_sha256) target.append(node('code', 'model-sha', model.checkpoint_sha256));
  for (const answer of result.answers ?? []) {
    const section = node('section', 'assessment-answer');
    section.append(node('h3', '', `Selected candidate: ${answer.value}`), node('p', '', answer.description ?? ''));
    const distribution = node('dl', 'distribution');
    for (const [label, mass] of Object.entries(answer.distribution ?? {})) {
      const value = Number(mass);
      distribution.append(node('dt', '', label));
      const detail = node('dd');
      const meter = node('meter');
      meter.min = 0; meter.max = 1; meter.value = value;
      meter.setAttribute('aria-label', `${label}: conditional model mass ${value}`);
      detail.append(meter, node('span', '', Number.isFinite(value) ? value.toFixed(6) : 'Invalid mass'));
      distribution.append(detail);
    }
    section.append(node('p', 'subtle', 'Full conditional model distribution'), distribution, node('p', 'quiet-note', `Top mass ${Number(answer.top_probability).toFixed(6)} · margin ${Number(answer.margin).toFixed(6)}. These values apply only to the supplied state and candidate set.`));
    target.append(section);
  }
  if (result.sha256) target.append(node('p', 'subtle', 'Receipt SHA-256'), node('code', 'model-sha', result.sha256), receiptLink(result.sha256));
  const full = node('details', 'request-preview');
  full.append(node('summary', '', 'Complete tool response'), node('pre', '', JSON.stringify(result, null, 2)));
  target.append(full);
}
async function submitJev(event) {
  event.preventDefault();
  let request;
  try { request = jevRequest(); }
  catch (error) { $('#jev-submit-status').textContent = error.message; return; }
  const body = JSON.stringify(request);
  if (new TextEncoder().encode(body).byteLength > 48000) { $('#jev-submit-status').textContent = 'The request exceeds 48,000 UTF-8 bytes. Decompose it explicitly before submitting.'; return; }
  $('#jev-submit').disabled = true;
  $('#jev-submit-status').textContent = 'Running actual local inference; awaiting a recorded result…';
  $('#jev-result').setAttribute('aria-busy', 'true');
  try {
    const response = await fetch('/api/jev/decide', {method: 'POST', headers: {'Content-Type': 'application/json', Accept: 'application/json'}, body});
    const result = await response.json();
    renderJevAssessment(result);
    $('#jev-submit-status').textContent = response.ok && result.status === 'judged' ? 'Actual assessment recorded. The source ledger has not been modified.' : `Assessment ${result.status ?? 'unavailable'}: ${result.error ?? 'no result returned'}`;
    await loadJevHistory();
  } catch (error) {
    renderJevAssessment({status: 'unavailable', error: `The local assessment request did not return a complete response. ${error.message}`});
    $('#jev-submit-status').textContent = 'Outcome not confirmed. Check receipt history before retrying.';
  } finally {
    $('#jev-submit').disabled = false;
    $('#jev-result').removeAttribute('aria-busy');
  }
}
async function loadJevHistory() {
  const target = $('#jev-history');
  try {
    const data = await api('/api/jev/history');
    const records = listFrom(data);
    target.replaceChildren(...records.slice(0, 20).map(record => {
      const payload = record.payload ?? {};
      const details = node('details', 'history-record');
      details.append(node('summary', '', `#${record.sequence ?? payload.sequence ?? '?'} · ${payload.purpose ?? 'Recorded assessment'} · ${formatDate(payload.completed_at)}`));
      const questions = payload.request?.questions ?? [];
      const answers = payload.response?.results?.[0]?.answers ?? [];
      for (const question of questions) details.append(node('p', '', question.question ?? ''));
      for (const answer of answers) details.append(node('p', 'subtle', `${answer.id}: ${readable(answer.value)} · conditional top mass ${Number(answer.top_probability).toFixed(6)}`));
      details.append(node('code', 'model-sha', record.sha256 ?? 'Hash not returned'));
      if (record.sha256) details.append(receiptLink(record.sha256));
      return details;
    }));
    if (!records.length) target.append(node('p', 'subtle', `No actual receipts returned (${data.status ?? 'unreported status'}). No inference is fabricated.`));
  } catch (error) { displayError(target, error.message); }
}

async function loadComparisonExample() {
  try {
    const example = await api('/api/compare/example');
    $('#comparison-input').value = JSON.stringify(example, null, 2);
    updateComparisonInput();
    ui.loaded.add('comparison');
  } catch (error) { $('#comparison-input-status').textContent = `The recovered example is unavailable: ${error.message}`; }
}
function updateComparisonInput() {
  try {
    const value = JSON.parse($('#comparison-input').value);
    const bytes = new TextEncoder().encode($('#comparison-input').value).byteLength;
    $('#comparison-input-status').textContent = `${count(value.candidates?.length ?? 0)} declared candidates · ${count(value.constraints?.length ?? 0)} constraints · ${count(bytes)} UTF-8 bytes. Source bindings are checked by the local service.`;
  } catch { $('#comparison-input-status').textContent = 'Enter valid JSON before submitting. No partial input is sent.'; }
}
function comparisonRunLink(id, label = 'Inspect exact input & outcome ↗') {
  const link = node('a', 'text-button', label);
  link.href = `/api/compare/run?id=${encodeURIComponent(id)}`;
  link.target = '_blank'; link.rel = 'noopener';
  return link;
}
function renderComparison(result) {
  const target = $('#comparison-result');
  target.replaceChildren(node('h3', 'comparison-verdict', result.status ?? 'No status returned'));
  if (result.error) target.append(node('div', 'error-state', result.error));
  if (result.scope) target.append(node('p', 'quiet-note', result.scope));
  if (result.inputSha256) target.append(node('p', 'subtle', 'Validated input SHA-256'), node('code', 'model-sha', result.inputSha256));
  const bindings = result.sourceBindings;
  if (bindings) {
    target.append(node('p', 'subtle', `Literal source bindings: ${bindings.status} · kernel-byte hash ${bindings.kernelBound ? 'bound' : 'unresolved'}`), node('p', 'quiet-note', bindings.semantics));
    for (const entry of bindings.sources ?? []) target.append(node('code', 'model-sha', `${entry.id} · ${entry.source?.sha256 ?? 'NOT RETRIEVED'}`));
  }
  const evaluation = result.evaluation;
  if (evaluation) {
    target.append(node('p', 'subtle', `${count(evaluation.admissible?.length ?? 0)} conditionally admissible · ${count(evaluation.rejected?.length ?? 0)} rejected under declared constraints · ${count(evaluation.unresolved?.length ?? 0)} unresolved`));
    for (const candidate of evaluation.results ?? []) {
      const details = node('details', 'comparison-candidate');
      details.append(node('summary', '', `${candidate.candidateId} · ${candidate.status}`));
      for (const witness of candidate.witnesses ?? []) {
        const item = node('div', 'comparison-witness');
        item.append(node('span', `witness-label ${witness.verdict}`, `${witness.verdict} · ${witness.constraintId}`), node('p', '', witness.reason), node('p', 'subtle', `Authority: ${witness.authority} · sources: ${readable(witness.sourceRefs)}`));
        details.append(item);
      }
      target.append(details);
    }
  } else target.append(node('p', 'quiet-note', 'No candidate calculation was executed. The observed deferral, missing binding, or failure remains explicit.'));
  if (result.jev) {
    const modelDetails = node('details', 'request-preview');
    const modelTarget = node('div');
    modelDetails.append(node('summary', '', 'Actual Jev eligibility assessment'), modelTarget);
    renderJevAssessment(result.jev, modelTarget);
    target.append(modelDetails);
  }
  if (result.runId) target.append(node('p', 'subtle', `Recorded run: ${result.runId}`), comparisonRunLink(result.runId));
  target.append(node('p', 'quiet-note', 'Canonical promotion: disabled. A literal source binding does not establish citation entailment or independent scientific support.'));
}
async function submitComparison(event) {
  event.preventDefault();
  const body = $('#comparison-input').value;
  try { JSON.parse(body); }
  catch { $('#comparison-status').textContent = 'The input is not valid JSON. Nothing was submitted.'; return; }
  if (new TextEncoder().encode(body).byteLength > 48000) { $('#comparison-status').textContent = 'The input exceeds 48,000 UTF-8 bytes. Decompose the comparison explicitly.'; return; }
  $('#comparison-submit').disabled = true;
  $('#comparison-status').textContent = 'Resolving source bindings and asking actual local Jev whether to calculate…';
  $('#comparison-result').setAttribute('aria-busy', 'true');
  try {
    const response = await fetch('/api/compare', {method: 'POST', headers: {'Content-Type': 'application/json', Accept: 'application/json'}, body});
    const result = await response.json();
    renderComparison(result);
    $('#comparison-status').textContent = response.ok ? `Observed comparison status: ${result.status}. Exact input and outcome retained.` : `Comparison ${result.status ?? 'unavailable'}: ${result.error ?? 'no structured outcome'}`;
    await loadComparisonHistory();
  } catch (error) {
    $('#comparison-status').textContent = `Outcome not confirmed: ${error.message}. Inspect recorded runs before retrying.`;
    renderComparison({status: 'unavailable', error: 'No complete local comparison response was returned.'});
  } finally { $('#comparison-submit').disabled = false; $('#comparison-result').removeAttribute('aria-busy'); }
}
async function loadComparisonHistory() {
  const target = $('#comparison-history');
  try {
    const data = await api('/api/compare/history');
    const records = listFrom(data);
    target.replaceChildren(...records.map(record => {
      const item = node('article', 'history-record');
      item.append(node('h3', '', `${record.run_id} · ${record.phase}`), node('p', 'subtle', formatDate(record.recorded_at)), comparisonRunLink(record.run_id));
      const restore = node('button', 'text-button restore-comparison', 'Restore exact input');
      restore.type = 'button';
      restore.addEventListener('click', async () => {
        try {
          const run = await api(`/api/compare/run?id=${encodeURIComponent(record.run_id)}`);
          const submitted = listFrom(run).find(event => event.phase === 'submitted');
          const text = submitted?.envelope?.payload?.requestText;
          if (typeof text !== 'string') throw new Error('The exact submitted text was not returned.');
          $('#comparison-input').value = text;
          updateComparisonInput();
          $('#comparison-status').textContent = 'Exact recorded input restored for inspection. No new assessment has been submitted.';
        } catch (error) { $('#comparison-status').textContent = error.message; }
      });
      item.append(restore);
      return item;
    }));
    if (!records.length) target.append(node('p', 'subtle', 'No recorded comparison runs returned. No result is inferred.'));
  } catch (error) { displayError(target, error.message); }
}

// Finite projection helpers. These do not assign research entities or establish a type law.
const TAU = Math.PI * 2;
function rotate(point, angles) {
  let [x, y, z] = point;
  const [a, b, c] = angles.map(value => value * Math.PI / 180);
  [y, z] = [y * Math.cos(a) - z * Math.sin(a), y * Math.sin(a) + z * Math.cos(a)];
  [x, z] = [x * Math.cos(b) + z * Math.sin(b), -x * Math.sin(b) + z * Math.cos(b)];
  [x, y] = [x * Math.cos(c) - y * Math.sin(c), x * Math.sin(c) + y * Math.cos(c)];
  return [x, y, z];
}
function sampleLine(fn, steps = 90) { return Array.from({length: steps + 1}, (_, i) => fn(i / steps)); }
function wheelLines() {
  const lines = [];
  for (let g = 0; g <= 5; g++) {
    const radius = .38 + g * .22;
    const z = -1.55 + g * .59;
    lines.push({points: sampleLine(t => [radius * Math.cos(t * TAU), radius * Math.sin(t * TAU), z]), kind: 'wheel'});
    for (let n = 0; n < 12; n++) {
      const angle = n / 12 * TAU;
      lines.push({points: [[radius * .92 * Math.cos(angle), radius * .92 * Math.sin(angle), z], [radius * 1.04 * Math.cos(angle), radius * 1.04 * Math.sin(angle), z]], kind: 'tick'});
    }
  }
  lines.push({points: sampleLine(t => {
    const g = t * 5;
    const r = .38 + g * .22;
    return [r * Math.cos(g * TAU * 2), r * Math.sin(g * TAU * 2), -1.55 + g * .59];
  }, 640), kind: 'accent'});
  lines.push({points: [[0, 0, -1.85], [0, 0, 1.7]], kind: 'axis'});
  return lines;
}
function torusLines() {
  const point = (u, v) => [(1.25 + .52 * Math.cos(v)) * Math.cos(u), (1.25 + .52 * Math.cos(v)) * Math.sin(u), .52 * Math.sin(v)];
  const lines = [];
  for (let n = 0; n < 30; n++) lines.push({points: sampleLine(t => point(n / 30 * TAU, t * TAU), 50), kind: n % 5 === 0 ? 'accent' : 'wheel'});
  for (let n = 0; n < 16; n++) lines.push({points: sampleLine(t => point(t * TAU, n / 16 * TAU), 100), kind: 'wheel'});
  return lines;
}
function tetrahedronLines() {
  const vertices = [[0, 0, 1.7], [0, 1.603, -.567], [-1.388, -.8015, -.567], [1.388, -.8015, -.567]];
  const lines = [];
  function recurse(points, depth) {
    if (!depth) {
      for (let i = 0; i < 4; i++) for (let j = i + 1; j < 4; j++) lines.push({points: [points[i], points[j]], kind: 'wheel'});
      return;
    }
    for (const vertex of points) recurse(points.map(other => other.map((v, axis) => (v + vertex[axis]) / 2)), depth - 1);
  }
  recurse(vertices, 3);
  for (let i = 0; i < 4; i++) for (let j = i + 1; j < 4; j++) lines.push({points: [vertices[i], vertices[j]], kind: 'accent'});
  return lines;
}
const models = {wheels: wheelLines(), torus: torusLines(), tetrahedron: tetrahedronLines()};
function draw(canvas, model, angles, overview = false) {
  if (!canvas || !canvas.clientWidth || !canvas.clientHeight) return;
  const ratio = Math.min(window.devicePixelRatio || 1, 2);
  const width = canvas.clientWidth, height = canvas.clientHeight;
  canvas.width = Math.round(width * ratio);
  canvas.height = Math.round(height * ratio);
  const context = canvas.getContext('2d');
  if (!context) return;
  context.scale(ratio, ratio);
  const scale = Math.min(width / 4.8, height / 4.2);
  const cx = width / 2, cy = height / 2 + (overview ? 8 : 0);
  const project = point => {
    const [x, y, z] = rotate(point, angles);
    const perspective = 6 / (6 - z);
    return [cx + x * scale * perspective, cy + y * scale * perspective, z];
  };
  // Quiet coordinate points, unrelated to source count or research placements.
  context.fillStyle = '#39402e';
  for (let x = 22; x < width; x += 28) for (let y = 24; y < height; y += 28) { context.beginPath(); context.arc(x, y, .6, 0, TAU); context.fill(); }
  const lines = models[model].map(line => ({...line, points: line.points.map(project)}));
  lines.sort((a, b) => a.points.reduce((s, p) => s + p[2], 0) / a.points.length - b.points.reduce((s, p) => s + p[2], 0) / b.points.length);
  for (const line of lines) {
    const z = line.points.reduce((sum, point) => sum + point[2], 0) / line.points.length;
    const alpha = Math.max(.18, Math.min(.75, .4 + z * .12));
    context.strokeStyle = line.kind === 'accent' ? `rgba(239,171,98,${Math.min(.95, alpha + .2)})` : line.kind === 'axis' ? 'rgba(146,153,124,.3)' : `rgba(162,181,132,${alpha})`;
    context.lineWidth = line.kind === 'accent' ? 1.3 : .7;
    context.setLineDash(line.kind === 'axis' ? [3, 5] : []);
    context.beginPath();
    line.points.forEach(([x, y], i) => i ? context.lineTo(x, y) : context.moveTo(x, y));
    context.stroke();
  }
  context.setLineDash([]);
  context.font = '9px "Segoe UI", sans-serif';
  context.fillStyle = '#8b8f7c';
  context.fillText('FINITE PROJECTION / UNASSIGNED', 4, height - 9);
  if (model === 'wheels') {
    const [x, y] = project([0, 0, -1.55]);
    context.beginPath(); context.arc(x, y, 3, 0, TAU); context.fillStyle = '#efab62'; context.fill();
  }
}
function drawCanvases() {
  draw($('#overview-canvas'), 'wheels', [63, -18, -15], true);
  const angles = ['x', 'y', 'z'].map(axis => Number($(`#rotation-${axis}`).value));
  draw($('#geometry-canvas'), ui.model, angles);
}
function chooseModel(model) {
  ui.model = model;
  for (const button of $$('[data-model]')) { button.classList.toggle('active', button.dataset.model === model); button.setAttribute('aria-pressed', String(button.dataset.model === model)); }
  const labels = {wheels: 'Unassigned generation scaffold', torus: 'Parametric torus / illustrative surface', tetrahedron: 'Sierpinski tetrahedron / finite depth 3'};
  $('#geometry-model-label').textContent = labels[model];
  $('#geometry-canvas').setAttribute('aria-label', `Interactive finite projection: ${labels[model]}. No canonical research assignments.`);
  $('#geometry-disclaimer').textContent = model === 'tetrahedron' ? 'This finite depth-3 construction is an inspection aid. It does not reach infinitum or establish the Monad’s mathematical identity.' : model === 'torus' ? 'This parametric torus is an inspection aid. A drawn surface does not establish a general equivalence with sound waveforms or a 4D causal law.' : 'The scaffold is an inspection aid. No source has been assigned a canonical generation, radius, or topological address by this drawing.';
  drawCanvases();
}

for (const button of $$('[data-view]')) button.addEventListener('click', () => setView(button.dataset.view));
for (const button of $$('[data-go]')) button.addEventListener('click', () => setView(button.dataset.go));
for (const button of $$('[data-query]')) button.addEventListener('click', () => searchSources(button.dataset.query));
for (const button of $$('[data-model]')) button.addEventListener('click', () => chooseModel(button.dataset.model));
$('#search-form').addEventListener('submit', event => { event.preventDefault(); searchSources($('#source-search').value.trim()); });
$('#search-more').addEventListener('click', () => { if (ui.searchNext !== null) searchSources(ui.searchQuery, {offset: ui.searchNext, append: true}); });
$('#decisions-more').addEventListener('click', () => { if (ui.decisionsNext !== null) loadDecisions(ui.decisionsNext, true); });
$('#conversation-more').addEventListener('click', () => { const current = ui.conversation; if (current && current.nextOffset !== null) openConversation(current.id, current.selectedMessage, current.nextOffset); });
$('#close-conversation').addEventListener('click', () => $('#conversation-dialog').close());
$('#add-jev-candidate').addEventListener('click', addJevCandidate);
$('#jev-form').addEventListener('input', updateJevPreview);
$('#jev-form').addEventListener('submit', submitJev);
$('#refresh-jev-history').addEventListener('click', loadJevHistory);
$('#comparison-example').addEventListener('click', loadComparisonExample);
$('#comparison-input').addEventListener('input', updateComparisonInput);
$('#comparison-form').addEventListener('submit', submitComparison);
$('#comparison-history-refresh').addEventListener('click', loadComparisonHistory);
$('#conversation-dialog').addEventListener('click', event => { if (event.target === $('#conversation-dialog')) { const rect = event.target.getBoundingClientRect(); if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) event.target.close(); } });
for (const axis of ['x', 'y', 'z']) $(`#rotation-${axis}`).addEventListener('input', event => { $(`#rotation-${axis}-value`).textContent = `${event.target.value}°`; drawCanvases(); });
$('#reset-view').addEventListener('click', () => { for (const [axis, value] of [['x', 58], ['y', 0], ['z', -12]]) { $(`#rotation-${axis}`).value = value; $(`#rotation-${axis}-value`).textContent = `${value}°`; } drawCanvases(); });
$('#refresh').addEventListener('click', async () => {
  $('#refresh').disabled = true;
  notice();
  ui.loaded.clear();
  await loadOverview();
  setView(ui.view);
  if (ui.view === 'evidence' && $('#source-search').value) await searchSources($('#source-search').value);
  $('#refresh').disabled = false;
});
function readLocation() {
  const [view, params] = location.hash.slice(1).split('?');
  setView(view || 'overview', false);
  const query = new URLSearchParams(params).get('q');
  if (view === 'evidence' && query) searchSources(query);
}
window.addEventListener('hashchange', readLocation);
window.addEventListener('resize', drawCanvases);
if (typeof ResizeObserver !== 'undefined') new ResizeObserver(drawCanvases).observe($('#main'));
readLocation();
addJevCandidate();
addJevCandidate();
loadOverview();
requestAnimationFrame(drawCanvases);
