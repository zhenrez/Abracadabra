"""Acquire exact publisher audio and retain provenance without inspecting targets."""
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import sys
import urllib.request

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCES = [
    ("publisher-book", "https://www.openbookpublishers.com/books/10.11647/obp.0163", "publisher-book.html"),
    ("OBP.0163.06", "https://doi.org/10.11647/OBP.0163.06", "OBP.0163.06.mp3"),
    ("OBP.0163.07", "https://doi.org/10.11647/OBP.0163.07", "OBP.0163.07.mp3"),
]
CDN = {
    "OBP.0163.06": "https://cdn.openbookpublishers.com/resources/10.11647/obp.0163/OBP.0163.06_Gen_1-13_forte_lene.mp3",
    "OBP.0163.07": "https://cdn.openbookpublishers.com/resources/10.11647/obp.0163/OBP.0163.07_Gen_1-13_forte_lene_melodic.mp3",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def acquire(item):
    identifier, requested_url, filename = item
    destination = HERE / "sources" / filename
    destination.parent.mkdir(exist_ok=True)
    record = {"id": identifier, "requested_url": requested_url, "start_utc": datetime.now(timezone.utc).isoformat(), "attempts": []}
    for url in [requested_url] + ([CDN[identifier]] if identifier in CDN else []):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 SUNNY-bounded-source-audit"})
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read()
                content_type = response.headers.get("Content-Type", "")
                if filename.endswith(".mp3") and not content_type.startswith("audio/"):
                    raise ValueError("Expected audio body, received " + content_type)
                destination.write_bytes(body)
                record["attempts"].append({"url": url, "status": "acquired"})
                record.update(status="acquired", final_url=response.url, http_status=response.status,
                              headers=dict(response.headers.items()), bytes=len(body), sha256=sha(body),
                              path=destination.relative_to(ROOT).as_posix(), completed_utc=datetime.now(timezone.utc).isoformat())
                return record
        except Exception as error:
            record["attempts"].append({"url": url, "status": "failed", "error": f"{type(error).__name__}: {error}"})
    record["status"] = "failed"
    return record


if __name__ == "__main__":
    method = HERE / "method-frozen.json"
    assert method.exists()
    with ThreadPoolExecutor(max_workers=3) as pool:
        records = list(pool.map(acquire, SOURCES))
    result = {"schema": "sunny.matched-audio.acquisition.v1", "created_utc": datetime.now(timezone.utc).isoformat(),
              "method_sha256": sha(method.read_bytes()), "method_frozen_utc": json.loads(method.read_text(encoding="utf-8-sig"))["frozen_utc"],
              "sources": records, "decoding_or_listening_performed": False, "new_model_requests": 0,
              "persistent_processes_started": 0, "protected_configuration_writes": 0}
    (HERE / "acquisition.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "acquired" if all(r["status"] == "acquired" for r in records) else "partial",
                      "sources": [{k: r.get(k) for k in ["id", "status", "bytes", "sha256", "final_url"]} for r in records]}))
