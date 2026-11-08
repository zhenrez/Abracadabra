"""Create instrumented copies of the operational worker; originals untouched."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
base=(ROOT/'dist/worker.js').read_text(encoding='utf-8')
helper=str(ROOT/'scripts/stop-jev-worker.ps1')
base=base.replace("const HELPER = fileURLToPath(new URL('../scripts/stop-jev-worker.ps1', import.meta.url));",'const HELPER = '+json.dumps(helper)+';')
base=base.replace("function helper(args, input = '') {", "function helper(args, input = '') {\n    const began=Date.now(); globalThis.__workerTrace?.push({event:'helper_begin',action:args[1],at:began});")
base=base.replace("child.on('close', code => {", "child.on('close', code => {\n            globalThis.__workerTrace?.push({event:'helper_close',action:args[1],code,at:Date.now(),elapsed:Date.now()-began});")
base=base.replace("const requestStop = (reason) => {", "const requestStop = (reason) => { globalThis.__workerTrace?.push({event:'request_stop',reason,at:Date.now()});")
base=base.replace("child.on('close', value => { code = value;", "child.on('close', value => { globalThis.__workerTrace?.push({event:'child_close',code:value,at:Date.now()}); code = value;")
base=base.replace("record = await helper(['-Action', 'capture', ...args]);", "record = await helper(['-Action', 'capture', ...args]); globalThis.__ownedRecords?.push({record,args});")
assert 'globalThis.__ownedRecords' in base
(OUT/'worker-observed.mjs').write_text(base,encoding='utf-8')
fixed=base.replace('await Promise.race([exited, interrupted]);','await Promise.race([exited, interrupted]);\n            clearTimeout(timer);\n            const executionReason = stopReason;')
fixed=fixed.replace("reason: spawnError ? 'spawn_error' : stopReason ?? 'complete'", "reason: spawnError ? 'spawn_error' : executionReason ?? 'complete'")
(OUT/'worker-proposed.mjs').write_text(fixed,encoding='utf-8')
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'src/worker.ts',ROOT/'dist/worker.js',ROOT/'scripts/stop-jev-worker.ps1',ROOT/'scripts/process-lifecycle.ps1',ROOT/'tests/worker-lifecycle.test.mjs']}
(OUT/'before-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print('Prepared instrumented original and timer-fix copies; original files unchanged')
