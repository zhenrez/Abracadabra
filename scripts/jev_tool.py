"""SUNNY's local AgentJev tool. No fixtures, hidden fallback, or fabricated decisions."""
from __future__ import annotations
import argparse, hashlib, json, math, sqlite3, sys, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
URL='http://127.0.0.1:8149'
PINNED_MODEL_SHA256='8166e46dc6019ae13f0d8fc97d603cdbcc2d20eb1882c7350c8deb9fc6bae215'

def canonical(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(v): return hashlib.sha256(canonical(v).encode('utf8')).hexdigest()

def http(path,request=None,timeout=45):
    data=canonical(request).encode('utf8') if request is not None else None
    req=urllib.request.Request(URL+path,data=data,headers={'Content-Type':'application/json','Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=timeout) as response:
        value=json.load(response)
    if not isinstance(value,dict): raise ValueError('Jev response is not an object')
    return value

def validate_request(request):
    if not isinstance(request,dict) or 'state' not in request: raise ValueError('request needs state')
    questions=request.get('questions')
    if not isinstance(questions,list) or not 1<=len(questions)<=32: raise ValueError('questions must contain 1..32 native AgentJev questions')
    ids=set()
    for q in questions:
        if not isinstance(q,dict) or not isinstance(q.get('id'),str) or q['id'] in ids: raise ValueError('question IDs must be unique strings')
        ids.add(q['id'])
        if not isinstance(q.get('question'),str) or not q['question'].strip(): raise ValueError('question text required')
        typ=q.get('type')
        if typ=='choice':
            opts=q.get('options')
            if not isinstance(opts,(dict,list)) or not 2<=len(opts)<=255: raise ValueError('choice needs 2..255 options')
            if not all(isinstance(v,str) and v.strip() for v in (opts.values() if isinstance(opts,dict) else opts)): raise ValueError('options require meaningful text')
        elif typ=='score':
            if not isinstance(q.get('levels'),list) or not 2<=len(q['levels'])<=10: raise ValueError('score needs 2..10 levels')
        elif typ!='boolean': raise ValueError('unsupported native question type')
    if len(canonical(request).encode('utf8'))>48000: raise ValueError('request exceeds 48000-byte local ceiling; decompose explicitly, never truncate')

def validate_result(request,result):
    if result.get('usage',{}).get('truncated_inputs',0)!=0: raise ValueError('Jev reported truncated input; no decision accepted')
    rows=result.get('results')
    if not isinstance(rows,list) or len(rows)!=1: raise ValueError('expected one result state')
    answers=rows[0].get('answers')
    if not isinstance(answers,list) or len(answers)!=len(request['questions']): raise ValueError('Jev omitted answers')
    by_id={a.get('id'):a for a in answers}
    if len(by_id)!=len(answers): raise ValueError('duplicate answer IDs')
    for q in request['questions']:
        a=by_id.get(q['id']); distribution=a.get('distribution') if a else None
        if not a or a.get('type')!=q['type']: raise ValueError('answer type differs from supplied question')
        if not isinstance(distribution,dict) or len(distribution)<2: raise ValueError('missing full distribution')
        probs=list(distribution.values())
        if not all(type(p) in (int,float) and math.isfinite(p) and 0<=p<=1 for p in probs) or abs(sum(probs)-1)>1e-5: raise ValueError('invalid decision probabilities')
        if q['type']=='choice':
            options=q['options']; keys=set(options) if isinstance(options,dict) else {str(i) for i in range(len(options))}
            if set(distribution)!=keys: raise ValueError('distribution labels differ from explicit candidates')
            value=a.get('value')
            if str(value) not in keys: raise ValueError('choice winner is not a supplied candidate')
            if distribution[str(value)]<max(probs)-1e-7: raise ValueError('choice winner is not a distribution maximum')
        if q['type']=='boolean' and set(distribution)!={'true','false'}: raise ValueError('invalid boolean labels')
    return answers

def validate_info(info):
    if info.get('status')!='ready' or info.get('checkpoint_sha256')!=PINNED_MODEL_SHA256:
        raise ValueError('unexpected or unready Jev model identity; explicit review required')

def record(request,result,info,purpose):
    path=ROOT/'state'/'jev-decisions.sqlite'; path.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(path,timeout=30)
    c.execute('CREATE TABLE IF NOT EXISTS decisions(sequence INTEGER PRIMARY KEY,previous_sha256 TEXT,sha256 TEXT UNIQUE,payload_json TEXT)')
    c.execute('BEGIN IMMEDIATE')
    row=c.execute('SELECT sequence,sha256 FROM decisions ORDER BY sequence DESC LIMIT 1').fetchone()
    payload={'sequence':row[0]+1 if row else 1,'previous_sha256':row[1] if row else None,'purpose':purpose,'completed_at':datetime.now(timezone.utc).isoformat(),'request_sha256':digest(request),'request':request,'response':result,'server_info':info,'semantics':'Real local model inference over exactly the supplied state and options. Conditional model distribution, not empirical law or calibrated SUNNY correctness. Host-authored candidate descriptions remain visible.'}
    sha=digest(payload)
    c.execute('INSERT INTO decisions VALUES(?,?,?,?)',(payload['sequence'],payload['previous_sha256'],sha,canonical(payload))); c.commit(); c.close()
    receipt={'status':'judged','sha256':sha,**payload}
    dest=ROOT/'state'/'jev-receipts'/f'{payload["sequence"]:06d}-{sha[:12]}.json'; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
    return receipt,str(dest)

def evaluate(request,purpose):
    validate_request(request)
    info=http('/api/info',timeout=6)
    validate_info(info)
    result=http('/api/evaluate',request)
    answers=validate_result(request,result)
    receipt,path=record(request,result,info,purpose)
    return {'status':'judged','receipt':path,'sha256':receipt['sha256'],'answers':answers,'model_info':info}

def verify_log():
    path=ROOT/'state'/'jev-decisions.sqlite'
    if not path.exists(): return {'status':'no_live_decisions','count':0}
    c=sqlite3.connect(path); previous=None; count=0
    for seq,prev,sha,payload in c.execute('SELECT * FROM decisions ORDER BY sequence'):
        obj=json.loads(payload)
        if seq!=count+1 or prev!=previous or sha!=digest(obj): raise ValueError('decision receipt chain failed verification')
        previous=sha; count+=1
    c.close(); return {'status':'intact','count':count,'head':previous}

def read_request(path):
    raw=sys.stdin.buffer.read().decode('utf-8-sig') if str(path)=='-' else path.read_text(encoding='utf-8-sig')
    return json.loads(raw)

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('command',choices=['health','info','decide','verify']); p.add_argument('--input',type=Path); p.add_argument('--purpose',default='Explicit SUNNY decision'); args=p.parse_args()
    try:
        if args.command in ('health','info'): out=http('/health' if args.command=='health' else '/api/info',timeout=6)
        elif args.command=='verify': out=verify_log()
        else:
            if not args.input: raise ValueError('--input request JSON is required')
            out=evaluate(read_request(args.input),args.purpose)
        print(json.dumps(out,ensure_ascii=True,indent=2)); return 0
    except Exception as e:
        print(json.dumps({'status':'unavailable' if isinstance(e,(urllib.error.URLError,TimeoutError,ConnectionError)) else 'invalid','error':str(e),'fallback_decision':None},ensure_ascii=True),file=sys.stderr); return 1

if __name__=='__main__': raise SystemExit(main())
