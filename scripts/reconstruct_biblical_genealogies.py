"""Source-qualified Biblical people, family assertions and independent Gospel lists.

No network, canonical model mutation, historical orientation or musical assignment.
Theographic family fields are curated assertions, never silently primary-witness ink.
"""
from pathlib import Path
from collections import defaultdict, deque
import csv, hashlib, json, re

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'state/research/biblical-genealogies'
OUT=ROOT/'state/reconstruction/biblical-genealogies.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
pid=lambda slug:'bible:theographic:'+slug
split=lambda value:[x.strip() for x in (value or '').split(',') if x.strip()]
PENTATEUCH={'Gen','Exod','Lev','Num','Deut'}

def main():
    people_path=BASE/'theographic-People.csv';verses_path=BASE/'theographic-Verses.csv'
    people=list(csv.DictReader(people_path.open(encoding='utf-8-sig',newline='')))
    verse_rows=list(csv.DictReader(verses_path.open(encoding='utf-8-sig',newline='')))
    verses={v['osisRef']:v for v in verse_rows};index={p['personLookup']:p for p in people}
    assert len(people)==len(index)==3067 and len(verses)==len(verse_rows)==31102
    commit=json.loads((BASE/'theographic-commit.json').read_text(encoding='utf-8'))
    tree=json.loads((BASE/'theographic-tree.json').read_text(encoding='utf-8'))
    tree_index={r['path']:r for r in tree['tree']}
    sources=[]
    for relative,path in [('CSV/People.csv',people_path),('CSV/Verses.csv',verses_path)]:
        raw=path.read_bytes();blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        assert blob==tree_index[relative]['sha']
        sources.append({'id':'theographic:'+relative,'path':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':sha(raw),'gitBlobSha':blob,'repository':'https://github.com/robertrouse/theographic-bible-metadata','commit':commit['sha'],'upstreamPath':relative,'url':'https://github.com/robertrouse/theographic-bible-metadata/blob/'+commit['sha']+'/'+relative,'license':'CC BY-SA 4.0 (captured maintainer declaration and LICENSE)','role':'Curated named-entity links and KJV1769 transcription; not a diplomatic MT/LXX/SP collation.'})
    entities=[];by_id={};names=defaultdict(list)
    for ordinal,row in enumerate(people,1):
        node={'id':pid(row['personLookup']),'nativeName':row['displayTitle'] or row['name'],'name':row['name'],'aliases':split(row['alsoCalled']),'unit':'Curated Biblical named-entity/person record','sourceRecordKey':row['personLookup'],'sourceRecordOrdinalOneBased':ordinal,'sourceRefs':['theographic:CSV/People.csv'],'verseRefs':split(row['verses']),'genderAsCurated':row['gender'],'ambiguousAsCurated':row['ambiguous']=='checked','disambiguationNote':row['Disambiguation (temp)'],'generation':None,'absoluteChronology':None,'musicalAssignment':None,'historicalIndividualIndependentlyConfirmed':False,'curatedChronologyNotAdopted':{'birthYear':row['birthYear'],'deathYear':row['deathYear'],'basis':'Maintainer follows modern Jones chronology; not substituted for received witness clocks.'}}
        entities.append(node);by_id[node['id']]=node;names[row['name'].casefold()].append(node['id'])
    relationships=[];claims=[];unresolved_links=[];grouped={}
    def ensure(slug):
        key=pid(slug)
        if key not in by_id:
            node={'id':key,'nativeName':slug,'name':None,'unit':'Unresolved curated lookup reference','sourceRefs':['theographic:CSV/People.csv'],'verseRefs':[],'generation':None,'identityStatus':'unresolved'}
            entities.append(node);by_id[key]=node;unresolved_links.append(slug)
        return key
    for ordinal,row in enumerate(people,1):
        for field in ['father','mother','children','partners','siblings','halfSiblingsSameMother','halfSiblingsSameFather']:
            for target in split(row[field]):
                actor=ensure(row['personLookup']);other=ensure(target)
                if field in ['father','mother']:parent,child=other,actor;kind='curated-parentage';role=field
                elif field=='children':parent,child=actor,other;kind='curated-parentage';role='parent-role-unspecified'
                else:parent,child=sorted([actor,other]);kind={'partners':'curated-partnership','siblings':'curated-sibling','halfSiblingsSameMother':'curated-half-sibling-same-mother','halfSiblingsSameFather':'curated-half-sibling-same-father'}[field];role=field
                special='ordinary-curated-claim'
                if parent==pid('god_1324') and kind=='curated-parentage':special='theological-or-creation-claim; not biological parenthood'
                if parent==pid('joseph_1715') and child==pid('jesus_905'):special='social/genealogical claim; biological parenthood not licensed'
                key=(kind,parent,child)
                if key not in grouped:
                    common=sorted(set(by_id[parent].get('verseRefs',[]))&set(by_id[child].get('verseRefs',[])))
                    edge={'id':'bible:curated-relation:'+str(len(grouped)+1),'source':parent,'target':child,'type':kind,'parentRoles':[],'sourceRefs':['theographic:CSV/People.csv'],'sourceAssertions':[],'candidateVerseRefs':common,'verseEvidenceStatus':'Co-mention candidates only; not proof that a verse states this relation.','assertionLayer':'curator-assertion','biologicalStatus':'not established','semanticQualification':special}
                    grouped[key]=edge;relationships.append(edge)
                edge=grouped[key];edge['parentRoles']=sorted(set(edge['parentRoles']+[role]))
                assertion={'id':'bible:curated-assertion:'+str(len(claims)+1),'csvRecordKey':row['personLookup'],'csvRecordOrdinalOneBased':ordinal,'field':field,'value':target,'relationId':edge['id']}
                claims.append(assertion);edge['sourceAssertions'].append(assertion['id'])
    text_claims=[];chains=[]
    def occurrence(chain,ordinal,name,ref):
        key='bible:genealogy:'+chain+':'+str(ordinal)
        rich=verses[ref]['richText']
        matches=re.findall(r'\[([^]]+)\]\(/person/([^\)]+)\)',rich)
        candidates=sorted({pid(slug) for label,slug in matches if label.casefold()==name.casefold()})
        node={'id':key,'nativeName':name,'name':name,'unit':'Addressed name occurrence in one published KJV genealogy','sourceRefs':['theographic:CSV/Verses.csv'],'verseRefs':[ref],'sequenceOrdinalOneBased':ordinal,'sequenceCountingUnit':'named entry in this genealogy, not elapsed biological generation','generation':None,'candidateCuratedIdentities':candidates,'identityBridgeStatus':'curated verse markup only; no homonym collapse','musicalAssignment':None}
        entities.append(node);by_id[key]=node;return key
    def text_edge(parent,child,kind,ref,qualification,pattern):
        edge={'id':'bible:scripture-claim:'+str(len(text_claims)+1),'source':parent,'target':child,'type':kind,'verseRefs':[ref],'sourceRefs':['theographic:CSV/Verses.csv'],'sourceEdition':'KJV1769 transcription','assertionLayer':'explicit translation wording with addressed genealogy occurrences','relationshipLanguage':pattern,'qualification':qualification,'biologicalStatus':'Not independently established; genealogy may telescope or express social/theological relations.'}
        text_claims.append(edge);relationships.append(edge);return edge['id']
    # Luke's list remains independent of the curator's harmonized family table.
    luke_nodes=[];luke_edges=[];ordinal=1;child=occurrence('Luke3',ordinal,'Jesus','Luke.3.23');luke_nodes.append(child)
    for number in range(23,39):
        ref='Luke.3.'+str(number);text=verses[ref]['verseText']
        for match in re.finditer(r'\bson of ([A-Z][A-Za-z-]*)',text):
            ordinal+=1;parent=occurrence('Luke3',ordinal,match.group(1),ref);luke_nodes.append(parent)
            qualification='KJV which-was-son-of genealogy; biological immediacy not forced'
            if child==luke_nodes[0]:qualification='Explicit as-was-supposed qualifier retained for Jesus/Joseph'
            kind='textual-genealogical-son-of'
            if match.group(1)=='God':kind='textual-theological-descent';qualification='Terminal God/Adam theological relation, not biological parentage'
            luke_edges.append(text_edge(parent,child,kind,ref,qualification,match.group(0)));child=parent
    chains.append({'id':'bible:genealogy:Luke3','title':'Luke3:23-38, KJV received genealogy','nodeIds':luke_nodes,'relationshipIds':luke_edges,'direction':'text lists child to ancestor; directed relationships point ancestor to child','sourceScope':'New Testament KJV comparison; not an SP witness','namedOccurrences':len(luke_nodes),'unknowns':['Independent Greek textual-variant collation','Biological/legal sense of each link','Cross-genealogy identity reconciliation']})
    # Matthew's literal begat clauses; repeated names retain distinct addresses.
    matt_nodes=[];matt_edges=[];tail=None;ordinal=0
    for number in range(2,17):
        ref='Matt.1.'+str(number);text=verses[ref]['verseText']
        for match in re.finditer(r'\b([A-Z][A-Za-z-]*)(?: the king)? begat ([A-Z][A-Za-z-]*)',text):
            father_name,child_name=match.groups()
            if tail is not None and by_id[tail]['name']==father_name:parent=tail
            else:ordinal+=1;parent=occurrence('Matthew1',ordinal,father_name,ref);matt_nodes.append(parent)
            ordinal+=1;child=occurrence('Matthew1',ordinal,child_name,ref);matt_nodes.append(child)
            matt_edges.append(text_edge(parent,child,'textual-begat',ref,'Begetting language is retained; chronological telescoping not erased.',match.group(0)));tail=child
    # Matthew1:16 deliberately does not say Joseph begat Jesus.
    mary=occurrence('Matthew1',ordinal+1,'Mary','Matt.1.16');jesus=occurrence('Matthew1',ordinal+2,'Jesus','Matt.1.16');matt_nodes.extend([mary,jesus])
    matt_edges.append(text_edge(mary,jesus,'textual-maternal-birth','Matt.1.16','Of whom was born Jesus; no Joseph-begetting substitution.','of whom was born Jesus'))
    matt_edges.append(text_edge(tail,mary,'textual-partnership','Matt.1.16','Joseph is husband of Mary; partnership is not a parentage edge.','Joseph the husband of Mary'))
    chains.append({'id':'bible:genealogy:Matthew1','title':'Matthew1:2-16, KJV begetting clauses and maternal endpoint','nodeIds':matt_nodes,'relationshipIds':matt_edges,'direction':'parent/genealogical ancestor to named descendant; partnership kept separate','sourceScope':'New Testament KJV comparison; not an SP witness','namedOccurrences':len(matt_nodes),'unknowns':['Coordinated sibling branches are retained in the curated layer pending separate verse-rule expansion','Telescoped entries and Greek textual variants','Complete primary-edition collation']})
    # Explicitly retain narrative parenthood where pronouns require declared context.
    primordial=[('adam_78','cain_533','father','Gen.4.1'),('eve_1231','cain_533','mother','Gen.4.1'),('adam_78','seth_2504','father','Gen.5.3'),('eve_1231','seth_2504','mother','Gen.4.25'),('cain_533','enoch_1191','father','Gen.4.17')]
    narrative=[]
    for parent,child,role,ref in primordial:
        narrative.append(text_edge(pid(parent),pid(child),'contextual-narrative-parentage',ref,'Declared narrative/pronominal context; role='+role+'; links to Eve also require Gen3:20 identity context.',role))
    anon='bible:anonymous:Gen4.17:cain-wife'
    entities.append({'id':anon,'nativeName':'Unnamed wife of Cain in Gen4:17','name':None,'unit':'Source-addressed unnamed person occurrence','sourceRefs':['theographic:CSV/Verses.csv'],'verseRefs':['Gen.4.17'],'generation':None,'identityStatus':'not equated with any named person'});by_id[anon]=entities[-1]
    narrative.append(text_edge(anon,pid('enoch_1191'),'textual-maternal-birth','Gen.4.17','She conceived and bare Enoch; unnamed mother kept individually addressed.','his wife; and she conceived, and bare Enoch'))
    narrative.append(text_edge(pid('cain_533'),anon,'textual-partnership','Gen.4.17','Wife relationship kept separate from descent.','Cain knew his wife'))
    master=json.loads((ROOT/'state/reconstruction/master-score.json').read_text(encoding='utf-8'))
    clocks=[]
    for view in master['program']['views']:
        if not view['id'].startswith('chronology:'):continue
        clocks.append({'id':view['id'],'title':view['system'],'sourceRefs':view['sourceRefs'],'condition':view['condition'],'participants':[{'id':p['id'],'name':p['label'],'onset':p['onset'],'duration':p['duration'],'GEN':p['coordinates'].get('GEN'),'TIME':p['coordinates'].get('TIME')} for p in view['participants']]})
    archive=ROOT/'data/raw/archive/SUN_Universal_Archive/Library/SOL_SATURN_ROSETTAS/SOL_Cainan_to_Judah_two_witness_lineage_2026-10-23.json'
    lineage=json.loads(archive.read_text(encoding='utf-8'))
    # Inherit actual received source placements before any global/music projection.
    # Fixed role+verse bridges retain both the native occurrence and curator ID.
    bridge_rows=[
      ('Adam','adam_78',None),('Seth','seth_2504','Gen.5.3'),('Enosh','enos_1193','Gen.5.6'),('Kenan I','cainan_534','Gen.5.9'),
      ('Mahalalel','mahalaleel_1885','Gen.5.12'),('Jared','jared_730','Gen.5.15'),('Enoch (son of Jared)','enoch_1192','Gen.5.18'),
      ('Methuselah','methuselah_2042','Gen.5.21'),('Lamech (father of Noah)','lamech_1809','Gen.5.25'),('Noah','noah_2210','Gen.5.29'),
      ('Shem','shem_2613','Gen.5.32'),('Arpachshad','arphaxad_312','Gen.11.10'),('Cainan II','cainan_535','Luke.3.36'),
      ('Shelah (son of Cainan II in expanded witness)','salah_2455','Gen.11.12'),('Eber','eber_1030','Gen.11.14'),('Peleg','peleg_2308','Gen.11.16'),
      ('Reu','reu_2428','Gen.11.18'),('Serug','serug_2503','Gen.11.20'),('Nahor','nahor_2142','Gen.11.22'),('Terah','terah_2841','Gen.11.24'),
      ('Abraham','abraham_58','Gen.11.26'),('Isaac','isaac_616','Gen.21.3'),('Jacob','israel_682','Gen.25.26'),('Judah','judah_1751','Gen.29.35'),
      ('Perez','pharez_2338','Gen.38.29'),('Hezron','hezron_1520','Gen.46.12'),('Ram','ram_2391','Ruth.4.19'),('Amminadab','amminadab_228','Ruth.4.19'),
      ('Nahshon','nahshon_2144','Ruth.4.20'),('Salmon/Salma','salmon_2463','Ruth.4.20'),('Boaz','boaz_519','Ruth.4.21'),('Obed','obed_2228','Ruth.4.21'),
      ('Jesse','jesse_903','Ruth.4.22'),('David','david_994','Ruth.4.22')]
    assert [x[0] for x in bridge_rows]==[x['person'] for x in lineage['people_expanded_lukan_genealogy']]
    native_nodes={};native_edges=[];native_chains=[];identity_bridges=[];source_placements=[]
    archive_id='received:expanded-lineage-2026-10-23'
    sources.append({'id':archive_id,'path':str(archive.relative_to(ROOT)).replace('\\','/'),'sha256':sha(archive.read_bytes()),'role':'Recovered analytical lineage and named-entry ranks; conditionally inherited, not newly collated original manuscript.'})
    for family in ['MT','SP','Greek']:
        selected=[r for r in bridge_rows if family=='Greek' or r[0]!='Cainan II']
        if family=='SP':selected=[r for r in selected if bridge_rows.index(r)<=25]
        ids=[];edge_ids=[];previous=None
        for ordinal,(name,slug,ref) in enumerate(selected,1):
            key='bible:received-lineage:'+family+':'+slug
            display='Shelah' if slug=='salah_2455' else name
            node={'id':key,'nativeName':display,'name':display,'unit':'Source-qualified named occurrence in inherited lineage','sourceRefs':[archive_id],'verseRefs':[ref] if ref else ['Gen.5.1'],'generation':None,'namedEntryOrdinalOneBased':ordinal,'countingUnit':'named entry under this received witness accounting; not universal biological generation','placementStatus':'known conditionally in recovered analytical source','witnessFamily':family,'musicalAssignment':None}
            entities.append(node);by_id[key]=node;native_nodes[(family,display)]=key;ids.append(key)
            proof_ref=ref or 'Gen.5.1'
            bridge={'id':'bible:identity-bridge:'+family+':'+slug,'sourceOccurrenceId':key,'candidateCuratedIdentity':pid(slug),'sourceVerseRole':{'reference':proof_ref,'personRole':'named descendant of preceding addressed entry' if previous else 'Adam root'},'bridgeBasis':'Explicit retained lineage person/parent role plus fixed CSV lookup and declared verse context; no equality from name alone.','KJVMarkupContainsCandidate':('/person/'+slug+')') in verses[proof_ref]['richText'],'identityStatus':'qualified cross-source correspondence, not independently proved historical identity'}
            if slug=='cainan_535':bridge['qualification']='Greek Gen11 insertion corresponds to Luke3:36 Cainan II; the KJV Gen11 absence is preserved.'
            identity_bridges.append(bridge)
            if previous:
                link_ref=ref
                if slug=='salah_2455':link_ref='Gen.11.13:inserted-Cainan-clause' if family=='Greek' else 'Gen.11.12'
                edge={'id':'bible:received-lineage-relation:'+family+':'+slug,'source':previous,'target':key,'type':'received-conditional-genealogical-descent','verseRefs':[link_ref],'sourceRefs':[archive_id],'assertionLayer':'inherited analytical witness lineage; source-qualified conditional claim','qualification':'Named descent/order retained without forcing immediate biology, absolute dates or musical orientation.'}
                relationships.append(edge);native_edges.append(edge);edge_ids.append(edge['id'])
            previous=key
        native_chains.append({'id':'bible:received-lineage:'+family,'family':family,'nodeIds':ids,'relationshipIds':edge_ids,'namedEntries':len(ids),'sourceRefs':[archive_id],'scope':'Adam–Hezron, Genesis only' if family=='SP' else 'Adam–David recovered conditional accounting; post-Genesis edition collation remains open','condition':'Adopt the recovered analytical lineage only at its declared source layer; no whole-Bible witness completion claimed.'})
    clock_roles={'A':'Arpachshad','B':'Shelah','C':'Eber'}
    clock_links=[]
    for clock in clocks:
        variant=clock['id'].split(':',1)[1];family='Greek' if variant.startswith('Greek') else 'SP' if variant=='SP' else 'MT'
        role_names={'A':'Arpachshad','B':'Cainan II','C':'Shelah'} if family=='Greek' else clock_roles
        previous=None
        for participant in clock['participants']:
            role=participant['id'].rsplit(':',1)[1];name=role_names[role];target=native_nodes[(family,name)]
            source_placements.append({'id':'bible:received-clock-placement:'+participant['id'],'entityId':target,'sourceParticipantId':participant['id'],'chronologyViewId':clock['id'],'nameAsReceived':participant['name'],'onset':participant['onset'],'duration':participant['duration'],'GEN':participant['GEN'],'TIME':participant['TIME'],'status':'known under inherited received chronology condition','sourceRefs':clock['sourceRefs'],'condition':clock['condition'],'scope':'Local three-person reported chain; GEN and TIME do not become universal coordinates.'})
            if previous:
                edge={'id':'bible:received-clock-relation:'+participant['id'],'source':previous,'target':target,'type':'received-conditional-chronology-descent','sourceRefs':clock['sourceRefs'],'chronologyViewId':clock['id'],'assertionLayer':'inherited received chronology','qualification':'Local participant order and supplied source condition; not new independent manuscript evidence.'}
                relationships.append(edge);clock_links.append(edge)
            previous=target
    primary_path=BASE/'genesis-witness-comparison.json'
    primary=json.loads(primary_path.read_text(encoding='utf-8'))
    sources.append({'id':'primary:genesis-comparison','path':str(primary_path.relative_to(ROOT)).replace('\\','/'),'sha256':sha(primary_path.read_bytes()),'role':'Finite MT/SP transcription and visually inspected Swete1887 publication claims; raw source hashes and exact addresses are in packet.'})
    primary_edges=[]
    for claim in primary['ageAtBegettingClaims']:
        family='Greek' if claim['family'].startswith('Greek') else claim['family']
        parent=native_nodes[(family,claim['parentRole'])];child=native_nodes[(family,claim['descendantRole'])]
        edge={'id':claim['id'].replace('primary-age','primary-begetting'),'source':parent,'target':child,'type':'edition-textual-genealogical-begetting','verseRefs':[claim['reference']],'sourceRefs':['primary:genesis-comparison'],'claimId':claim['id'],'assertionLayer':claim['sourceLayer'],'reportedAgeAtNamedBegetting':claim['reportedAgeAtNamedBegetting'],'unit':'reported-year','sourceRegion':claim['sourceRegion'],'biologicalImmediacyIndependentlyEstablished':False,'ancientInkIndependentlyInspected':False}
        relationships.append(edge);primary_edges.append(edge)
    views=[]
    for family,title,scope,clock_ids in [('MT','Masoretic family','Hebrew Bible witness family; KJV corpus is a translation comparison, not diplomatic MT.', ['chronology:MT']),('Greek','Greek expanded/Septuagint family','Greek OT witnesses and independent Gospel lists require edition-specific collation; Greek430/400 are retained variants.', ['chronology:Greek_430','chronology:Greek_400']),('SP','Samaritan Pentateuch family','Pentateuch only; no Samaritan whole-Bible or New Testament witness is invented.', ['chronology:SP'])]:
        comparable=[e['id'] for e in grouped.values() if family!='SP' or any(ref.split('.')[0] in PENTATEUCH for ref in e['candidateVerseRefs'])]
        views.append({'id':'bible:witness-family:'+family,'label':title,'scope':scope,'identityStatus':'Working three-family grouping recovered from the existing MT/SP/Greek analytical comparison; exact user-intended three still to be confirmed.','receivedChronologyViewIds':clock_ids,'receivedWitnessRelationIds':[e['id'] for e in native_edges if e['id'].split(':')[2]==family]+[e['id'] for e in clock_links if e['chronologyViewId'] in clock_ids],'receivedPlacementIds':[p['id'] for p in source_placements if p['chronologyViewId'] in clock_ids],'comparisonRelationIds':comparable,'comparisonRelationStatus':'Curator/KJV comparison only, not uniformly admitted in this original witness.','originalEditionParentageAssertions':[e['id'] for e in primary_edges if e['source'].split(':')[2]==family],'editionAssertionQualification':'Finite scholarly transcription/published-edition readings; independent ancient-ink verification remains zero.','gospelComparisonChainIds':[c['id'] for c in chains] if family!='SP' else [],'outsideWitnessScope':{'afterPentateuch':'not witnessed by SP' if family=='SP' else 'requires original-edition collation','NewTestament':'not witnessed by SP' if family=='SP' else 'Gospel comparison layer retained independently, not an OT original-witness projection'},'completeOriginalWitnessGenealogy':False})
    homonyms=[{'name':name,'entityIds':ids} for name,ids in sorted(names.items()) if len(ids)>1]
    verse_refs={ref for e in text_claims for ref in e['verseRefs']}
    scripture_evidence=[{'osisRef':ref,'verseText':verses[ref]['verseText'],'annotatedRichText':verses[ref]['richText'],'sourceRefs':['theographic:CSV/Verses.csv'],'annotationRole':'Person IDs in rich text are curator links, distinct from the unannotated KJV verse.'} for ref in sorted(verse_refs)]
    issues=[{'id':'JOSEPH-HELI-MARY','scope':'Luke3:23 versus curated family fields','sourceVerse':'Luke.3.23','curatedHeliChildren':index['heli_1484']['children'],'curatedJosephFather':index['joseph_1715']['father'],'qualification':'Curator assigns Heli a Mary child while KJV wording places Heli after Joseph. Retain both at distinct evidence layers; no harmonized biological join selected.'},
        {'id':'CAINAN-INSERTION','scope':'Gen11/1Chr1 versus Luke3:36 and received Greek variants','qualification':'Curator has Arphaxad->CainanII->Salah globally. Do not project this into MT/SP Gen11; source-qualified received chronology and expanded archive stay separate.'},
        {'id':'MATTHEW-TELESCOPING','sourceVerses':['Matt.1.8','Matt.1.11','1Chr.3.10','1Chr.3.11','1Chr.3.12','1Chr.3.15','1Chr.3.16'],'qualification':'Preserve listed begetting links without identifying every list step with one biological generation or forcing agreement with Chronicles.'},
        {'id':'CREATION-NOT-BIOLOGY','qualification':'Curator God->Adam/Eve and Luke terminal God/Adam are theological/creation claims, never ordinary biological parenthood.'}]
    result={'schema':'sunny.biblical-genealogies.v1','status':'working-source-qualified-corpus; original three-witness collation incomplete','sources':sources,'entities':entities,'relationships':relationships,'curatedAssertions':claims,'gospelGenealogyChains':chains,'narrativeRelationIds':narrative,'scriptureEvidence':scripture_evidence,'views':views,'receivedChronologyViews':clocks,'additionalChronologyComparison':{'id':'chronology:Clementine_Latin','preserved':True,'notCollapsedIntoThreeFamilies':True},'retainedArchiveLineage':{'path':str(archive.relative_to(ROOT)).replace('\\','/'),'sha256':sha(archive.read_bytes()),'claims':lineage['claims'],'peopleExpandedLukanGenealogy':lineage['people_expanded_lukan_genealogy']},'homonymGroups':homonyms,'discrepancies':issues,'unresolvedLookupReferences':sorted(set(unresolved_links)),'successionClaims':[],'successionBoundary':'No succession or authority link is inferred from family order.','counts':{'curatedPeopleRecords':len(people),'scriptureVersesInAcquiredCorpus':len(verses),'individuallyAddressedEntities':len(entities),'curatedFamilyRelations':len(grouped),'curatedFieldAssertions':len(claims),'independentTextualClaims':len(text_claims),'homonymGroups':len(homonyms),'receivedChronologyVariants':len(clocks),'workingWitnessFamilies':len(views),'originalEditionParentageAssertionsAdmitted':0},'generationBoundary':'Named-entry order, biological descent, semantic genealogy, received chronology, source address and musical phase are distinct. No universal generation ranks assigned.','chronologyBoundary':'Modern curator dates retained as unadopted metadata; received MT/SP/Greek/Latin source clocks remain independently qualified.','unresolved':['Exact user-intended three accountings require confirmation against recovered context/current direction.','Original MT/LXX/SP edition-level whole-scope parentage and textual variants','SP has no post-Pentateuch witness scope','Complete explicit verse licensing for every curated family assertion','All identity joins, adoption/levirate/legal relationships and homonyms','Original musical/phase/orientation bridge'],'completeAgainstAcquiredPeopleTable':True,'wholeBibleGenealogyScientificallyComplete':False,'historicalOrientationSelected':False,'fullMissionComplete':False}
    result.update({'status':'working whole-Bible curator corpus plus inherited source placements and finite primary Genesis comparison; complete original-witness collation remains open','receivedNativeLineageChains':native_chains,'qualifiedIdentityBridges':identity_bridges,'receivedSourcePlacements':source_placements,'primaryGenesisComparison':primary,'primaryGenesisRelationshipIds':[e['id'] for e in primary_edges],'originalEditionGlobalProjectionAssertions':0,'ancientInkIndependentlyInspectedAssertions':0})
    result['counts'].update({'individuallyAddressedEntities':len(entities),'totalRelationships':len(relationships),'receivedConditionalLineageRelations':len(native_edges),'receivedConditionalClockRelations':len(clock_links),'receivedSourcePlacements':len(source_placements),'qualifiedIdentityBridges':len(identity_bridges),'originalEditionParentageAssertionsAdmitted':len(primary_edges),'primaryGenesisAgeClaims':len(primary['ageAtBegettingClaims']),'originalEditionGlobalProjectionAssertions':0,'ancientInkIndependentlyInspectedAssertions':0})
    result['discrepancies'].append({'id':'SWETE-APPARATUS-VS-RECEIVED-GREEK400','scope':'Gen11:13, Swete1887 printedp17','qualification':'Swete main430, apparatusE330 andD130. Received Greek_400 is retained, but this inspected apparatus does not corroborate it. Earlier low-resolution D=400 report was an acknowledged reading error; high-resolution image and packet preserve correction.'})
    result['unresolved'].append('Independent original-edition source for inherited Greek_400 and Clementine_Latin timing branches; Swete apparatus D130 is not Greek400.')
    assert len({e['id'] for e in entities})==len(entities)
    assert all(e['source'] in by_id and e['target'] in by_id for e in relationships)
    assert len(clocks)==5 and all(v['completeOriginalWitnessGenealogy'] is False for v in views)
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assert len(primary_edges)==49 and len(source_placements)==15
    assert [len(v['originalEditionParentageAssertions']) for v in views]==[16,17,16]
    assert len({e['id'] for e in relationships})==len(relationships)
    validation={'status':'passed','outputPath':str(OUT.relative_to(ROOT)).replace('\\','/'),'outputSha256':sha(OUT.read_bytes()),'counts':result['counts'],'sourceCommit':commit['sha'],'allEntityIdsUnique':True,'allRelationIdsUnique':True,'allRelationEndpointsAddressed':True,'globalOriginalWitnessProjectionWithheld':True,'finiteEditionClaimsAdmitted':49,'receivedChronologyPlacementsPreserved':15,'SPPostPentateuchEdgesInvented':0,'boundary':'Finite corpus integrity, inherited conditional placements and explicitly scoped edition/transcription readings; not every relation historically or biologically verified.'}
    (BASE/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(validation,ensure_ascii=True,indent=2))

if __name__=='__main__':main()
