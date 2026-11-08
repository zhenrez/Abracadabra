"""Source-faithful supplemental views; never rewrites the existing hierarchy atlas."""
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import hashlib
import json
import sqlite3

ROOT=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()


def main():
    decision=json.loads((ROOT/'docs/evidence/angelic-supplement-superjev.json').read_text(encoding='utf-8-sig'))
    assert decision['status']=='judged' and decision['answers']['source_extension']['winner']=='separate_classification_and_production_views'
    baseline=ROOT/'state/reconstruction/hierarchy-atlas.json'; baseline_hash=sha(baseline.read_bytes())
    manifest=json.loads((ROOT/'docs/evidence/angelic-primary-retrieval.json').read_bytes())
    sources=[]; evidence=[]; entities=[]; relationships=[]; views=[]
    for s in manifest['sources']:
        if s['status']!=200:continue
        raw=(ROOT/s['path']).read_bytes();assert sha(raw)==s['sha256']
        sid='angelic:'+s['id'];sources.append({'id':sid,**s,'sourceRole':'Current digital transcription, source-reported theology; not an autograph or historical/supernatural truth certificate.'})
        sources[-1]['id']=sid
        soup=BeautifulSoup(raw,'html.parser')
        if s['id'].startswith('pd_'):
            content=soup.select_one('div.book-content');assert content
            for p in content.select('p.normal'):
                clone=BeautifulSoup(str(p),'html.parser')
                for note in clone.select('.mnote,.footnote,.note'):note.decompose()
                text=clone.get_text(' ',strip=True)
                if text:evidence.append({'sourceId':sid,'selector':'p#'+str(p.get('id')),'exact_extracted_text':text,'sha256':sha(text.encode()),'extraction':'DOM text with editorial footnotes removed. Exact extraction text, separately preserved raw HTML.'})
        else:
            for i,p in enumerate(soup.find_all('p')):
                text=p.get_text(' ',strip=True)
                if any(x in text for x in ['Achamoth','Cosmocrator','seven heavens','angels and archangels']):evidence.append({'sourceId':sid,'selector':'p at document index'+str(i),'exact_extracted_text':text,'sha256':sha(text.encode()),'extraction':'Exact normalized DOM paragraph text; original HTML bytes separately pinned.'})
    i4path=ROOT/'data/raw/angelic-primary/irenaeus-i4-web-tool-response.json';i4raw=i4path.read_bytes();i4text=json.loads(i4raw)
    assert isinstance(i4text,str) and 'enthymesis of that Sophia' in i4text
    sources.append({'id':'angelic:irenaeus_i_4_response','title':'Irenaeus I.4, actual successful web-tool source-body response','url':'https://www.newadvent.org/fathers/0103104.htm','path':str(i4path.relative_to(ROOT)).replace('\\','/'),'sha256':sha(i4raw),'kind':'preserved-web-tool-text-response','sourceRole':'Actual retrieved source body; direct HTML request returned403. This hash covers the tool response, not original HTTP bytes.'})
    evidence.append({'sourceId':'angelic:irenaeus_i_4_response','selector':'preserved complete web response','exact_extracted_text':i4text,'sha256':sha(i4text.encode()),'extraction':'Original returned web-tool text retained verbatim, including its page locators.'})
    image=next(x for x in json.loads((ROOT/'state/reconstruction/hierarchy-inputs.json').read_bytes())['occurrences'] if x['sha256'].startswith('7115f189'))
    assert sha((ROOT/image['snapshot']).read_bytes())==image['sha256']
    image_id=image['id'];sources.append({'id':image_id,'title':'User supplied Analysis output6.png','path':image['snapshot'],'sha256':image['sha256'],'kind':'user-supplied-historical-diagram-image','sourceRole':'Image was visually inspected in this worker. Exact column labels recorded; attribution to Fludd is supplied research context, not independently established edition provenance.'})

    db=sqlite3.connect('file:'+(ROOT/'data/sunny.sqlite').as_posix()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
    mid='1347136bc29093c453cac4440816fe6f3ca0bf89b431be11ad7dc753644a2c3b'
    r=db.execute('select m.*,s.path source_path,s.sha256 source_sha256 from messages m join sources s on s.id=m.source_id where m.id=?',(mid,)).fetchone()
    assert sha(Path(r['source_path']).read_bytes())==r['source_sha256'] and sha(r['text'].encode())==r['content_sha256']
    frame=json.loads(r['text']);block=next(x['text'] for x in frame['output'] if isinstance(x.get('text'),str) and 'Yaldabaoth is the first ruler' in x['text'])
    a=block.index('Yaldabaoth is the first ruler');b=block.index('These are the names and the corresponding appearances:',a)
    excerpt=block[a:b]
    source_john='archive:apocryphon-meyer-primary-fragment'
    sources.append({'id':source_john,'title':'Recovered prior primary Meyer translation fragment: Yaldabaoth world order','url':'https://www.gnosis.org/naghamm/apocjn-meyer.html','path':r['source_path'],'sha256':r['source_sha256'],'kind':'archived-original-tool-response','sourceRole':'Recovered actual prior primary text excerpt within a preserved custom_tool_call_output, not an assistant paraphrase or a fresh URL retrieval.','messageId':mid,'messageContentSha256':r['content_sha256'],'nativeLocator':r['locator']})
    evidence.append({'sourceId':source_john,'messageId':mid,'messageRole':r['role'],'messageContentSha256':r['content_sha256'],'jsonPointer':'/output/1/text','decodedCharStart':a,'decodedCharEnd':b,'exact_extracted_text':excerpt,'sha256':sha(excerpt.encode()),'extraction':'Exact decoded original tool-output text span; root JSON-line bytes and native locator separately hash-verified.'})
    db.close()

    def entity(id,name,unit,tradition,witness,refs,**extra):
        row={'id':id,'nativeName':name,'aliases':[],'unit':unit,'tradition':tradition,'witnessId':witness,'position':{'generation':None,'sequence':None,'cyclicCoordinate':None,'orientation':None},'sourceRefs':refs,'exceptions':[],'assertionLayer':'source-assertion',**extra};entities.append(row);return row
    def edge(a,b,t,v,refs,layer='source-assertion'):
        relationships.append({'id':'angelic-rel:'+str(len(relationships)),'source':a,'target':b,'type':t,'viewIds':v,'sourceRefs':refs,'assertionLayer':layer})
    def view(id,label,roots,witness,coverage):views.append({'id':id,'label':label,'roots':roots,'witnessIds':[witness],'coverage':coverage})

    # Classification and transmitted illumination; no genealogical birth or troop command implied.
    pw='Pseudo-Dionysius-CH-VI-IX-CCEL';pv='angelic:Dionysius-native-three-triads'
    entity('pd:classification','Celestial angelic classification','classification-record','Dionysian Christian angelology',pw,['angelic:pd_ch_vi'],exceptions=['A source-defined classification record, not one additional angel.'])
    triads=[['Seraphim','Cherubim','Thrones'],['Dominions','Virtues','Powers'],['Principalities','Archangels','Angels']]
    flat=[n for group in triads for n in group];chapter=['pd_ch_vii','pd_ch_viii','pd_ch_ix'];order_ids={}
    for k,names in enumerate(triads):
        gid='pd:triad:'+str(k+1);refs=['angelic:pd_ch_vi','angelic:'+chapter[k]]
        entity(gid,['First / nearest','Middle','Last / lowest'][k]+' threefold hierarchy','angelic-triad-classification','Dionysian Christian angelology',pw,refs,statedExtent={'value':3,'unit':'angelic-order-classes'},position={'generation':None,'sequence':k+1,'cyclicCoordinate':None,'orientation':None})
        edge('pd:classification',gid,'classifies-threefold-hierarchy',[pv],refs)
        for j,name in enumerate(names):
            oid='pd:order:'+name;order_ids[name]=oid
            entity(oid,name,'angelic-order-class','Dionysian Christian angelology',pw,refs,position={'generation':None,'sequence':k*3+j+1,'cyclicCoordinate':None,'orientation':None},exceptions=['Class/order, not a census of one individual angel.','Sequence is chapter-heading presentation; group hierarchy and illumination are not biological or emanation parentage.','ChapterVI describes the first triad as a coequal unity; no total within-triad generation order is imposed.'])
            edge(gid,oid,'has-angelic-order',[pv],refs)
        if k:edge('pd:triad:'+str(k),gid,'mediates-illumination-to',[pv],['angelic:pd_ch_viii','angelic:pd_ch_ix'])
    edge(order_ids['Principalities'],order_ids['Archangels'],'precedes-in-reported-ministry',[pv],['angelic:pd_ch_ix'])
    edge(order_ids['Archangels'],order_ids['Angels'],'precedes-in-reported-ministry',[pv],['angelic:pd_ch_ix'])
    view(pv,'Pseudo-Dionysius: nine source-native angelic order classes in three triads',['pd:classification'],pw,{'status':'complete-for-nine-declared-order-classes','orderClasses':9,'triads':3,'individualAngelsEnumerated':False,'legionCommandsEstablished':False})

    fw='User-Fludd-Analysisoutput6';fv='angelic:Fludd-image-column-order'
    latin=['Seraphin','Cherubin','Throni','Dominationes','Principatus','Potestates','Virtutes','Archangeli','Angeli']
    aliases=['Seraphim','Cherubim','Thrones','Dominions','Principalities','Powers','Virtues','Archangels','Angels']
    entity('fludd:order-column','Nine angelic labels in supplied central column','diagram-column-record','Fludd-attributed supplied diagram',fw,[image_id],assertionLayer='editorial',exceptions=['Column transcription from the actual supplied image; no independent historical edition attribution.'])
    for i,name in enumerate(latin):
        oid='fludd:order:'+str(i+1)
        entity(oid,name,'diagram-angelic-order-label','Fludd-attributed supplied diagram',fw,[image_id],position={'generation':None,'sequence':i+1,'cyclicCoordinate':None,'orientation':None},assertionLayer='source-assertion',exceptions=['Literal top-to-bottom central column position, not a source-proved birth, troop command or universal rank assignment.'])
        edge('fludd:order-column',oid,'lists-diagram-order-label',[fv],[image_id])
        if i:edge('fludd:order:'+str(i),oid,'precedes-in-diagram-column',[fv],[image_id])
        edge(oid,order_ids[aliases[i]],'proposed-textual-label-correspondence',['comparison:Fludd-Dionysius-labels'],[image_id,'angelic:pd_ch_vi','angelic:'+chapter[flat.index(aliases[i])//3]],'research-hypothesis')
    view(fv,'Supplied Fludd image: literal nine-label central column',['fludd:order-column'],fw,{'status':'complete-for-visible-nine-label-column','editionProvenanceIndependentlyVerified':False,'nativeTriadPartitionInferred':False,'angelLegionCommands':False})
    views.append({'id':'comparison:Fludd-Dionysius-labels','label':'Proposed lexical correspondences; records remain distinct','roots':['fludd:order-column','pd:classification'],'witnessIds':[fw,pw],'coverage':{'status':'explicit-comparison-hypothesis','identityMerge':False,'musicalOperatorProved':False}})

    # Irenaeus's lower Valentinian account is not automatically the Sethian Yaldabaoth account.
    iw='Irenaeus-I.4-I.5-NewAdvent';iv='archonic:Irenaeus-Achamoth-Demiurge'
    s4='angelic:irenaeus_i_4_response';s5='angelic:irenaeus_i_5'
    native=[('upper-Sophia','Sophia who dwells above','source-named-aeon',[s4]),('Achamoth','Achamoth / Enthymesis of Sophia','source-named-enthymesis',[s4,s5]),('Demiurge','Demiurge','source-named-creator',[s5]),('Cosmocrator','Cosmocrator','source-named-world-ruler',[s5]),('created-angels','Angels created by the Demiurge','source-reported-angelic-collective',[s5]),('created-archangels','Archangels created by the Demiurge','source-reported-angelic-collective',[s5]),('seven-heavens','Seven intelligent heavens, spoken of as angels','source-reported-jurisdiction-collection',[s5]),('wicked-spirits','Demons/angels/spirits of wickedness from grief','source-reported-spiritual-collective',[s5]),('grief','Achamoth grief','source-reported-passion',[s5]),('Paradise','Paradise / fourth angel above third heaven','source-named-jurisdiction',[s5])]
    for key,name,unit,refs in native:entity('i45:'+key,name,unit,'Valentinian reported by Irenaeus',iw,refs,exceptions=['Source-role record scoped to I.4–5; matching names across recensions are not silently identified.'])
    by_id={x['id']:x for x in entities}
    by_id['i45:Achamoth']['aliases']=['Sophia (after the upper Sophia)','Holy Spirit','Ogdoad','Terra','Jerusalem','Lord (masculine reference)']
    by_id['i45:Achamoth']['exceptions']+=['I.4calls upperSophia herfather inname-etiology and hermother/firstSophia later. Preserve both textual role expressions without forcing a biological-sex model.','Do not collapse upperSophia andAchamoth solely because the latter is also calledSophia.']
    by_id['i45:Demiurge']['aliases']=['Metropator','Apator','Father','Hebdomas']
    by_id['i45:Demiurge']['exceptions']+=['Source both describes him above the seven heavens and as dwelling in the heavenly/hebdomad place; no single numeric coordinate is imposed.']
    by_id['i45:Cosmocrator']['aliases']=['devil (this source account)']
    by_id['i45:seven-heavens']['statedExtent']={'value':7,'unit':'source-reported-heavens'}
    edge('i45:upper-Sophia','i45:Achamoth','reported-origin-of-enthymesis',[iv],[s4])
    edge('i45:Achamoth','i45:Demiurge','forms-from-animal-substance',[iv],[s5])
    for name in ['created-angels','created-archangels','seven-heavens']:edge('i45:Demiurge','i45:'+name,'creates-reported-collective',[iv],[s5])
    edge('i45:Demiurge','i45:Cosmocrator','creates-named-creature',[iv],[s5])
    edge('i45:Achamoth','i45:grief','has-reported-passion',[iv],[s5]);edge('i45:grief','i45:wicked-spirits','reported-origin-from-passion',[iv],[s5])
    edge('i45:seven-heavens','i45:Paradise','reported-related-heavenly-location',[iv],[s5])
    view(iv,'Irenaeus I.4–5: upperSophia / Achamoth / Demiurge and lower creations',['i45:upper-Sophia'],iw,{'status':'bounded-source-native-opening-bridge','sevenHeavensNamedIndividually':False,'allAngelsNamed':False,'GoeticJoinEstablished':False})

    jw='Apocryphon-John-Meyer-recovered-primary-fragment';jv='archonic:John-Meyer-twelve-authorities'
    names=['Athoth','Harmas','Kalila-Oumbri','Yabel','Adonaios','Cain','Abel','Abrisene','Yobel','Armoupieel','Melcheir-Adonein','Belias']
    assert all(name in excerpt for name in names)
    entity('john:Yaldabaoth','Yaldabaoth','source-named-ruler','Apocryphon of John',jw,[source_john],aliases=['Sakla','Samael'],exceptions=['Aliases occur in this actual recovered primary excerpt; no equation with Irenaeus Demiurge or Goetic chiefs is imposed.'])
    entity('john:authorities','Twelve named authorities','source-reported-authority-collection','Apocryphon of John',jw,[source_john],statedExtent={'value':12,'unit':'named-authority-list-positions'})
    edge('john:Yaldabaoth','john:authorities','produces-authority-collection',[jv],[source_john])
    for i,name in enumerate(names):
        e=entity('john:authority:'+str(i+1),name,'source-named-authority-position','Apocryphon of John',jw,[source_john],position={'generation':None,'sequence':i+1,'cyclicCoordinate':None,'orientation':None},exceptions=['List position, not automatic assignment to a particular heaven or abyssal office.'])
        if i==4:e['aliases']=['Sabaoth (this list occurrence)']
        if i==5:e['exceptions'].append('Source calls thisCain the sun; no automatic identity with GenesisCain or a musical pitch.')
        edge('john:authorities',e['id'],'has-listed-authority',[jv],[source_john])
    for key,label,n,unit in [('heaven-kings','Kings stationed over seven heavens',7,'reported-heavenly-king-offices'),('abyss-kings','Kings stationed over depth of abyss',5,'reported-abyssal-king-offices'),('seven-powers','Powers created by rulers',7,'reported-power-count'),('angels-365','Angels, stated total365',365,'reported-angel-count')]:
        entity('john:'+key,label,'source-reported-jurisdiction-or-power-collection','Apocryphon of John',jw,[source_john],statedExtent={'value':n,'unit':unit},exceptions=['Collection/extent reported by text; no invented individual names or uniquely assigned catalogue identities.'])
    edge('john:Yaldabaoth','john:heaven-kings','appoints-jurisdictional-collection',[jv],[source_john]);edge('john:Yaldabaoth','john:abyss-kings','appoints-jurisdictional-collection',[jv],[source_john])
    edge('john:authorities','john:seven-powers','reported-rulers-create-powers',[jv],[source_john]);edge('john:seven-powers','john:angels-365','reports-six-apiece-and-total365',[jv],[source_john])
    entity('john:underworld-depth','Depth of underworld','source-named-jurisdiction','Apocryphon of John',jw,[source_john]);edge('john:authority:12','john:underworld-depth','rules-reported-jurisdiction',[jv],[source_john])
    view(jv,'Recovered native ApocryphonJohn passage: Yaldabaoth and twelve authority names',['john:Yaldabaoth'],jw,{'status':'complete-for-selected-twelve-name-list-in-archived-primary-excerpt','freshLivePageRetrieved':False,'upperMonadAeonsConnected':False,'namedSevenFivePartitionResolved':False,'GoeticJoinEstablished':False})

    supplement={'schema':'sunny.angelic-hierarchy-supplement.v1','generated_utc':datetime.now(timezone.utc).isoformat(),'decisionReceipt':'docs/evidence/angelic-supplement-superjev.json','sources':sources,'entities':entities,'relationships':relationships,'views':views,'sourceEvidence':evidence,
      'visualTranscription':{'sourceId':image_id,'sourceSha256':image['sha256'],'region':'central column, nine labels abovePrimumMobile','topToBottomLabels':latin,'inspectedBy':'/root/continuation_guard with actual view_image tool','boundary':'No hidden-label OCR, triad partition or historical edition provenance inferred.'},
      'comparison':{'kind':'conditional-lexical-comparison','DionysiusHeadingPresentation':flat,'FluddColumnUnderProposedAliases':aliases,'permutationIntoDionysiusHeadingPositions':[flat.index(x)+1 for x in aliases],'nontrivialPositionExchange':[5,7],'boundary':'Under proposed translations, source-column positions5/7exchange. Not a proved musical operator, individual identity, within-triad birth order or deliberate historical alteration.'},
      'discrepancies':[{'sourceId':source_john,'reportedPowers':7,'reportedAngelsPerPower':6,'reportedTotalAngels':365,'oneGenerationProduct':42,'status':'Aggregation/generation rule not supplied by this excerpt. Preserve all reported quantities; do not force42=365, invent a recurrence or discard the witness.'}],
      'externalJoinCandidates':[{'sourceEntityId':'i1:I1-Dodecad:12','targetEntityId':'i45:upper-Sophia','type':'proposed-shared-source-narrative-role','assertionLayer':'research-hypothesis','sourceRefs':['angelic:irenaeus_i_4_response'],'boundary':'I.4explicitly speaks ofSophiaabove/firstSophia; comparison to the I.1Dodecad source-role remains declared, not an automatic cross-source entity merge.'}],
      'unresolved':['Full individual angel population/rankmembership is not enumerated by nineorderclasses.','The complete SethianMonad-to-aeon-to-Sophia chain remains beyond the recovered lower passage.','Which named authority occupies each of sevenheavens/fiveabyss offices is not assigned merely by listorder.','No source-native Goetic72join to these angelic/archonic structures is established.','Fludd diagram edition attribution and a lawful musical transform between its order-column and Dionysian grouping need additional evidence.'],
      'baselineAtlasNotMutated':{'sha256Before':baseline_hash,'sha256After':sha(baseline.read_bytes()),'same':sha(baseline.read_bytes())==baseline_hash},'coverage':{'completeUniversalHierarchy':False,'DionysiusOrderClasses':9,'DionysiusTriads':3,'FluddVisibleOrderLabels':9,'JohnSelectedNamedAuthorities':12,'allCrossSourceIdentitiesResolved':False}}
    assert supplement['baselineAtlasNotMutated']['same'] and len({e['id'] for e in entities})==len(entities)
    ids={e['id'] for e in entities};sids={s['id'] for s in sources};vids={v['id'] for v in views}
    assert all(r['source'] in ids and r['target'] in ids and set(r['sourceRefs'])<=sids and set(r['viewIds'])<=vids for r in relationships)
    assert all(set(e['sourceRefs'])<=sids for e in entities)
    out=ROOT/'state/reconstruction/angelic-hierarchy-supplement.json';out.write_text(json.dumps(supplement,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'docs/reconstruction/ANGELIC_HIERARCHY_SUPPLEMENT.md').write_text('# Native angelic and archonic source supplement\n\nThis separate source-bound graph adds nine Dionysian order classes in three triads, the nine literal Fludd-image column labels, a bounded IrenaeusI.4–5lower production chain, and twelve authority names from an actual preserved primary ApocryphonJohn excerpt. It does not alter the baseline atlas or establish a Goetic join.\n\nDionysian hierarchy describes classification and transmission of illumination. These edges are not birth or command relations. The image labels remain a separate witness: under explicitly proposed lexical correspondences, Principalities/Virtues exchange presentation positions5and7. The source does not prove an equivalent musical operator or a deliberate alteration.\n\nIrenaeusI.4distinguishes upperSophia fromAchamoth/Enthymesis; I.5connectsAchamoth toDemiurge, his angelic creations, sevenintelligentheavens andCosmocrator. The recovered ApocryphonJohn passage names twelveauthorities and reports sevenheaven/fiveabyss appointments without identifying that partition by listorder. It also reports sevenpowers, sixangelsapiece and365angels; the missing aggregation rule remains explicit.\n\nCurrent liveJohnlong retrieval failed; the twelve-name source is an archived original tool-output passage, with exact messageJSONpointer, native locator, sourcebyteshash and excerpt retained. I.4is pinned as the actual web-tool body because a directHTML request returned403. Other new primarypages have originalHTMLbytes and hashes. The supplied image was visually read directly.\n\nMerge the sources/entities/relationships/views arrays as separate views. Proposed textual correspondences stay hypotheses; names, populations, parentage, rankmembership, jurisdiction and command are distinct dimensions.\n',encoding='utf-8')
    print(json.dumps({'result':'PASS','exit_code':0,'views':len(views),'entityRecords':len(entities),'relationships':len(relationships),'sourceRecords':len(sources),'DionysiusClasses':9,'FluddLabels':9,'JohnNamedAuthorities':12,'baselineUnchanged':True,'sha256':sha(out.read_bytes())}))


if __name__=='__main__':main()
