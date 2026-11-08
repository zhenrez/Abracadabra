"""Verify the recorded snapshot, allowing native logs to append after its cutoff."""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parent

def main():
    index = json.loads((ROOT / 'snapshot-index.json').read_text(encoding='utf-8'))
    messages = json.loads((ROOT / 'message-readback.json').read_text(encoding='utf-8'))
    source_prefixes = {}
    for source in index['sources']:
        raw = Path(source['path']).read_bytes()[:source['snapshot_bytes']]
        if hashlib.sha256(raw).hexdigest() != source['sha256']:
            raise ValueError('Native source prefix changed')
        source_prefixes[source['path']] = raw.splitlines()
    for record in index['response_items']:
        line = source_prefixes[record['source']][record['line'] - 1]
        if hashlib.sha256(line).hexdigest() != record['native_line_sha256']:
            raise ValueError('Native line identity changed')
    for message in messages:
        if hashlib.sha256(message['text'].encode('utf-8')).hexdigest() != message['sha256']:
            raise ValueError('Readback text hash changed')
        event = json.loads(source_prefixes[message['source']][message['line'] - 1])
        actual = ''.join(b.get('text', '') for b in event['payload']['content'] if isinstance(b, dict))
        if message['text'] != actual:
            raise ValueError('Readback differs from native source')
    if len(messages) != index['counts']['user_assistant_messages']:
        raise ValueError('Message count mismatch')
    preview = json.loads((ROOT / 'parent-preview.json').read_text(encoding='utf-8'))
    if preview['conversationId'] != '6ae9304f-c5c8-83e8-9993-26deecd505e6':
        raise ValueError('Wrong parent preview')
    for path in ROOT.glob('*.md'):
        text = path.read_text(encoding='utf-8')
        if not text.endswith('\n') or any(line.rstrip() != line for line in text.splitlines()) or '<<<<<<<' in text:
            raise ValueError('Markdown formatting failure')
    print(json.dumps({'status': 'PASSED', 'source_prefix_hashes': len(index['sources']),
        'native_line_hashes': len(index['response_items']), 'exact_message_roundtrips': len(messages),
        'parent_full_transcript': 'NOT_RETRIEVED', 'markdown': 'PASSED'}, indent=2))

if __name__ == '__main__':
    main()
