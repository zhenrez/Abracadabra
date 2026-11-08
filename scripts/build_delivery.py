"""Build the connected offline SUNNY visual dataset from preserved project artifacts."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, shutil, base64, gzip

ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT/'web/delivery-2026-11-07'
STATE=ROOT/'state/delivery-2026-11-07'
UNITS=['coverage','native-derivations','orientation-predictions','tol-history-math',
       'native-execution','generational-constraints','algebraic-extension','derived-laws',
       'master-score','contextual-alignment','symbol-sound-constraints','score-anchor-constraints','phonological-context-constraints','phonological-history-constraints','reading-operations',
       'indian-hierarchy','western-expanded','chinese-expanded','native-class-constructors','biblical-genealogies','upper-legion-color-constraints']

def digest(raw): return hashlib.sha256(raw).hexdigest()

def build():
    WEB.mkdir(parents=True,exist_ok=True);STATE.mkdir(parents=True,exist_ok=True)
    inputs=[]
    def load(relative,required=True):
        path=ROOT/relative
        if not path.is_file():
            if required: raise FileNotFoundError(relative)
            return None
        raw=path.read_bytes();inputs.append({'path':relative,'bytes':len(raw),'sha256':digest(raw)})
        return json.loads(raw.decode('utf-8-sig'))
    mission=load('state/mission.json')
    graph=load('state/reconstruction/hierarchy-atlas-combined.json')
    modules={name:load('state/reconstruction/'+name+'.json') for name in UNITS}
    requirements=load('state/delivery-2026-11-07/acceptance.json',False)
    mathematics=load('state/delivery-2026-11-07/mathematics/frontier.json',False)
    receipt=load('state/jev-receipts/000057-95bc223acd84.json')
    jev_history=[{'path':'state/jev-receipts/000057-95bc223acd84.json','record':receipt}]
    for path in ['state/jev-receipts/000058-bbb3ab44bbf5.json','state/jev-receipts/000059-6581ee8c1ffa.json','state/jev-receipts/000060-a1b30f75db7d.json','state/jev-receipts/000061-54b57b45fbcd.json','state/jev-receipts/000062-5fcc72f3ccd7.json','state/jev-receipts/000063-298ff24c136a.json']:
        item=load(path,False)
        if item is not None:jev_history.append({'path':path,'record':item})
    model=load('state/reconstruction/model.json')
    latest_jev=load('state/jev-receipts/000064-fc22fe7cfcff.json')
    jev_history.append({'path':'state/jev-receipts/000064-fc22fe7cfcff.json','record':latest_jev})
    # Receipt65 belongs to an adjacent publication task; its chain occurrence is
    # retained locally but is not represented as SUNNY direction.
    receipt=load('state/jev-receipts/000066-af96bb712929.json')
    jev_history.append({'path':'state/jev-receipts/000066-af96bb712929.json','record':receipt})
    entities=graph['entities'];ids={e['id'] for e in entities}
    assert len(ids)==len(entities),'Duplicate entity IDs'
    dangling=[r['id'] for r in graph['relationships'] if r['source'] not in ids or r['target'] not in ids]
    assert not dangling,('Dangling relationship endpoints',dangling[:10])
    assert len(mission['goals'])==16
    assert len(model['mandated_output_status'])==8
    artifacts=[{'id':entry['output'],'status':entry['status'],'units':entry['units'],
                'remaining':entry['remaining']} for entry in model['mandated_output_status']]
    audio=load('state/research/reactivation/matched-audio/measurements.json',False)
    anchors=load('state/delivery-2026-11-07/mathematics/score-anchors.json',False)
    census={}
    for name in ['dated-witnesses','reading-tradition-prior-art','alef-operational-hypotheses',
                 'secunda-transcription-control','secunda-ps46-control','secunda-internal-vowel-controls',
                 'wlc-dotted-alef-census','six-alef-loci','rounded-qames-tree-control','qames-topology-discrimination']:
        item=load('docs/reconstruction/symbol-sound-census/'+name+'.json',False)
        if item is not None:census[name]=item
    for name,path in [('english-word-a-control','docs/evidence/english-a-pronunciation-control.json'),
                      ('latin-vindolanda-control','docs/evidence/latin-vindolanda-291.json')]:
        item=load(path,False)
        if item is not None:census[name]=item
    assets=[]
    # Referenced originals remain byte-for-byte copies. Content deduplication retains
    # every filename/path occurrence; displaying an image is not semantic processing.
    figures=[];by_hash={};unavailable_figures=[]
    supplied=[f'musi{i}' for i in range(1,21)]+['pythagh1','conglmusi2',
        'music_chart2.jpg','music_chart3 (1).jpg','CONTACT_SHEET_24_UNIQUE.png',
        'CONTACT_SHEET_24_UNIQUE (1).png','CONTACT_SHEET_24_UNIQUE (2).png',
        'Analysis output 9m.png']+[f'Analysis output {i}.png' for i in range(8,0,-1)]
    figure_folder=WEB/'assets/figures';figure_folder.mkdir(parents=True,exist_ok=True)
    for name in supplied:
        path=Path('C:/Users/Brend/Downloads')/name
        if not path.is_file():unavailable_figures.append({'name':name,'status':'not available at supplied path; not nonexistent'});continue
        raw=path.read_bytes();sha=digest(raw)
        extension='.png' if raw.startswith(b'\x89PNG\r\n\x1a\n') else '.jpg' if raw.startswith(b'\xff\xd8\xff') else None
        if extension is None:unavailable_figures.append({'name':name,'status':'unsupported image encoding; original untouched'});continue
        occurrence={'name':name,'path':str(path).replace('\\','/'),'bytes':len(raw),'sha256':sha}
        inputs.append({**occurrence,'sourceRole':'User-supplied image; content is source data, not active instructions'})
        if sha not in by_hash:
            target=figure_folder/(sha+extension);target.write_bytes(raw)
            figure={'id':'provided-image:'+sha,'url':'assets/figures/'+target.name,'sha256':sha,
                'occurrences':[],'processingStatus':'Original bytes inventoried and available; no new semantic reconstruction claimed by copying/display',
                'claimBoundary':'Received diagrams and annotations preserve claims to examine; their contents are not adopted as mathematical or historical proof.'}
            by_hash[sha]=figure;figures.append(figure)
        by_hash[sha]['occurrences'].append(occurrence)
    if audio:
        folder=WEB/'assets';folder.mkdir(exist_ok=True)
        for track in audio['tracks']:
            for item in track['derived']:
                if not item['path'].endswith('.opening15s.wav'): continue
                source=ROOT/item['path'];target=folder/source.name
                assert digest(source.read_bytes())==item['sha256']
                shutil.copyfile(source,target)
                assets.append({'id':track['id'],'condition':track['condition'],
                    'url':'assets/'+target.name,'sha256':item['sha256'],'scope':'First15seconds; token alignment unresolved'})
        for filename in ['opening-comparison.png']:
            source=ROOT/'state/research/reactivation/matched-audio/derived'/filename
            if source.is_file():shutil.copyfile(source,folder/filename)
    data={'schema':'sunny.connected-delivery.v1','version':'2026-11-07',
        'generatedAt':datetime.now(timezone.utc).isoformat(),'timezone':'America/Phoenix',
        'title':'SUNNY • Symphonia Universalis Numinous Nominal YARN',
        'goals':mission['goals'],'requirements':requirements or {'status':'acceptance-matrix-pending','items':[]},
        'registers':artifacts,'graph':graph,'modules':modules,'mathematics':mathematics,
        'audio':audio,'assets':assets,'figures':figures,'unavailableFigures':unavailable_figures,
        'symbolCensus':census,'scoreAnchors':anchors,'geometry':{
            'status':'candidate-constructions; exact SUNNY realization not established',
            'premises':mission['working_premises'],
            'rotationRule':'Two rotations before lift is a user working premise; the display parameters do not establish growth or physical dynamics.',
            'cliffordTorus':{'formula':'(r cos u,r sin u,s cos v,s sin v) in R4','intrinsicDimension':2,'ambientDimension':4,
                'boundary':'A candidate embedding, not a proved identification with the intended complete geometry.'},
            'sierpinski':{'construction':'Four half-scale tetrahedra per refinement; displayed finite depth approximates the declared limit.',
                'limitBoundary':'A finite rendering does not demonstrate the full at-infinitum model.'}},
        'jev':{'provider':'local','model':receipt['server_info'].get('model'),
            'checkpointSha256':receipt['server_info'].get('checkpoint_sha256'),
            'receipt':'state/jev-receipts/000066-af96bb712929.json','answers':receipt['response'],
            'request':receipt['request'],'history':jev_history,'billing':'No hosted call for these receipts; cloud-account attribution remains unverified.',
            'automaticObservers':'Not task routing or completion certification.'},
        'continuity':{'path':'CONTINUE.md','goalStatus':'active','fullMissionComplete':False},
        'evidenceStatus':{'sourceFidelity':'See current hash-bound verification; not historical truth.',
            'globalOrientationSelected':False,'originalSoundSystemRecovered':False,'blindPredictionEstablished':False,
            'entityCountBoundary':'Graph records include witness/context entities and anonymous membership slots, not a global population of unique beings.'},
        'manifest':{'inputs':inputs,'recordCounts':{'goals':len(mission['goals']),'registers':len(artifacts),
            'graphRecords':len(entities),'relationships':len(graph['relationships']),'views':len(graph['views']),
            'masterScoreViews':len(modules['master-score']['program']['views']),
            'providedImageOccurrences':sum(len(f['occurrences']) for f in figures),'distinctProvidedImages':len(figures)},
            'projection':'All supplied graph entities/relationships and all declared execution modules retained. Full source bytes remain at their recorded paths.'}}
    raw=json.dumps(data,ensure_ascii=False,separators=(',',':')).encode('utf8')
    (WEB/'data.json').write_bytes(raw)
    # JSON.parse avoids treating untrusted source keys as JavaScript object-literal semantics.
    # Identical records share graph objects after hydration. The standalone JSON keeps
    # the complete original module shapes for inspection and machine replay.
    compact={**data,'modules':{name:dict(unit) for name,unit in modules.items()}}
    graph_maps={kind:{row['id']:row for row in graph[kind]} for kind in ['entities','relationships','views']}
    reference_count=0
    for name,unit in compact['modules'].items():
        for kind,records in graph_maps.items():
            if not isinstance(unit.get(kind),list): continue
            projected=[]
            for row in unit[kind]:
                if isinstance(row,dict) and row.get('id') in records and row==records[row['id']]:
                    projected.append({'__sunny_graph_ref__':[kind,row['id']]});reference_count+=1
                else: projected.append(row)
            unit[kind]=projected
    packed=gzip.compress(json.dumps(compact,ensure_ascii=False,separators=(',',':')).encode('utf8'),compresslevel=6,mtime=0)
    encoded=base64.b64encode(packed).decode('ascii')
    aliases={'SUNNY_INDIAN_HIERARCHY':'indian-hierarchy','SUNNY_WESTERN_EXPANDED':'western-expanded','SUNNY_CHINESE_EXPANDED':'chinese-expanded','SUNNY_NATIVE_CLASSES':'native-class-constructors','SUNNY_BIBLICAL_GENEALOGIES':'biblical-genealogies','SUNNY_UPPER_COLOR':'upper-legion-color-constraints'}
    global_js=''.join('window.'+k+'=window.SUNNY_DELIVERY.modules['+json.dumps(v)+'];\n' for k,v in aliases.items())
    loader='''window.SUNNY_DATA_READY=(async()=>{
 const compressed=Uint8Array.from(atob("PACKED"),c=>c.charCodeAt(0));
 const stream=new Blob([compressed]).stream().pipeThrough(new DecompressionStream('gzip'));
 const data=JSON.parse(await new Response(stream).text());
 const maps=Object.fromEntries(['entities','relationships','views'].map(kind=>[kind,new Map(data.graph[kind].map(row=>[row.id,row]))]));
 for(const unit of Object.values(data.modules))for(const kind of Object.keys(maps))if(Array.isArray(unit[kind]))unit[kind]=unit[kind].map(row=>{
  const ref=row?.__sunny_graph_ref__;if(!ref)return row;
  const original=maps[ref[0]]?.get(ref[1]);if(!original)throw new Error('Unresolved SUNNY graph reference '+ref[1]);return original;
 });
 window.SUNNY_DELIVERY=data;
 GLOBALS
 return data;
})();
'''.replace('PACKED',encoded).replace('GLOBALS',global_js)
    (WEB/'data.js').write_text(loader,encoding='utf8')
    manifest={'schema':'sunny.delivery-build.v1','generatedAt':data['generatedAt'],'inputs':inputs,
        'outputs':[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'bytes':p.stat().st_size,
                    'sha256':digest(p.read_bytes())} for p in [WEB/'data.json',WEB/'data.js']],
        'counts':data['manifest']['recordCounts'],'offlineEncoding':{'method':'gzip-base64; exact graph-record reference hydration','compressedBytes':len(packed),'sharedGraphRecords':reference_count,'fullJsonBytes':len(raw)},'fullMissionComplete':False}
    (STATE/'build.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'built','exit_code':0,'datasetBytes':len(raw),**manifest['counts']}))
    return data

if __name__=='__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    build()
