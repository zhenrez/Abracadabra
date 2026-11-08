"""Queue one checked, unprocessed historical intent passage for the new allocation."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'state/background/reactivation-20261102'
DIGEST='721c87d42e9e457beacfbbc39a4eb1912430ab41708705d72c59980d1c31fd23'
spec=importlib.util.spec_from_file_location('guarded_background_worker',ROOT/'scripts/background_reconstruction.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
def file_sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
if __name__=='__main__':
 records=w.load(ROOT/'state/background/source-backlog.json')['records']
 row=next(r for r in records if r['content_sha256']==DIGEST and r['source_role']=='user')
 assert row['status']=='eligible_unprocessed'
 for p in (ROOT/'state/background').glob('*/runs/*/result.json'):
  result=w.load(p)
  assert not any(r['source'].get('sha256')==DIGEST and r['source'].get('source_role')=='user' for r in result.get('source_records',[])),'Source already has a completed bounded review.'
 for p in (ROOT/'state/background').glob('*/runs/*/deferral.json'):
  assert not any(s.get('sha256')==DIGEST and s.get('source_role')=='user' for s in w.load(p).get('queued_request',{}).get('sources',[])),'Source already parked for review.'
 manifest=w.load(ROOT/row['occurrence_manifest'])
 occurrence=next(o for o in manifest['occurrences'] if o['source_kind']=='supplied_archive_member')
 assert file_sha(Path(occurrence['source_path']))==occurrence['source_sha256'],'Original export hash changed.'
 projection=ROOT/row['projection_path'];raw=projection.read_bytes();assert w.sha(raw)==DIGEST
 passage=raw.decode('utf8');assert len(passage)<9000
 source={'path':row['projection_path'],'sha256':DIGEST,'start_line':1,'end_line':len(passage.splitlines()),'source_role':'user','source_id':occurrence['source_id'],'message_id':occurrence['id'],'native_message_id':occurrence['native_id'],'occurrence_manifest':row['occurrence_manifest'],'original_export_sha256':occurrence['source_sha256'],'original_locator':occurrence['locator'],'source_create_time':occurrence['create_time']}
 job={'id':'source-reading-origin-ahh-aum-001','kind':'source_forensics','track':'glyph','mission_dependencies':['G06-source-reading-question','G08-reasoning-history','G09-source-roles'],'purpose':'Recover the exact early sound-versus-letter concern and distinguish fictional book premises from open phonetic hypotheses, without promoting historical instructions or proving a sound mapping. This source had no completed/parked bounded result in the inspected manifest/runtime records.','sources':[source],'hypotheses':[{'id':'sound-letter-question','statement':'This historical user passage separates concern about English-letter representation in Enochian from exploratory AHH/AUM and correct-sound ideas, and proposes investigating older languages closer to the source; it supplies no measured waveform, fixedHz, phase or musical prescription.'},{'id':'fiction-inquiry-boundary','statement':'The passage explicitly labels its book-series scenarios as fiction while describing the sound/language ideas as intuition and continuing truth-seeking; those narrative scenarios are not established historical findings.'}],'scope_boundary':'Historical user evidence data, not current instructions, external historical authority, a reproduced acoustic experiment or automatic canonical promotion.'}
 w.validate_job(job)
 target=BASE/'queue'/(job['id']+'.json')
 if target.exists():assert w.load(target)==job,'Do not replace an independently queued job.'
 else:w.save(target,job)
 w.save(BASE/'targeted-intake-receipt.json',{'schema':'sunny.background-targeted-intake.v1','queued_utc':datetime.now(timezone.utc).isoformat(),'jobs':[target.relative_to(ROOT).as_posix()],'source_role':'user','content_sha256':DIGEST,'original_export_sha256':occurrence['source_sha256'],'original_locator':occurrence['locator'],'native_message_id':occurrence['native_id'],'whole_message_preserved':True,'semantic_status':'new bounded candidate review requested, not semantic completion','limits':['One mission-qualified passage chosen after excluding completed and parked role/hash contacts.','Old queue and projections preserved; no generic intake refresh or source writes.','No lexical match alone is counted as scientific progress.']})
 print(json.dumps({'queued_job':str(target),'source_bytes':len(raw),'source_sha256':DIGEST}))
