# W72 upstream research — Vaticanus and DSS checkpoint 2

3 November 2026, America/Phoenix. This is a bounded research result under the user's pasted SUNNY protocol. It does not change the frozen SUN kernel, choose a W72 coordinate map, or claim a blind prediction. No Git workflow was used.

## Result and exact source locations

The Greek passage is present in **Vat. gr. 1209, manuscript pages 64–65**, not wholly on page 64. The official manifest labels image sequence 0068 as manuscript page 64 and sequence 0069 as page 65. Image collation places 14:19 at 64.III.37–42 continuing through 65.I.1–4; 14:20 at 65.I.4–11; and 14:21 at 65.I.12–19. Initial/final lines sometimes contain adjoining verses. These are counted physical lines; the modern verse labels are analytical additions. [Vatican Library (accessed 2026/11), pages 64–65: [64](https://digi.vatlib.it/view/MSS_Vat.gr.1209/0068), [65](https://digi.vatlib.it/view/MSS_Vat.gr.1209/0069)].

Masoretica's three target lookups all pointed to page 64 and displayed an explicitly labeled Rahlfs reference text. Direct image inspection established the continuation onto page 65. Its reference text must not be mislabeled a Vaticanus diplomatic transcription. [Dershowitz (accessed 2026/11), [Exodus 14:20 lookup](https://www.masoretica.org/?book=Exodus&chapter=14&manuscript=vaticanus&verse=20)].

**Native Greek count, conditional on the saved image-collated draft:**

| Letter-count layer | 14:19 | 14:20 | 14:21 |
|---|---:|---:|---:|
| Transcribed visible alphabet letters; abbreviation marks excluded | 147 | 137 | 133 |
| Line-end nasal suspensions expanded; contracted names retained | 148 | 138 | 134 |
| Nasal suspensions and contracted names expanded | 153 | 141 | 138 |

The calculation joins the located line segments and verifies that the declared expansions reproduce each saved expanded verse exactly. Punctuation, spaces, accents, breathings, diaeresis and overbars are excluded; lunate sigma is represented by ordinary capital sigma. The draft records ΘΥ→ΘΕΟΥ and ΙΣΛ→ΙΣΡΑΗΛ in 14:19, ΙΣΛ→ΙΣΡΑΗΛ in 14:20, and ΚΣ→ΚΥΡΙΟΣ in 14:21, plus a line-end nasal suspension in each verse. This is an alphabet-letter count under an explicit convention, not a stroke count or full palaeographic encoding. The line transcription, expansion locations, English translations and remaining checks are in `transcription.json`; executable count results are in `counts.json`. [Local observation/calculation (2026/11), the two cited Vatican images and saved transcription].

**Consequence for SUNNY:** none of these layers is a three-row 72-letter input. The fixed Hebrew extraction was therefore not applied to them. A Greek-native sequence remains a valid research object; a 72-slot cross-language representation would require a separately justified alignment, which has not been constructed. [Experimental deduction from the local counts and the user's fixed 3×72 acceptance rule].

## A corroborated Greek textual difference

The visible Vaticanus text in 14:20 reads, in expanded form:

```text
ἀνὰ μέσον τῶν Αἰγυπτίων

between the Egyptians
```
[Vatican Library (accessed 2026/11), [65.I.4–5](https://digi.vatlib.it/view/MSS_Vat.gr.1209/0069)].

The displayed Rahlfs reference has an additional phrase before “the Egyptians”:

```text
τῆς παρεμβολῆς

of the camp
```
[Dershowitz / Rahlfs reference (accessed 2026/11), [14:20](https://www.masoretica.org/?book=Exodus&chapter=14&manuscript=vaticanus&verse=20)].

Swete's Vaticanus-based printed text agrees with the shorter reading, and its apparatus explicitly records the added phrase in A and F. A scan of volume I, printed page 132, was inspected; its OCR was used only as a locator. The printed phrase has 13 alphabet letters, so adding it alone changes the expanded 14:20 count from 141 to 154. That is an edition/witness difference, not a cipher effect. [Swete (scanned 1896 issue), [vol. I p.132, leaf 157](https://archive.org/details/GRCSWET_DBS_HS/page/n157/mode/1up)].

Swete explains that his base text follows Vaticanus where available but includes editorial policies and textual notes. He also discusses the difficulty of distinguishing Vaticanus's corrections and retracing. Agreement with his printed text corroborates wording; it does not certify that every visible letter belongs to the first hand. [Swete (1887 introduction), [pp. xi–xvi and xviii–xx](https://www.ccel.org/s/swete/lxx1/htm/ii.i.htm)].

**Hand status:** the saved transcription represents the visible main-text sequence. Accents/breathings, retracing and corrective hands have not been completely stratified. No claim of a certified fourth-century first-hand reading, absence of correction, or “most unadulterated” text follows from this checkpoint. An independent second palaeographic collation remains open. [Scope limit of this image inspection].

## DSS comparison without filling gaps

The current comparison uses Qumran-Digital's versioned scholarly transcriptions, not a new reading of the physical DSS images. Brackets and uncertainty marks remain decisive. [Qumran-Digital (2025/11), [4Q11](https://lexicon.qumran-digital.org/transcriptions/4Q11/2025-11-11/index.html), [4Q365](https://lexicon.qumran-digital.org/transcriptions/4Q365/2025-11-11/index.html)].

- **4Q11 frg.10 ii.6–7:** the edited text supports agreement with the control for complete unbracketed/unmarked words including מלאך, ההלך and עמוד. Surrounding partially restored or uncertain words do not certify an entire verse's equality or length. [Qumran-Digital (2025/11), 4Q11 frg.10 ii.6–7].
- **4Q365 frg.6a i.12:** the unbracketed, unmarked end of the line reads the following; the name has an additional waw compared with the control's משה. [Qumran-Digital (2025/11), 4Q365 frg.6a i.12].

```text
ויט מושה

Moses stretched [out].
```
[Qumran-Digital (2025/11), [4Q365 frg.6a i.12](https://lexicon.qumran-digital.org/transcriptions/4Q365/2025-11-11/index.html)].

- **Critical restoration boundary:** לוא and כול earlier in 4Q365 line 12, and the long text including כול in line 13, occur inside editorial reconstruction brackets. They were not accepted as certain surviving spellings. The heading's verse coverage cannot override those brackets. [Qumran-Digital (2025/11), 4Q365 frg.6a i.12–13].
- **4Q18 frg.1.1–2:** the transcription intersects 14:21 but includes extensive reconstructed portions; its apparent long sequence cannot be treated as a complete surviving row. No full-row count or extraction was run. [Qumran-Digital (2026/10), [4Q18 frg.1](https://lexicon.qumran-digital.org/transcriptions/4Q18/2026-10-06/index.html)].

The bounded **single-edit control** substitutes only משה→מושה in the already saved modern Hebrew 14:21 control. It changes that control row from 72 to 73 letters. This is not a reconstructed 4Q365 verse and says nothing about compensating variants in its missing material. It demonstrates that this attested editorial reading, considered alone, breaks fixed-length eligibility; no triplet collision graph was fabricated by dropping or padding a letter. See `single-edit-control.json`. [Local calculation (2026/11), edition control and the cited 4Q365 line].

## Acceptance gates and remaining work

| Gate | Current result |
|---|---|
| Textual | Target Greek images located and visibly collated; wording corroborated against a Vaticanus-based printed edition. Full hand stratification and independent second collation remain partial. DSS evidence is editorial-transcription evidence pending image collation. |
| Structural | Native Greek lengths computed under three explicit conventions. Fixed 3×72 eligibility fails for these Greek streams. The single Hebrew spelling edit changes the control row to 73. Complete DSS witness collision graphs remain unevaluable here. |
| SUN/W72 | Unrun. No coordinate assignment, exceptional fiber, fitted epoch or held-out prediction was introduced. Known collision pairs remain exposed regression observations. |

Next bounded research action: acquire the original DSS plate locators and inspect the specific מושה reading; Jev's completion review selected this next unit. Independently collating the Greek line-end suspensions and main-text draft remains open, followed by Ge'ez target-witness/date/page verification in the retained source queue. The user's Jacob→Israel identity-resolution definition is now supplied; earlier “exact algorithm not retrieved” describes the previous checkpoint, not absence of the current operational definition. [Current user protocol, present research scope and `jev-review-receipt.json`].

Actual capability use: SuperJev `jev-1.14.0` selected image-first collation followed by edition comparison; requests and complete receipts are saved here. Supermemory retrieved checkpoint-1 continuity. Firecrawl retrieved the secondary page locator and official-viewer screenshot. The research source-documentation specialist instructions were applied. Proofline's bundled verifier passed the package binding the explicit first-hand limitation to this worksheet; this establishes exact local span integrity, not historical truth. No independent human reviewer, AgentProof capture, W72 solver, blind test, or mathematical-specialist backend ran. [Saved capability receipts and current tool results].

## Bounded progress

- [100%] Locate and inspect Vaticanus target images, retaining the reference-text distinction.
- [100%] Save the line-level draft and calculate declared Greek letter-count layers.
- [100%] Corroborate the visible wording with Swete and compare bounded DSS editorial evidence.
- [100%] Check the saved research worksheet, provenance hashes, kernel preservation and handoff limits.

The native plan tool was not exposed. These percentages describe the bounded checkpoint, not completion of SUNNY or of manuscript criticism.

## Sources

[Vatican Library, accessed 2026/11] Biblioteca Apostolica Vaticana. “Vat.gr.1209,” manuscript pp.64–65. https://digi.vatlib.it/view/MSS_Vat.gr.1209/0068 and https://digi.vatlib.it/view/MSS_Vat.gr.1209/0069

[Swete, scanned 1896 issue] H. B. Swete, editor. *The Old Testament in Greek according to the Septuagint*, vol. I, p.132. https://archive.org/details/GRCSWET_DBS_HS/page/n157/mode/1up

[Swete, 1887] H. B. Swete. Introduction to volume I. https://www.ccel.org/s/swete/lxx1/htm/ii.i.htm

[Qumran-Digital, 2025/11 and 2026/10] DFG Project “Qumran-Digital: Text und Lexikon.” Versioned transcriptions of 4Q11, 4Q365 and 4Q18, linked at the observations above. These are scholarly editorial transcriptions, not facsimiles.

[Dershowitz, accessed 2026/11] Idan Dershowitz. “Masoretica: Manuscript Explorer,” Exodus 14:20 Vaticanus lookup. https://www.masoretica.org/?book=Exodus&chapter=14&manuscript=vaticanus&verse=20
