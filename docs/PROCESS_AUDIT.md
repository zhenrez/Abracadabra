# Process ownership audit

Observed on October 30, 2026, America/Phoenix. This is an independent, read-only process and launcher audit prompted by the user's report of excessive command prompts, Node and Python processes. SuperJev recovery and Agent Skills debugging-and-error-recovery were read and applied. No background worker, browser or service was started by this audit. No process was stopped and no installed plugin or global configuration was changed.

The current evidence does **not** reproduce the earlier reported 90+ command prompts. The saved snapshot at `docs/evidence/process-audit-snapshot.json` contains 9 `cmd.exe`, 20 `node.exe`, 9 `python.exe`, 4 `pwsh.exe`, 42 `conhost.exe` and 2 `codex.exe` processes. Counts include transient commands/hooks and change while Codex works. `conhost.exe` is distinct from `cmd.exe`; adding the two counts would misstate the number of command prompts.

The main observed multiplication is separate Codex plugin contexts. Three matching AgentJev adapters, three Data launch trees and three Mindbridge launch trees belonged to the same live Codex host, PID 25144. Their creation times were 18:40:02, 18:40:51 and 18:42:02. Desktop log entries identify the first two cohorts with separate resumed chats and the third with a plugin extension host. Identical command lines therefore do not prove that these are abandoned workers.

| Cohort | Observed AgentJev adapter PID | Ownership evidence |
| --- | --- | --- |
| 18:40:02 | 23424 | Parent 25144; desktop log line 1440 resumes chat `01a18ccb-4240-70d1-a7d5-983439842d49` |
| 18:40:51 | 4904 | Parent 25144; line 1861 resumes SUNNY chat `01a18f6a-af21-78c1-83e2-02117c13aa7a` |
| 18:42:02 | 21732 | Parent 25144; line 2143 records `mcp_extension_host_thread_starting` |

The log is `C:/Users/Brend/AppData/Local/Codex/Logs/2026/10/31/codex-desktop-8165051d-6653-4599-8f73-cecdd76f1940-25448-t0-i1-013535-0.log`. The saved evidence extracts startup fields and process identities without copying full command lines, environment variables, authentication headers or private chat content. A second live Codex host, PID 14412, owned four additional relative-path MCP Node servers. Their exact plugin identities were not recoverable from command lines alone in this audit.

The inspected launchers explain part of the per-context overhead:

- AgentJev Decisions declares a Python stdio adapter in its `.mcp.json`. This adapter is separate from the local inference service. Three adapters do not mean three loaded inference models.
- Mindbridge declares `npx -y @pinkpixel/mindbridge@1.2.0`. In each observed tree, Windows retained a `cmd` launcher, the Node/npm launcher, another `cmd`, and the actual Node server. Associated console hosts add further processes.
- Data uses a Windows batch launcher and one Node server. Its inspected batch file launches Node and exits when Node exits; it contains no restart loop.
- SuperJev itself declares skills and two reminder hooks, each with a five-second timeout. Its inspected reminder script reads bounded stdin, prints JSON and exits. It declares no MCP server or persistent monitor. This inspection establishes its installed reminder design, not a fresh live model-inference result.

The two observed SUNNY-path Python processes, PIDs 22996 and 7468, form one parent/child pair. The parent executable was the workspace virtual-environment Python launcher and the child executable was the base Python interpreter. That identity alone is insufficient to classify either as an abandoned job. An absent parent shell is expected for an intentionally detached service. No Edge browser was present in the initial snapshot. The historical GPU PID in a JSON record is not evidence that that PID still belongs to SUNNY.

The desktop log also contains repeated tool-discovery failures, including missing authentication, an HTTP 403, a missing executable for a different plugin, and an unsupported `mcpServerStatus/list` request against a durable host. Those failures should be diagnosed separately; they do not establish that the three successfully initialized local adapter cohorts leaked or that SuperJev was responsible.

For the main implementation, the concrete lifecycle gaps in the inspected workspace launchers are: `start-sunny.ps1` does not persist the app process identity, `start-jev.ps1` persists a PID without the process creation identity, and neither launcher provides a scoped stop operation or failed-start cleanup. The browser check has a `finally` block but its error path calls `browser.kill()` without verifying browser-tree exit. These are source observations, not claims that those paths caused the user's earlier counts. Main-agent lifecycle edits and their tests must be reviewed separately.

Safe remediation should track only processes started for this workspace, retain PID plus creation identity and executable/argument evidence, reuse a healthy existing service, and stop owned test/browser/failed-start descendants in `finally`. A stop operation should refuse a stale PID that now belongs to another process. Live Codex connectors and other chats should be managed through the owning host rather than killed by executable name. No operating-system-wide `node`, `python`, `cmd` or console-host termination is supported by this evidence.

Verification for this audit: two independent CIM snapshots, bounded current desktop-log inspection, and direct reads of the installed launchers/hooks and workspace startup/browser code. Earlier maximum counts, host shutdown behavior, plugin cancellation cleanup and the exact purpose of all relative-path MCP servers remain unverified. The audit's own short shell commands completed; it left no service or browser running.

## Independent review of lifecycle changes

The main agent subsequently added scoped browser cleanup and delegated managed-service lifecycle changes. This section records review findings against the code as read at approximately 18:51 Phoenix; it does not claim the final edits are unchanged. The independent reviewer started or stopped no service or browser. The existing real browser cleanup report was read, rather than rerun: it reports invalid-profile refusal, live owned-tree cleanup and repeated cleanup passing.

Three concrete findings were sent to the implementers:

1. In `stop-test-browser.ps1`, `Sort-Object -Property CreationDate -Descending -Unique` deduplicated different processes with the same creation timestamp. A bounded, process-free PowerShell reproduction supplied two distinct PIDs with the same timestamp and received only one result. Deduplication must use process identity. The helper also counted only profile-bearing processes after cleanup. If the root had already exited, a renderer without the profile argument was not discoverable from the supplied root PID, so the helper could return zero without accounting for that child. The live-root test does not cover this path.
2. In the initial `Get-SunnyOwnedTree` implementation, a child’s parent and creation time were checked from one CIM snapshot, but a fresh identity for its PID was admitted without matching it back to that snapshot. A PID reused between those reads could enroll a replacement process outside the owned tree. The fresh identity needs the snapshot's creation identity and validated parent linkage before admission. This was a source-level race finding; no unrelated process was targeted to reproduce it.
3. In the initial `src/server.ts` subprocess handling, timeout/output-limit paths killed the spawned Python handle, released the concurrency slot immediately and did not verify descendant exit. This host's observed virtual-environment Python launcher/interpreter pair makes single-handle termination an incomplete process-tree guarantee. The server had no registry for active children on shutdown; its close handler only closed the database. Browser disconnection is separate from cancellation of an already accepted decision and does not itself require a retry or an invented cancellation result.

These findings concern process ownership and truthful cleanup results. They do not authorize killing Codex-owned adapters or other chats. Final resolution needs a fresh source review and focused evidence after each implementation change.
