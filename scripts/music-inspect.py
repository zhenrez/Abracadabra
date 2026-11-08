import json,re,collections,sys,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'docs/evidence/music-discovery.json').read_text(encoding='utf8'))
c=sqlite3.connect('file:'+str(ROOT/'data/sunny.sqlite')+'?mode=ro',uri=True)
for row in d['user_messages']:
    if 'text' not in row:row['text']=c.execute('SELECT text FROM messages WHERE id=?',(row['id'],)).fetchone()[0]
def shape(v):
    if isinstance(v,dict): return {k:(len(x) if isinstance(x,(dict,list,str)) else x) for k,x in v.items()}
    if isinstance(v,list): return {'length':len(v),'first':v[:1]}
    return v
for r in d['native_sources']:
    if r['group'] not in ('generative_graph','structural_graph','scientific_alphabet'):continue
    obj=json.loads(Path(r['path']).read_text(encoding='utf-8-sig'))
    print('\nNATIVE',r['group'],json.dumps(shape(obj),ensure_ascii=True))
    for k,v in obj.items():
        print(k,json.dumps(shape(v),ensure_ascii=True)[:8500])
    if r['group']=='scientific_alphabet':print('FULL_ALPHABET',json.dumps(obj,ensure_ascii=True))
patterns=[r'chinese|huang|zhong|\bl[u\u00fc]\b|\bpipe',r'720|generational|tetrahed|sierpinski|4d|fourth.axis']
for pat in patterns:
    out=[];seen=set()
    for r in reversed(d['user_messages']):
        if not re.search(pat,r['text'],re.I):continue
        h=r['content_sha256']
        if h in seen:continue
        seen.add(h);out.append(r)
    dest=ROOT/'docs/evidence'/('music-chinese-user-turns.json' if 'chinese' in pat else 'music-geometry-user-turns.json')
    dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
    print('\nTURN_SCOPE',pat,len(out),'FULL_ROWS',str(dest))
    for r in out[:40]:
        txt=r['text'];m=re.search(pat,txt,re.I)
        print(json.dumps({'id':r['id'],'title':r['conversation_title'],'date':r['create_time'],'characters':len(txt),'excerpt':txt[max(0,m.start()-250):m.end()+700]},ensure_ascii=True))
