import json,re,collections,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'docs/evidence/music-discovery.json').read_text(encoding='utf8'))
c=sqlite3.connect('file:'+str(ROOT/'data/sunny.sqlite')+'?mode=ro',uri=True)
seen=set(); selected=[]
for r in d['documents']:
    if re.search(r'chinese|calibration|music.*(grammar|alphabet|biblical)|glossary|alignment|master.score|tree.of.life|mi.fa|sefer|founder|fludd|ab.ba',r['title'],re.I) and r['sha256'] not in seen:
        seen.add(r['sha256']);r['text']=r.get('text') or c.execute('SELECT text FROM documents WHERE id=?',(r['id'],)).fetchone()[0];selected.append(r)
(ROOT/'docs/evidence/music-focused-documents.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2),encoding='utf8')
for r in selected:print(json.dumps({'id':r['id'],'source_id':r['source_id'],'title':r['title'],'characters':len(r['text']),'path':r['path']},ensure_ascii=True))
for group in ('generative_graph','structural_graph'):
    s=next(r for r in d['native_sources'] if r['group']==group); obj=json.loads(Path(s['path']).read_text(encoding='utf-8-sig'))
    if group=='generative_graph':
        print('REGISTRY_FULL',json.dumps(obj['generative_registry'],ensure_ascii=True))
        print('GRAMMAR_FULL',json.dumps(obj['music_native_relation_grammar'],ensure_ascii=True))
        print('LIMITS',json.dumps(obj['limits'],ensure_ascii=True))
        print('CORE_LOCKS',json.dumps(obj['empirical_layer']['locks'],ensure_ascii=True))
        by_system=collections.Counter(v['System / tradition'] for v in obj['empirical_layer']['vertices']);print('SYSTEM_COUNTS',json.dumps(by_system,ensure_ascii=True))
        for v in obj['empirical_layer']['vertices']:
            if re.search(r'chinese|sanfen|huang|zhong|jing fang|zhu',json.dumps(v),re.I):print('CHINESE_VERTEX',json.dumps(v,ensure_ascii=True))
        for e in obj['empirical_layer']['empirical_hyperedges']:
            if re.search(r'chinese|sanfen|huang|zhong|jing fang|zhu',json.dumps(e),re.I):print('CHINESE_EDGE',json.dumps(e,ensure_ascii=True))
