"""Bounded edition control; never reconstruct manuscript lacunae."""
import collections
import hashlib
import json
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'state/research/w72-upstream'
OUT.mkdir(parents=True, exist_ok=True)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

bindings = {}
base = ROOT / 'data/raw/archive/SUN_Universal_Archive/Library/SUN_DEEP_RECOVERY'
for name in ['SUN_GG_v1_final.json', 'W72_certification.json', 'W72_matched_nulls.json', 'SUN_Yetzirah_Shem_Template_Comparison_v1.json']:
    p = base / name
    bindings[str(p.relative_to(ROOT))] = sha(p.read_bytes())
assert bindings[str((base/'SUN_GG_v1_final.json').relative_to(ROOT))] == '6a92f9710fa6cd2937b9b07c42315b7d9c80644bd453c659f17318f95c55f95d'
save('frozen-bindings.json', bindings)

url = 'https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Exod.xml'
cache = OUT / 'edition-exod.xml'
if not cache.exists():
    cache.write_bytes(urllib.request.urlopen(url, timeout=25).read())
raw = cache.read_bytes()
tree = ET.fromstring(raw)
ns = {'o':'http://www.bibletechnologies.net/2003/OSIS/namespace'}
verses = []
for num in [19,20,21]:
    v = tree.find(f'.//o:verse[@osisID="Exod.14.{num}"]', ns)
    # Only word nodes: exclude editorial notes and punctuation. Keep final forms.
    words = [''.join(w.itertext()) for w in v.findall('o:w', ns)]
    verses.append(''.join(c for w in words for c in w if '\u05d0' <= c <= '\u05ea'))
lengths = list(map(len, verses))
assert lengths == [72,72,72], lengths
rows = [verses[0], verses[1][::-1], verses[2]]
triplets = [''.join(row[i] for row in rows) for i in range(72)]
def partition(items):
    d = collections.defaultdict(list)
    for i,s in enumerate(items,1): d[s].append(i)
    return sorted([v for v in d.values() if len(v)>1])
alphabet = 'אבגדהוזחטיכלמנסעפצקרשת'
finals = str.maketrans('ךםןףץ','כמנפצ')
normalized = [s.translate(finals) for s in triplets]
assert partition(triplets) == [[1,49],[11,17]]
assert partition(normalized) == [[1,49],[11,17],[14,55]]
formal = {}
for name, mapping in [('atbash', dict(zip(alphabet,alphabet[::-1]))), ('albam',dict(zip(alphabet,alphabet[11:]+alphabet[:11])))]:
    def transform(s): return ''.join(mapping[c] for c in s)
    transformed_rows = [transform(r.translate(finals)) for r in verses]
    extracted = [''.join([transformed_rows[0][i],transformed_rows[1][71-i],transformed_rows[2][i]]) for i in range(72)]
    assert extracted == [transform(s) for s in normalized]
    assert all(mapping[mapping[c]] == c for c in alphabet)
    assert partition(extracted) == partition(normalized)
    formal[name] = {'row_lengths':list(map(len,transformed_rows)), 'commutes_with_extraction':True, 'involution':True, 'collision_partition':partition(extracted), 'normalization':'final forms folded BEFORE substitution; compare normalized baseline only'}
# Recover exact historic claims without silently granting them manuscript authority.
historical = ROOT / 'data/raw/archive/SUN_Universal_Archive/Library/HISTORICAL_MUSIC/ChatGPT-Branch · Mapping Primordials to Music-20261018-0134.md'
save('edition-control.json', {'source_url':url,'source_sha256':sha(raw),'source_role':'OSHB/WLC digital edition control, not a newly collated ancient manuscript','normalization':'Hebrew word-node letters U+05D0..U+05EA only; final forms retained in raw branch; no padding or truncation','verses':dict(zip(['14:19','14:20','14:21'],verses)),'lengths':lengths,'indexed_occurrences':[{'index':i+1,'raw':s,'normalized':normalized[i]} for i,s in enumerate(triplets)],'distinct_raw':len(set(triplets)),'raw_collision_partition':partition(triplets),'distinct_normalized':len(set(normalized)),'normalized_collision_partition':partition(normalized),'formal_controls':formal,'historical_source':str(historical.relative_to(ROOT)),'historical_source_sha256':sha(historical.read_bytes()),'coordinate_mapping':'NOT_ESTABLISHED; no collision-informed mapping accepted','held_out':'NOT_RUN; known collisions exposed','greek':'NOT_RUN; Vaticanus target folio/transcription not yet collated; no Greek row padded to 72'})
assert all(sha((ROOT/p).read_bytes()) == h for p,h in bindings.items())
print(json.dumps({'status':'PASS_EDITION_AND_FORMAL_CONTROLS','lengths':lengths,'raw_collisions':partition(triplets),'normalized_collisions':partition(normalized),'frozen_files_unchanged':len(bindings),'ancient_manuscript_collation':False,'held_out_validation':False}))
