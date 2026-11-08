"""Retry only target verses with explicit range syntax, retaining first errors."""
from concurrent.futures import ThreadPoolExecutor
import json
from fetch_targets import ROOT, fetch

TARGETS = {
    "uxlc-gen43-26-range": "https://tanach.us/Server.xml?Gen43:26-26",
    "uxlc-ezra8-18-range": "https://tanach.us/Server.xml?Ezra8:18-18",
    "uxlc-lev23-17-range": "https://tanach.us/Server.xml?Lev23:17-17",
    "uxlc-job33-21-range": "https://tanach.us/Server.xml?Job33:21-21",
    "uxlc-servers-documentation": "https://tanach.us/Pages/Servers.html",
}

if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=5) as pool:
        receipts = list(pool.map(fetch, TARGETS.items()))
    (ROOT / "retrieval-corrected.json").write_text(json.dumps(receipts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for r in receipts:
        print(r["id"], r["status"], r.get("bytes"), r.get("sha256"), r.get("error", ""))
