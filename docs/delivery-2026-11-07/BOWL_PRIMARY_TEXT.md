# Molin's Num 9:23 bowl witness: primary publication text acquired

**Current result:** the supplied Exa connector response for the original LOC-hosted volume contains Molin's published Num 9:23 example as `שומורו`. It has **three** waw characters. Molin identifies **two qameṣ-corresponding vowel letters** in the example; those are the two additions relative to the comparison form's consonantal letters `שמרו`, which already include the final waw. This is an edition/publication-text observation, not independent inspection of ink, a securely dated specimen, or a direct measurement of ancient sound.

This is an additive source-coverage update. Earlier `BOWL_WITNESS.md`, `recovery.json`, and the failed one-request LOC acquisition remain accurate records of those earlier phases. They were not overwritten. The present record is a standalone primary-text addition; it does not assert that the integrated SUNNY modules consume it.

## Source layer and exact coordinates

Source: Dorota Molin (2020), *Biblical Quotations in the Aramaic Incantation Bowls and Their Contribution to the Study of the Babylonian Reading Tradition*, DOI [10.11647/OBP.0207.04](https://doi.org/10.11647/OBP.0207.04), in Hornkohl and Khan (eds.), *Studies in Semitic Vocalisation and Reading Traditions*, pp. 147–170. The [original volume locator](https://tile.loc.gov/storage-services/master/gdc/gdcebookspublic/20/19/39/45/70/2019394570/2019394570.pdf) is preserved in the connector's text response.

The coordinating agent obtained the connector response; this reader independently read the saved response's `/content/0/text`. No network request was made by this verification. The response is text rendered from the publication, with visibly fragmented Hebrew, extraction-order anomalies, and occasional corrupted characters elsewhere. It is not original PDF bytes. No PDF render, bowl photograph, or physical artefact was inspected.

| Captured layer | Exact size | SHA-256 |
| --- | --- | --- |
| Saved Exa response JSON bytes | 853,595 bytes | `9460acbac92c678bf0b4bfbc7fc73a6b99f679e6a8e349e4b378f8a13ac59f96` |
| Decoded `/content/0/text`, encoded unchanged as UTF-8 | 842,781 bytes; 800,209 code points / UTF-16 units | `bc5c28a6247e0ed254d0ad55ad68cbdf160c76692fcbab34674352e1e1fd67c2` |
| Original PDF bytes | NOT RETRIEVED | UNKNOWN |

All spans below are zero-based and half-open in that exact connector text, not in the JSON serialization or unseen PDF. The full text contains no supplementary characters, so its code-point and UTF-16 positions coincide. UTF-8 byte spans and one-based text-line coordinates are separately recorded in `evidence-passages.json`.

- Molin chapter window begins at `249024`; the following chapter title begins at `284209`.
- The six-letter spelling occupies **`[274601,274607)`**.
- The raw example row, its prose interpretation, method assumptions, general dating paragraph, bibliographic expansion, and footnotes are preserved as seven verified passages.
- The known printed-page citation target is pp. 163–164. The relevant subsection is present, but a page-by-page PDF mapping was not independently established from this connector rendering.

## Exact spelling and the counting correction

| Form | Role | Waw count | Waw indices, zero-based |
| --- | --- | --- | --- |
| `שומורו` | Primary publication connector spelling | **3** | 1, 3, 5 |
| `שומרו` | Earlier secondary indexed discovery lead | **2** | 1, 4 |
| `שמרו` | Comparison consonantal letters normalized from the raw BHS segment | **1** | 3 |

The raw connector row has a fragmented BHS segment rather than a contiguous `שמרו`. The script preserves that raw row and derives its consonantal letters by retaining U+05D0–U+05EA and dropping extraction spaces/combining signs. That is an explicit normalization for this comparison only; the immutable source snapshot was not normalized. Removing waw at indices 1 and 3 from `שומורו` yields `שמרו`; its final waw remains. The script asserts all three counts and the two-insertion relationship. It does not identify visible ink from a photograph.

The earlier `שומרו` discovery lead is consequently incomplete relative to the present primary-publication text. It must not replace the newly captured reading or be counted as an independent bowl witness.

## Citation identity and its remaining limit

Molin's bibliography explicitly expands **HLIB** to **Shaul Shaked (1995), “Peace be Upon You, Exalted Angels: On Hekhalot Liturgy and Incantation Bowls,” *Jewish Studies Quarterly* 2/3: 197–219**. This is distinct from Shaked, Ford and Bhayro's 2013 *Aramaic Bowl Spells* volume.

The example's citation is editorially reordered from the connector row as **`HLIB, 213; 684.14`**. Page 213 and the literal locator `684.14` are present. **The exact definition of the components of `684.14` remains unresolved.** The inspected Molin chapter supplies the locator but does not explicitly define it as a catalogue/bowl number plus line. The sole occurrence of `684.14` and both HLIB occurrences were checked within the chapter window. An edition-level identification must be verified against Shaked 1995 or its apparatus before the likely numbering interpretation is promoted to a confirmed bowl ID/line.

## Published interpretation and qualifications

In subsection 2.4, Molin treats the spelling as evidence of a **pausal** form and oral/liturgical transmission. The published phonetic reconstruction is `[ʃɔːˈmɔːruː]`, contrasted with a contextual Babylonian form `[ʃɔːmaˈruː]`. These IPA strings are the author's reconstruction and comparison, not acoustic observations. In particular, the second qameṣ-corresponding vowel is tied to the pausal analysis; it must not silently become evidence that every contextual position had the same vowel quality.

Footnote 46 places the use of waw parallel to Tiberian qameṣ in the broader Hebrew and Aramaic bowl literature and points to Juusola 1999 and Molin 2017, pp. 17–22, for evaluation. Footnote 47 cites Yeivin 1985, p. 427, and specifies that the displayed `[a]` denotes shewa. These references were read in Molin's text; their underlying sources were not independently acquired here.

Molin's method compares orthographic differences against the Leningrad Codex consonantal tradition. Her footnote 8 makes the assumptions explicit: a proto-Masoretic text already authoritative at bowl production and a high similarity to Leningrad's consonantal text. She describes approximately 155 biblical verses collected from publications of transcribed spells. That edition-mediated method is a material provenance condition, not an independent epigraphic collation by this reader.

The introduction reports positive evidence for bowl production in the sixth and seventh centuries CE and a possible earlier beginning. It does **not** provide an independently verified date for the cited `684.14` specimen in the acquired material. The inherited-rounding versus contact/parallel-change question therefore remains open. This case now establishes a published, source-bound pausal spelling argument, with its explicit assumptions; it does not by itself establish the innovation's date, branch ancestry, or a precise ancient phoneme independently of that argument.

**Remaining discriminator:** verify the edition locator, letter reading and specimen-specific dating; then compare the claimed vowel-letter use across pausal/contextual positions, vernacular/orthographic environments and independently dated traditions. A genealogical conclusion requires evidence distinguishing shared inheritance from contact or parallel change beyond this one published example.

## Checks actually run

`verify_primary_text.py` read the supplied transport locally, preserved its exact text, computed both hashes, verified the **3/2/1 waw counts** and the two insertions, and executed the installed Prumo + Jev Evidence Audit helper: **seven passage records validated**. The installed **Proofline 2.0.2** verifier also executed on the six-letter span and returned **`valid: true`**, citation count 1, package root `6eac104e06082ea611a7733c2e7f04522b77fce24e0bb993ad6d15a745db6f25`.

Both verifiers establish local text/span/package consistency only. The package is unsigned; its numerical confidence field denotes exact span fidelity and is not historical confidence. No new Jev inference, hosted model run, SuperJev success, PDF/ink verification or broader SUNNY completion is claimed.

Machine-readable result: `state/delivery-2026-11-07/symbol-contact/bowls/connector-acquisition/primary-text-record.json`. Exact text and passage records, both verifier outputs and artifact hashes are in the same directory.
