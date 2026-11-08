"""One public LOC request; bounded time/bytes, no redirects/retries/credentials."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import time
import urllib.request

BASE = Path(__file__).resolve().parent
URL = 'https://tile.loc.gov/storage-services/master/gdc/gdcebookspublic/20/19/39/45/70/2019394570/2019394570.pdf'
MAX_BYTES = 55_000_000
DEADLINE_SECONDS = 35

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError('Redirect rejected; one-request limit retained: ' + str(code))

def main():
    BASE.mkdir(parents=True, exist_ok=True)
    partial = BASE / '2019394570.original-volume.pdf.part'
    target = BASE / '2019394570.original-volume.pdf'
    record_path = BASE / 'http-acquisition.json'
    if target.exists() or partial.exists() or record_path.exists():
        raise RuntimeError('Acquisition artifacts already exist; refusing another request.')
    record = {'url': URL, 'method': 'GET', 'request_limit': 1, 'redirects_allowed': False,
              'max_bytes': MAX_BYTES, 'deadline_seconds': DEADLINE_SECONDS,
              'started_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'status': 'STARTED', 'bytes_received': 0, 'original_source_sha256': None}
    started = time.monotonic()
    digest = hashlib.sha256()
    try:
        opener = urllib.request.build_opener(NoRedirect())
        request = urllib.request.Request(URL, headers={'User-Agent': 'SUNNY-public-source-recovery/1.0', 'Accept': 'application/pdf', 'Accept-Encoding': 'identity'})
        with opener.open(request, timeout=DEADLINE_SECONDS) as response:
            record.update({'http_status': response.status, 'http_reason': response.reason,
                           'response_url': response.geturl(), 'response_headers': dict(response.headers.items())})
            length = response.headers.get('Content-Length')
            if length is not None and int(length) > MAX_BYTES:
                raise RuntimeError('Declared content length exceeds byte limit.')
            with partial.open('xb') as sink:
                while True:
                    remaining = DEADLINE_SECONDS - (time.monotonic() - started)
                    if remaining <= 0:
                        raise TimeoutError('Total acquisition deadline reached.')
                    response.fp.raw._sock.settimeout(remaining)
                    block = response.read(min(65536, MAX_BYTES - record['bytes_received'] + 1))
                    if not block:
                        break
                    record['bytes_received'] += len(block)
                    if record['bytes_received'] > MAX_BYTES:
                        raise RuntimeError('Response exceeds byte limit.')
                    sink.write(block)
                    digest.update(block)
            if length is not None and record['bytes_received'] != int(length):
                raise RuntimeError('Received byte count differs from Content-Length.')
            if not partial.read_bytes()[:5] == b'%PDF-':
                raise RuntimeError('Retrieved bytes are not a PDF signature.')
            os.replace(partial, target)
            record.update({'status': 'DOWNLOADED', 'path': str(target), 'original_source_sha256': digest.hexdigest()})
    except Exception as exc:
        record.update({'status': 'FAILED', 'error_type': type(exc).__name__, 'error': str(exc),
                       'partial_path': str(partial) if partial.exists() else None,
                       'partial_sha256': hashlib.sha256(partial.read_bytes()).hexdigest() if partial.exists() else None})
    finally:
        record['elapsed_seconds'] = round(time.monotonic() - started, 6)
        record['completed_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0 if record['status'] == 'DOWNLOADED' else 1

if __name__ == '__main__':
    raise SystemExit(main())
