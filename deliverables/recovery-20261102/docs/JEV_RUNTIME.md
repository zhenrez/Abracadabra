# Working local Jev runtime

The local AgentJev inference service is running at `http://127.0.0.1:8149`, which remains the default after a recorded Jev device-route choice. A second verified instance runs on the GPU at `http://127.0.0.1:8150`. It was bootstrapped following the user's explicit instruction to clone and build an alternative when the installed adapter could not connect. This supplies the missing service behind AgentJev Decisions and a native HTTP route for SUNNY.

The initial adapter failure was reproducible: connection refused on port 8149. The underlying cause was a missing running inference service, rather than a missing MCP function. The adapter package contains no model weights and does not launch the upstream server. After the workspace runtime was downloaded, verified and launched, `/health`, `/api/info` and actual `/api/evaluate` requests succeeded. No cloud inference account or API key was used.

## Exact identity

- Source repository: [malevrigns/agent-jev](https://github.com/malevrigns/agent-jev), commit `fbe1bc97c76873d08f0820adf0dead55e95d5fc6`.
- Public release: [aimeigaoshou/agent-jev](https://huggingface.co/aimeigaoshou/agent-jev), revision `7d433994fbde17a3f0993c2f2b02fe8ca1370db1`, variant `v1`.
- Checkpoint: `agentjev-v1`, SHA-256 `8166e46dc6019ae13f0d8fc97d603cdbcc2d20eb1882c7350c8deb9fc6bae215`.
- All seven release files match their pinned upstream sizes and SHA-256 hashes. The safetensors header contains 343 BF16 tensors; model file size is 1,196,881,242 bytes.
- Installed hardware is an NVIDIA RTX 3060 with 12 GB VRAM. The original service on 8149 loaded the already installed global `2.9.1+cpu` build and runs on CPU with four compute threads. That global CPU installation remains unchanged.
- Workspace environment: `runtime/.venv`, Python 3.13, inheriting existing system packages through `--system-site-packages`. Following a later recorded Jev choice, `torch2.9.1+cu128` was installed into this environment alone. CUDA12.8 and BF16 support were actually checked on the RTX3060, and the GPU service on8150 uses this local build. This is environment separation, not a fully self-contained dependency bundle.
- Exact dependencies and all file hashes are recorded in `docs/evidence/jev-runtime-manifest.json`. Transformers is 4.57.3, safetensors 0.7.0 and huggingface_hub 0.34.4. `pip check` passed.

## Start and inspect

Run `scripts/start-jev.ps1` from PowerShell. It starts the existing pinned service in a hidden window, binds upstream to loopback, writes process/log paths under `docs/evidence`, and avoids starting another instance when the pinned checkpoint is already healthy. It defaults to CPU. The service is a normal background process; no recurring automation, OS startup service or global plugin configuration was installed.

`scripts/start-jev.ps1 -Device cuda:0 -Port 8150` starts or inspects the verified GPU instance. A failed GPU launch is not silently replaced by a different model. After installing the local CUDA wheel, a fresh CPU launch through this script also uses that CUDA-capable package with `--device cpu`; the existing 8149 process retains its original CPU package already loaded in memory. Changing model/runtime policy requires a recorded Jev decision under the user's latest directive.

Startup uses the inspected upstream module `jev_service.server`. Loading uses the verified `.safetensors` release and local tokenizer/configuration. Offline environment flags prevent subsequent model downloads. The upstream application binds `127.0.0.1` only and performs a warmup before reporting ready. Logs are `docs/evidence/jev-runtime-service.stdout.log` and `.stderr.log`; the launch record is `jev-runtime-process.json`.

The GPU instance uses corresponding `jev-runtime-service-8150` log names and `jev-runtime-process-8150.json`, so its launch does not overwrite the CPU instance's logs.

## Actual observations

| Check | Observed result |
|---|---|
| `/health` and `/api/info` | Ready; expected checkpoint hash and `agentjev.decision.v1` |
| First real request | Two questions, five candidate paths, 861 path tokens; 0 generated tokens and 0 truncated inputs; model wall time 2,043.23 ms |
| Runtime path choice | `use_live_cpu` won with model mass 0.5059213; keep the functioning CPU route and measure workload before replacing it |
| Completion question | `false`; ready runtime alone does not establish SUNNY research completion |
| Verification route choice | `run_upstream` won with model mass 0.5597412 |
| Inspected upstream HTTP suite | Exit 0; its controlled smoke checks passed |
| Counterfactual smoke check | Failing-test state true mass 0.0370778; passing-test state true mass 0.9203956 |
| Candidate permutation difference | Maximum absolute difference 0.0000001192093 |
| Additional-question isolation difference | Maximum absolute difference 0.0000000260770 |
| 255 choice candidates | Accepted, full distribution returned |
| Excess path tokens | HTTP 400 with explicit rejection; no silent truncation |
| Re-running startup script | Returned existing pinned healthy service; no duplicate process launched |

The full requests, model distributions, usage and elapsed times are preserved, rather than summarized away: `jev-runtime-first-inference.json`, `jev-runtime-verification-choice.json`, and `jev-runtime-http-verification.json`. The upstream smoke runner writes its generated report at `runtime/agent-jev/jev_service/verification.json`, so that generated report is the sole observed modified tracked file in the upstream checkout. Runtime/model source code and trained weights were not modified.

## Subsequent GPU choice and measured comparison

The initial runtime request selected keeping the live CPU instance. A later shared request, `state/jev-receipts/000001-65ef5aadf59c.json`, selected preparing GPU inference with model mass 0.2733009 versus CPU 0.2703864, a margin of only 0.0029145. These differently framed requests are retained as distinct observations; they do not establish consensus or a strong preference.

Jev then selected `torch2.9.1+cu128` over the documented CUDA12.6 alternative in shared receipt `000005-fae9b69bcea7.json` (model mass 0.7763191). The exact Python3.13 Windows wheel came from the official PyTorch download host and its SHA256 fragment `ad9183864acdd99fc5143d7ca9d3d2e7ddfc9a9600ff43217825d4e5e9855ccc` was enforced by pip. Installation used `--ignore-installed --no-deps` in the workspace environment; global packages were not uninstalled or changed. The build availability was checked against the [official PyTorch previous-version instructions](https://pytorch.org/get-started/previous-versions/).

For comparison, Jev selected a single fixed request rather than a mixed suite in receipt `000008-3a5d06507e59.json` (model mass 0.5542798). The request was frozen before observing GPU output; `runtime/compare_devices.py` verifies its bytes before execution. The exact same two questions were then evaluated once on CPU8149 and GPU8150. Both selected values matched. Maximum probability differences were 0.0019037724 for the choice and 0.0016974807 for the boolean; outputs were therefore not bit-identical. CPU elapsed divided by GPU elapsed was 3.2693 for this one observation. The CPU server also served other SUNNY requests, so no exclusive timing isolation is claimed.

The resulting route decision in receipt `000014-0c74b9e04860.json` selected keeping CPU8149 as the default, while retaining GPU8150 for further work. Its narrow distribution is preserved in the receipt and `jev-runtime-final-state.json`; there is no hidden threshold or requery to obtain a desired route. The GPU service remains available, but the default was not switched.

Full environment, freeze, health and comparison evidence is in `jev-runtime-cuda-environment.json`, `jev-runtime-comparison-freeze.json`, `jev-runtime-gpu-health.json`, `jev-runtime-device-comparison.json` and `jev-runtime-final-state.json`. This single-workload comparison is not evidence of general speed, quality or hardware equivalence. The broader upstream HTTP suite was run on the CPU service; it was not rerun on GPU, and the GPU's current evidence boundary is health plus the frozen two-question inference.

## Boundaries that remain explicit

AgentJev returns boolean, bounded-choice and ordered-score distributions. It does not generate source code, independently read SUNNY's database, or invent its own complete candidate set. The host must supply exact source-linked states and explicit questions/options; those supplied boundaries remain part of the decision's provenance. A choice is conditional on the supplied alternatives.

The service limit is 2,048 tokens per candidate path. Large archives require source-preserving decomposition into bounded requests, with full originals retained outside the model input. Over-limit requests fail rather than being silently cropped.

These observations establish actual runtime availability and controlled transport/model behavior. They do not establish SUNNY domain calibration, exhaustive account recovery, historical truth, scientific correspondence, a lawful orientation, or the completeness of SUNNY itself. The supplied calibration temperatures were fitted upstream on that model's benchmark, not on SUN research.

Bootstrap before the first live call was host-executed under the user's explicit fallback instruction. It cannot retroactively become Jev-selected. Existing SUNNY implementation written before the strict directive still requires Jev review. Subsequent substantive choices should attach their real Jev request/response receipt, source context and executed outcome; unavailable inference must remain unavailable.

Only public code and model files were downloaded. No private archive or account history was uploaded during this runtime bootstrap. The first two runtime decision requests were sent solely to the local service.
