"""Source-defined Chinese musical expansions; no invented census/register padding."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from html.parser import HTMLParser
from fractions import Fraction
from collections import Counter,defaultdict
from urllib.request import Request,urlopen
from urllib.parse import quote
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/'state/research/chinese-expanded'
SPECS={
 'houhan91':('https://zh.wikisource.org/wiki/後漢書/卷91','html','Public-domain primary text, modern Wikisource transcription; annotations retained separately.'),
 'suishu16':('https://zh.wikisource.org/wiki/隋書/卷16','html','Public-domain primary treatise, modern Wikisource transcription; historical critics remain source claims.'),
 'hkco-bowed':('https://www.hkco.org/en/Instrument-Rd/Chinese-Instruments/Bowed-String-Instruments.html','html','Current first-party orchestra instrument-family description.'),
 'hkco-plucked':('https://www.hkco.org/en/Instrument-Rd/Chinese-Instruments/Plucked-String-Instruments.html','html','Current first-party orchestra instrument-family description.'),
 'hkco-wind':('https://www.hkco.org/en/Instrument-Rd/Chinese-Instruments/Wind-Instruments.html','html','Current first-party orchestra instrument-family description.'),
 'hkco-percussion':('https://www.hkco.org/en/Instrument-Rd/Chinese-Instruments/Percussion-Instruments.html','html','Current first-party orchestra instrument-family description.'),
 'hkco-range2025':('https://dir.hkco.org/uploads/docs/682542db204771.pdf','pdf','First-party 2025 orchestra instrumentation/range chart; performed notes are not instrument types or players.')}
def digest(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,s):self.parts.append(s)
def norm(raw):
 p=Text();p.feed(raw.decode('utf-8-sig'));return re.sub(r'\s+',' ',' '.join(p.parts)).strip()
def acquire_one(item):
 name,(url,ext,role)=item;path=PACKET/(name+'.'+ext)
 if not path.exists():
  try:
   req=Request(quote(url,safe=':/?=&'),headers={'User-Agent':'SUNNY-source-research/1.0'})
   with urlopen(req,timeout=30) as response:raw=response.read()
   path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
  except Exception as e:return {'id':'chinese-expanded:'+name,'url':url,'status':'unavailable','error':str(e),'sourceRole':role}
 raw=path.read_bytes()
 if ext=='html':(PACKET/(name+'.normalized.txt')).write_text(norm(raw)+'\n',encoding='utf8')
 return {'id':'chinese-expanded:'+name,'url':url,'status':'retrieved','path':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':digest(raw),'bytes':len(raw),'sourceRole':role}
def acquire():
 PACKET.mkdir(parents=True,exist_ok=True)
 rows=list(ThreadPoolExecutor(max_workers=5).map(acquire_one,SPECS.items()));write(PACKET/'source-register.json',{'sources':rows});return rows
def cnint(s):
 digits=dict(zip('零一二三四五六七八九',range(10)));units={'十':10,'百':100,'千':1000};total=section=last=0
 for c in s:
  if c in digits:last=digits[c]
  elif c in units:section+=(last or 1)*units[c];last=0
  elif c=='萬':total+=(section+last)*10000;section=last=0
  else:raise ValueError(s)
 return total+section+last
def main():
 sources=load('state/research/chinese-expanded/source-register.json')['sources'];assert all(s['status']=='retrieved' for s in sources)
 for s in sources:assert digest((ROOT/s['path']).read_bytes())==s['sha256']
 graph=load('state/reconstruction/hierarchy-atlas-combined.json');oldHash=digest((ROOT/'state/reconstruction/hierarchy-atlas-combined.json').read_bytes())
 baseline=PACKET/'baseline-chinese-graph.json'
 if not baseline.exists():
  old=[e for e in graph['entities'] if e.get('tradition')=='Chinese' and not e['id'].startswith('chinese-expanded:')];oldIds={e['id'] for e in old};assert len(old)==162
  write(baseline,{'sourceGraphSha256':oldHash,'entities':old,'relationships':[r for r in graph['relationships'] if r['source'] in oldIds and r['target'] in oldIds],
   'sources':[s for s in graph['sources'] if s['id'] in {sid for e in old for sid in e['sourceRefs']}],'views':[v for v in graph['views'] if v['id']=='music:chinese']})
 base=json.loads(baseline.read_text(encoding='utf8'));old=base['entities'];oldIds={e['id'] for e in old};assert len(old)==162
 currentById={e['id']:e for e in graph['entities']};assert all(currentById[e['id']]==e for e in old)
 entities=list(old);relations=list(base['relationships']);views=list(base['views'])
 def ent(key,name,unit,witness,source,**extra):
  row={'id':'chinese-expanded:'+key,'nativeName':name,'aliases':[],'unit':unit,'tradition':'Chinese','witnessId':witness,
   'position':{'generation':None,'sequence':None,'cyclicCoordinate':None,'orientation':None},'sourceRefs':[source],
   'assertionLayer':'source-assertion','exceptions':[],**extra};entities.append(row);return row['id']
 def edge(a,b,kind,source,**extra):
  row={'id':'chinese-expanded:relation:'+str(len(relations)),'source':a,'target':b,'type':kind,'sourceRefs':[source],
       'assertionLayer':'source-assertion','viewIds':[],**extra};relations.append(row);return row
 def ev(name,start,end):
  t=(PACKET/(name+'.normalized.txt')).read_text(encoding='utf8');return {'sourceId':'chinese-expanded:'+name,'normalizedTextPath':'state/research/chinese-expanded/'+name+'.normalized.txt',
   'startCodePoint':start,'endCodePointExclusive':end,'text':t[start:end]}
 def phrase(name,needle,length=240):
  t=(PACKET/(name+'.normalized.txt')).read_text(encoding='utf8');i=t.index(needle);return ev(name,i,min(len(t),i+length))
 # The actual sixty-standard source gives names, integer values, directions and finite exceptions.
 t=(PACKET/'houhan91.normalized.txt').read_text(encoding='utf8');sid='chinese-expanded:houhan91';witness='HouHanShu91-JingFang'
 root=ent('houhan:root','後漢書志第一：京房六十律','native-text-musical-system',witness,sid)
 matches=list(re.finditer(r'([\u4e00-\u9fff]{2,3})，([一二三四五六七八九十百千萬零]+)。([上下])生([^。]*)。',t));assert len(matches)==60
 rows=[];names=[m[1] for m in matches]
 alt='|'.join(names);triplePattern=re.compile('('+alt+')為宮，('+alt+')商，?('+alt+')徵')
 for i,m in enumerate(matches):
  stop=matches[i+1].start() if i<59 else t.index('截管為律',m.end());span=ev('houhan91',m.start(),stop);local=t[m.start():stop]
  day=re.search(r'([一二三四五六七八九十]+)日',local);assert day
  rows.append({'nativeName':m[1],'sourceInteger':cnint(m[2]),'sourceIntegerSpelling':m[2],'generationDirection':m[3],'generatedName':m[4] or None,
   'dayDurationAsPrinted':cnint(day[1]),'sourceEntry':span,'lengthAndZhunText':local.split('日',1)[1].strip(),'triple':triplePattern.search(local)})
 lookup={r['nativeName']:r for r in rows};assert len(lookup)==60
 chain=[];current='黃鐘';ideal=Fraction(177147)
 while current:
  assert current not in [x['name'] for x in chain];r=lookup[current];chain.append({'name':current,'exactIdealInteger':str(ideal),'sourceInteger':r['sourceInteger'],
   'sourceMinusIdeal':str(Fraction(r['sourceInteger'])-ideal)});r['generationIndex']=len(chain)-1;r['exactIdealInteger']=ideal
  if r['generatedName']:ideal*=Fraction(2,3) if r['generationDirection']=='下' else Fraction(4,3)
  current=r['generatedName']
 assert len(chain)==60 and chain[-1]['name']=='南事'
 for r in rows:
  r['id']=ent('houhan:standard:'+r['nativeName'],r['nativeName'],'JingFang-witness-named-lu-standard',witness,sid,
   sourceInteger=r['sourceInteger'],sourceIntegerSpelling=r['sourceIntegerSpelling'],sourceLengthCunRatio=str(Fraction(r['sourceInteger'],19683)),
   exactIdealLengthCunRatio=str(r['exactIdealInteger']/19683),idealFrequencyRelativeHuangzhong=str(Fraction(177147)/r['exactIdealInteger']),
   physicalFrequencyHz=None,sourceEntry=r['sourceEntry'],lengthAndZhunText=r['lengthAndZhunText'],dayDurationAsPrinted=r['dayDurationAsPrinted'],
   nativeCoordinates={'sourceLengthOrderIndex':names.index(r['nativeName']),'generationOrderIndex':r['generationIndex']},
   exceptions=['Exact ideal string/pipe inverse-length ratios are conditional on common wave speed and ideal acoustic boundary; source integers/units remain separately preserved.'])
  edge(root,r['id'],'has-witness-lu-standard',sid)
 for r in rows:
  if r['generatedName']:
   factor=Fraction(2,3) if r['generationDirection']=='下' else Fraction(4,3);target=lookup[r['generatedName']]
   edge(r['id'],target['id'],'source-generates-next-lu',sid,lengthMultiplierExact=str(factor),sourceIntegerResidual=str(Fraction(target['sourceInteger'])-factor*r['sourceInteger']),evidence=r['sourceEntry'])
 contexts=0;roleCount=0;terminal=[]
 for r in rows:
  if r['triple']:
   tri=r.pop('triple');context=ent('houhan:gong-context:'+r['nativeName'],r['nativeName']+'為宮','JingFang-explicit-gong-shang-zhi-context',witness,sid,evidence=r['sourceEntry'])
   edge(r['id'],context,'serves-as-gong-in-source-context',sid);contexts+=1
   for role,name in zip(['宮','商','徵'],tri.groups()):
    occ=ent('houhan:role:'+r['nativeName']+':'+role,name+' '+role,'source-explicit-context-tone-membership',witness,sid,nativeRole=role,evidence=r['sourceEntry'])
    edge(context,occ,'has-source-role-member',sid);edge(occ,lookup[name]['id'],'uses-witness-lu-standard',sid);roleCount+=1
  else:
   r.pop('triple');assert '不為宮' in r['sourceEntry']['text'];terminal.append({'standardId':r['id'],'text':r['sourceEntry'],'notGong':True})
 assert contexts==58 and roleCount==174 and {lookup[n]['id'] for n in ['分烏','南事']}=={r['standardId'] for r in terminal}
 views.append({'id':'chinese-expanded:jingfang60','label':'Jing Fang：60lü /58explicitcontexts /174roleoccurrences','roots':[root],'witnessIds':[witness],
  'coverage':{'wholeSystemComplete':False,'completeEnumeratedStandardsForThisTranscription':True,'countedUnit':'named-lu-standard; context tone membership counted separately'}})
 # Lam's explicit mode restriction in section4 is additional to the already verified sixty note contexts.
 ls=next(s for s in graph['sources'] if s['id']=='music:source:lam2024');lamText=norm((ROOT/ls['path']).read_bytes())
 needle='To narrow the analytical object to modes only';at=lamText.index(needle);modeEvidence={'sourceId':ls['id'],'normalizedTextChars':[at,at+510],'text':lamText[at:at+510]}
 lamRoot=ent('lam:modes','Lam2024：六十調 as modal-final contexts','source-qualified-pentatonic-mode-family','Lam2024',ls['id'],evidence=modeEvidence,
  exceptions=['C fixed to huangzhong and chromatic pc indices are the paper convention, not established ancient Hz or twelve-tone equal-tempered tuning.'])
 toneOffsets=[0,2,4,7,9];roles=['宮','商','角','徵','羽']
 for k in range(12):
  for p in range(5):
   mode=ent('lam:mode:'+str(k)+':'+str(p),str(k)+' set '+roles[p]+' final','Lam-source-defined-mode-final-context','Lam2024',ls['id'],
    pcPent=k,posFinal=p,pcFinal=(k+toneOffsets[p])%12,assertionLayer='source-rule-derived',evidence=modeEvidence)
   edge(lamRoot,mode,'has-source-defined-mode-final-context',ls['id'],assertionLayer='source-rule-derived')
   edge(mode,'music:chinese:lam:set:'+str(k),'uses-source-pentatonic-set',ls['id'],assertionLayer='source-rule-derived')
   for j in range(5):
    pos=(p+j)%5;occ=ent('lam:mode-tone:'+str(k)+':'+str(p)+':'+str(j),roles[pos]+' in mode('+str(k)+','+str(p)+')','mode-qualified-tone-membership-occurrence','Lam2024',ls['id'],
     abstractPitchClass=(k+toneOffsets[pos])%12,nativeTonePosition=pos,modeRelativePosition=j,physicalFrequencyHz=None,absoluteRegister=None,
     assertionLayer='source-rule-derived',exceptions=['Five memberships per source-defined mode; repeated pitch identities across modes are not new physical notes.'])
    edge(mode,occ,'has-native-mode-tone-occurrence',ls['id'],assertionLayer='source-rule-derived')
    edge(occ,'music:chinese:lam:context:'+str(k)+':'+str(pos),'projects-to-existing-solmization-context',ls['id'],assertionLayer='source-rule-derived')
 views.append({'id':'chinese-expanded:lam60modes','label':'Lam2024：60modalfinals /300tone-memberships','roots':[lamRoot],'witnessIds':['Lam2024'],'coverage':{'wholeSystemComplete':False,'modeContexts':60,'toneMemberships':300}})
 # First-party modern instrument families remain separate from ZhouLi eight materials.
 hkroot=ent('hkco:root','Hong Kong Chinese Orchestra：source-defined families','modern-orchestra-instrument-family-collection','HKCO2025-2026','chinese-expanded:hkco-range2025')
 families={
  'bowed':(['erhu','gaohu','zhonghu','gehu','bass gehu'],['banhu','jinghu','yehu','leiqin']),
  'plucked':(['yangqin','liuqin','pipa','zhongruan','daruan','sanxian','zheng'],['guqin','konghou','Western harp']),
  'wind':(['bangdi','qudi','dadi','xindi','soprano keyed sheng','alto paisheng','bass baosheng','alto guan','bass guan','suona'],['dongxiao','bawu','xun','koudi','conch']),
  'percussion':(['large gongs','small gongs','cloud gongs','cymbals','bells','chimes','clappers','bamboo clappers','bangzi','temple block','dagu','paigu','hand drums'],
    ['timpani','xylophone','chimes','glockenspiel','vibraphone','bass drum','snare drum','cymbals'])}
 instrumentCount=0
 for family,(regular,additional) in families.items():
  sid='chinese-expanded:hkco-'+family;nt=(PACKET/('hkco-'+family+'.normalized.txt')).read_text(encoding='utf8');n=nt.index('The configuration of the Hong Kong Chinese Orchestra') if family in ['bowed','plucked'] else nt.index('In the Hong Kong Chinese Orchestra') if family=='wind' else nt.index("The Hong Kong Chinese Orchestra's percussion section")
  evidence=ev('hkco-'+family,n,min(len(nt),n+1500));parent=ent('hkco:family:'+family,family,'HKCO-playing-technique-family','HKCO2025-2026',sid,evidence=evidence)
  edge(hkroot,parent,'has-modern-orchestra-family',sid)
  for group,labels in [('standard',regular),('repertory-dependent' if family!='percussion' else 'Western-percussion-examples',additional)]:
   for j,label in enumerate(labels):
    iid=ent('hkco:instrument:'+family+':'+group+':'+str(j),label,'first-party-instrument-name-occurrence','HKCO2025-2026',sid,
     sourceMembership=group,evidence=evidence,completeHistoricalInstrumentInventory=False,individualPlayerCount=None,physicalInstrumentCount=None,
     exceptions=['Witness-named kind/reference, not a physical player or complete tradition-wide inventory; percussion bilingual labels can overlap.'])
    edge(parent,iid,'lists-instrument-kind-or-repertory-reference',sid);instrumentCount+=1
 # The chart explicitly defines26bells×2strikepositions and37semitone-gongs.
 for kind,label,count in [('bianzhong','編鐘',26),('yunluo','雲鑼',37)]:
  sid='chinese-expanded:hkco-range2025';parent=ent('hkco:chart:'+kind,label,'HKCO-source-bounded-instrument-set','HKCO2025',sid,
   evidence={'sourceId':sid,'pageZeroBased':0,'sourceText':'26 bells, each with main and side note;52 notes, lowest C# and highest E absent' if kind=='bianzhong' else '37 pieces in semitone'},statedExtent={'value':count,'unit':'physical-bell' if kind=='bianzhong' else 'physical-gong'})
  edge(hkroot,parent,'has-chart-defined-instrument-set',sid)
  for i in range(count):
   item=ent('hkco:'+kind+':member:'+str(i),label+' member '+str(i+1),'source-counted-unnamed-bell' if kind=='bianzhong' else 'source-counted-unnamed-gong','HKCO2025',sid,
    sourceProvidedIndividualName=False,physicalPitchHz=None,pitchSpelling=None)
   edge(parent,item,'has-counted-set-member',sid)
   for strike in (['main','side'] if kind=='bianzhong' else ['single-pitch']):
    note=ent('hkco:'+kind+':sound:'+str(i)+':'+strike,label+' '+str(i+1)+' '+strike,'source-bounded-instrument-sound-address','HKCO2025',sid,
     strikePosition=strike,physicalPitchHz=None,pitchSpelling=None,sourceProvidedIndividualName=False)
    edge(item,note,'has-source-defined-sound-address',sid)
 # Source endpoints are transcribed from the retained PDF glyph/staff coordinates.
 # Chromatic intermediate addresses are derived only where the chart licenses semitones.
 rangePath='state/research/chinese-expanded/hkco-source-ranges.json';rangeRaw=(ROOT/rangePath).read_bytes();rangeData=json.loads(rangeRaw)
 assert rangeData['validation']['status']=='passed' and rangeData['profileCount']==29
 assert digest((ROOT/rangeData['sourcePath']).read_bytes())==rangeData['sourceSha256']
 assert rangeData['instrumentQualifiedSoundingNoteAddresses']==1045
 sid='chinese-expanded:hkco-range2025';packetBinding={'path':rangePath,'sha256':digest(rangeRaw)}
 rangeIds={};rangeMemberIds=[]
 for profile in rangeData['profiles']:
  key=profile['id'];parent='chinese-expanded:hkco:family:'+profile['family']
  pid=ent('hkco:range:'+key,profile['nativeName'],'HKCO-source-range-profile','HKCO2025',sid,parent=parent,
   nativeAddress={'frame':'HKCO2025-range-chart','profile':key},sourceRange=profile,rangePacket=packetBinding,
   physicalInstrumentCount=None,physicalFrequencyHz=None,
   exceptions=['A source range profile is not a physical instrument, player, unique historical tuning or global SUNNY generational class.'])
  rangeIds[key]=pid;edge(parent,pid,'has-source-range-profile',sid)
  if key in ['bianzhong','yunluo']:
   edge('chinese-expanded:hkco:chart:'+key,pid,'has-source-pitch-range',sid,pitchToPhysicalMemberMapKnown=False,
    qualification='Counted physical/strike slots and ordered pitch addresses are different units; no individual bell/gong mapping inferred.')
  for member in profile['members']:
   value=member['sourceSoundingChromaticIndex'];nid=ent('hkco:range-note:'+key+':'+str(value),profile['nativeName']+' · chromatic staff address '+str(value),
    'instrument-qualified-chromatic-staff-note-address','HKCO2025',sid,parent=pid,assertionLayer='source-range-derived',
    nativeAddress={'frame':'HKCO2025-range-chart','profile':key,'sourceSoundingChromaticIndex':value,'writtenEffectiveChromaticIndex':value-profile['sourceWrittenToSoundingSemitones']},
    rangeCapability=member['capability'],physicalFrequencyHz=None,rangePacket=packetBinding,
    derivation={'rule':'Every semitone in the explicitly licensed source range, excluding source-stated absent notes.',
     'sourceLow':profile['writtenLow'],'sourceNormalHigh':profile['writtenNormalHigh'],'sourceExtremeHigh':profile['writtenExtremeHigh'],
     'writtenToSoundingSemitones':profile['sourceWrittenToSoundingSemitones'],'excludedIndices':profile['excludedSoundingChromaticIndices']},
    exceptions=['The chromatic index encodes staff-note arithmetic; no equal-temperedHz, measured acoustic realization or unique physical bell/strike assignment is asserted.'])
   rangeMemberIds.append(nid);edge(pid,nid,'has-source-range-note-address',sid,assertionLayer='source-range-derived')
 zroot=ent('hkco:zheng:source-strings','Zheng:21 open-string occurrences and local bridge settings','HKCO-source-tunable-string-system','HKCO2025',sid,
  parent='chinese-expanded:hkco:family:plucked',rangePacket=packetBinding,sourceOperation=rangeData['zhengOperationControl'],
  exceptions=['Ascending source occurrence ordinals are editorial addresses, not official instrument string numbers. Local pitch union does not establish simultaneous playability.'])
 edge('chinese-expanded:hkco:family:plucked',zroot,'has-source-tunable-string-system',sid)
 pitchIds={};zhengControl=rangeData['zhengOperationControl']
 for value in zhengControl['distinctPitchUnion']:
  pitchIds[value]=ent('hkco:zheng:pitch-union:'+str(value),'Zheng local-setting pitch union · staff address '+str(value),'retuning-union-chromatic-staff-address','HKCO2025',sid,
   parent=zroot,assertionLayer='source-operation-derived',nativeAddress={'frame':'HKCO2025-zheng-local-setting-union','sourceSoundingChromaticIndex':value},physicalFrequencyHz=None,
   exceptions=['Derived union over local settings; these51 pitches do not form one fixed21-string tuning.'])
  edge(zroot,pitchIds[value],'has-local-setting-union-pitch',sid,assertionLayer='source-operation-derived')
 for string in rangeData['zhengSourceStringsAndLocalOperations']:
  ordinal=string['sourceOrdinalAscending'];stringId=ent('hkco:zheng:string:'+str(ordinal),'Zheng open-string occurrence '+str(ordinal)+' (ascending)',
   'source-ordered-open-string-occurrence','HKCO2025',sid,parent=zroot,sourceProvidedStringNumber=False,openString=string['openString'],
   nativeAddress={'frame':'HKCO2025-zheng-open-strings','ascendingOccurrenceOrdinal':ordinal},rangePacket=packetBinding,physicalFrequencyHz=None)
  edge(zroot,stringId,'has-source-ordered-string-occurrence',sid)
  for setting in string['localBridgeSettings']:
   delta=setting['localShiftSemitones'];value=setting['sourceSoundingChromaticIndex'];settingId=ent('hkco:zheng:setting:'+str(ordinal)+':'+str(delta),
    'Zheng occurrence '+str(ordinal)+' local shift '+str(delta),'string-qualified-local-bridge-setting','HKCO2025',sid,parent=stringId,assertionLayer='source-operation-derived',
    nativeAddress={'frame':'HKCO2025-zheng-local-bridge-setting','ascendingOccurrenceOrdinal':ordinal,'localShiftSemitones':delta,'sourceSoundingChromaticIndex':value},
    physicalFrequencyHz=None,rangePacket=packetBinding,simultaneousCondition='At most one bridge setting per source string occurrence before playing.')
   edge(stringId,settingId,'admits-local-bridge-setting',sid,assertionLayer='source-operation-derived')
   edge(settingId,pitchIds[value],'projects-to-local-setting-union-pitch',sid,assertionLayer='source-operation-derived')
 views.append({'id':'chinese-expanded:hkco','label':'HKCO modern families, source ranges, strings and counted bell/gong sets','roots':[hkroot],'witnessIds':['HKCO2025-2026','HKCO2025'],'coverage':{'wholeSystemComplete':False,'staffRangeTranscription':'29boundedprofiles; non-keyed wind variants and continuous drum tuning remain open','namedReferences':instrumentCount,'rangeNoteAddresses':1045,'zhengOpenStringOccurrences':21,'zhengLocalSettings':63,'zhengPitchUnion':51}})
 for r in relations:
  if r['id'].startswith('chinese-expanded:'):
   r['viewIds']=['chinese-expanded:jingfang60' if 'houhan' in r['source'] else 'chinese-expanded:lam60modes' if 'lam' in r['source'] else 'chinese-expanded:hkco']
 ids=[e['id'] for e in entities];assert len(set(ids))==len(ids)
 assert all(r['source'] in ids and r['target'] in ids for r in relations)
 counts=Counter(e['unit'] for e in entities);oldIdsUnchanged=all(e in entities for e in old)
 result={'schema':'sunny.chinese-expanded.v1','createdAt':datetime.now(timezone.utc).isoformat(),'sources':sources+base['sources'],'entities':entities,'relationships':relations,'views':views,
  'jevReceipt':'state/jev-receipts/000064-fc22fe7cfcff.json','guards':{'memory':'state/research/chinese-expanded/supermemory-retrieval.json','research':'state/research/chinese-expanded/prior-art-exa-search.json'},
  'nativeGeneration':{'source':'chinese-expanded:houhan91','chain':chain,'rules':['Down-generation length ×2/3; up-generation length ×4/3, using the explicit source direction for each edge.',
   '177147 integer units /19683 =9cun for Huangzhong; retain source integer and exact rational ideal separately.','Source register bounds and tube/string calibration conditions do not establish modern absoluteHz.'],
   'completeNamedStandards':60,'documentedGongContexts':58,'explicitRoleMemberships':174,'terminalExceptions':terminal,
   'printedDayDurationSum':sum(r['dayDurationAsPrinted'] for r in rows),'calendarBoundary':'Sum of this transcription as printed, not a reconstructed correct year or institutional date.'},
  'sourceDiscrepancies':[{'name':r['nativeName'],'sourceInteger':r['sourceInteger'],'exactIdeal':str(r['exactIdealInteger']),'residual':str(Fraction(r['sourceInteger'])-r['exactIdealInteger']),
   'status':'unresolved rounding/transmission/interpretation distinction; original bytes preserved'} for r in rows if abs(Fraction(r['sourceInteger'])-r['exactIdealInteger'])>10],
  'qian360':{'reportedBy':'chinese-expanded:suishu16','evidence':phrase('suishu16','宋元嘉中，太史錢樂之',300),'reportedStandards':360,
   'exactGeneratorAndAddressDomainRecovered':False,'notEnumeratedAsKnownNotes':True,'gap':'The continuation statement and terminallength do not yet fix every direction, exact historical name/value and register exception.'},
  'hkcoSourceRangeCensus':{'packet':packetBinding,'profiles':29,'instrumentQualifiedStaffNotes':1045,'zhengOpenStrings':21,'zhengLocalSettings':63,'zhengUnionPitches':51,
   'pitchOrContextAddressOccurrencesExcludingUnmappedPhysicalSlots':174+300+1045+63,'legacyAnonymousBellAndGongSoundSlots':89,
   'physicalSlotToPitchMappingKnown':False,'zhengOperator':zhengControl},
  'unitCensus':dict(counts),'existingChineseRecordsPreserved':len(old),'censusReconciliation':{'targetRange':[2500,2700],
   'entitiesIncludingClassifiersAndContextNodes':len(entities),'noteMembershipUnits':174+300+89+1045+63,'noteMembershipMeaning':'Different witness/context/instrument sound units, including89 anonymous physical/strike slots and their unresolved pitch mapping; not a disjoint population of physical tones.',
   'targetMet':False,'missingPremises':['Complete source-qualified staff-range/key-variant transcription for remaining HKCO instruments and source pitch-to-bell/strike mappings.',
    'A source-defined common accounting unit matching the user target; heterogeneous classifiers/performers/notes cannot be summed as one census.',
    'Exact360lü construction/names/register exceptions before any larger classical expansion.'],
   'bracketingConditionalConfigurations':{'sevenRoleAddressesPer360Standards':2520,'status':'Arithmetic conditional only; not enumerated or treated as an established historical configuration.',
    'missingPremise':'All360standards lawfully act as gong and support seven distinct roles. HouHan60 contains explicit counterexamples to unrestricted all-root promotion.'}},
  'notClaimed':{'completeChineseMusic':False,'allHKCORangesTranscribed':False,'allPhysicalSoundsKnown':False,'sourceIntegersEqualExactIdeal':False,'targetArtificiallyPadded':False},
  'validation':{'oldChinesePreserved':oldIdsUnchanged,'allReferencesResolve':True,'graphUnchanged':digest((ROOT/'state/reconstruction/hierarchy-atlas-combined.json').read_bytes())==oldHash}}
 assert result['validation']['graphUnchanged'] and oldIdsUnchanged
 target=ROOT/'state/reconstruction/chinese-expanded.json'
 if target.exists():
  prior=target.read_bytes();history=PACKET/'history'/('chinese-expanded.'+digest(prior)+'.json');history.parent.mkdir(exist_ok=True)
  if not history.exists():history.write_bytes(prior)
  else:assert history.read_bytes()==prior
  result['previousModuleSnapshot']={'path':str(history.relative_to(ROOT)).replace('\\','/'),'sha256':digest(prior)}
 write(target,result)
 check={'status':'passed','exit_code':0,'existingChineseRecordsPreserved':162,'namedJingFangStandards':60,'generationEdges':59,'sourceGongContexts':58,'explicitToneRoles':174,
        'LamModes':60,'LamModeToneMemberships':300,'HKCOInstrumentReferences':instrumentCount,'HKCOBellAndGongSoundAddresses':89,'HKCORangeProfiles':29,'HKCOInstrumentQualifiedStaffNotes':1045,
        'ZhengOpenStringOccurrences':21,'ZhengLocalSettings':63,'ZhengPitchUnion':51,'entities':len(entities),'relationships':len(relations),
        'printedDayDurationSum':result['nativeGeneration']['printedDayDurationSum'],'integerDiscrepanciesOver10':len(result['sourceDiscrepancies']),'sourceGraphUnchanged':True}
 write(PACKET/'validation.json',check);print(json.dumps(check,ensure_ascii=False,indent=2))
if __name__=='__main__':
 if '--acquire' in sys.argv:print(json.dumps(acquire(),ensure_ascii=False,indent=2))
 else:main()
