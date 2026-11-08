"""Frozen local SUNNY transport/source-role probes, selected by actual Jev receipt27."""
from pathlib import Path
import json,hashlib
from jev_tool import evaluate
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'/'evidence'
CASES=[
 {'id':'direct_user','source':'state/latest-user-correction.txt','state':{'source_role':'user','source_kind':'current direct user message','exact_excerpt':'use jev for absolutely everything, every possible decision absolutely MUST be dictated by jev'},'question':'Which source-native status describes this exact excerpt?','options':['Direct user instruction','Assistant proposal without a user answer','Source not retrieved'],'expected':'Direct user instruction'},
 {'id':'unanswered_proposal','source':'docs/REQUIREMENTS.json','state':{'source_role':'assistant','source_kind':'Final Q10 question in supplied transcript','excerpt':'My proposed answer is yes. Is that the distinction you are reaching for?','source_following_user_reply':'No following user answer exists in the supplied transcript.'},'question':'Which recorded authority status follows from these source-role facts?','options':['User-approved final law','Assistant proposal without a user answer','Complete scientific proof'],'expected':'Assistant proposal without a user answer'},
 {'id':'hash_binding','source':'docs/evidence/recovery-integrity.json','state':{'observed':'Preserved file SHA256 exactly matches the hash named in an inherited W72 report.','source_role':'machine byte-hash observation; inherited report is a separate source','unverified':'Historical truth, scientific law and live-account completeness have not been established.'},'question':'What does this exact file-hash match establish within the supplied evidence?','options':['Byte identity relative to the named hash','Every historical claim is true','All live-account material is complete'],'expected':'Byte identity relative to the named hash'}
]

def main():
 frozen={'selected_by':'state/jev-receipts/000027-54bdd517dab6.json','cases':CASES,'source_versions':{c['source']:hashlib.sha256((ROOT/c['source']).read_bytes()).hexdigest() for c in CASES},'protocol':'Three already-inspected cases; original and reversed option LISTS plus classification-question isolation. Labels are mechanically declared source roles/hash scope, not scientific outcomes. No blind or calibrated accuracy claim.'}
 freeze=OUT/'jev-source-probe-freeze.json'
 if freeze.exists(): raise ValueError('freeze already exists; do not overwrite a completed probe')
 freeze.write_text(json.dumps(frozen,ensure_ascii=False,indent=2),encoding='utf8')
 results=[]
 for case in CASES:
  runs=[]
  for mode,options,extra in [('original',case['options'],True),('reverse',list(reversed(case['options'])),True),('isolated',case['options'],False)]:
   questions=[{'id':'classification','type':'choice','question':case['question'],'options':options}]
   if extra: questions.append({'id':'originals','type':'boolean','question':'Should the original source bytes and this exact assessment record remain preserved?','criteria':{'true':'Preserve originals and all results.','false':'Discard or rewrite the original source.'}})
   request={'state':{'probe':'Already-inspected source/integrity engineering diagnostic; no canonical domain action is authorized by this result.',**case['state']},'questions':questions}
   answer=evaluate(request,f'SUNNY source probe {case["id"]}/{mode}')
   row=answer['answers'][0]; chosen=options[int(row['value'])]; dist={options[int(k)]:v for k,v in row['distribution'].items()}
   runs.append({'mode':mode,'receipt':answer['receipt'],'receipt_sha256':answer['sha256'],'selected_meaning':chosen,'distribution_by_meaning':dist,'matches_source_metadata':chosen==case['expected']})
  a,b,i=runs
  results.append({'case_id':case['id'],'expected_source_metadata':case['expected'],'runs':runs,'permutation_max_abs_mass_difference':max(abs(a['distribution_by_meaning'][k]-b['distribution_by_meaning'][k]) for k in a['distribution_by_meaning']),'isolation_max_abs_mass_difference':max(abs(a['distribution_by_meaning'][k]-i['distribution_by_meaning'][k]) for k in a['distribution_by_meaning']),'same_selected_meaning_under_permutation':a['selected_meaning']==b['selected_meaning'],'same_selected_meaning_in_isolation':a['selected_meaning']==i['selected_meaning']})
  print(json.dumps({'case':case['id'],'completed_calls':len(runs),'metadata_agreements':sum(r['matches_source_metadata'] for r in runs)}),flush=True)
 report={'freeze':str(freeze),'case_count':len(CASES),'actual_model_calls':sum(len(r['runs']) for r in results),'metadata_agreements':sum(x['matches_source_metadata'] for r in results for x in r['runs']),'results':results,'scope':'Three deliberately selected, already-inspected engineering cases and nine dependent model calls. This is not a representative benchmark, blind prediction, calibrated success probability, scientific law or complete-account check. Failures and differences are retained, never corrected by favorable resampling.'}
 (OUT/'jev-source-probes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))

if __name__=='__main__': main()
