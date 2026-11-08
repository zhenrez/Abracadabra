"""Independent structural/arithmetic audit and installed Proofline exact-span guard."""
from pathlib import Path
import hashlib,importlib.util,json,uuid
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf8'))
def main():
 modulePath=ROOT/'state/reconstruction/chinese-expanded.json';d=load(modulePath);p=load(HERE/'hkco-source-ranges.json');checks=[]
 def check(name,condition):
  assert condition,name;checks.append({'name':name,'status':'passed'})
 baseline=load(HERE/'history/chinese-expanded.df2cddfe83fbaf2d58cfb72036ee34de033c21e8489c22a97f11848c310f0897.json')
 for kind in ['sources','entities','relationships']:
  by={x['id']:x for x in d[kind]};check('Exact original '+kind+' preserved',all(by[x['id']]==x for x in baseline[kind]))
 entities={e['id']:e for e in d['entities']};check('Unique entity IDs',len(entities)==len(d['entities']))
 check('Every relationship endpoint resolves',all(r['source'] in entities and r['target'] in entities for r in d['relationships']))
 check('Every explicit parent resolves',all(e.get('parent') is None or e['parent'] in entities for e in entities.values()))
 check('Global generations not fabricated',all(e['position']['generation'] is None for e in entities.values()))
 for source in d['sources']:check('Source byte hash '+source['id'],sha((ROOT/source['path']).read_bytes())==source['sha256'])
 notes=[e for e in entities.values() if e['unit']=='instrument-qualified-chromatic-staff-note-address'];check('1045 instrument-qualified staff notes',len(notes)==1045)
 for profile in p['profiles']:
  expected=set(range(profile['sourceSoundingMinimum'],profile['sourceSoundingMaximum']+1))-set(profile['excludedSoundingChromaticIndices'])
  actual={e['nativeAddress']['sourceSoundingChromaticIndex'] for e in notes if e['nativeAddress']['profile']==profile['id']}
  check('Complete admitted semitone span '+profile['id'],actual==expected)
  for e in notes:
   if e['nativeAddress']['profile']==profile['id']:
    check('Written/sounding '+e['id'],e['nativeAddress']['writtenEffectiveChromaticIndex']+profile['sourceWrittenToSoundingSemitones']==e['nativeAddress']['sourceSoundingChromaticIndex'])
 z=p['zhengSourceStringsAndLocalOperations'];owners={}
 for string in z:
  v=string['openString']['writtenChromaticIndex'];check('Three local settings '+str(string['sourceOrdinalAscending']),{s['sourceSoundingChromaticIndex'] for s in string['localBridgeSettings']}=={v-1,v,v+1})
  for value in [v-1,v,v+1]:owners.setdefault(value,[]).append(string['sourceOrdinalAscending'])
 check('51-pitch union',len(owners)==51);check('No joint C#2/D2 setting',owners[37]==owners[38]==[1])
 check('2,500 target remains unresolved',d['censusReconciliation']['targetMet'] is False and d['notClaimed']['targetArtificiallyPadded'] is False)
 plugin=Path('C:/Users/Brend/.codex/plugins/cache/openai-curated-remote/proofline/2.0.2/skills/manage-evidence-decisions/scripts/proofline_package.py')
 spec=importlib.util.spec_from_file_location('chinese_proofline',plugin);proof=importlib.util.module_from_spec(spec);spec.loader.exec_module(proof)
 sourcePath=HERE/'hkco-zheng-operation-crop.txt';content=sourcePath.read_text(encoding='utf8');quote='Each String (note) can be adjusted a half step higher / lower by moving the bridges prior to playing.'
 start=content.index(quote);end=start+len(quote);uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,s));sid=uid(str(sourcePath));vid=uid(sha(sourcePath.read_bytes()));parser='sunny-hkco-pdf-crop-v1';stamp=datetime.now(timezone.utc).isoformat()
 def node(kind,obj):return {**obj,'node_hash':proof.node_hash(kind,obj)}
 source=node('source-version',{'workspace_id':uid(str(ROOT)),'source_id':sid,'source_identity_sha256':sha(('source:'+sid).encode()),'source_version_id':vid,'version_number':1,'content':content,'content_sha256':sha(content.encode()),'content_length':len(content),'parser_version':parser})
 chunk=node('chunk',{'id':uid(vid+'/chunk'),'source_node_hash':source['node_hash'],'source_id':sid,'source_version_id':vid,'ordinal':0,'start_offset':0,'end_offset':len(content),'start_line':1,'end_line':proof.line_number(content,len(content)-1),'content':content,'content_sha256':sha(content.encode())})
 citation=node('citation',{'id':uid(vid+'/citation'),'source_node_hash':source['node_hash'],'chunk_node_hashes':[chunk['node_hash']],'source_id':sid,'source_version_id':vid,'start_offset':start,'end_offset':end,'start_line':proof.line_number(content,start),'end_line':proof.line_number(content,end-1),'quote':quote,'quote_sha256':sha(quote.encode())})
 transform=node('transformation',{'method':'deterministic','parser_version':parser,'model_runs':[],'input_node_hashes':[source['node_hash'],chunk['node_hash'],citation['node_hash']]})
 artifact=node('decision-artifact',{'id':uid('SUNNY/HKCO/zheng-operation'),'kind':'constraint','title':'Zheng source-local bridge operation','statement':'The captured chart text licenses a half-step local adjustment before playing; the Chinese special-tuning exception and independent joint-tuning uncertainty remain explicit.','rationale':'Exact text integrity only, not manuscript authenticity, acoustic measurement, calibrated probability or overall completion.','confidence':1.0,'valid_from':None,'valid_to':None,'transformation_node_hash':transform['node_hash'],'citation_node_hashes':[citation['node_hash']]})
 review=node('review-state',{'artifact_node_hash':artifact['node_hash'],'status':'candidate','created_at':stamp,'updated_at':stamp})
 package={'manifest':{'schema':proof.SCHEMA,'created_at':stamp,'app_version':'SUNNY-Chinese-native-range','root_hash':proof.envelope('package-root',{'artifact_node_hash':artifact['node_hash'],'review_node_hash':review['node_hash']})},'payload':{'source_version':source,'chunks':[chunk],'citations':[citation],'transformation':transform,'artifact':artifact,'review':review}}
 verified=proof.verify(package);check('Installed Proofline exact-span package',verified['valid'])
 (HERE/'zheng-proofline-package.json').write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 report={'status':'passed','exit_code':0,'checkedAt':stamp,'moduleSha256':sha(modulePath.read_bytes()),'checks':checks,'entities':len(entities),'relationships':len(d['relationships']),
  'sourceRangePacketSha256':sha((HERE/'hkco-source-ranges.json').read_bytes()),'pdfSha256':sha((HERE/'hkco-range2025.pdf').read_bytes()),'guard':{'plugin':'Proofline','verifierPath':str(plugin),'verifierSha256':sha(plugin.read_bytes()),'result':verified},
  'boundary':'Structure, exact source bytes, admitted semitone arithmetic and one extracted text span. No universal Chinese completeness, physical measurement or complete independent endpoint-ink review.'}
 (HERE/'independent-range-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k not in ['checks','guard']},ensure_ascii=False));print('checks',len(checks),'proofline',verified['valid'])
if __name__=='__main__':main()
