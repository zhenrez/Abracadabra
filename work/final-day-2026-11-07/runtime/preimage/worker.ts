/** Fixed-script request workers, isolated from the long-lived inference service. */
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';

type StopReason = 'timeout' | 'output_limit' | 'shutdown';
export interface WorkerOptions {
  root: string; executable: string; script: string; input: string; purpose: string;
  timeoutMs?: number; maxOutputBytes?: number;
}
export interface WorkerResult {
  reason: 'complete' | StopReason | 'spawn_error' | 'cleanup_error';
  code: number | null; stdout: string; stderr: string; reaped: boolean;
  cleanup?: unknown; error?: string;
}
export interface ManagedWorker {
  result: Promise<WorkerResult>;
  stop: (reason?: StopReason) => Promise<WorkerResult>;
}
const HELPER = fileURLToPath(new URL('../scripts/stop-jev-worker.ps1', import.meta.url));
async function waitForExit(exited: Promise<void>, milliseconds: number): Promise<void> {
  let timer: ReturnType<typeof setTimeout> | undefined;
  try { await Promise.race([exited, new Promise<void>(resolve => { timer = setTimeout(resolve, milliseconds); })]); }
  finally { if (timer) clearTimeout(timer); }
}

function helper(args: string[], input = ''): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const child = spawn('powershell.exe', ['-NoProfile', '-NonInteractive', '-File', HELPER, ...args], {windowsHide: true, shell: false, stdio: ['pipe', 'pipe', 'pipe']});
    const output: Buffer[] = [], errors: Buffer[] = [];
    let bytes = 0, timedOut = false;
    const timer = setTimeout(() => { timedOut = true; child.kill(); }, 15000);
    child.stdout.on('data', (chunk: Buffer) => { bytes += chunk.length; if (bytes <= 2_000_000) output.push(chunk); else child.kill(); });
    child.stderr.on('data', (chunk: Buffer) => { if (Buffer.concat(errors).length < 64_000) errors.push(chunk); });
    child.on('error', error => { clearTimeout(timer); reject(error); });
    child.on('close', code => {
      clearTimeout(timer);
      if (timedOut || code !== 0 || bytes > 2_000_000) { reject(new Error(timedOut ? 'Worker identity helper timed out.' : Buffer.concat(errors).toString('utf8').trim() || 'Worker identity helper failed.')); return; }
      try { resolve(JSON.parse(Buffer.concat(output).toString('utf8').replace(/^\uFEFF/, ''))); }
      catch { reject(new Error('Worker identity helper returned invalid JSON.')); }
    });
    child.stdin.on('error', () => {});
    child.stdin.end(input, 'utf8');
  });
}

export function startJevWorker(options: WorkerOptions): ManagedWorker {
  const createdAfter = new Date().toISOString();
  const child = spawn(options.executable, [options.script, 'decide', '--input', '-', '--purpose', options.purpose], {cwd: options.root, windowsHide: true, shell: false, stdio: ['pipe', 'pipe', 'pipe']});
  const output: Buffer[] = [], errors: Buffer[] = [];
  let outputBytes = 0, errorBytes = 0, code: number | null = null, closed = false, spawnError: string | undefined;
  let stopReason: StopReason | undefined, signalStop!: () => void;
  const interrupted = new Promise<void>(resolve => { signalStop = resolve; });
  const exited = new Promise<void>(resolve => {
    child.on('error', error => { spawnError = error.message; });
    child.on('close', value => { code = value; closed = true; resolve(); });
  });
  const requestStop = (reason: StopReason) => { if (!stopReason) { stopReason = reason; signalStop(); } };
  child.stdout.on('data', (chunk: Buffer) => {
    outputBytes += chunk.length;
    if (outputBytes <= (options.maxOutputBytes ?? 4_000_000)) output.push(chunk);
    else requestStop('output_limit');
  });
  child.stderr.on('data', (chunk: Buffer) => { errorBytes += chunk.length; if (errorBytes < 1_000_000) errors.push(chunk); else requestStop('output_limit'); });
  child.stdin.on('error', () => {});
  const result = (async (): Promise<WorkerResult> => {
    if (!child.pid) { await exited; return {reason: 'spawn_error', code, stdout: '', stderr: '', reaped: true, error: spawnError}; }
    const args = ['-WorkerPid', String(child.pid), '-Script', options.script, '-Executable', options.executable, '-CreatedAfter', createdAfter];
    let record: unknown;
    try { record = await helper(['-Action', 'capture', ...args]); }
    catch (error) {
      // No unverified kill. EOF lets the fixed tool reject empty input and exit.
      child.stdin.end();
      await waitForExit(exited, 3000);
      return {reason: 'cleanup_error', code, stdout: '', stderr: '', reaped: false, error: error instanceof Error ? error.message : 'Ownership capture failed.'};
    }
    const timer = setTimeout(() => requestStop('timeout'), options.timeoutMs ?? 65000);
    try {
      if (!stopReason) child.stdin.end(options.input, 'utf8');
      await Promise.race([exited, interrupted]);
      const cleanup = await helper(['-Action', 'stop', ...args], JSON.stringify(record));
      if (!cleanup || typeof cleanup !== 'object' || !('status' in cleanup) || cleanup.status !== 'reaped' || !('remaining_owned_processes' in cleanup) || cleanup.remaining_owned_processes !== 0) throw new Error('Worker exit was not verified.');
      await waitForExit(exited, 3000);
      if (!closed) throw new Error('Worker handle did not close after verified cleanup.');
      return {reason: spawnError ? 'spawn_error' : stopReason ?? 'complete', code, stdout: Buffer.concat(output).toString('utf8'), stderr: Buffer.concat(errors).toString('utf8'), reaped: true, cleanup, error: spawnError};
    } catch (error) {
      return {reason: 'cleanup_error', code, stdout: Buffer.concat(output).toString('utf8'), stderr: Buffer.concat(errors).toString('utf8'), reaped: false, error: error instanceof Error ? error.message : 'Worker cleanup failed.'};
    } finally { clearTimeout(timer); }
  })();
  return {result, stop: (reason = 'shutdown') => { requestStop(reason); return result; }};
}
