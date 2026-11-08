"""Fetch only the four directed Alef passages and bounded publisher metadata.

No model calls, corpus crawling, background processes, or source normalization.
Run from the SUN root: python -X utf8 state/research/reactivation/alef-witness/fetch_targets.py
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import urllib.request

ROOT = Path(__file__).resolve().parent
TARGETS = {
    "uxlc-gen43-26": "https://tanach.us/Server.xml?Gen43:26",
    "uxlc-ezra8-18": "https://tanach.us/Server.xml?Ezra8:18",
    "uxlc-lev23-17": "https://tanach.us/Server.xml?Lev23:17",
    "uxlc-job33-21": "https://tanach.us/Server.xml?Job33:21",
    "uxlc-about": "https://tanach.us/Pages/About.html",
    "uxlc-server": "https://tanach.us/Server.html",
}

def fetch(item):
    name, url = item
    record = {"id": name, "requested_url": url,
              "attempted_utc": datetime.now(timezone.utc).isoformat()}
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "SUNNY-bounded-source-verification/1.0"})
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read(2_000_001)
            if len(raw) > 2_000_000:
                raise ValueError("bounded response exceeded 2 MB; not saved")
            suffix = ".xml" if "Server.xml" in url else ".html"
            path = ROOT / "sources" / (name + suffix)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            record.update(status=response.status, final_url=response.url,
                          headers=dict(response.headers), bytes=len(raw),
                          sha256=sha256(raw).hexdigest(), path=str(path.relative_to(ROOT)))
    except Exception as error:
        record.update(status="retrieval_failed", error_type=type(error).__name__, error=str(error))
    return record

if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=6) as pool:
        receipts = list(pool.map(fetch, TARGETS.items()))
    (ROOT / "retrieval.json").write_text(json.dumps(receipts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for r in receipts:
        print(r["id"], r["status"], r.get("bytes"), r.get("sha256"), r.get("error", ""))
