/** Fixed-script request workers, isolated from the long-lived inference service. */
import {EventEmitter} from 'node:events';

function spawn() {
 const child=new EventEmitter(); child.pid=42;
 child.stdout=new EventEmitter(); child.stderr=new EventEmitter(); child.stdin=new EventEmitter();
 child.stdin.end=()=>setTimeout(()=>child.emit('close',1),2);
 return child;
}

import { fileURLToPath } from 'node:url';
const HELPER = "C:\\Users\\Brend\\Documents\\ChatGPT\\SUN\\scripts\\stop-jev-worker.ps1";
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

async function helper(args,input='') {
 if(args[1]==='capture')return {kind:'SYNTHETIC_TRANSPORT_ONLY'};
 await new Promise(resolve=>setTimeout(resolve,80));
 return {status:'reaped',remaining_owned_processes:0,simulation:true};
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
        child.on('close', value => { globalThis.__workerTrace?.push({event:'child_close',code:value,at:Date.now()}); code = value; closed = true; resolve(); });
    });
    const requestStop = (reason) => { globalThis.__workerTrace?.push({event:'request_stop',reason,at:Date.now()}); if (!stopReason) {
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
            record = await helper(['-Action', 'capture', ...args]); globalThis.__ownedRecords?.push({record,args});
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
            clearTimeout(timer);
            const executionReason = stopReason;
            const cleanup = await helper(['-Action', 'stop', ...args], JSON.stringify(record));
            if (!cleanup || typeof cleanup !== 'object' || !('status' in cleanup) || cleanup.status !== 'reaped' || !('remaining_owned_processes' in cleanup) || cleanup.remaining_owned_processes !== 0)
                throw new Error('Worker exit was not verified.');
            await waitForExit(exited, 3000);
            if (!closed)
                throw new Error('Worker handle did not close after verified cleanup.');
            return { reason: spawnError ? 'spawn_error' : executionReason ?? 'complete', code, stdout: Buffer.concat(output).toString('utf8'), stderr: Buffer.concat(errors).toString('utf8'), reaped: true, cleanup, error: spawnError };
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
