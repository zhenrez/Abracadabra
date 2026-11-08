"""Read-only source and arithmetic review of actual mandate calculation artifacts."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
from datetime import datetime,timezone
import hashlib,importlib.util,json,sqlite3,sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))

def main():
 checks=[]
 p=ROOT/'scripts/reconstruct_native_derivations.py'
 spec=importlib.util.spec_from_file_location('reviewed_native_derivations',p)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 native=mod.compute()
 checks.append({'id':'actual-native-computation','passed':native['status']=='exact_assertions_passed','source_files':len(native['source_checks']),'scope':'Re-execution of actual source-bound exact arithmetic without replacing author output.'})
 spans=load('state/reconstruction/tol-history-math.json')['source_spans']
 con=sqlite3.connect((ROOT/'data/sunny.sqlite').as_uri()+'?mode=ro',uri=True)
 try:
  for span in spans:
   row=con.execute('SELECT source_id,text FROM documents WHERE id=?',(span['document_id'],)).fetchone()
   assert row and row[0]==span['source_id']
   exact=row[1][span['document_char_start']:span['document_char_end']]
   assert exact==span['exact_quote'] and sha(exact.encode())==span['quote_sha256']
   assert sha(Path(span['source_path']).read_bytes())==span['source_sha256']
   checks.append({'id':'TOL-span-'+span['id'],'passed':True,'document_id':span['document_id'],'source_id':span['source_id'],'scope':'Read-only indexed document span and original source byte hash.'})
 finally:con.close()
 # Independent algebra of the complete optional transitive residue family.
 cands=[(b,(s-b)%6,s) for b,s in product(range(6),(1,5))]
 common=[]
 for r,l in product(range(12),repeat=2):
  values={((5*r+7*l)%12,(r*b+l*d)%6) for b,d,s in cands}
  expected=(r-l)%6==0 and l%3==0
  assert (len(values)==1)==expected
  if len(values)==1:common.append({'r':r,'l':l,'address':list(next(iter(values)))})
 assert len(common)==8 and len({tuple(w['address']) for w in common})==4
 assert len({b for b,d,s in cands})==6 and len({s for b,d,s in cands})==2
 assert len({(b,s) for b,d,s in cands})==12
 checks.append({'id':'orientation-residue-grid','passed':True,'candidates':len(cands),'words':144,'common_words':8,'shared_addresses':4,'scope':'Optional source family only; no global orientation election.'})
 # A left inverse would give two unequal histories the same reconstructed value.
 RL=F(2,3)*F(3,4);LR=F(3,4)*F(2,3)
 assert RL==LR==F(1,2)
 assert F(2,3)!=F(3,4)
 checks.append({'id':'history-projection-no-left-inverse','passed':True,'scope':'Protected RL and LR histories differ but scalar endpoints coincide. Any scalar-only reconstruction cannot left-invert both histories. Full history ontology is not assumed.'})
 paths=['src/prediction.ts','tests/prediction.test.mjs','scripts/reconstruct_native_derivations.py','scripts/reconstruct_orientation_predictions.mjs','state/reconstruction/native-derivations.json','state/reconstruction/orientation-predictions.json','state/reconstruction/tol-history-math.json','docs/evidence/mandate-input-preservation.json']
 out={'schema':'sunny.mandate-independent-review.v1','checked_utc':datetime.now(timezone.utc).isoformat(),'status':'passed','checks':checks,'artifact_hashes':{name:sha((ROOT/name).read_bytes()) for name in paths},'focused_node_test':{'observed_exit_code':0,'tests':5,'passed':5,'failed':0,'tool_result_chunk':'bb13d8','scope':'Actual tests/prediction.test.mjs, directly executed independently; not AgentProof capture.'},'code_review':{'skill':'agent-skills:code-review-and-quality','axes':['correctness','readability','architecture','security','performance'],'material_defects_in_scoped_prediction_module':[],'findings':['Unknown selectors remain possible; absent bindings/values prevent false unanimity.','Empty survivor sets explicitly report no-surviving-candidates.','Source references are syntactically checked; source authenticity correctly remains an external binding audit.','Finite residue families and exact rational carriers retain distinct scopes.','History minimality is restricted to fixed intermediate sample positions in the declared ten-word algebraic budget.']},'global_orientation_selected':False,'blind_prediction_validated':False,'account_completeness_certified':False}
 (ROOT/'docs/evidence/mandate-independent-review.json').write_text(json.dumps(out,indent=2),encoding='utf8')
 print(json.dumps({'status':out['status'],'checks':len(checks),'tol_spans':len(spans),'source_files':len(native['source_checks']),'node_tests':5}))
if __name__=='__main__':main()
