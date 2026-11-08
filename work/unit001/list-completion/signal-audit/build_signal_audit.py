"""Inventory an explicit current-chat snapshot without exporting private reasoning."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, collections

OUT = Path(__file__).resolve().parent
PROJECT = OUT.parents[3]
ROOT_ID = '01a1af33-7e1f-7a13-b0da-24adc96bb98d'
PARENT_ID = '6ae9304f-c5c8-83e8-9993-26deecd505e6'

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    previous = json.loads((PROJECT / 'work/unit002/context-audit.json').read_text(encoding='utf-8'))
    sources, index, messages = [], [], []
    for item in previous['current_chat_sources']:
        path = Path(item['path'])
        raw = path.read_bytes()
        sources.append({'path': str(path), 'snapshot_bytes': len(raw), 'sha256': digest(raw),
                        'earlier_snapshot_sha256': item['sha256'],
                        'snapshot_policy': 'Native log may append; verify this exact byte prefix, never rewrite it.'})
        for number, line in enumerate(raw.splitlines(), 1):
            event = json.loads(line)
            payload = event.get('payload', {})
            if event.get('type') != 'response_item':
                continue
            kind = payload.get('type')
            role = payload.get('role')
            # Account for original record locations and hashes; do not publish private reasoning bodies.
            index.append({'source': str(path), 'line': number, 'kind': kind, 'role': role,
                          'native_line_sha256': digest(line)})
            if kind == 'message' and role in ('user', 'assistant'):
                text = ''.join(block.get('text', '') for block in payload.get('content', []) if isinstance(block, dict))
                messages.append({'source': str(path), 'line': number, 'role': role,
                                 'sha256': digest(text.encode('utf-8')), 'text': text})
    write('snapshot-index.json', {'created_utc': datetime.now(timezone.utc).isoformat(),
        'current_chat_id': ROOT_ID, 'sources': sources, 'response_items': index,
        'counts': {'source_segments': len(sources), 'response_items': len(index),
                   'user_assistant_messages': len(messages),
                   'message_roles': dict(collections.Counter(m['role'] for m in messages)),
                   'record_kinds': dict(collections.Counter(i['kind'] for i in index))},
        'boundary': 'Locations and hashes inventory all response items at this snapshot. Tool records are accounted for, not all semantically adjudicated. Private reasoning bodies are not exported.'})
    write('message-readback.json', messages)
    preview_text = next(m['text'] for m in messages if '"conversationId":"' + PARENT_ID + '"' in m['text'])
    preview_line = next(line for line in preview_text.splitlines() if line.startswith('{"conversationId"'))
    write('parent-preview.json', json.loads(preview_line))
    write('parent-access.json', {'conversation_id': PARENT_ID, 'status': 'NOT_RETRIEVED_FULL_TRANSCRIPT',
        'available': 'Exact supplied bounded preview; assistant bodies are three unresolved chatgpt-content-reference placeholders.',
        'no_substitution': 'Magic Patterns read_thread is a different service; the related backup has a different conversation ID.',
        'prior_attempts': previous['parent'], 'related_backup': previous['related_backup'],
        'consequence': 'No exhaustive parent review claimed. This is a contextual acquisition gap, not a reason to discard signals or block verified G0/G1 architecture.'})
    print(json.dumps({'sources': len(sources), 'response_items': len(index), 'messages': len(messages),
                      'parent': 'NOT_RETRIEVED_FULL_TRANSCRIPT'}, indent=2))

if __name__ == '__main__':
    main()
