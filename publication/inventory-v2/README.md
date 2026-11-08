# Fresh publication metadata snapshot

The two inventory/classification scripts were copied byte-for-byte from v1 and
executed successfully. The metadata inventory observed 40,797 accessible files,
24,801,169,596 logical bytes, zero enumeration errors and zero followed reparse
points. No source contents, credential material or private archive contents were
opened. Input classification indexes and the project version manifest were read.

The filtered product projection contains 6,101 paths and 2,475,498,613 logical
bytes. All 82 authored candidates under `work/github-delivery*` and
`work/publication*` are excluded from the selection to prevent recursive copies.
These local control artifacts remain preserved separately.

Compared with the 5,988-path v1 projection, 113 paths were added and zero removed.
Among shared paths, 51 sizes changed and 53 timestamps alone changed. These are
metadata indicators; source content hashes were not computed by this unit.
Root must review/rebind actual changed bytes before copying or publication.

The workspace remained live. In particular, `data.js` was observed at 5,644,232
bytes during enumeration, differing from an earlier reported larger size.
No atomic snapshot or stable source tree is claimed.

The unchanged v1 classifier retains static text referring to an earlier denied
directory. That wording is not evidence of a current error: the fresh inventory
observed zero enumeration errors. Read the actual `summary.json` counts and
`enumeration-errors.jsonl`, alongside this qualification.

The final selection and public hash summary are
`include-candidates.public.jsonl` and `include-candidates-summary.public.json`.
`selection-diff.LOCAL-ONLY.json` retains the complete additions and metadata
changes. Every v1 artifact and original source remains untouched; no Git or
remote operation was performed.
