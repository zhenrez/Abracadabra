# Matched modern Tiberian audio control

The two publisher recordings are acquired, hashed, decoded and measured. The paired source is Alex Foreman's modern reconstructed Tiberian **dagesh forte–dagesh lene** reading of Genesis 1.1–13: [without melody](https://doi.org/10.11647/OBP.0163.06) and [with Sefardi melody](https://doi.org/10.11647/OBP.0163.07). The [publisher's resource list](https://www.openbookpublishers.com/books/10.11647/obp.0163) was freshly inspected and identifies both conditions. The exact request redirects, response headers and original MP3 bytes are retained.

This completes the acquisition/decode dependency in the earlier prospective operational packet. **No source-aligned Alef realization has yet been measured.** This modern performance comparison supplies neither an ancient waveform nor a universal frequency per glyph.

As of 2026-11-03 in America/Phoenix (measurement receipt: 2026-11-04T03:29:36Z). The method was frozen before either MP3 GET began; validation checks that ordering against the retained UTC timestamps.

| Measured field | OBP.0163.06, without melody | OBP.0163.07, Sefardi melody |
|---|---:|---:|
| Exact original bytes | 3,295,259 | 11,989,494 |
| Native decoded format | Stereo, 44,100 Hz, signed16 | Stereo, 44,100 Hz, signed16 |
| Native decoded frames | 7,632,240 | 16,517,376 |
| Decoded duration, seconds | 173.066667 | 374.543673 |
| Whole-record RMS, dBFS | -16.126797 | -22.180767 |
| Whole-record peak, fraction of digital full scale | 0.987183 | 0.982483 |
| Full-scale sample codes | 0 | 0 |
| Algorithmic opening activity mark, seconds | 0.615 | 1.345 |

RMS dBFS means `20 log10(rms(samples) / 32768)`; it is uncalibrated digital level. The activity mark uses ten-millisecond RMS windows every five milliseconds: nine consecutive windows above -40 dBFS cover fifty milliseconds. It is an energy mark, with no word-onset interpretation. Whole-file durations include file padding and pauses, so their ratio is not a measured tempo ratio. The files' different levels are not calibrated loudness or phonation differences.

The retained SHA256 hashes are:

```text
OBP.0163.06  de4732cf81c83a98329207f414eba384d7ea8bfdc778505ead37dcafb258a17c
OBP.0163.07  1d9667de1cf1bf242028c1d403994ce1f3899869ccd515de6c98ae4600731475
```

The existing decoder was recovered at `C:/Users/Brend/AppData/Local/Temp/sunny-miniaudio-analysis/miniaudio.py`: Python miniaudio 1.71, native library 0.11.25. Its module and extension hashes are recorded. No package was installed. Native stereo signed16 WAVs preserve the original decoded rate/channels; separate mono 16,000 Hz signed16 WAVs support analysis. Resampling and the lossy MP3 source remain explicit. The [official package documentation](https://pypi.org/project/miniaudio/) documents the decoder and conversion functions used.

The fixed opening 0–15 seconds of each file has a saved clip, RMS table, exploratory periodicity table, and waveform/spectrogram figure. The spectrogram uses a 25 ms Hann window, 5 ms hop, 1,024-point FFT and 0–5,000 Hz display. Periodicity uses mean-removed 60 ms frames, 10 ms hop and overlap-normalized autocorrelation, with energy and correlation gates defined in `method-frozen.json`. Every rejected frame is retained. These candidates admit octave/subharmonic errors; the two fifteen-second windows contain different unknown amounts of linguistic material. Their pooled frequencies cannot establish a token contrast or a melody effect.

The actual page-615 image was inspected alongside the selected transcription artifact. For the first displayed reading profile, the medial Alef of בראשית and final Alef of ברא have no corresponding [ʔ] marker; the initial Alef of אלהים has an explicit [ʔ]. These are documentary source roles. All six performance-specific token intervals remain `null` in `measurements.json`, and each token's glottal realization remains `indeterminate`. No listening, validated automatic transcript, or independent timing annotation occurred. A filename, energy gap or periodicity candidate cannot supply that missing alignment. Absence of exact digital silence cannot establish absence of a glottal target.

The source text, intended roles, earlier operational packet and retained Jev direction were exposed before this work. This is an exposed modern control, with no blind-prediction claim. The retained `jev-next-native-question-v2` receipt selects `tiberian_context` at 0.61 and records `jev-1.14.0`; provider/account attribution remains unresolved. There was no new manual Jev or other model request in this unit.

Installed SuperJev coordination and Riqor evidence-engineering instructions were applied to scope, acquisition and verification. HUMMBL work-triage and operating-brief were applied to the local handoff. The worker's actual Supermemory search returned tool-unavailable; it is retained as an unavailable capability, and is not described as a successful continuity retrieval. No Proofline, AgentProof, MightShape or listening runtime is claimed by this worker. Their separate root-level receipts must be assessed in their own scope.

The focused validator passed **81 checks**: original/derived hash bindings, successful DOI-to-publisher retrievals, Content-Length matches, native and resampled headers/counts, fresh re-decodes equal to every retained PCM sample, independent WAV RMS and activity marks, candidate accounting, direct dot-product checks of the FFT-derived correlation, and preservation of unknown token intervals. This proves local reproducibility within the recorded decoder, not phonetic or historical correctness.

Now: this bounded acquisition/decode/measurement result is ready for root review. Next: an authorized reviewer or suitable validated alignment procedure must annotate the three tokens against these exact recordings, retain onset/end uncertainty and exposure, and inspect token-local waveform/spectrogram/pulses before applying the conditional glottal rubric. Later: compare aligned controls and targets across conditions, preserving source prescription and performance as separate factors. Resolve: exact publisher HTML acquisition returned HTTP429; the fresh web-readable page and successful DOI redirects support identity, while no raw book-page HTML body is claimed.

Reproduce from `C:/Users/Brend/Documents/ChatGPT/SUN`:

```powershell
python state/research/reactivation/matched-audio/analyze.py
python state/research/reactivation/matched-audio/validate.py
```

`SUNNY_MATCHED_AUDIO_DECODER` can point to the recorded existing dependency folder. `acquire.py` is the separate network acquisition command; rerunning it replaces its own retrieval receipt and may observe changed server metadata. It is unnecessary for local replay. The decoder currently lives in a temporary folder, so reproducibility later depends on its continued availability or an equivalent verified environment. No global setting, durable local user memory, protected Codex configuration, shared model/task file or persistent process was changed.
