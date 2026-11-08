"""Run the existing project acceptance with a structured, readable receipt."""
from datetime import datetime, timezone
from pathlib import Path
import json
import hashlib
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
serial = "--serial" in sys.argv[1:]
diagnostic = "--diagnostic" in sys.argv[1:]
identity_diagnostic = "--identity-diagnostic" in sys.argv[1:]
after_repair = "--after-repair" in sys.argv[1:]
final_run = "--final" in sys.argv[1:]
command = (["node", "--test", "--test-concurrency=1", *[str(path.relative_to(PROJECT)) for path in sorted((PROJECT / "tests").glob("*.test.mjs"))]]
           if serial else ["cmd.exe", "/d", "/c", "npm test"])
if diagnostic:
    command = ["node", "--test", "--test-name-pattern=output overflow", str(HERE / "worker-lifecycle-diagnostic.test.mjs")]
if identity_diagnostic:
    command = ["node", "--test", "--test-name-pattern=HTTP server close", str(HERE / "worker-identity-diagnostic.test.mjs")]
def snapshot():
    # npm test executes *.test.mjs and the imported identity assertion, not the
    # separately maintained browser programs. Retain those other signals elsewhere.
    paths=sorted(set((PROJECT/'src').glob('*.ts'))|set((PROJECT/'tests').glob('*.test.mjs'))|
                 {PROJECT/'tests/worker-identity.mjs',PROJECT/'scripts/stop-jev-worker.ps1',
                  PROJECT/'scripts/process-lifecycle.ps1',PROJECT/'package.json',PROJECT/'tsconfig.json'})
    return {str(path.relative_to(PROJECT)).replace('\\','/'):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
before=snapshot()
result = subprocess.run(command, cwd=PROJECT, capture_output=True, text=True,
                        encoding="utf-8", errors="backslashreplace", timeout=240)
output = result.stdout + result.stderr
counts = {name: int(value) for name, value in re.findall(r"^# (tests|pass|fail|cancelled|skipped) (\d+)$", output, re.MULTILINE)}
receipt = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "command": command,
           "exit_code": result.returncode, "observed_counts": counts, "output": output,
           "checked_inputs":before,"inputs_unchanged":before==snapshot(),
           "source_binding_scope":"Actual TypeScript sources, npm test entrypoints/imported assertion, ownership helpers and build configuration; separate browser programs are retained outside this run",
           "scope": "Single HTTP-close diagnostic; compare exact original process birth identities if a PID is present" if identity_diagnostic else "Single output-overflow diagnostic copy; original assertions and ownership checks retained" if diagnostic else "Full original Node acceptance suite in serial execution; existing build already verified" if serial else "Existing TypeScript build and full original Node acceptance suite"}
target = HERE / ("identity-diagnostic-checks.json" if identity_diagnostic else "cleanup-diagnostic-checks.json" if diagnostic else "project-serial-checks.json" if serial else "project-final-checks.json" if final_run else "project-after-repair-checks.json" if after_repair else "project-checks.json")
target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if json.loads(target.read_bytes()) != receipt:
    raise RuntimeError("Project receipt failed readback")
print(json.dumps({key: value for key, value in receipt.items() if key != "output"}, indent=2))
sys.exit(result.returncode if result.returncode else (0 if counts.get("tests", 0) > 0 and counts.get("fail") == 0 and receipt['inputs_unchanged'] else 1))
