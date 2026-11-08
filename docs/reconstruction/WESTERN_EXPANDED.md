# Western source-defined expansion

The bounded lower census contains **2,670 units**: **2,464 registered scale-degree occurrences, 31 voice/instrument range profiles, 128 GM1 sound programs and 47 GM1 percussion addresses**. These are different unit classes. This meets the requested 2,500–2,700 reconciliation range for the declared witness contract; it does not establish the size or completeness of Western music or its physical instruments.

The graph contains **4,059 entities, 6,755 relations and four views**. It preserves all **875 earlier Western entities and 1,059 internal relations exactly**, retaining chords, modes, rhythm, form and source-concept branches. Structural contexts and those earlier branches are not added to the 2,670 lower-unit count. Main graph and interface files were not edited by this lane.

## Supplied pitch and range witnesses

The supplied `music_chart3 (1).jpg` shows Major, Natural Minor, Harmonic Minor and Melodic Minor rows. Their C-root degree collections are read from the chord roots. The melodic-minor row has raised sixth and seventh; the generator models that ascending-form collection and does not invent a descending rule.

The supplied `Analysis output 7.png` gives an 88-key A0–C8 address range, MIDI 21–108, an A4 reference of 440 Hz, and an explicit equal-temperament caption. The extension composes those bounds with 12 transposition pitch classes and four seven-degree forms. There are 48 root/form contexts, 336 degree classes and **4 × 88 × 7 = 2,464** registered memberships. Every key belongs to seven roots within each form. These are relational memberships, not 2,464 different physical frequencies or performed notes.

Written degree names retain diatonic spelling, including E-sharp and C-flat where required by an explicitly declared root representative. Written pitch, scale-degree role and equal-tempered key address are separate fields. Root spelling representatives are computational choices, not historical selections of enharmonic identity. Derived reference Hz values are unmeasured equal-temperament calculations.

All **31 visible range-profile labels** are represented: six voices, 12 woodwinds, four brass profiles, three timpani sizes and six strings. Their absolute endpoints remain unknown because the blurred range bars do not support reliable pitch-bound transcription. Voices and timpani sizes are not counted as distinct physical instrument types.

The preserved originals are addressed by SHA256 in `source-readings.json`. The range original is `data/raw/hierarchy-inputs/74713030aa3b182bd1fde35bcd0ef1f8350f7084837514c81ebd881733650ed8/original.png`; the scale original is the `bfe232625c4cae6e88672cb38d79d375ad49a699e2adfb916cc635c42dbc0659` snapshot. Both were visually inspected.

## Original GM1 standard acquired

The [official MIDI Association page](https://midi.org/general-midi-level-1) links **MMA0007 / RP003, General MIDI System Level 1**. Its public Drive download succeeded on the first direct route: HTTP 200, **89,114 bytes**, SHA256 `ba09e13069ce3ad79989c3abc1d70c8f1e8ce3e3dd1097d9c241d6665e152bac`. Raw PDF and HTTP metadata are saved under `state/research/western-expanded/gm-acquisition/`. The earlier legacy-URL failure remains preserved in the existing acquisition record.

The original has ten PDF pages. Printed page 5 / PDF page 7 gives Table 1's **16 named program families** and Table 2's **128 numbered programs**, applicable outside channel 10. Printed page 6 / PDF page 8 gives Table 3's **47 channel-10 percussion-key mappings**, keys 35–81. The complete identified sound-set tables are represented, rather than omitting the percussion branch to match a provisional total.

Program numbers printed as 1–128 remain native addresses; a separate zero-based index is derived. These are sound-program identifiers. They are not a physical instrument inventory, and their worldwide instrument names and sound effects are not all claims of Western origin. Printed page 7 / PDF page 9 leaves synthesis/playback method and exact timbres to manufacturers. Acoustic characteristics remain undefined.

The actual original visibly clips program 25 after `Acoustic Guitar (nylon` and program 29 after `Electric Guitar (muted`. Observed strings and clipping flags are retained without reconstructing missing closing characters.

## Executed checks and remaining scope

`runtime/.venv/Scripts/python.exe -X utf8 scripts/reconstruct_western_expanded.py` exited **0**. Eight checks cover source hashes and actual Jev64 direction; exact preservation of the earlier 875 records; finite form/context counts; all 2,464 native addresses and per-key memberships; enharmonic spelling round-trips; all 31 profile labels with unknown endpoints; complete GM families/programs/percussion and clipped names; and valid ancestry with unknown global GEN. A separate source replay validates **191 exact GM table spans**: 16 families, 128 programs and 47 percussion mappings.

The frozen model SHA256 is `915917ab4ba7509d173686d29714de8ed2e2b5205edb6e5c2a1e2d0743923ba1`. `validation.json`, `source-ledger.json` and original acquisition metadata preserve the evidence.

Actual Supermemory retrieval and Exa source access ran. Existing actual local Jev receipt 64, AgentJev-0.6B, directs source-defined class expansion. No new hosted inference or successful unavailable SuperJev hook execution is claimed. Global SUNNY generation, orientation and shared geometry remain unresolved. Historical tunings, further notation practices, full instrument populations and other Western traditions remain open; MIDI's address space does not replace that structure.
