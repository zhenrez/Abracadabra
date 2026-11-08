# One-request LOC volume acquisition addendum

This adds to, and does not overwrite, `docs/delivery-2026-11-07/BOWL_WITNESS.md` or the earlier `recovery.json`.

On 2026-11-07 at 22:28:14 UTC, one direct public request was attempted for:

https://tile.loc.gov/storage-services/master/gdc/gdcebookspublic/20/19/39/45/70/2019394570/2019394570.pdf

The installed `runtime/.venv/Scripts/python.exe` ran the bounded downloader. It permits one GET, no redirects/retries, a total 35-second deadline and at most 55,000,000 bytes. No credentials or access-check bypass were used. The sole attempt failed during address resolution with `URLError: <urlopen error [Errno 11001] getaddrinfo failed>` after 0.065016 seconds. It received zero bytes. No HTTP status or response headers exist because the request did not reach an HTTP response. No source PDF, partial file, or original-source SHA-256 was produced. No further network request was made.

`http-acquisition.json` preserves the actual result, URL, limits, timestamps and error; `download_once.py` preserves the downloader used. Local artifact hashes do not substitute for an unavailable source hash.

Printed pp. 163–164 and the chapter start were not extracted or rendered. No Num 9:23 spelling, edition ID, editorial qualification or glyph was newly inspected. Neither pypdfium2 nor pdfplumber was run on an absent PDF. The earlier reading-status and historical-inference limits remain unchanged.

The remaining dependency is a successful authorized retrieval of the known original volume or an accessible publisher chapter copy. Once bytes are available, establish pagination from the Molin chapter header, extract and visually inspect printed pp. 163–164, and report edition readings separately from independently verified ink and reconstructed phonetics. No chronology/contact conclusion follows from this failed acquisition.

Prumo + Jev Research and Evidence Audit source/status rules remain applied from this bounded task. No new Jev inference, SuperJev execution success, source mutation or corpus restart is claimed.
