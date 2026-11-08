"""Independent, bounded review of native execution and generation constraints; no author-output writes."""
from pathlib import Path
from fractions import Fraction as F
from functools import reduce
from itertools import combinations
from math import gcd,lcm
from datetime import datetime,timezone
import hashlib,json,sqlite3
ROOT=Path(__file__).resolve().parents[1]
def load(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def sha(raw):return hashlib.sha256(raw).hexdigest()
def rank(matrix):
 a=[[F(v) for v in row] for row in matrix];r=0
 for col in range(len(a[0])):
  p=next((i for i in range(r,len(a)) if a[i][col]),None)
  if p is None:continue
  a[r],a[p]=a[p],a[r];v=a[r][col];a[r]=[x/v for x in a[r]]
  for i in range(len(a)):
   if i!=r:
    f=a[i][col];a[i]=[x-f*y for x,y in zip(a[i],a[r])]
  r+=1
 return r
def mm(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def main():
 checks=[];native=load('state/reconstruction/native-execution.json');generation=load('state/reconstruction/generational-constraints.json')
 graphpath=ROOT/native['source']['path'];raw=graphpath.read_bytes();graph=json.loads(raw)
 assert sha(raw)==native['source']['sha256']=='6a92f9710fa6cd2937b9b07c42315b7d9c80644bd453c659f17318f95c55f95d'
 con=sqlite3.connect((ROOT/'data/sunny.sqlite').as_uri()+'?mode=ro',uri=True)
 try:
  source=con.execute('SELECT path,sha256 FROM sources WHERE id=?',(native['source']['sourceId'],)).fetchone()
  assert source and Path(source[0]).resolve()==graphpath.resolve() and source[1]==sha(raw)
  for i,(registered,original) in enumerate(zip(native['registry'],graph['generative_registry'])):
   assert registered['id']==original['id'] and registered['canonical']==original['canonical']
   assert registered['source']['pointer']==f'/generative_registry/{i}'
   assert [f['sourceMember'] for f in registered['families']]==original['members']
  assert len(native['registry'])==10 and sum(len(x['families']) for x in native['registry'])==19
  checks.append({'id':'native-original-GG-binding','passed':True,'mechanisms':10,'source_member_occurrences':19,'scope':'Exact original bytes, actual indexed occurrence ID/path and every literal registry/member definition.'})
  for span in generation['sources']:
   row=con.execute('SELECT source_id,role,text,content_sha256 FROM messages WHERE id=?',(span['message_id'],)).fetchone()
   assert row and row[0]==span['source_id'] and row[1]==span['message_role']
   assert sha(row[2].encode())==row[3]==span['message_content_sha256']
   exact=row[2][span['message_char_start']:span['message_char_end']]
   assert exact==span['exact_quote'] and sha(exact.encode())==span['quote_sha256']
   assert sha(Path(span['source_path']).read_bytes())==span['source_sha256']
   checks.append({'id':'generation-source-'+span['id'],'passed':True,'scope':'Exact native message role/hash/span and original source bytes, not external historical adjudication.'})
 finally:con.close()
 byid={c['id']:c for c in generation['constraints']};overlap=byid['GT-TIME-OVERLAP']
 A=overlap['matrix'];assert rank(A)==3
 assert rank(overlap['nullspace_basis'])==2
 for v in overlap['nullspace_basis']:assert mm(A,[[x] for x in v])==[[0],[0],[0]]
 runs=overlap['witness_executions']
 for case in runs:
  times=sorted(t for name,t in case['ordered_events']);durations=[b-a for a,b in zip(times,times[1:])]
  assert durations==case['durations'] and all(x>0 for x in durations)
  assert [sum(x*y for x,y in zip(row,durations)) for row in A]==case['lifespans']
 for a,b in combinations(runs,2):assert any(F(x,a['durations'][0])!=F(y,b['durations'][0]) for x,y in zip(a['durations'],b['durations']))
 witness=overlap['same_lifespans_counterexample'];assert witness['reported_MT']!=witness['conditional_alternative_not_a_historical_witness']
 assert mm(A,[[x] for x in witness['reported_MT']])==mm(A,[[x] for x in witness['conditional_alternative_not_a_historical_witness']])
 checks.append({'id':'overlap-window-rank-and-witnesses','passed':True,'rank':3,'nullity':2,'witness_readings':5,'non_tempo_equivalent_pairs':10,'scope':'Declared five-stage entrance/exit experiment; no years-to-beats conversion.'})
 insertion=byid['GT-INSERTION-PHASE'];offsets=insertion['reported_time_offsets']
 vals=offsets['SP_minus_MT']+offsets['Greek_minus_SP'];assert reduce(gcd,vals)==10
 assert [n for n in range(1,11) if all(v%n==0 for v in vals)]==[1,2,5,10]
 assert F(3,2)**12/F(2)**7==F(531441,524288)
 checks.append({'id':'pure-time-modulus-and-residual','passed':True,'maximal_modulus':10,'scope':'Listed main witness changes only; formal twelvefold transport is not twelve historical insertions.'})
 joint=byid['GT-JOINT-TIME-GEN'];M=joint['shift_lattice']['basis_columns'];cert=joint['shift_lattice']['smith_certificate']
 assert M==[[50,130],[0,1]] and mm(mm(cert['U'],M),cert['V'])==[[1,0],[0,50]]
 assert abs(cert['U'][0][0]*cert['U'][1][1]-cert['U'][0][1]*cert['U'][1][0])==1
 assert abs(cert['V'][0][0]*cert['V'][1][1]-cert['V'][0][1]*cert['V'][1][0])==1
 for case in joint['actual_source_row_checks']:
  assert (case['delta_reported_years']-130*case['delta_genealogical_index'])%50==0
 assert len(joint['actual_source_row_checks'])==14
 # Exact membership equivalence in a signed grid; the displayed algebra extends to Z².
 for t in range(-150,151):
  for g in range(-8,9):assert ((t-130*g)%50==0)==(F(t-130*g,50).denominator==1)
 assert reduce(gcd,[100,200,300,400,500,600,651])==1
 assert (131-130)%50==1 and (134-130)%50==4
 assert lcm(5,12)==60 and next(k for k in range(1,61) if 20*k%50==0 and 7*k%12==0)==60
 checks.append({'id':'joint-witness-lattice','passed':True,'source_shifts':14,'smith_diagonal':[1,50],'joint_character':'t-130g mod50','fixed_time_period':60,'scope':'Witness-representation quotient, not conservation along genealogy; adverse651/131 and actual134/1 edge invalidate stronger claims.'})
 adr=byid['GT-GEN-ADR']['witness_values'];assert adr[0]['expanded_GEN']==adr[1]['expanded_GEN'] and adr[0]['camp_ADR']!=adr[1]['camp_ADR']
 assert (7*adr[0]['camp_ADR'])%12!=(7*adr[1]['camp_ADR'])%12
 checks.append({'id':'generation-only-address-obstruction','passed':True,'scope':'The declared distinct addresses cannot both be a deterministic function of their shared generation; no tradition rejected.'})
 for row in byid['GT-720-REGISTER']['execution']:
  k=row['RL_circuits'];assert row['angle_degrees_if_common_angle']==360*k
  assert k==2*row['720_class_counter']+row['circuit_parity_separate_unidentified_coordinate']
  assert F(row['SUN_scalar_ratio'])==F(1,2)**k
 checks.append({'id':'conditional-720-class-register-carry','passed':True,'scope':'Shared positive angular-lift premise required. Winding parity is not identified with W72 beta; actual radius/height/fourth-axis laws unresolved.'})
 assert generation['canonical_orientation_selected'] is False and generation['blind_prediction'] is False
 manifest=load('docs/evidence/native-execution-audit-run001/manifest.json');assert manifest['run']['exit_status']==0
 for group in ['input_artifacts','outputs']:
  for item in manifest[group]:assert sha((ROOT/item['path']).read_bytes())==item['sha256'],item['path']
 paths=['src/native-operators.ts','tests/native-operators.test.mjs','scripts/reconstruct_native_execution.mjs','state/reconstruction/native-execution.json','scripts/reconstruct_generational_constraints.py','state/reconstruction/generational-constraints.json','docs/reconstruction/GENERATIONAL_CONSTRAINTS.md','docs/evidence/native-execution-audit-run001/manifest.json']
 out={'schema':'sunny.extended-native-math-independent-review.v1','checked_utc':datetime.now(timezone.utc).isoformat(),'status':'passed','checks':checks,'focused_native_tests':{'tests':14,'passed':14,'failed':0,'observed_exit_code':0,'tool_result_chunk':'cf9170','duration_ms':290.6441},'reviewed_artifact_hashes':{p:sha((ROOT/p).read_bytes()) for p in paths},'required_defects':[],'scope_notes':['MEC04 mapping sourceRefs/admissibility are caller declarations; result explicitly says they are not an independent source proof.','MEC09 execution witnesses a declared rule only when all required distinct references are supplied; no physical/acoustic constitution claimed.','MEC10 evaluates the supplied finite kernel row, exact sum1, preserving distribution and without electing its highest-probability event.','MEC01 is a rational subset, not a representation of Zhu irrational root extensions.','Actual indexed GG occurrence binding was checked outside the interpreter; the caller-provided occurrence ID is not self-authenticating.','The joint lattice character is invariant only across specified witness shifts, not all ancestor edges.','Fixed-time g mod60 suffices only for the two stated finite observables; it does not preserve exact pitch/residual or define a universal generational class.'],'canonical_orientation_elected':False,'blind_predictive_success_claimed':False,'software_full_suite_pass_claimed':False}
 (ROOT/'docs/evidence/extended-native-math-independent-review.json').write_text(json.dumps(out,indent=2),encoding='utf8')
 print(json.dumps({'status':'passed','checks':len(checks),'native_tests':14,'generation_source_spans':len(generation['sources']),'constraints':len(byid),'material_required_defects':0}))
if __name__=='__main__':main()
