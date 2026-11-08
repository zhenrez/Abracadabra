/** Read-only local source service. Source content is data, never instructions. */
import { createServer, type Server, type ServerResponse, type IncomingMessage } from 'node:http';
import Database from 'better-sqlite3';
import { readFileSync, existsSync, mkdirSync } from 'node:fs';
import { createHash, randomUUID } from 'node:crypto';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { prepareComparison, completeComparison } from './comparison.js';
import {startJevWorker, type ManagedWorker} from './worker.js';

type Row = Record<string, unknown>;
export interface SunnyServerOptions {
  root?: string;
  databasePath?: string;
  /** Internal factory limits for focused transport tests; HTTP cannot override these. */
  workerTimeoutMs?: number;
  workerMaxOutputBytes?: number;
}

const PROJECT_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const ASSETS: Record<string, [string, string]> = {
  '/': ['index.html', 'text/html; charset=utf-8'],
  '/index.html': ['index.html', 'text/html; charset=utf-8'],
  '/app.js': ['app.js', 'text/javascript; charset=utf-8'],
  '/style.css': ['style.css', 'text/css; charset=utf-8'],
};
const MESSAGE_SELECT = `SELECT m.*,c.title,c.current_node,s.path AS source_path,s.original_path,s.sha256 AS source_sha256
  FROM messages m JOIN conversations c ON c.id=m.conversation_id JOIN sources s ON s.id=m.source_id`;

function numberLimit(value: string | null, fallback: number, maximum: number): number {
  if (value === null) return fallback;
  const number = Number(value);
  return Number.isSafeInteger(number) && number > 0 ? Math.min(number, maximum) : fallback;
}
function pageOffset(value: string | null): number {
  const number = Number(value ?? 0);
  return Number.isSafeInteger(number) && number >= 0 ? number : 0;
}
function pageEnvelope(results: Row[], total: number, offset: number): Row {
  const next = offset + results.length;
  return {results, total, offset, truncated: next < total, next_offset: next < total ? next : null};
}
function parsedJson(value: unknown): unknown {
  if (typeof value !== 'string') return value;
  try { return JSON.parse(value); } catch { return value; }
}
function messageView(row: Row): Row {
  return { ...row,
    is_current_path: row.branch_status === 'current' ? true : row.branch_status === 'alternate' ? false : null,
    branch: row.branch_status,
    authority: 'Original speaker; not automatically promoted to a canonical decision',
    raw: parsedJson(row.raw_json),
    parent_semantics: row.sequence_semantics ?? (['recorded_sequence', 'exported_sequence'].includes(String(row.branch_status)) ? 'Imported record sequence; not native JSON parentage or causal order.' : 'Native mapping parent ID, when available; not an assertion of causal parentage.'),
  };
}
function json(response: ServerResponse, status: number, data: unknown): void {
  response.writeHead(status, {'Content-Type': 'application/json; charset=utf-8'});
  response.end(JSON.stringify(data, (_key, value: unknown) => typeof value === 'bigint' ? value.toString() : value));
}
export function isLocalHost(host: string | undefined): boolean {
  if (!host) return false;
  try { return ['127.0.0.1', 'localhost', '[::1]'].includes(new URL(`http://${host}`).hostname); }
  catch { return false; }
}
function fixedJson(root: string, path: string, fallback: unknown): unknown {
  const file = join(root, path);
  return existsSync(file) ? JSON.parse(readFileSync(file, 'utf8')) : fallback;
}

export function createSunnyServer(options: SunnyServerOptions = {}): Server {
  const root = resolve(options.root ?? PROJECT_ROOT);
  const database = new Database(resolve(options.databasePath ?? join(root, 'data', 'sunny.sqlite')), {readonly: true, fileMustExist: true});
  database.exec('PRAGMA query_only=ON; PRAGMA busy_timeout=5000;');
  const get = (sql: string, ...args: (string | number)[]): Row | undefined => database.prepare(sql).get(...args) as Row | undefined;
  const all = (sql: string, ...args: (string | number)[]): Row[] => database.prepare(sql).all(...args) as Row[];
  const hasPositions = Boolean(get("SELECT name FROM sqlite_master WHERE type='table' AND name='source_positions'"));
  const hasLocatorHistory = Boolean(get("SELECT name FROM sqlite_master WHERE type='table' AND name='source_locator_history'"));
  const messageSelect = hasPositions ? `SELECT m.*,c.title,c.current_node,s.path AS source_path,s.original_path,s.sha256 AS source_sha256,
    p.physical_lf_line,p.utf8_byte_start,p.utf8_byte_end,p.raw_record_sha256,p.legacy_locator,p.legacy_native_id,p.native_ordinal,p.sequence_semantics,p.mapping_basis,p.decision_receipt
    FROM messages m JOIN conversations c ON c.id=m.conversation_id JOIN sources s ON s.id=m.source_id
    LEFT JOIN source_positions p ON p.message_id=m.id AND p.source_id=m.source_id` : MESSAGE_SELECT;
  let decisionsInFlight = 0;
  let shuttingDown = false;
  const workers = new Set<ManagedWorker>();
  const comparisonPath = join(root, 'state', 'comparison-runs.sqlite');
  function appendComparisonEvent(runId: string, phase: string, payload: unknown): void {
    mkdirSync(join(root, 'state'), {recursive: true});
    const ledger = new Database(comparisonPath);
    try {
      ledger.exec('CREATE TABLE IF NOT EXISTS comparison_events(sequence INTEGER PRIMARY KEY AUTOINCREMENT,run_id TEXT NOT NULL,phase TEXT NOT NULL,recorded_at TEXT NOT NULL,payload_json TEXT NOT NULL,sha256 TEXT NOT NULL)');
      const recordedAt = new Date().toISOString();
      const envelope = JSON.stringify({runId, phase, recordedAt, payload});
      const sha = createHash('sha256').update(envelope).digest('hex');
      ledger.prepare('INSERT INTO comparison_events(run_id,phase,recorded_at,payload_json,sha256) VALUES(?,?,?,?,?)').run(runId, phase, recordedAt, envelope, sha);
    } finally { ledger.close(); }
  }

  // Jev receipt000006 selected at most two concurrent explicit submissions, with no hidden queue.
  function submitAssessment(request: IncomingMessage, response: ServerResponse, operation: 'decision' | 'comparison'): void {
    if (shuttingDown) { json(response, 503, {status: 'unavailable', error: 'SUNNY is shutting down. Nothing was submitted.', fallback_decision: null}); request.resume(); return; }
    const origin = request.headers.origin;
    if (origin && origin !== `http://${request.headers.host}`) { json(response, 403, {status: 'invalid', error: 'A foreign Origin cannot submit decisions.', fallback_decision: null}); request.resume(); return; }
    if (request.headers['sec-fetch-site'] === 'cross-site') { json(response, 403, {status: 'invalid', error: 'Cross-site decision submissions are refused.', fallback_decision: null}); request.resume(); return; }
    if (request.headers['content-type']?.split(';')[0]?.trim().toLowerCase() !== 'application/json') { json(response, 415, {status: 'invalid', error: 'Decision submissions require application/json.', fallback_decision: null}); request.resume(); return; }
    if (Number(request.headers['content-length'] ?? 0) > 48000) { json(response, 413, {status: 'invalid', error: 'The request exceeds 48,000 UTF-8 bytes. Decompose explicitly.', fallback_decision: null}); request.resume(); return; }
    if (decisionsInFlight >= 2) { json(response, 429, {status: 'busy', error: 'Two explicit Jev assessments are already running. Try again after one completes.', fallback_decision: null}); request.resume(); return; }
    const chunks: Buffer[] = [];
    let bytes = 0, rejected = false;
    request.on('data', (chunk: Buffer) => {
      if (rejected) return;
      bytes += chunk.length;
      if (bytes > 48000) { rejected = true; json(response, 413, {status: 'invalid', error: 'The request exceeds 48,000 UTF-8 bytes. Nothing was submitted.', fallback_decision: null}); return; }
      chunks.push(chunk);
    });
    request.on('end', () => {
      if (rejected) return;
      const body = Buffer.concat(chunks).toString('utf8');
      let payload: unknown;
      try { payload = JSON.parse(body); }
      catch { json(response, 400, {status: 'invalid', error: 'The request body is not valid JSON.', fallback_decision: null}); return; }
      let prepared: ReturnType<typeof prepareComparison> | undefined;
      const runId = operation === 'comparison' ? randomUUID() : undefined;
      // Jev receipt000044 selected append-only SQLite events for exact comparison continuity.
      if (runId) {
        try { appendComparisonEvent(runId, 'submitted', {requestText: body, requestSha256: createHash('sha256').update(body).digest('hex'), supplied: payload}); }
        catch { json(response, 503, {status: 'unavailable', error: 'The exact comparison input could not be preserved. Nothing was submitted to Jev.', fallback_decision: null}); return; }
      }
      const respond = (status: number, result: Row): void => {
        let output: Row = result;
        if (operation === 'comparison') {
          if (status === 200 && result.status === 'judged' && prepared) {
            try {
              const answer = (Array.isArray(result.answers) ? result.answers as Row[] : []).find(row => row.id === 'comparison_action');
              output = {...completeComparison(prepared, answer?.value), jev: result, runId};
            } catch {
              status = 502;
              output = {status: 'invalid', error: 'No accepted actual Jev comparison action was returned. No calculation was inferred.', jev: result, runId, canonicalPromotion: false};
            }
          } else output = {...result, runId, canonicalPromotion: false};
          try { appendComparisonEvent(runId!, status === 200 ? 'completed' : 'failed', output); }
          catch { status = 503; output = {status: 'unavailable', error: 'The comparison outcome could not be preserved. Inspect the run and Jev receipt before retrying.', runId, canonicalPromotion: false, fallback_decision: null}; }
        }
        if (!response.writableEnded && !response.destroyed) json(response, status, output);
      };
      let modelBody = body;
      if (operation === 'comparison') {
        try {
          prepared = prepareComparison(payload, id => {
            const source = get('SELECT id,sha256 FROM sources WHERE id=?', id);
            return source ? {id: String(source.id), sha256: String(source.sha256)} : undefined;
          });
          modelBody = JSON.stringify(prepared.reviewRequest);
        } catch (error) { respond(400, {status: 'invalid', error: error instanceof Error ? error.message : 'Invalid comparison input.', fallback_decision: null}); return; }
      } else if (!payload || typeof payload !== 'object' || !('state' in payload) || !('questions' in payload) || !Array.isArray(payload.questions) || payload.questions.length < 1 || payload.questions.length > 32) {
        respond(400, {status: 'invalid', error: 'A native request needs state and 1–32 explicit typed questions.', fallback_decision: null}); return;
      }
      if (shuttingDown) { respond(503, {status: 'unavailable', error: 'SUNNY is shutting down. Nothing was submitted.', fallback_decision: null}); return; }
      if (decisionsInFlight >= 2) { respond(429, {status: 'busy', error: 'Two Jev assessments are already running. Nothing was queued.', fallback_decision: null}); return; }
      const script = join(root, 'scripts', 'jev_tool.py');
      if (!existsSync(script)) { respond(503, {status: 'unavailable', error: 'The fixed local Jev tool is unavailable.', fallback_decision: null}); return; }
      const localPython = join(root, '.venv', 'Scripts', 'python.exe');
      const executable = existsSync(localPython) ? localPython : 'python';
      decisionsInFlight++;
      // Jev receipt000050: hold capacity until the fixed worker's owned tree exits.
      // stdin remains open while its birth/script/executable identity is captured.
      const worker = startJevWorker({root, executable, script, input: modelBody,
        purpose: operation === 'comparison' ? 'SUNNY browser structural comparison' : 'SUNNY browser decision',
        timeoutMs: options.workerTimeoutMs, maxOutputBytes: options.workerMaxOutputBytes});
      workers.add(worker);
      void worker.result.then(result => {
        if (result.reaped) { workers.delete(worker); decisionsInFlight--; }
        if (!result.reaped) { respond(503, {status: 'unavailable', error: 'Request-worker cleanup could not be verified. Capacity remains reserved; inspect local service logs before retrying.', fallback_decision: null}); return; }
        if (result.reason === 'timeout') { respond(504, {status: 'unavailable', error: 'The local Jev tool timed out and its owned workers were closed. Inspect receipt history before retrying.', fallback_decision: null}); return; }
        if (result.reason === 'output_limit') { respond(502, {status: 'invalid', error: 'The local tool exceeded its output limit and its owned workers were closed. Inspect receipts.', fallback_decision: null}); return; }
        if (result.reason === 'shutdown') { respond(503, {status: 'unavailable', error: 'SUNNY closed its request workers during shutdown. Inspect receipt history before retrying.', fallback_decision: null}); return; }
        if (result.reason === 'spawn_error') { respond(503, {status: 'unavailable', error: 'The fixed local Jev tool could not be started.', fallback_decision: null}); return; }
        try {
          const output = JSON.parse(result.code === 0 ? result.stdout : result.stderr) as Row;
          respond(result.code === 0 && output.status === 'judged' ? 200 : output.status === 'invalid' ? 400 : 503, output);
        } catch { respond(502, {status: 'invalid', error: 'The local tool did not return a complete structured result. No decision was inferred.', fallback_decision: null}); }
      });
    });
    request.on('error', () => { if (!response.writableEnded) json(response, 400, {status: 'invalid', error: 'The request body could not be read.', fallback_decision: null}); });
  }

  const server = createServer((request, response) => {
    response.setHeader('Cache-Control', 'no-store');
    response.setHeader('X-Content-Type-Options', 'nosniff');
    response.setHeader('Referrer-Policy', 'no-referrer');
    response.setHeader('X-Frame-Options', 'DENY');
    response.setHeader('Content-Security-Policy', "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'self'; frame-ancestors 'none'");
    if (!isLocalHost(request.headers.host)) { json(response, 403, {error: 'Local host required.'}); return; }
    let url: URL;
    try { url = new URL(request.url ?? '/', `http://${request.headers.host}`); }
    catch { json(response, 400, {error: 'Invalid request URL.'}); return; }
    const path = url.pathname;
    if (request.method === 'POST' && (path === '/api/jev/decide' || path === '/api/compare')) { submitAssessment(request, response, path === '/api/compare' ? 'comparison' : 'decision'); return; }
    if (request.method !== 'GET') {
      response.setHeader('Allow', ['/api/jev/decide', '/api/compare'].includes(path) ? 'POST' : 'GET');
      json(response, 405, {error: 'Sources are read-only. Only the explicit local Jev assessment and comparison POST operations are permitted.'});
      return;
    }
    // Only these three public assets can be read through HTTP; no request path is joined to disk.
    const asset = ASSETS[path];
    if (asset) {
      try {
        const bytes = readFileSync(join(root, 'public', asset[0]));
        response.writeHead(200, {'Content-Type': asset[1]});
        response.end(bytes);
      } catch { json(response, 404, {error: 'Public asset unavailable.'}); }
      return;
    }
    if (path === '/favicon.ico') { response.writeHead(204); response.end(); return; }
    try {
      if (path === '/api/compare/example') {
        const example = fixedJson(root, 'state/native-comparison.json', null);
        if (!example) { json(response, 404, {error: 'The recovered native comparison example is unavailable.'}); return; }
        json(response, 200, example); return;
      }
      if (path === '/api/compare/history' || path === '/api/compare/run') {
        if (!existsSync(comparisonPath)) { json(response, path === '/api/compare/run' ? 404 : 200, {results: [], status: 'not_available'}); return; }
        const ledger = new Database(comparisonPath, {readonly: true, fileMustExist: true});
        try {
          if (path === '/api/compare/run') {
            const runId = url.searchParams.get('id') ?? '';
            if (!/^[a-f0-9-]{36}$/.test(runId)) { json(response, 400, {error: 'A full recorded run ID is required.'}); return; }
            const results = (ledger.prepare('SELECT * FROM comparison_events WHERE run_id=? ORDER BY sequence').all(runId) as Row[]).map(row => ({...row, envelope: parsedJson(row.payload_json)}));
            json(response, results.length ? 200 : 404, {results, runId, semantics: 'Append-only comparison input/outcome events with content hashes; not a source-truth certificate.'}); return;
          }
          const results = (ledger.prepare('SELECT e.* FROM comparison_events e JOIN (SELECT run_id,max(sequence) AS latest FROM comparison_events GROUP BY run_id) n ON n.latest=e.sequence ORDER BY e.sequence DESC LIMIT 20').all() as Row[]).map(row => ({...row, envelope: parsedJson(row.payload_json)}));
          json(response, 200, {results, status: 'recorded_comparisons', boundary: 'Recent20runs; exact submitted input and later outcome remain accessible by runID.'}); return;
        } finally { ledger.close(); }
      }
      if (path === '/api/summary') {
        const counts: Row = {};
        for (const table of ['sources', 'conversations', 'messages', 'nodes', 'documents', 'refs', 'decisions'] as const) {
          counts[table] = get(`SELECT count(*) AS count FROM ${table}`)?.count ?? 0;
        }
        counts.artifacts = counts.sources;
        counts.distinct_native_conversation_ids = get('SELECT count(DISTINCT native_id) AS count FROM conversations')?.count ?? 0;
        const report = fixedJson(root, 'data/recovery-report.json', {}) as Row;
        json(response, 200, {
          counts, status: 'Imported sources available', account_complete: false,
          scope: {description: report.coverage ?? 'Accessible imported records; not a complete live-account certificate.', status: 'Bounded source recovery'},
          coverage: all('SELECT * FROM coverage ORDER BY id'),
          source_statuses: all('SELECT status,count(*) AS count FROM sources GROUP BY status ORDER BY status'),
          duplicate_semantics: report.duplicate_semantics ?? 'Counts are source occurrences; matching native IDs and hashes are not silently merged.',
          narrative_review: report.narrative_review ?? 'Import is separate from semantic review and Jev reconstruction.',
        }); return;
      }
      if (path === '/api/search') {
        const query = url.searchParams.get('q') ?? '';
        if (query.length > 1000) { json(response, 400, {error: 'Search text exceeds 1,000 characters.'}); return; }
        const limit = numberLimit(url.searchParams.get('limit'), 40, 100);
        const offset = pageOffset(url.searchParams.get('offset'));
        // User text is tokenized and quoted as literal FTS terms. No FTS operators or SQL are executed from input.
        const tokens = query.match(/[\p{L}\p{N}_]+/gu)?.slice(0, 24) ?? [];
        if (!query.trim()) {
          const results = all(`${messageSelect} ORDER BY m.rowid DESC,m.id LIMIT ? OFFSET ?`, limit, offset).map(row => {
            const view = messageView(row); delete view.raw_json; delete view.raw;
            view.text = String(view.text ?? '').slice(0, 1200);
            return view;
          });
          json(response, 200, {...pageEnvelope(results, Number(get('SELECT count(*) AS count FROM messages')?.count ?? 0), offset), search_mode: 'Latest source records'}); return;
        }
        if (!tokens.length) { json(response, 200, {...pageEnvelope([], 0, offset), search_mode: 'No indexed word tokens'}); return; }
        const fts = tokens.map(token => `"${token.replaceAll('"', '""')}"`).join(' AND ');
        const results = all(`SELECT search_index.id,search_index.kind,search_index.title,
          snippet(search_index,3,'','',' … ',60) AS text,
          m.conversation_id,m.role,m.native_id,m.parent_id,m.branch_status,m.create_time,
          coalesce(m.source_id,d.source_id) AS source_id,s.path AS source_path,s.original_path,
          s.sha256 AS source_sha256,coalesce(m.locator,'document:'||d.id) AS locator
          FROM search_index LEFT JOIN messages m ON m.id=search_index.id LEFT JOIN documents d ON d.id=search_index.id
          LEFT JOIN sources s ON s.id=coalesce(m.source_id,d.source_id)
          WHERE search_index MATCH ? ORDER BY bm25(search_index),search_index.id LIMIT ? OFFSET ?`, fts, limit, offset).map(row => ({...row,
          role: row.role ?? 'source_document',
          is_current_path: row.branch_status === 'current' ? true : row.branch_status === 'alternate' ? false : null,
          branch: row.branch_status ?? 'document',
        }));
        json(response, 200, {...pageEnvelope(results, Number(get('SELECT count(*) AS count FROM search_index WHERE search_index MATCH ?', fts)?.count ?? 0), offset), search_mode: 'Literal indexed terms; all terms required'}); return;
      }
      if (path === '/api/message') {
        const id = url.searchParams.get('id') ?? '';
        const message = get(`${messageSelect} WHERE m.id=?`, id);
        if (message) { json(response, 200, {message: {...messageView(message), locator_history: hasLocatorHistory ? all('SELECT * FROM source_locator_history WHERE message_id=? ORDER BY recorded_at,id', id) : []}}); return; }
        const document = get(`SELECT d.*,s.path AS source_path,s.original_path,s.sha256 AS source_sha256 FROM documents d JOIN sources s ON s.id=d.source_id WHERE d.id=?`, id);
        if (document) { json(response, 200, {message: {...document, role: 'source_document', locator: `document:${id}`, authority: 'Extracted source document; native file retained'}}); return; }
        json(response, 404, {error: 'No indexed message or document has this ID.'}); return;
      }
      if (path === '/api/conversation') {
        const id = url.searchParams.get('id') ?? '';
        const conversation = get(`SELECT c.*,s.path AS source_path,s.original_path,s.sha256 AS source_sha256 FROM conversations c JOIN sources s ON s.id=c.source_id WHERE c.id=?`, id);
        if (!conversation) { json(response, 404, {error: 'No indexed conversation has this ID.'}); return; }
        const limit = numberLimit(url.searchParams.get('limit'), 2000, 10000);
        const offset = pageOffset(url.searchParams.get('offset'));
        const total = Number(get('SELECT count(*) AS count FROM messages WHERE conversation_id=?', id)?.count ?? 0);
        const mapped = hasPositions ? Number(get('SELECT count(*) AS count FROM source_positions p JOIN messages m ON m.id=p.message_id AND m.source_id=p.source_id WHERE m.conversation_id=?', id)?.count ?? 0) : 0;
        // Live Jev receipt000038 selected literal physical source order for repaired scopes.
        const order = mapped > 0 ? 'coalesce(p.physical_lf_line,m.rowid),m.id' : 'm.rowid,m.id';
        const messages = all(`${messageSelect} WHERE m.conversation_id=? ORDER BY ${order} LIMIT ? OFFSET ?`, id, limit, offset).map(messageView);
        json(response, 200, {conversation: {...conversation, metadata: parsedJson(conversation.metadata_json)}, messages,
          nodes: all('SELECT * FROM nodes WHERE conversation_id=? ORDER BY rowid', id), total, offset,
          truncated: offset + messages.length < total,
          next_offset: offset + messages.length < total ? offset + messages.length : null,
          source_position_count: mapped,
          message_order: mapped === total && mapped > 0 ? 'Exact physical LF source-record order; not causal parentage. Legacy locator history retained.' : mapped > 0 ? 'Partially mapped physical LF positions with import-row fallback; complete source order remains unresolved.' : 'Import record order; native branch graph retained separately. This is not causal order.',
        }); return;
      }
      if (path === '/api/artifacts') {
        const limit = numberLimit(url.searchParams.get('limit'), 10000, 10000);
        const results = all('SELECT * FROM sources ORDER BY original_path,path LIMIT ?', limit);
        const total = Number(get('SELECT count(*) AS count FROM sources')?.count ?? 0);
        json(response, 200, {results, total, truncated: results.length < total}); return;
      }
      if (path === '/api/source') {
        const id = url.searchParams.get('id') ?? '';
        const source = get('SELECT * FROM sources WHERE id=?', id);
        if (!source) { json(response, 404, {error: 'No indexed source has this ID.'}); return; }
        json(response, 200, {source, documents: all('SELECT * FROM documents WHERE source_id=?', id), delivery: 'Indexed source metadata and extracted text; arbitrary native files are not served.'}); return;
      }
      if (path === '/api/decisions') {
        const limit = numberLimit(url.searchParams.get('limit'), 200, 1000);
        const offset = pageOffset(url.searchParams.get('offset'));
        const results = all(`SELECT d.*,d.excerpt AS statement,m.role,m.conversation_id,m.locator,m.create_time,
          c.title,s.path AS source_path,s.original_path FROM decisions d JOIN messages m ON m.id=d.message_id
          JOIN conversations c ON c.id=m.conversation_id JOIN sources s ON s.id=m.source_id ORDER BY d.rowid DESC,d.id LIMIT ? OFFSET ?`, limit, offset);
        const total = Number(get('SELECT count(*) AS count FROM decisions')?.count ?? 0);
        json(response, 200, {...pageEnvelope(results, total, offset), semantics: 'Lexical candidates retain their recorded status; this endpoint does not adjudicate canonical authority.'}); return;
      }
      if (path === '/api/state') {
        json(response, 200, fixedJson(root, 'state/task.json', {status: 'not_available', goal: 'Checkpoint unavailable', constraints: [], open_questions: ['Recover the current task checkpoint.'], next_actions: ['Inspect the source-linked task state.']})); return;
      }
      if (path === '/api/capabilities') {
        json(response, 200, fixedJson(root, 'state/capabilities.json', {plugins: [], status: 'not_available', boundary: 'No capability invocation is inferred from an absent ledger.'})); return;
      }
      if (path === '/api/jev/history') {
        const historyPath = join(root, 'state', 'jev-decisions.sqlite');
        if (!existsSync(historyPath)) { json(response, 200, {results: [], status: 'not_available'}); return; }
        const history = new Database(historyPath, {readonly: true, fileMustExist: true});
        try {
          const tables = new Set((history.prepare("SELECT name FROM sqlite_master WHERE type='table'").all() as Row[]).map(row => row.name));
          const table = ['decisions', 'assessments', 'evaluations'].find(name => tables.has(name));
          if (!table) { json(response, 200, {results: [], status: 'unsupported_history_schema'}); return; }
          const results = (history.prepare(`SELECT * FROM ${table} ORDER BY rowid DESC LIMIT 100`).all() as Row[]).map(row => ({...row, payload: parsedJson(row.payload_json)}));
          json(response, 200, {results, status: 'recorded_assessments', boundary: 'Model output is retained assessment evidence, not calibrated scientific probability.'});
        } finally { history.close(); }
        return;
      }
      if (path === '/api/jev/receipt') {
        const sha = url.searchParams.get('sha256') ?? '';
        if (!/^[a-f0-9]{64}$/.test(sha)) { json(response, 400, {error: 'A full SHA-256 receipt ID is required.'}); return; }
        const historyPath = join(root, 'state', 'jev-decisions.sqlite');
        if (!existsSync(historyPath)) { json(response, 404, {error: 'The receipt ledger is unavailable.'}); return; }
        const history = new Database(historyPath, {readonly: true, fileMustExist: true});
        try {
          const row = history.prepare('SELECT * FROM decisions WHERE sha256=?').get(sha) as Row | undefined;
          if (!row) { json(response, 404, {error: 'No recorded receipt has this SHA-256.'}); return; }
          json(response, 200, {sha256: row.sha256, ...parsedJson(row.payload_json) as Row});
        } finally { history.close(); }
        return;
      }
      json(response, 404, {error: 'Unknown local resource.'});
    } catch (error) {
      console.error('SUNNY read request failed:', error instanceof Error ? error.message : 'Unknown error');
      json(response, 503, {error: 'The indexed local record could not be read. No source was changed.'});
    }
  });
  const closeServer = server.close.bind(server);
  server.close = ((callback?: (error?: Error) => void): Server => {
    shuttingDown = true;
    const cleanup = Promise.all([...workers].map(worker => worker.stop('shutdown')));
    closeServer(error => { void cleanup.then(results => callback?.(error ?? (results.some(result => !result.reaped) ? new Error('Request-worker cleanup was not verified.') : undefined))); });
    return server;
  }) as Server['close'];
  server.once('close', () => database.close());
  return server;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const port = Number(process.env.SUNNY_PORT ?? 4317);
  if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error('SUNNY_PORT must be an integer from 1 to 65535.');
  const server = createSunnyServer();
  server.listen(port, '127.0.0.1', () => console.log(`SUNNY source workspace: http://127.0.0.1:${port}`));
  for (const signal of ['SIGINT', 'SIGTERM'] as const) process.once(signal, () => {
    server.close(error => { if (error) { console.error(error.message); process.exitCode = 1; } });
  });
}
