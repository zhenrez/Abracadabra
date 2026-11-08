# Four canonical Alef loci: raw-token witness test

The raw-token check left open in `tiberian-alef-operations.json` is now performed for **UXLC 2.6, 19 October 2026, build 27.7**, compared with the retained Open Scriptures/WLC token snapshot labeled commit `3d15126fb1ef74867fc1434be1942e837932691f`. All four target Alef clusters contain **U+05BC**. Job additionally places **U+05BD** in the Alef cluster. No Alef-marker disagreement was observed between these two inputs at these four loci. The exact complete token strings differ and are preserved below.

This completes the bounded transcription check. It does not complete the larger SUNNY mission, establish an ancient sound, or close the direct-manuscript and acoustic gaps.

| Locus | Exact publisher XML `<w>` text | Alef cluster, in original order | Retained WLC-derived token | Observed difference |
|---|---|---|---|---|
| Genesis 43:26 | `וַיָּבִ֥יאּוּ` | `אּ`: U+05D0 U+05BC | `וַ/יָּבִ֥יאּוּ` | Snapshot includes a slash marking its morphological segmentation. |
| Ezra 8:18 | `וַיָּבִ֨יאּוּ` | `אּ`: U+05D0 U+05BC | `וַ/יָּבִ֨יאּוּ` | Same segmentation difference; accent differs from Genesis and is preserved. |
| Leviticus 23:17 | `תָּבִ֣יאּוּ ׀` | `אּ`: U+05D0 U+05BC | `תָּבִ֣יאּוּ` | UXLC includes U+0020 SPACE and U+05C0 PASEQ inside this word element. |
| Job 33:21 | `רֻאּֽוּ׃` | `אּֽ`: U+05D0 U+05BC U+05BD | `רֻאּֽוּ` | UXLC includes final U+05C3 SOF PASUQ in this word element. |

U+05BC is named **HEBREW POINT DAGESH OR MAPIQ**. Its Unicode name does not adjudicate the function of this point. U+05BD is **HEBREW POINT METEG**. U+05C4 and U+05C5 (upper/lower dots) are different characters and are absent from these four target Alef clusters. The three nonconsonantal word-final dotted Alefs in the separate 3TS248 case are not reclassified or duplicated here.

A concrete encoding counterexample occurs in the already fetched Genesis verse: `<w>` 6 is `אֶת־`, whose Alef cluster is **U+05D0 U+05B6 (SEGOL)**, without U+05BC. Thus a rule that treats any combining mark on Alef as the canonical point fails on these actual source bytes. Its exact source span is retained as `same_verse_encoding_control`. This is a different lexical/morphological context and supplies no matched acoustic comparison or independent new source-context census.

The complete character-by-character lists, original UTF-8 token hashes, exact XML locations, zero-based half-open byte spans and comparison operations are in [token-comparison.json](../../state/research/reactivation/alef-witness/token-comparison.json). Removing only `/`, SPACE, PASEQ and SOF PASUQ makes each paired token string equal. That explicitly labeled formatting comparison does not erase the originals or imply that the punctuation lacks prosodic significance.

## Source recovery and reproducibility

The official publisher describes UXLC as a Unicode/XML transcription of Leningrad and a fork of WLC 4.20 (25 January 2016), with later revisions. These are related transcription lineages, not two independent ancient manuscripts. [Publisher provenance](https://www.tanach.us/Pages/About.html).

Four valid single-verse XML records and two small publisher metadata pages were retrieved; four initial verse-error responses and one missing-parameter error page are also retained. The corrected requests use the publisher's documented range syntax: [Genesis 43:26](https://tanach.us/Server.xml?Gen43:26-26), [Ezra 8:18](https://tanach.us/Server.xml?Ezra8:18-18), [Leviticus 23:17](https://tanach.us/Server.xml?Lev23:17-17), [Job 33:21](https://tanach.us/Server.xml?Job33:21-21). [Server syntax](https://www.tanach.us/Pages/Servers.html), [XML format](https://www.tanach.us/Pages/XMLFiles.html).

| Source file | Bytes | SHA-256 |
|---|---:|---|
| `uxlc-gen43-26-range.xml` | 10,692 | `c6af40efa7811e5eed60518836da06491cd7b1489997f4ed488d1a066d3a64b6` |
| `uxlc-ezra8-18-range.xml` | 8,127 | `135bd620088d520f86d691aabd3d51647725a4e19c08748ba9453f8c1a529299` |
| `uxlc-lev23-17-range.xml` | 9,999 | `b598cce53eb8c962b334239bf4e80428da6a689d436d3957936f5ee2b0341a21` |
| `uxlc-job33-21-range.xml` | 7,859 | `991d13f4442f63ba185fdc8037af65297ae8a95680aff1b00320ce10af7a8de4` |

Original response bytes and receipt headers are retained under `state/research/reactivation/alef-witness/sources/` and `retrieval-corrected.json`. Total target XML: **36,677 bytes**. Version/date/build come from each record's TEI header, rather than the search engine's older UXLC 2.5 snippet. The publisher adds Documentary Hypothesis metadata to its server output; that metadata plays no role in this Alef check.

The initial bare single-verse queries returned HTTP 200 **error documents**, explicitly reporting incorrect citation format. They are retained in `retrieval.json` and separately identified in `verification.json`; HTTP 200 is not treated as successful scripture retrieval. The web reader could verify the publisher metadata pages but could not open the query URLs. Direct raw-byte requests, followed by XML parsing and verse validation, retrieved the four passages. The older snapshot's report that a prior UXLC request returned 403 is historical and is not a claim about this successful retrieval.

The second comparison input is the retained `docs/reconstruction/symbol-sound-census/six-alef-loci.json`, whose SHA is recomputed and recorded. Its four original-book URLs and reported hashes remain available in the new output. Original full-book bytes for that commit were not newly retrieved or independently rehashed in this unit. The comparison accurately identifies that provenance limit.

Run the extraction offline from the workspace root:

```powershell
python -X utf8 state/research/reactivation/alef-witness/extract_compare.py
```

The replay verifies receipt hashes, parses exactly one expected verse per response, selects one lexical target, replays its exact raw UTF-8 byte span, enumerates all original codepoints, and records agreements and disagreements without requiring the editions to agree. Network retrieval is a separate, explicit operation in `fetch_targets.py` / `fetch_corrected.py`; no request runs during extraction.

## Comparison with Khan and the manuscript/reading layers

The retained Khan PDF has SHA-256 `bcab644037f62795041c3c6e6e37f1c1eb28f29d147b6d2c4409fd6bc3c0da24`. Printed pages 140–144 were inspected as page images; page 141 was newly rendered from that retained PDF. PDF extraction scrambles some right-to-left character/diacritic order, so its extracted Hebrew strings are not substituted for the XML tokens. [Publisher book record](https://www.openbookpublishers.com/books/10.11647/obp.0163).

The PDF's hash was freshly recomputed. [Khan page evidence](../../state/research/reactivation/alef-witness/khan-page-evidence.json) retains each inspected image's hash and PDF/printed page mapping.

| Source layer | What the inspected source supplies | Limit retained |
|---|---|---|
| Khan p.140 | Consonantal-only interpretation associated with Morag; contrasting analysis of the pointed Alef. | Competing interpretation remains visible. |
| Khan pp.140–141 | Ibn Nūḥ's grammatical comparison involving Genesis, Ezra and Job. | This is Khan's edition/analysis of that testimony. |
| Khan pp.141–142 | Reproduced Arabic-script Job excerpt, BL Or 2552 fol.51r line 1; shadda corresponds to the pointed Hebrew Alef. | Only the reproduced excerpt was visually inspected; the full manuscript and its distribution of shadda were not audited. Dating to the tenth/eleventh century remains Khan's attribution. |
| Khan p.143 | Geminate-Alef transcriptions attributed to modern Aleppo, Baghdad and Yemen traditions; four Aleppo examples. | Those traditions are not interchangeable with the Leningrad page or a measured medieval recording. |
| Khan pp.143–144 | Argument for gemination/extra articulatory effort in the four Standard Tiberian places. | A scholarly phonetic conclusion, not a result of the Unicode test. |
| UXLC 2.6 | Four explicit U+05BC Alef clusters and their edition context. | This transcription was checked; the four corresponding Leningrad ink tokens were not independently examined in facsimile. |

Job's verse contains a ketiv/qere pair on an **earlier word** (`ושפי` / `וְשֻׁפּ֥וּ`). Its marked `רֻאּֽוּ׃` is a `<w>` element, not the qere itself. The new result records the apparatus at its actual location rather than attaching a verse-level qere flag to the target Alef.

The resulting source constraint is narrow: these four version-bound tokens require a distinction between Alef alone, Alef plus U+05BC, and the separate meteg/punctuation context. They do not provide an absolute duration, a 2:1 timing ratio, Hz, an F0 value, a musical interval or an entire waveform. Direct Leningrad facsimile comparison, a full BL Or 2552 shadda audit and controlled acoustic observations remain unperformed. No blind or independently predicted outcome is claimed.

## Guardrails and task boundary

Installed SuperJev 0.1.3 coordination/verification and Riqor documentation/evidence methods were applied locally. The retained `jev-next-native-question-v2` request/receipt remains the substantive direction: `tiberian_context` 0.61, resolved model `jev-1.14.0`; the full distribution stays in the receipt. **No new Jev or other model inference, background launch, external message, durable local memory write or new remote specialist runtime occurred in this unit.** Account/billing attribution of the retained receipt remains **UNVERIFIED**. Supermemory continuity was supplied by the root's already retrieved checkpoint.

This is one symbol/sound-first contribution within the continuing sixteen-goal/eight-output SUNNY program. [Verification receipt](../../state/research/reactivation/alef-witness/verification.json) states exactly what passed and what remains outside the test.
