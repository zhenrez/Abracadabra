/** Fixed-script request workers, isolated from the long-lived inference service. */
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
const HELPER = fileURLToPath(new URL('../scripts/stop-jev-worker.ps1', import.meta.url));
async function waitForExit(exited, milliseconds) {
    let timer;
    try {
        await Promise.race([exited, new Promise(resolve => { timer = setTimeout(resolve, milliseconds); })]);
    }
    finally {
        if (timer)
            clearTimeout(timer);
    }
}
function helper(args, input = '') {
    return new Promise((resolve, reject) => {
        const child = spawn('powershell.exe', ['-NoProfile', '-NonInteractive', '-File', HELPER, ...args], { windowsHide: true, shell: false, stdio: ['pipe', 'pipe', 'pipe'] });
        const output = [], errors = [];
        let bytes = 0, timedOut = false;
        // Cleanup performs several verified Windows identity reads after execution.
        const helperTimeout = args[1] === 'stop' ? 30000 : 15000;
        const timer = setTimeout(() => { timedOut = true; child.kill(); }, helperTimeout);
        child.stdout.on('data', (chunk) => { bytes += chunk.length; if (bytes <= 2_000_000)
            output.push(chunk);
        else
            child.kill(); });
        child.stderr.on('data', (chunk) => { if (Buffer.concat(errors).length < 64_000)
            errors.push(chunk); });
        child.on('error', error => { clearTimeout(timer); reject(error); });
        child.on('close', code => {
            clearTimeout(timer);
            if (timedOut || code !== 0 || bytes > 2_000_000) {
                reject(new Error(timedOut ? 'Worker identity helper timed out.' : Buffer.concat(errors).toString('utf8').trim() || 'Worker identity helper failed.'));
                return;
            }
            try {
                resolve(JSON.parse(Buffer.concat(output).toString('utf8').replace(/^\uFEFF/, '')));
            }
            catch {
                reject(new Error('Worker identity helper returned invalid JSON.'));
            }
        });
        child.stdin.on('error', () => { });
        child.stdin.end(input, 'utf8');
    });
}
export function startJevWorker(options) {
    const createdAfter = new Date().toISOString();
    const child = spawn(options.executable, [options.script, 'decide', '--input', '-', '--purpose', options.purpose], { cwd: options.root, windowsHide: true, shell: false, stdio: ['pipe', 'pipe', 'pipe'] });
    const output = [], errors = [];
    let outputBytes = 0, errorBytes = 0, code = null, closed = false, spawnError;
    let stopReason, signalStop;
    const interrupted = new Promise(resolve => { signalStop = resolve; });
    const exited = new Promise(resolve => {
        child.on('error', error => { spawnError = error.message; });
        child.on('close', value => { code = value; closed = true; resolve(); });
    });
    const requestStop = (reason) => { if (!stopReason) {
        stopReason = reason;
        signalStop();
    } };
    child.stdout.on('data', (chunk) => {
        outputBytes += chunk.length;
        if (outputBytes <= (options.maxOutputBytes ?? 4_000_000))
            output.push(chunk);
        else
            requestStop('output_limit');
    });
    child.stderr.on('data', (chunk) => { errorBytes += chunk.length; if (errorBytes < 1_000_000)
        errors.push(chunk);
    else
        requestStop('output_limit'); });
    child.stdin.on('error', () => { });
    const result = (async () => {
        if (!child.pid) {
            await exited;
            return { reason: 'spawn_error', code, stdout: '', stderr: '', reaped: true, error: spawnError };
        }
        const args = ['-WorkerPid', String(child.pid), '-Script', options.script, '-Executable', options.executable, '-CreatedAfter', createdAfter];
        let record;
        try {
            record = await helper(['-Action', 'capture', ...args]);
        }
        catch (error) {
            // No unverified kill. EOF lets the fixed tool reject empty input and exit.
            child.stdin.end();
            await waitForExit(exited, 3000);
            return { reason: 'cleanup_error', code, stdout: '', stderr: '', reaped: false, error: error instanceof Error ? error.message : 'Ownership capture failed.' };
        }
        const timer = setTimeout(() => requestStop('timeout'), options.timeoutMs ?? 65000);
        try {
            if (!stopReason)
                child.stdin.end(options.input, 'utf8');
            await Promise.race([exited, interrupted]);
            // The request deadline ends with the worker, before verified cleanup.
            clearTimeout(timer);
            const completionReason = stopReason;
            const cleanup = await helper(['-Action', 'stop', ...args], JSON.stringify(record));
            if (!cleanup || typeof cleanup !== 'object' || !('status' in cleanup) || cleanup.status !== 'reaped' || !('remaining_owned_processes' in cleanup) || cleanup.remaining_owned_processes !== 0)
                throw new Error('Worker exit was not verified.');
            await waitForExit(exited, 3000);
            if (!closed)
                throw new Error('Worker handle did not close after verified cleanup.');
            return { reason: spawnError ? 'spawn_error' : completionReason ?? 'complete', code, stdout: Buffer.concat(output).toString('utf8'), stderr: Buffer.concat(errors).toString('utf8'), reaped: true, cleanup, error: spawnError };
        }
        catch (error) {
            return { reason: 'cleanup_error', code, stdout: Buffer.concat(output).toString('utf8'), stderr: Buffer.concat(errors).toString('utf8'), reaped: false, error: error instanceof Error ? error.message : 'Worker cleanup failed.' };
        }
        finally {
            clearTimeout(timer);
        }
    })();
    return { result, stop: (reason = 'shutdown') => { requestStop(reason); return result; } };
}
