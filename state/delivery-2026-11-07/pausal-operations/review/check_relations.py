"""Independent pairwise FD, exhaustive refinement and SQLite projection checks."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,itertools,json,random,sqlite3,subprocess
DIR=Path(__file__).resolve().parent;ROOT=Path(__file__).resolve().parents[4]
def row(i,v):return {'id':str(i),'values':v,'sourceRefs':['explicit-independent-control']}
def val(r,k):return r['values'].get(k)
def complete(r,fields):return all(val(r,f) is not None for f in fields)
def fd(rows,base,out):
    known=[r for r in rows if complete(r,base+[out])]
    bad=any(all(val(a,f)==val(b,f) for f in base) and val(a,out)!=val(b,out) for a,b in itertools.combinations(known,2))
    return ('contradicted' if bad else 'no-counterexample-on-complete-rows' if known else 'no-complete-rows'),[r['id'] for r in rows if r not in known]
def refs(rows,base,candidates,out):
    valid=[]
    for size in range(len(candidates)+1):
        for sub in itertools.combinations(candidates,size):
            status,unknown=fd(rows,base+list(sub),out)
            if status=='no-counterexample-on-complete-rows' and not unknown:valid.append(frozenset(sub))
    return {v for v in valid if not any(other<v for other in valid)}
def sqljoin(rows,left,right):
    fields=list(dict.fromkeys(left+right));known=[r for r in rows if complete(r,fields)]
    quote=lambda x:'"'+x.replace('"','""')+'"'
    conn=sqlite3.connect(':memory:')
    conn.execute('create table native('+','.join(quote(f)+' TEXT COLLATE BINARY' for f in fields)+')')
    conn.executemany('insert into native values('+','.join('?' for _ in fields)+')',[tuple(val(r,f) for f in fields) for r in known])
    original=set(conn.execute('select distinct '+','.join(map(quote,fields))+' from native'))
    query='select distinct '+','.join(map(quote,fields))+' from (select distinct '+','.join(map(quote,left))+' from native) natural join (select distinct '+','.join(map(quote,right))+' from native)'
    joined=set(conn.execute(query));conn.close()
    return fields,original,joined,[r['id'] for r in rows if r not in known]
def main():
    examples=[row('keep',{'lexeme':'keep','input':'a','mode':'pausal','onset':'m','output':'ɔː','comparandum':'HLIB213'}),row('eat',{'lexeme':'eat','input':'a','mode':'pausal','onset':'χ','output':'eː','comparandum':'AMB176'})]
    cases=[]
    def add(i,rows,base=['input'],candidates=['lexeme','onset','comparandum'],conditions={'lexeme':'keep'},left=['lexeme','input'],right=['input','output'],out='output'):
        cases.append({'id':i,'rows':rows,'base':base,'candidates':candidates,'conditions':conditions,'left':left,'right':right,'output':out})
    add('Molin-admitted-two-row',examples,base=['input','mode'])
    add('duplicate-occurrences',examples+[row('keep-again',examples[0]['values'])])
    add('null-and-missing',examples+[row('null',{'input':'a','lexeme':None,'output':None}),row('missing',{'input':'a'})])
    add('empty-string-known',[row('empty',{'input':'','lexeme':'','output':'','onset':'','comparandum':''})],conditions={'lexeme':''})
    add('unicode-exact',[row('greek',{'input':'χ','lexeme':'first','output':'one','onset':'χ','comparandum':'same'}),row('latin',{'input':'x','lexeme':'second','output':'two','onset':'x','comparandum':'same'})],conditions={'input':'χ'})
    add('prototype-keys',[row('one',{'__proto__':'literal','constructor':'ctor','toString':'own','output':'yes'}),row('two',{'__proto__':'other','constructor':'ctor','output':'no'})],base=['constructor'],candidates=['__proto__','toString'],conditions={'__proto__':'literal'},left=['constructor','__proto__'],right=['constructor','output'])
    add('empty-relation',[])
    rng=random.Random(63111);alphabet=['','a','b','χ','x',None]
    for i in range(80):
        rows=[]
        for j in range(rng.randrange(1,8)):
            values={f:rng.choice(alphabet) for f in ['input','lexeme','onset','comparandum','output'] if rng.random()>.14}
            rows.append(row(str(i)+'-'+str(j),values))
        add('sample-'+str(i),rows,conditions={'lexeme':rng.choice(['','a','χ'])})
    (DIR/'relation-cases.json').write_text(json.dumps(cases,ensure_ascii=False),encoding='utf8')
    node=subprocess.run(['node',str(DIR/'run_relation_cases.mjs')],cwd=ROOT,capture_output=True,text=True)
    assert node.returncode==0,(node.stdout,node.stderr)
    actual=json.loads((DIR/'relation-actual.json').read_text(encoding='utf8'));assert actual['start']==actual['finish']
    failures=[];checks=0
    for c,a in zip(cases,actual['output']):
        if a.get('error'):failures.append({'id':c['id'],'issue':a['error']});continue
        status,unresolved=fd(c['rows'],c['base'],c['output'])
        if a['fd']['status']!=status or a['fd']['unresolvedRows']!=unresolved:failures.append({'id':c['id'],'issue':'FD mismatch'})
        if {frozenset(r) for r in a['refinements']}!=refs(c['rows'],c['base'],c['candidates'],c['output']):failures.append({'id':c['id'],'issue':'minimal refinement mismatch'})
        retained=[r for r in c['rows'] if all(val(r,f) is None or val(r,f)==v for f,v in c['conditions'].items())]
        expectedIds=[r['id'] for r in retained];expectedOutputs={val(r,c['output']) for r in retained if val(r,c['output']) is not None}
        queryUnresolved=[r['id'] for r in retained if not complete(r,list(c['conditions'])+[c['output']])]
        if a['query']['rowIds']!=expectedIds or set(a['query']['outputs'])!=expectedOutputs or a['query']['unresolvedRows']!=queryUnresolved:failures.append({'id':c['id'],'issue':'query mismatch'})
        fields,original,joined,joinUnresolved=sqljoin(c['rows'],c['left'],c['right'])
        actualExcess={tuple(r['values'][f] for f in fields) for r in a['join']['excessCombinations']}
        if a['join']['knownOriginalDistinctTuples']!=len(original) or a['join']['rejoinedDistinctTuples']!=len(joined) or actualExcess!=joined-original or a['join']['unresolvedRows']!=joinUnresolved:failures.append({'id':c['id'],'issue':'SQLite projection/join mismatch'})
        checks+=4
    malformedAccepted=[x for x in actual['malformed'] if 'error' not in x]
    result={'schema':'sunny.independent-reading-relation-review.v1','checkedAt':datetime.now(timezone.utc).isoformat(),'status':'passed' if not failures else 'failed','exit_code':int(bool(failures)),
        'datasets':len(cases),'independentOperationComparisons':checks,'failures':failures,'testedHashes':actual['start'],'sourceStable':True,
        'MolinAdmittedSampleJoin':{'originalDistinct':actual['output'][0]['join']['knownOriginalDistinctTuples'],'rejoinedDistinct':actual['output'][0]['join']['rejoinedDistinctTuples'],'excessDistinct':len(actual['output'][0]['join']['excessCombinations'])},
        'runtimeBoundaryObservations':{'malformedConditionInputsAccepted':malformedAccepted,'severity':'Runtime validation consistency; TypeScript signature already excludes these inputs, and no finite valid-input math defect was found.'},
        'oracle':'Pairwise FD; exhaustive valid-subset then strict-inclusion filtering; Python unknown-preserving selection; SQLite DISTINCT projections and NATURAL JOIN with binary collation.',
        'guardUse':'Actual Supermemory retrieval earlier in this bounded review; no new Jev call.',
        'boundary':'Admitted finite sample only; identifiers/finite keys are not inferred historical causes or universal laws.'}
    (DIR/'relation-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,ensure_ascii=False));return result['exit_code']
if __name__=='__main__':raise SystemExit(main())
