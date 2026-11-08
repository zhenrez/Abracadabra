import datetime, hashlib, json, pathlib, time
import requests

base = pathlib.Path('state/delivery-2026-11-07/symbol-contact/secunda/edition-acquisition')
url = 'https://repository.sbts.edu/bitstream/handle/10392/6977/CarreraCompanioni_sbts_0207D_10773.pdf?isAllowed=y&sequence=1'
record = {'started_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'attempt_limit': 2, 'attempts': [], 'original_pdf_acquired': False, 'manuscript_image_collated': False, 'prior_recovery_overwritten': False}
start = time.monotonic()
entry = {'attempt': 1, 'url': url, 'timeout_seconds': 25, 'allow_redirects': False}
try:
    response = requests.get(url, timeout=25, allow_redirects=False)
    entry.update({'status_code': response.status_code, 'response_url': response.url, 'headers': dict(response.headers), 'bytes_received': len(response.content), 'elapsed_seconds': round(time.monotonic()-start, 3)})
    if response.status_code == 200 and response.content.startswith(b'%PDF-'):
        path = base / 'carrera-2022.pdf'
        path.write_bytes(response.content)
        entry.update({'status': 'PDF_ACQUIRED', 'sha256': hashlib.sha256(response.content).hexdigest(), 'local_path': str(path)})
        record['original_pdf_acquired'] = True
    else:
        entry.update({'status': 'NOT_PDF_OR_NON200', 'body_prefix': response.content[:250].decode('utf-8',errors='replace')})
except requests.RequestException as exc:
    entry.update({'status': 'REQUEST_FAILED', 'exception_type': type(exc).__name__, 'exception': str(exc), 'elapsed_seconds': round(time.monotonic()-start,3)})
record['attempts'].append(entry)
record['finished_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
record['remaining_attempt_policy'] = 'Second attempt permitted only if an actual redirect or metadata supplies an exact current server/api/core/bitstreams identifier; no identifier inferred.'
(base/'download-result.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record,ensure_ascii=False,indent=2))
