# EU-001R-CLOSEOUT

## Verified result

47 current tests and six original Sefer tests passed. Full original demonstration output reproduced exactly; the three recorded checks passed. Frozen source, baseline and SUN source hashes matched. G7 registration, evaluation and serialized unlock attempts remained denied. See certification-receipt.json, all_tests.log and original_six.log. Syntax was parsed for all Unit001 Python modules. No downstream model was implemented.

## Historical controls

Four bounded source-identified controls are serialized in historical-controls.json. Synthetic schema fixtures remain unchanged.

1. Sefer Yetzirah and Gra-version chapter 1: exact Sefaria JSON response bytes, version labels and content hashes retained. Both Hebrew responses identify Warsaw 1884; the records preserve distinct textual arrangements without asserting independent manuscripts. Neither is claimed to be the oldest surviving witness.
2. Ruth 3:3: two written/read pairs extracted from edition-specific markup. Raw HTML, pointing and spelling remain preserved; phonetic realization and historical explanation remain unassigned.
3. Lachish Basket B736, Locus C283: primary scholarly publication inspected, with candidate totals 13/14/16 retained as competing claims. The captured record is explicitly a host-transcribed short inspected excerpt plus paraphrase, not original PDF or artifact-image bytes. Direct PDF download returned an HTML error; it is retained as a FAILED_HTTP_CAPTURE, never as a verified PDF. DOI: https://doi.org/10.52486/01.00008.2, printed pages 44/47. The 2025 interpretation is separate from the ancient artifact.
4. Two 72-name orientation descriptions: the retrieved evidence is the modern Strickman/Silver translation's footnote 74 at Ibn Ezra on Exodus 14:19:1. The Hebrew commentary, annotated translation and footnote remain separate fields. The earlier 14:18:2 locator does not contain the relevant discussion. No direct medieval attribution of both procedures, preferred orientation or W72 identification is inferred.

These controls test faithful representation and provenance. They do not test whether the ancient readings or transmission hypotheses are historically correct, and are not prospective blind evidence. Exact captured response metadata, source URLs and license fields are in source-manifest.json. Missing original-manuscript information remains unresolved.

## Demonstrated correction

The first control test run failed because a nested italic tag prematurely ended footnote extraction. closeout_fixtures.py now balances nested i tags. The subsequent full run passed. No kernel schema change was required by the four controls.

## Work-state log dependency

Pasted text(20261106-072010).txt and Pasted text (2)(20261106-072251).txt remain SEARCHED / NOT RETRIEVED. Searches covered filenames in Documents, Downloads, Desktop and local Codex attachments; targeted current-session references and distinctive work-state phrases in attachment text were also checked. References in the EU-001R instruction were found; those references do not supply the files' content. No log was reconstructed from conversation summaries. Their contents or exact accessible attachment locators remain required for authoritative import and dependency reconciliation.

## Gate verdict

G0 functional conservation/real-fixture representation: PASS.

G1 original and adapter regression: PASS.

Formal closeout G0: PARTIAL; G1: PARTIAL, pending the explicit work-state source dependency. Historical root proof is not a condition of these architectural gates. G2–G7: LOCKED.

## Changed files and verification

Added acquire_closeout.py, closeout_fixtures.py, test_closeout.py, verify_closeout.py and the closeout source/control/receipt artifacts. Updated CLOSEOUT_PLAN.md and the plugin-capability ledger. Existing synthetic controls, earlier receipts, original Sefer files and SUN core remain preserved. No new manual Jev inference, independent review or historical certification is claimed.

Reproduce offline: python -B work/unit001/verify_closeout.py. Source acquisition is a separate explicit command and is not run by verification. No corpus ingestion, embeddings, model training or cross-orientation execution occurred.

Next dependency: attach the two named work-state documents again or provide their exact accessible attachment locators. After exact import and reconciliation, issue a new gate receipt rather than retroactively changing earlier partial receipts.
