"""Source-qualified upper/legion joins and recovered color/vortex constraints."""
from pathlib import Path
from datetime import datetime,timezone
from html.parser import HTMLParser
from collections import defaultdict,deque
from fractions import Fraction
import hashlib,itertools,json,math,re
ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/'state/research/upper-legion-color'
OUT=ROOT/'state/reconstruction/upper-legion-color-constraints.json'
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
class Text(HTMLParser):
    def __init__(self):super().__init__();self.data=[];self.markers=[]
    def handle_data(self,value):self.data.append(value)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='p' and attrs.get('id'):self.markers.append((attrs['id'],len(self.data)))
def decode_html(p):
    raw=(ROOT/p).read_bytes()
    try:text=raw.decode('utf8');encoding='utf8'
    except UnicodeDecodeError:text=raw.decode('cp1252');encoding='cp1252'
    parser=Text();parser.feed(text)
    flat=re.sub(r'\s+',' ',' '.join(parser.data)).strip()
    return flat,parser,encoding
def reachable(roots,relationships):
    adj=defaultdict(list)
    for r in relationships:adj[r['source']].append(r['target'])
    seen=set(roots);todo=deque(roots)
    while todo:
        for x in adj[todo.popleft()]:
            if x not in seen:seen.add(x);todo.append(x)
    return seen

def main():
    PACKET.mkdir(parents=True,exist_ok=True)
    graphPath='state/reconstruction/hierarchy-atlas-combined.json';graph=load(graphPath);beforeSha=sha(graphPath)
    byid={e['id']:e for e in graph['entities']};sources={s['id']:s for s in graph['sources']}
    sourcePaths=[graphPath,'state/reconstruction/master-score.json','state/jev-receipts/000064-fc22fe7cfcff.json',
        'data/raw/nested/963ffddeba5ffad501d3aa56d1adf2640f5190703e1bb970ab77abf466b5e1ec/Color_Carriers_FROZEN_v1.json',
        'data/raw/nested/963ffddeba5ffad501d3aa56d1adf2640f5190703e1bb970ab77abf466b5e1ec/Sound_Color_Residual_Rerun_v1.json',
        'data/raw/nested/be3005359fb120063ae8f1ddb52398bccc0a6de7923c42858247e101826e9300/Recovered_PreMusic_Color_Ledger_v1.json',
        'data/raw/nested/be3005359fb120063ae8f1ddb52398bccc0a6de7923c42858247e101826e9300/P0_SoundGeometry_Light_Color_Compression.json',
        'data/raw/archive/SUN_Universal_Archive/Library/HISTORICAL_MUSIC/ChatGPT-Mapping Primordials to Music-20261018-0133.md',
        'data/raw/archive/SUN_Universal_Archive/Library/SOL_SATURN_ROSETTAS/SOL_primordial_dependency_atlas_2026-10-18.md']
    witnesses=['uploaded-repository','de-laurence-1916','peterson-sloane3825'];expected=[2648,2645,2618]
    trees=[];vectors={}
    for wid,total in zip(witnesses,expected):
        chiefs=sorted([e for e in graph['entities'] if e['witnessId']==wid and e['unit']=='catalogue-chief'],key=lambda e:e['position']['sequence'])
        slots=[e for e in graph['entities'] if e['witnessId']==wid and e['unit']=='catalogue-attributed-legion-membership-slot']
        ids={e['id'] for e in chiefs+slots};relations=[r for r in graph['relationships'] if r['source'] in ids or r['target'] in ids]
        assert len(chiefs)==72 and len(slots)==total and sum(e['statedExtent']['value'] for e in chiefs)==total
        counts={}
        for c in chiefs:
            memberIds=[r['target'] for r in relations if r['source']==c['id'] and r['target'] in {s['id'] for s in slots}]
            assert len(set(memberIds))==c['statedExtent']['value']
            counts[c['id']]={'stated':c['statedExtent']['value'],'membershipOccurrenceIds':memberIds}
        vectors[wid]=chiefs
        trees.append({'witnessId':wid,'rootId':wid+':catalogue','chiefRecords':chiefs,'rankRecords':[e for e in graph['entities'] if e['witnessId']==wid and 'rank' in e['unit']],
            'chiefAndMembershipRelations':relations,'membershipAssignments':counts,'catalogueChiefCount':72,'membershipOccurrenceCount':total,
            'uniqueLegions':None,'uniquePersonnel':None,'sourceStatus':'Existing exact vector and identified occurrence histories reused; not new historical counting proof.'})
    differences=[]
    for a,b in itertools.combinations(witnesses,2):
        changed=[]
        for ca,cb in zip(vectors[a],vectors[b]):
            if ca['statedExtent']['value']!=cb['statedExtent']['value']:
                changed.append({'nativeSequence':ca['position']['sequence'],'leftChiefId':ca['id'],'rightChiefId':cb['id'],'leftName':ca['nativeName'],'rightName':cb['nativeName'],
                    'leftCount':ca['statedExtent']['value'],'rightCount':cb['statedExtent']['value'],'deltaRightMinusLeft':cb['statedExtent']['value']-ca['statedExtent']['value']})
        differences.append({'leftWitness':a,'rightWitness':b,'scope':'Same recovered catalogue-position comparison; names/roles are retained, not silently merged across witnesses.','changedEntries':changed})
    origins=[];chiefIds={e['id'] for v in vectors.values() for e in v}
    upperViews=[]
    for v in graph['views']:
        if v['id'].startswith(('origin:','upper:','archonic:','angelic:')):
            rels=[r for r in graph['relationships'] if v['id'] in r.get('viewIds',[])]
            memberIds=set(v['roots'])|{r[k] for r in rels for k in ['source','target']}
            upperViews.append({'id':v['id'],'roots':v['roots'],'entities':[byid[x] for x in sorted(memberIds) if x in byid],'relationships':rels,
                'rootReachableIds':sorted(reachable(v['roots'],rels)),
                'viewBoundary':'Retains every source comparison component and its endpoints. A displayed comparison is not necessarily reachable from the origin condition.'})
    for letter in ['A','B','C']:
        root='origin:'+letter+':condition';seen=reachable([root],graph['relationships'])
        assert not seen&chiefIds
        origins.append({'configuration':letter,'rootId':root,'allRelationReachableIds':sorted(seen),'reachableCatalogueChiefIds':[],
            'boundary':'No downstream catalogue prediction follows through a missing join in this admitted graph. This is not proof that no historical relationship exists.'})
    product=[{'configuration':o['configuration'],'witnessId':w,'pairingStatus':'independent axes; not an established correspondence','membershipOccurrenceCount':n}
        for o in origins for w,n in zip(witnesses,expected)]
    # Recover actual Goetic superiors and order claims, preserving relation type.
    additions=[];texts={};primarySources=[];directionClaims=[]
    for sid,wid in [('public:goetia_peterson_sloane3825','peterson-sloane3825'),('public:goetia_de_laurence_1916','de-laurence-1916')]:
        path=sources[sid]['path'];sourcePaths.append(path);text,parser,encoding=decode_html(path);texts[wid]=text
        textPath=PACKET/(wid+'-normalized-text.txt');textPath.write_text(text+'\n',encoding='utf8')
        primarySources.append({'id':sid,'path':path,'sha256':sha(path),'decoding':encoding,'derivedTextPath':str(textPath.relative_to(ROOT)).replace('\\','/'),
            'textTransformation':'HTML data nodes joined, whitespace collapsed; quoted offsets refer to this derived text, not raw manuscript or HTML byte offsets.'})
        def quote(needle,before=70,after=230):
            index=text.lower().index(needle.lower());start=max(0,index-before);end=min(len(text),index+len(needle)+after)
            return {'text':text[start:end],'startCodePoint':start,'endCodePointExclusive':end,'derivedTextPath':str(textPath.relative_to(ROOT)).replace('\\','/'),'sourceId':sid}
        additions.extend([
            {'witnessId':wid,'source':'goetic-upper:'+wid+':Lucifer','target':wid+':chief:9','type':'receives-obedience-from','sourceMeaning':'Paimon is obedient to Lucifer; not asserted begetting.','evidence':quote('Lucifer')},
            {'witnessId':wid,'source':'goetic-upper:'+wid+':Lucifer','target':wid+':chief:68','type':'precedes-in-created-order','sourceMeaning':'Belial was created next after Lucifer; source ordering is not a father-child statement.','evidence':quote('created next after Lucifer')},
            {'witnessId':wid,'source':'goetic-upper:'+wid+':four-quarter-rulers','target':wid+':catalogue','type':'jurisdiction-over-collective','sourceMeaning':'The catalogue is collectively under four quarter kings. Individual king-to-chief allocation and exact direction/name alignment remain open.','evidence':quote('These 72',0,420)},
        ])
        target=wid+':chief:32';index=text.lower().index('amaymon',text.lower().index('asmoday'))
        additions.append({'witnessId':wid,'source':'goetic-upper:'+wid+':Amaymon','target':target,'type':'source-reported-power-over','sourceMeaning':'Asmoday under Amaymon; not primordial parentage.','evidence':{'text':text[max(0,index-130):index+170],'sourceId':sid,'derivedTextPath':str(textPath.relative_to(ROOT)).replace('\\','/'),'startCodePoint':max(0,index-130),'endCodePointExclusive':index+170}})
        east=re.search(r'(?i)under Amaymon\s*,\s*king of (?:y e |the )East',text);assert east
        ev={'text':text[max(0,east.start()-110):east.end()+120],'sourceId':sid,'derivedTextPath':str(textPath.relative_to(ROOT)).replace('\\','/'),
            'startCodePoint':max(0,east.start()-110),'endCodePointExclusive':east.end()+120}
        additions.append({'witnessId':wid,'source':'goetic-upper:'+wid+':Amaymon','target':wid+':chief:70','type':'source-reported-power-over',
            'sourceMeaning':'Seere under Amaymon in the chief70 passage; do not transfer this direction across different witnesses.','evidence':ev})
        directionClaims.append({'entityId':'goetic-upper:'+wid+':Amaymon','direction':'East','context':'chief70-Seere main description','evidence':ev,
            'scope':'Source-qualified cardinal claim, not a universal quarter-name alignment. Peterson editorial notes report Amaymon South in the separate Folger witness.'})
    rulerNames={'peterson-sloane3825':['Amaymon','Corson','Ziminiar [*Zimimar]','Goap'],'de-laurence-1916':['Amaymon','Corson','Zimimay or Ziminair','Göap']}
    proposedEntities=[];proposedRelations=[]
    for source in primarySources:
        wid='peterson-sloane3825' if 'peterson' in source['id'] else 'de-laurence-1916'
        entities=[('Lucifer','Lucifer','source-named-superior'),('four-quarter-rulers','Four quarter rulers','quarter-ruler-collective')]
        entities += [(name if name=='Amaymon' else 'quarter-ruler:'+str(i),name,'quarter-ruler') for i,name in enumerate(rulerNames[wid])]
        for key,name,unit in entities:
            proposedEntities.append({'id':'goetic-upper:'+wid+':'+key,'nativeName':name,'aliases':[],'unit':unit,'tradition':'Solomonic Goetia','witnessId':wid,
                'position':{'generation':None,'sequence':None,'cyclicCoordinate':None,'orientation':None},'sourceRefs':[source['id']],
                'assertionLayer':'source-assertion','exceptions':['Witness-scoped reference; no cross-witness identity or primordial genealogy asserted.']})
        ev=next(a['evidence'] for a in additions if a['witnessId']==wid and a['type']=='jurisdiction-over-collective')
        for i,name in enumerate(rulerNames[wid]):
            proposedRelations.append({'source':'goetic-upper:'+wid+':four-quarter-rulers','target':'goetic-upper:'+wid+':'+(name if name=='Amaymon' else 'quarter-ruler:'+str(i)),
                'type':'has-source-member','witnessId':wid,'sourceRefs':[source['id']],'assertionLayer':'source-assertion','evidence':ev})
    proposedRelations += [dict(a,sourceRefs=[a['evidence']['sourceId']],assertionLayer='source-assertion') for a in additions]
    # Modern editorial note87 supplies complete lists, not a manuscript population census.
    pt=texts['peterson-sloane3825'];start=pt.index('87. To summarize:');end=pt.index('[111v',start)
    summary=pt[start:end];rankNames='Kings|Dukes|Marquises|Earls|Prelates/Princes|Knights|Presidents'
    rankSections=list(re.finditer(r'('+rankNames+r') \(([0-9.]+)\): (.*?)(?= (?:'+rankNames+r') \(|$)',summary));assert len(rankSections)==7
    chiefLookup={re.sub('[^a-z]','',n.lower()):c for c in vectors['peterson-sloane3825'] for n in [c['nativeName']]+c.get('aliases',[])}
    # The same primary transcription explicitly prints Furtur [*Furfur] in chief34.
    chiefLookup['furfur']=byid['peterson-sloane3825:chief:34']
    rankRows=[];memberships=defaultdict(list)
    for i,m in enumerate(rankSections):
        name,header,nativeList=m.groups();items=[v.strip() for v in nativeList.split(',')];ids=[]
        for item in items:
            primaryName=re.sub(r' \(.*?\)','',item).strip();key=re.sub('[^a-z]','',primaryName.lower());assert key in chiefLookup,(name,item)
            c=chiefLookup[key];ids.append(c['id']);memberships[c['id']].append(name)
        rid='peterson-sloane3825:rank:editorial87:'+str(i)
        ev={'sourceId':'public:goetia_peterson_sloane3825','derivedTextPath':'state/research/upper-legion-color/peterson-sloane3825-normalized-text.txt',
            'startCodePoint':start+m.start(),'endCodePointExclusive':start+m.end(),'text':pt[start+m.start():start+m.end()]}
        proposedEntities.append({'id':rid,'nativeName':name,'aliases':[],'unit':'modern-editorial-rank-membership-class','tradition':'Solomonic Goetia',
            'witnessId':'peterson-sloane3825','position':{'generation':None,'sequence':i+1,'cyclicCoordinate':None,'orientation':None},
            'sourceRefs':['public:goetia_peterson_sloane3825'],'assertionLayer':'source-assertion',
            'exceptions':['Modern editor note87; heading count is fractional allocation, not distinct chiefs or legions.']})
        for cid in ids:
            proposedRelations.append({'source':rid,'target':cid,'type':'has-editorially-listed-rank-member','witnessId':'peterson-sloane3825',
                'sourceRefs':['public:goetia_peterson_sloane3825'],'assertionLayer':'source-assertion','sourceRole':'modern editorial note87','evidence':ev})
        rankRows.append({'rankClassId':rid,'nativeName':name,'nativeList':nativeList,'chiefIds':ids,'distinctChiefs':len(set(ids)),
            'reportedEditorialAllocation':header,'evidence':ev})
    assert len(memberships)==72 and sum(map(len,memberships.values()))==80
    for row in rankRows:
        exact=sum((Fraction(1,len(memberships[c])) for c in row['chiefIds']),Fraction(0))
        assert exact==Fraction(row['reportedEditorialAllocation'])
        row['reproducedEditorialAllocationExact']=str(exact)
    rankCountControl={'sourceRole':'modern editorial note87 in Peterson digital transcription; not the manuscript body or a new mathematical ontology',
        'rankGroups':rankRows,'distinctChiefs':72,'rankMembershipOccurrences':80,'dualRankChiefIds':[k for k,v in memberships.items() if len(v)==2],
        'sumReportedAllocationsExact':str(sum((Fraction(r['reportedEditorialAllocation']) for r in rankRows),Fraction(0))),
        'allocationRule':'Each chief contributes 1/m to each of its m listed ranks; this exactly reproduces the editor headings. This is an observed editorial convention, not a required SUN law.',
        'boundary':'Do not conflate chief entities, rank memberships, fractional allocations, legion slots and personnel.'}
    allIds=set(byid)|{e['id'] for e in proposedEntities}
    assert len(proposedEntities)==19 and len(proposedRelations)==98
    assert all(r['source'] in allIds and r['target'] in allIds for r in proposedRelations)
    # Color carriers retain their native physical/perceptual units and original slot map.
    frozen=load(sourcePaths[3]);residual=load(sourcePaths[4]);ledger=load(sourcePaths[5]);stack=load(sourcePaths[6])
    assert len(frozen['fixed_additive_states'])==13 and frozen['fixed_additive_states'][0]==frozen['fixed_additive_states'][-1]
    colorStates=[]
    projections=frozen['carriers']['CIE1931_BOUNDARY_PROJECTION_ARCLENGTH']['projections']
    for index,label in enumerate(frozen['fixed_additive_states'][:12]):
        rgb={c:Fraction(0) for c in 'RGB'}
        for term in label.split('+'):
            match=re.fullmatch(r'(0\.5)?([RGB])',term);assert match,label;rgb[match[2]]=Fraction(1,2) if match[1] else Fraction(1)
        colorStates.append({'id':'color:fixed-linear-srgb:'+str(index),'nativeName':label,'unit':'frozen linear-light sRGB mixture state','nativeOrdinalZeroBased':index,
            'linearRGB':{c:str(value) for c,value in rgb.items()},'carrierPositions':{k:v['positions'][index] for k,v in frozen['carriers'].items() if 'positions' in v},
            'boundaryProjection':projections[index],'singleMonochromaticStimulus':None,'musicalAbsoluteHz':None,'globalGenerationalClass':None,
            'globalW72Phase':None,'sourceRole':'Recovered frozen experimental carrier; no objective note-is-color identity asserted.'})
    replay=[]
    for name,carrier in frozen['carriers'].items():
        if 'positions' not in carrier:continue
        diffs={note:value-carrier['positions'][residual['fixed_original_12_slot_indices'][note]] for note,value in residual['sound_positions'].items()}
        score=4*sum(abs(v) for v in diffs.values());reported=residual['results'][name]['score']
        assert math.isclose(score,reported,abs_tol=1e-12)
        replay.append({'carrier':name,'score':score,'reportedScore':reported,'sourceMetric':'(1/3)*sum12*abs(soundPosition-colorPosition[fixedSlot])','signedResiduals':diffs,'replayed':True})
    assert [x['index'] for x in projections if x['wavelength_nm'] is None]==[9,10,11]
    # The F/G symmetry is algebraically forced only in the original complementary-slot adapter.
    fg=Fraction(5,12)+Fraction(7,12);assert fg==1
    assert math.isclose(residual['sound_positions']['F']+residual['sound_positions']['G'],1,abs_tol=1e-15)
    history=(ROOT/sourcePaths[7]).read_text(encoding='utf8');lines=history.splitlines()
    sourceSpans=[]
    for start,end in [(146,171),(239,260),(710,730),(778,785)]:
        sourceSpans.append({'sourcePath':sourcePaths[7],'lineStartOneBased':start,'lineEndOneBased':end,'quote':'\n'.join(lines[start-1:end]),
            'sourceRole':'Historical conversational formulation; proposals/interpretations require their stated conditions and are not established geometry.'})
    score=load('state/reconstruction/master-score.json');workingLock=next(v for v in score['program']['views'] if v['id']=='sophia-working-lock')
    productionRegister=[]
    for event in sorted({e['id']:e for v in upperViews for e in v['entities'] if e['unit']=='production-event'}.values(),key=lambda e:e['id']):
        inputs=[r for r in graph['relationships'] if r['target']==event['id'] and 'input' in r['type']]
        outputs=[r for r in graph['relationships'] if r['source']==event['id'] and 'output' in r['type']]
        productionRegister.append({'event':event,'inputRelationships':inputs,'outputRelationships':outputs,
            'declaredOutputUnits':[{'id':r['target'],'unit':byid[r['target']]['unit'],'statedExtent':byid[r['target']].get('statedExtent')} for r in outputs],
            'globalClassOrAcousticGeneration':None,'boundary':'Source-qualified production/event structure is not a command rank, an independently sufficient parent, or an automatic musical class.'})
    sourcePaths.append('state/research/upper-legion-color/supermemory-retrieval.json')
    result={'schema':'sunny.upper-legion-color-constraints.v1','createdAt':datetime.now(timezone.utc).isoformat(),'jevReceipt':'state/jev-receipts/000064-fc22fe7cfcff.json',
        'strategy':'Source-defined class/generation construction and explicit finite bounds before unsupported common-address assignment.',
        'sourceBindings':[{'path':p,'sha256':sha(p)} for p in dict.fromkeys(sourcePaths)],'primaryTextPackets':primarySources,
        'catalogueTrees':trees,'witnessDifferences':differences,'upperViews':upperViews,'primordialConfigurations':origins,'independentOriginWitnessCombinations':product,
        'existingProposedJoins':graph.get('proposedExternalJoins',[]),'recoveredGoeticUpperAssertions':additions,
        'proposedGraphExtension':{'entities':proposedEntities,'relationships':proposedRelations,'allReferencesResolvable':True,'changesCanonicalGraph':False},
        'quarterRulerNames':rulerNames,
        'sourceQualifiedQuarterDirectionClaims':directionClaims,'petersonEditorialRankCountControl':rankCountControl,
        'quarterAllocationBoundary':'Collective authority is not an assignment of each chief to a particular quarter king. Goap/Gaap identity and cardinal alignment require an explicit source relation.',
        'attendanceCountControl':{'primaryPaimonCommandCount':200,'reportedAttendingHostCount':25,'unitDistinction':'standing command extent versus conditional attendance; do not add as disjoint populations',
            'conditionalSubsetModel':{'assumption':'If the attending25legions are a subset of the200command legions in this reading, with the same count unit','remainingCount':175},
            'unknowns':['Disjointness of actual legions','Whether every legion has one homogeneous angelic order','Unique personnel per legion','Exact manuscript variant scope']},
        'sourceNativeUpperBreadth':{'ValentinianI1':{'ogdoad':8,'decad':10,'dodecad':12,'sum':30,'unit':'aeon member positions in the source I1 construction'},
            'globalGrowthLaw':None,'boundary':'Native emanation groups and recurring pitch relations do not establish a universal class-growth law or fixed radii.'},
        'sourceQualifiedProductionRegister':productionRegister,
        'retainedWorkingPitchLock':workingLock,'color':{'nativeAlgebras':ledger['original_color_algebras'],'generatedHierarchy':ledger['generated_color_hierarchy'],
            'fixedStates':colorStates,'closureOccurrence':{'stateId':'color:fixed-linear-srgb:0','ordinal':12,'notAnotherDistinctState':True},'carrierDefinitions':frozen['carriers'],
            'soundAdapter':{'source':residual['sound_positions'],'fixedSlots':residual['fixed_original_12_slot_indices'],'status':'Declared just-intonation-to-color-position comparison, not physical identity'},
            'residualReplays':replay,'F_G_symmetry':{'colorSlotSumExact':str(fg),'soundLogPositionSum':1,'consequence':'Opposite signed residuals are forced by the chosen complementary slots, not independent confirmation.'},
            'monochromaticBoundary':{'fullClosed12WavelengthCycle':False,'nonspectralIndices':[9,10,11],'meaning':'Line-of-purples closure has no single monochromatic wavelength.'},
            'infraUltra':ledger['infra_ultra_status'],'laterPrimeEncoding':ledger['later_prime_reinterpretation']},
        'stack':{'sourceHierarchy':stack['revised_layer_model'],'hypothesisUnderTest':stack['hypothesis_under_test'],'sourceNoveltyLimits':stack['sun_specific_work_remaining']},
        'vortex':{'sourceSpans':sourceSpans,'sourceFrame':'class/generation, native identity, ordinal/cycle address, cumulative winding, domain and witness remain separate',
            'candidateTierState':'X_k=W72×D_k in the recovered proposal; not a derived complete geometry',
            'actualGlobalPositionsAssigned':0,'radiusByClass':None,'heightByClass':None,'classGrowthFactor':None,'dimensionalLiftLaw':None,
            'boundary':'No inferred color/syllable/catalogue count pads or selects a universal generation, radius, frequency or phase.'},
        'unresolvedJoins':[
            'PrimordialA/B/CtoexactsourceMonad/Pleroma variant','Upperaeon/archon/angelic graphs toGoetic quarter-ruler command hierarchy',
            'RemainingGoeticchieftouniquequarterking/cardinaldirectionbeyondAsmoday/SeerepoweredgesandSeereAmaymonEastcontext','GoapquarterrulertoGaapcataloguechief','Totalcommandcounttouniquelegions/personnel',
            'Source-native hierarchy rank toSUNNY class/generation','Color observation carrier toW72phase/cumulativevortexstate','Spectral/material/observer operation tofullmusic-native bridge',
        ],'guards':{'actualSupermemorySearchReceipt':'state/research/upper-legion-color/supermemory-retrieval.json','primarySourceReopened':'https://www.esotericarchives.com/solomon/goetia.htm','rawGraphUnchanged':sha(graphPath)==beforeSha},
        'notClaimed':{'completeCriticalEditionCollation':False,'completeUniversalHierarchy':False,'uniqueGlobalAddress':False,'originalSoundRecovered':False,'fullMissionComplete':False}}
    assert len(product)==9 and all(x['replayed'] for x in replay) and sha(graphPath)==beforeSha
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (PACKET/'validation.json').write_text(json.dumps({'status':'passed','exit_code':0,'catalogueVectorsReused':3,'existingMembershipOccurrencesAttributed':7911,'independentOriginWitnessCases':9,
        'recoveredGoeticUpperAssertions':len(additions),'resolvableProposedUpperEntities':len(proposedEntities),'resolvableProposedUpperRelations':len(proposedRelations),
        'petersonRankDistinctChiefs':72,'petersonRankMembershipOccurrences':80,'petersonEditorialAllocationExact':'72',
        'colorStates':12,'colorCarrierReplays':len(replay),'nonspectralIndices':[9,10,11],'sourceGraphUnchanged':True},indent=2)+'\n',encoding='utf8')
    print((PACKET/'validation.json').read_text(encoding='utf8'))
if __name__=='__main__':main()
