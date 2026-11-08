"""Build a standalone, source-preserving workbench without network dependencies."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,sys

ROOT=Path(__file__).resolve().parent
DEFAULT_SOURCE=ROOT.parent/'results/dashboard-data.json'

def validate(data):
    if not isinstance(data,dict) or not isinstance(data.get('matrix'),list) or not isinstance(data.get('counts'),dict):
        raise ValueError('An evidence matrix and explicit counts are required')
    counts=data['counts'];rows=data['matrix']
    if any(type(counts.get(k)) is not int or counts[k]<0 for k in ('positions','populated','empty')):
        raise ValueError('Nonnegative integer evidence counts required')
    if counts['positions']!=len(rows) or counts['populated']!=sum(bool(r.get('glyph')) for r in rows) or counts['empty']!=sum(not r.get('glyph') for r in rows):
        raise ValueError('Source counts differ from actual matrix positions')
    if counts['positions']!=counts['populated']+counts['empty']:raise ValueError('Evidence accounting mismatch')
    for row in rows:
        if not isinstance(row,dict) or any(k not in row for k in ('script','ordinal','glyph','ipa','record_id')):raise ValueError('Native source coordinates required')
        if type(row['ordinal']) is not int or not 1<=row['ordinal']<=36:raise ValueError('Invalid source ordinal')
    return True

def safe_json(value):
    return json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False).replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e').replace('\u2028','\\u2028').replace('\u2029','\\u2029')

def render(data,metadata):
    template=(ROOT/'workbench.template.html').read_text(encoding='utf-8')
    return template.replace('@@DATA@@',safe_json(data)).replace('@@META@@',safe_json(metadata))

def build(source=DEFAULT_SOURCE,output=None,assessment_source=None):
    source=Path(source);output=Path(output) if output else ROOT/'SUN_ARIADNE_Workbench.html'
    output.parent.mkdir(parents=True,exist_ok=True)
    metadata={'source_path':str(source.resolve()),'built_utc':datetime.now(timezone.utc).isoformat()}
    if not source.exists():
        data=None;metadata.update(status='WAITING_FOR_SOURCE',message='Waiting for the evidence file')
    else:
        raw=source.read_bytes();data=json.loads(raw);validate(data)
        metadata.update(status='READY',sha256=hashlib.sha256(raw).hexdigest(),counts=data['counts'],requirements=len(data.get('requirements',[])))
        snapshot=output.parent/'dashboard-data.snapshot.json';snapshot.write_bytes(raw)
        if snapshot.read_bytes()!=raw:raise RuntimeError('Source snapshot readback mismatch')
        current_path=Path(assessment_source) if assessment_source else source.parent.parent/'current-deliverables.json'
        if current_path.exists():
            current_raw=current_path.read_bytes();current=json.loads(current_raw)
            entries=current.get('requirements')
            if not isinstance(entries,list):raise ValueError('Current assessment requirements required')
            originals={r['id']:r for r in data.get('requirements',[])}
            current_ids=[r.get('original',{}).get('id') for r in entries]
            if len(current_ids)!=len(set(current_ids)) or set(current_ids)!=set(originals):
                raise ValueError('Current assessment coverage differs from original requirements')
            if any(entry['original']!=originals[entry['original']['id']] or not isinstance(entry.get('engineering_assessment'),dict) for entry in entries):
                raise ValueError('Current assessment must retain original rows verbatim')
            data['current_delivery']=current
            data['current_delivery_source']={'path':str(current_path.resolve()),'sha256':hashlib.sha256(current_raw).hexdigest()}
            metadata['current_delivery_sha256']=hashlib.sha256(current_raw).hexdigest()
            current_snapshot=output.parent/'current-deliverables.snapshot.json';current_snapshot.write_bytes(current_raw)
            if current_snapshot.read_bytes()!=current_raw:raise RuntimeError('Current assessment snapshot mismatch')
        else:metadata['current_delivery_status']='NOT_AVAILABLE'
        sefer_path=ROOT.parents[2]/'work/unit001/final-acceptance/acceptance-receipt.json'
        if sefer_path.exists():
            sefer_raw=sefer_path.read_bytes();sefer=json.loads(sefer_raw)
            data['sefer_baseline']={'source':{'path':str(sefer_path.resolve()),'sha256':hashlib.sha256(sefer_raw).hexdigest()},
                                    'scope':'Preserved Sefer structural baseline; not a musical pitch mapping','record':sefer}
            metadata['sefer_baseline_sha256']=hashlib.sha256(sefer_raw).hexdigest()
            sefer_snapshot=output.parent/'sefer-baseline.snapshot.json';sefer_snapshot.write_bytes(sefer_raw)
            if sefer_snapshot.read_bytes()!=sefer_raw:raise RuntimeError('Sefer source snapshot mismatch')
    html=render(data,metadata);output.write_text(html,encoding='utf-8')
    if output.read_text(encoding='utf-8')!=html:raise RuntimeError('HTML write/readback mismatch')
    receipt={**metadata,'html_path':str(output.resolve()),'html_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
             'template_sha256':hashlib.sha256((ROOT/'workbench.template.html').read_bytes()).hexdigest(),
             'source_preservation':'All JSON fields embedded; original source bytes separately snapshotted when available',
             'runtime_scope':'Standalone local HTML; no network, publishing, audio or original-source mutation'}
    target=output.parent/'build-receipt.json';target.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if json.loads(target.read_bytes())!=receipt:raise RuntimeError('Build receipt readback mismatch')
    return receipt

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,default=DEFAULT_SOURCE);parser.add_argument('--output',type=Path);parser.add_argument('--assessments',type=Path)
    args=parser.parse_args();receipt=build(args.source,args.output,args.assessments);print(json.dumps(receipt,ensure_ascii=True,indent=2))
    return 0 if receipt['status']=='READY' else 2

if __name__=='__main__':sys.exit(main())
