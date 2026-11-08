"""Preserve exactly the newly supplied hierarchy/music image occurrences."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def main():
    inventory=json.loads((ROOT/'docs/evidence/hierarchy-supplied-input-inventory.json').read_text(encoding='utf8'))
    rows=[]
    for item in inventory['inputs']:
        original=Path('C:/Users/Brend/Downloads')/item['name'];raw=original.read_bytes()
        sha=hashlib.sha256(raw).hexdigest()
        if sha!=item['sha256']:raise ValueError('Supplied input changed since inventory: '+item['name'])
        with Image.open(original) as im:
            kind=im.format;dimensions=list(im.size);frames=getattr(im,'n_frames',1)
        suffix={'JPEG':'.jpg','MPO':'.jpg','PNG':'.png'}.get(kind)
        if suffix is None:raise ValueError('Unexpected supplied image format')
        target=ROOT/'data/raw/hierarchy-inputs'/sha/('original'+suffix);target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():
            if target.read_bytes()!=raw:raise ValueError('Immutable input snapshot collision')
        else:
            with target.open('xb') as f:f.write(raw)
        rows.append({'id':'upload-'+sha,'occurrence_name':item['name'],'original_path':str(original),
          'snapshot':target.relative_to(ROOT).as_posix(),'sha256':sha,'bytes':len(raw),'format':kind,'dimensions':dimensions,'frames':frames,
          'source_role':'user_supplied_image','inspected_semantically':False,
          'boundary':'Byte identity preserves repeat occurrences. Image claims and captions remain source assertions, not current instructions or independently proved relationships.'})
    report={'schema':'sunny.hierarchy-supplied-images.v1','created_utc':datetime.now(timezone.utc).isoformat(),
      'occurrences':rows,'counts':{'supplied_occurrences':len(rows),'distinct_byte_contents':len({r['sha256'] for r in rows}),
      'missing':0,'preserved_occurrences':len(rows)},'account_scope':'Exact newly supplied paths only, not the entire account image collection.'}
    target=ROOT/'state/reconstruction/hierarchy-inputs.json'
    if target.exists():
        old=target.read_bytes();saved=ROOT/'state/checkpoint-history'/('before-hierarchy-inputs-'+hashlib.sha256(old).hexdigest()+'.json')
        if not saved.exists():saved.write_bytes(old)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'preserved','exit_code':0,**report['counts'],'originals_changed':False}))
if __name__=='__main__':main()
