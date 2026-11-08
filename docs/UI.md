# SUNNY source and geometry workspace

The local interface lives in `public/index.html`, `public/app.js`, and `public/style.css`, served by `src/server.ts`. It uses the local HTTP API only. It loads no remote scripts, fonts, trackers, or research data services.

## Observable behavior

- Overview shows collection counts returned by `/api/summary` and the recoverable task state from `/api/state`. Missing counts stay unreported. A source-service failure produces an explicit recovery message.
- Source explorer searches `/api/search?q=...&limit=40`, preserves searches in the URL fragment, distinguishes the original user and assistant, and opens message details and conversation context. Search results and source text enter the document through `textContent`; source markup is never executed.
- Conversation context preserves native identifiers and displays current-path / alternate-branch labels when the API reports them. The interface does not infer branch authority from displayed order.
- Decisions show the returned status and original source references. Missing decision data does not become an empty-account claim.
- Archive inventory shows original source paths, sizes, hashes, and reported extraction status. A checksum is presented as byte identity, not semantic verification.
- Capabilities show recorded use, runtime status, evidence, and limitations. No plugin use is inferred when its record is unavailable.
- The Jev workbench submits exactly the visible state, question, and explicit candidate meanings to the actual local model through the fixed `scripts/jev_tool.py` stdin bridge. It displays the full conditional distribution, model/checkpoint hash, and receipt. A model outage has no fabricated fallback. Actual assessment history is distinct from a canonical musical law or complete account investigation.
- The geometry workspace exposes wheel, torus, and finite depth-3 Sierpinski tetrahedron projections. The wheel preview has two turns per generation interval. Its radii and six display levels are illustrative parameters, with no named research entities or canonical placements. The torus is parametric; no general waveform equivalence or 4D causal law is inferred. The tetrahedron preview is finite and makes no infinitum claim.

## Skills applied

Agent Skills `frontend-ui-engineering` supplied keyboard and focus behavior, semantic labels, responsive layouts, meaningful error and empty states, and the restrained visual system. `browser-testing-with-devtools` supplied the runtime verification checklist, applied through isolated native Microsoft Edge/CDP because Chrome DevTools MCP was unavailable. `code-review-and-quality` supplied correctness, injection, boundary, dependency, and performance review criteria. SuperJev supplied bounded actual model gates and evidence-preserving verification; root's HUMMBL/Proofline/AgentProof/Supermemory work supplies its separately recorded planning and guardrail evidence.

The required `12ui-design` skill was read after the workspace guardrail update. Its existing-interface workflow was inspected without replacing the source-linked behavior. The skill-directed installer failed on Windows with `spawn EINVAL`; invoking the downloaded `@12ui/design`0.2.130 CLI directly recovered its real command/help/auth and improve dry-run behavior. The actual dry run is `docs/evidence/12ui-review-dryrun.txt`: no design was captured, generated, dispatched, approved or purchased. Hosted design work requires 12ui sign-in; no approved target image or completed 12ui visual-alignment pass is claimed. The displayed screenshots are observed SUNNY runtime output, not 12ui-generated design targets.

## Live Jev implementation decisions

- `docs/evidence/jev-source-driver-choice.json`: selected exact `better-sqlite3`13.0.3 after the built-in Node SQLite FTS5 failure.
- `docs/evidence/jev-source-types-choice.json`: selected exact development declarations `@types/better-sqlite3`9.6.0.
- `state/jev-receipts/000006-9260a70542fa.json`: selected a visible structured request form and at most two simultaneous browser assessment processes, with no hidden queue.
- `state/jev-receipts/000010-e228ad790f93.json`: selected direct Host-validation unit testing after observed Node fetch refused to transmit a custom Host header. Source-service Host validation remains intact. A network-level foreign-Host check is not claimed by that unit test.
- `docs/evidence/jev-browser-http-smoke.json` and `docs/evidence/jev-browser-form-smoke.json`: actual HTTP and visible browser-form inferences, with stored exact requests and checkpoint identity. Model masses are conditional on their supplied state and candidates.

## API contract

The client accepts response lists at `results` (or explicitly supported endpoint alternatives) and renders unknown fields without changing their authority. Endpoints:

| Endpoint | Expected response |
|---|---|
| `/api/summary` | `{counts: {conversations, messages, artifacts}, scope, status}` |
| `/api/state` | `{goal, constraints, open_questions, next_actions}`; a checkpoint `payload` envelope is accepted |
| `/api/search?q=...&limit=40` | `{results: [{id, conversation_id, title, role, text, source_path, locator, create_time, is_current_path}], total?}` |
| `/api/message?id=...` | A message or `{message: ...}` |
| `/api/conversation?id=...` | `{conversation: {id, title, current_node?}, messages: [...]}` |
| `/api/artifacts` | `{results: [{path, bytes, sha256, status}], total?, truncated?}` |
| `/api/decisions` | `{results: [{title?, statement?, text?, role?, status?, locator?, source_path?, message_id?, conversation_id?}]}` |
| `/api/capabilities` | `{plugins: [{name, status, contribution, limitation?, evidence?}]}` |
| `POST /api/jev/decide` | Native `{state, questions}` JSON, maximum48,000UTF-8bytes. Fixed local subprocess only; returns real assessment/receipt or explicit failure. Sources remain read-only. |
| `/api/jev/history` | Actual hash-chained assessment rows and parsed recorded payloads, at most100returned. |
| `/api/jev/receipt?sha256=...` | Exact recorded payload for a full receiptSHA-256; no arbitrary file path. |

## Verification record

Implementation checks and browser outcomes are recorded below as they run. A static syntax check is not a browser pass or an account-completeness check.

- `node --check public/app.js`: passed after initial implementation.
- Static HTML inspection: 44 unique IDs, all four form inputs have associated labels, six named panels, and 21 native buttons.
- Source insertion inspection: no `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, or `eval` sink; no remote asset URL in the HTML.
- Node22.14 built-in SQLite3.47.2 reports `ENABLE_FTS5=0`; creating the actual importer's FTS5 table failed with `no such module: fts5`. The Jev-selected installed driver reports SQLite3.53.4 / `ENABLE_FTS5=1`; the same original schema now executes. The original unavailable-builtin condition remains covered by the regression test when present.
- `npm run build` and `node --disable-warning=ExperimentalWarning --test tests/server.test.mjs`: passed2tests, including real FTS/schema/source/branch/locator checks, SQL-like input, refused source writes, traversal rejection, foreign-Origin and wrong-content-type rejection,48kbodylimit, malformed request, absent fixed Jev tool, and unchanged source-DB hash.
- `npm audit --omit=dev --json`: zero reported production vulnerabilities at the observed check.
- `node tests/ui-browser.mjs`: passed against actual imported sources and actual local Jev in isolated native Edge. Checks include59,894-message summary,92-matchSUNNYsearch, full10,796-character source text,18-message conversation context, all3finitegeometry modes, all6views without horizontal page overflow at320/768/1024/1440pixels, labelled native accessibility state textbox, and zero observed console errors/exceptions. No source content became executable markup.
- The visible browser form produced actual receipt `f04a95bb9be800d46a77deadb2c9cc0d4c9de8fb37d131d182bc9790ab46c9d7`; its exact browser request matched the stored payload and the actual receipt chain verified intact. Evidence: `docs/evidence/ui-browser-check.json` and `docs/evidence/jev-browser-form-smoke.json`.
- Desktop overview,390pxmobile overview, and1440pxJev workbench screenshots were visually inspected. No formal WCAG contrast audit, human screen-reader session, or comprehensive keyboard interaction audit was performed. Basic labelled native controls and dialog structure are observed, not a complete accessibility certification.
- A later native pipe check found Windows Python stdin default `cp1252`, which corrupts raw UTF-8 non-ASCII request text. Root was notified; Unicode exact-request regression must be rerun after the wrapper's selected fix. The above successful live inference checks used ASCII inputs and do not establish Unicode request fidelity.
