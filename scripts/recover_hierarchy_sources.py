"""Bounded, read-only reconstruction of exact ABC origins and separate legion witnesses."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict
from bs4 import BeautifulSoup
import csv
import hashlib
import json
import re
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def main():
    connection = sqlite3.connect('file:' + (ROOT / 'data/sunny.sqlite').as_posix() + '?mode=ro', uri=True)
    connection.row_factory = sqlite3.Row
    spans = []

    def message(mid, label, start=None, end=None):
        row = connection.execute('select m.*,c.title,s.path source_path,s.sha256 source_sha256,s.original_path from messages m join sources s on s.id=m.source_id join conversations c on c.id=m.conversation_id where m.id=?', (mid,)).fetchone()
        assert row is not None, mid
        assert sha(Path(row['source_path']).read_bytes()) == row['source_sha256']
        text = row['text']
        assert sha(text.encode()) == row['content_sha256']
        a = text.index(start) if start else 0
        b = text.index(end, a) if end else len(text)
        quote = text[a:b]
        occurrences = [dict(r) for r in connection.execute('select id,source_id,conversation_id,role,locator,create_time from messages where content_sha256=? order by source_id,id', (row['content_sha256'],))]
        span = {'id': label, 'kind': 'message', 'message_id': mid, 'native_id': row['native_id'], 'conversation_id': row['conversation_id'],
                'conversation_title': row['title'], 'role': row['role'], 'source_id': row['source_id'], 'source_path': row['source_path'],
                'source_sha256': row['source_sha256'], 'message_content_sha256': row['content_sha256'], 'native_locator': row['locator'],
                'native_create_time': row['create_time'], 'display_date_line': text.splitlines()[0], 'char_start': a, 'char_end': b,
                'exact_quote': quote, 'quote_sha256': sha(quote.encode()), 'identical_content_occurrences': occurrences,
                'role_boundary': 'Outer user role may contain pasted analysis; retain inner authorship uncertainty. Historical assistant statements remain proposals/reports, not current user authority or newly verified source facts.'}
        spans.append(span)
        return span

    def document(did, label, start=None, end=None):
        row = connection.execute('select d.*,s.path source_path,s.sha256 source_sha256 from documents d join sources s on s.id=d.source_id where d.id=?', (did,)).fetchone()
        assert row is not None
        assert sha(Path(row['source_path']).read_bytes()) == row['source_sha256']
        text = row['text']; a = text.index(start) if start else 0; b = text.index(end, a) if end else len(text); quote = text[a:b]
        span = {'id': label, 'kind': 'document', 'document_id': did, 'title': row['title'], 'source_id': row['source_id'],
                'source_path': row['source_path'], 'source_sha256': row['source_sha256'], 'char_start': a, 'char_end': b,
                'exact_quote': quote, 'quote_sha256': sha(quote.encode()), 'extractor': row['extractor'],
                'locator_boundary': 'Offsets and quote refer to stored extracted document; original source bytes separately hash-verified.',
                'source_role': 'Recovered research artifact; source statements and imported interpretations are not silently promoted into historical facts.'}
        spans.append(span)
        return span

    direct = message('47c97755b17d92884afd2db1e577f377fdc5c111536d94eecc16a0fbc28e444a', 'USER-PRIMORDIAL-PAIRINGS')
    definitions = message('4cdbd1f7380acf7e276ea4e0121937812b98ab6f50e5da85f8cd6049636f8225', 'ASSISTANT-ABC-DEFINITIONS', '**A. Source-identity orientation**', '## 4')
    accounting = message('28af9b9ea1907696c1b86e0e9ecfb47a024a0675b4d09a84430773bcd63c7eb3', 'USER-SUPPLIED-ABC-ACCOUNTING', 'The F_9 = 34', 'The Dodecad regrouping')
    source_comparison = message('adc72fa87038d1e486d8a57264bd3393fccccf367377d3e676fc7aa1d238caf0', 'HISTORICAL-GENERATIVE-WITNESSES', '# SUN V3', '## 5')
    origin_atlas = document('0c35fcdacccd0ab504638849f6f61b36a6f03e47bd724e0bcaa288d13148ccc3', 'PRIMORDIAL-SOURCE-ATLAS')
    legion_atlas = document('7c31e9933d3bb486b267ba81e9ff3a26faf85f47d1240af791b99e61a5bc6798', 'LEGION-WITNESS-ACCOUNTING', '### 6.2', '## 7')
    chinese = document('eb81c784171cc18b5e848078a93560db4422145033839cfb4ccd5c6bc3134065', 'CHINESE-NATIVE-ORDER-VS-ADAPTER', 'Non-negotiable safeguards', 'Expanded profiles')
    chinese_locked = document('f61d2ead943f3f0632d20ff16109269bf8e20ecd1105f7dac1a0d230f7b9bd67', 'CHINESE-CONDITIONAL-SOURCE-LOCK', 'Result: conditional pass.', '4. The Fludd/Kepler/STCH bridge')

    queries = []
    for query in ['"primordial" AND "A/B/C"', '"functional-unfolding"', '"four-relational-units"', '"legions" AND "2645"', '"legion" AND "2648"', '"Ose" AND "Valac"', '"starting configurations"', '"6ae6a870"']:
        count = connection.execute('select count(*) from search_index where search_index match ?', (query,)).fetchone()[0]
        hits = [dict(r) for r in connection.execute('select id,kind,title from search_index where search_index match ? order by bm25(search_index) limit 8', (query,))]
        queries.append({'query': query, 'match_count': count, 'selected_hit_headers': hits, 'boundary': 'FTS contact is not semantic processing coverage.'})

    source_rows = json.loads((ROOT/'docs/evidence/hierarchy-primary-retrieval.json').read_bytes())['sources']
    source_by_id = {s['id']:s for s in source_rows}
    soups = {}
    for source in source_rows:
        raw = (ROOT/source['path']).read_bytes(); assert sha(raw)==source['sha256']; soups[source['id']]=BeautifulSoup(raw,'html.parser')

    csv_source = connection.execute('select * from sources where id=?', ('db5f0a5687f19c44a5ef3c501a4491d405731e9224163936c69e89d5b3d5737d',)).fetchone()
    csv_bytes = Path(csv_source['path']).read_bytes(); assert sha(csv_bytes)==csv_source['sha256']
    repository_rows=list(csv.DictReader(csv_bytes.decode('utf-8-sig').splitlines()))
    assert len(repository_rows)==72 and [int(r['gate']) for r in repository_rows]==list(range(1,73))
    repo=[int(r['goetic_legions_repo']) for r in repository_rows]
    assert sum(repo)==2648

    def clean(element):
        copy=BeautifulSoup(str(element),'html.parser')
        for sup in copy.find_all('sup'):sup.decompose()
        with_brackets=copy.get_text(' ',strip=True)
        without_brackets=re.sub(r'\[[^\]]*\]','',with_brackets)
        return with_brackets, re.sub(r'\s+',' ',without_brackets).strip()

    witness_rows={}; vectors={}; policies={}
    for key in ['goetia_de_laurence_1916','goetia_peterson_sloane3825']:
        soup=soups[key]
        if key=='goetia_de_laurence_1916':
            nodes=[p for p in soup.find_all('p') if re.match(r'^\(\d+\.?\)',p.get_text(' ',strip=True)) and p.find_previous('h2') and p.find_previous('h2').get_text(' ',strip=True)=='SHEMHAMPHORASH.']
        else:nodes=soup.find_all('p',id=True)
        assert len(nodes)==72
        records=[]
        for i,node in enumerate(nodes,1):
            element=node if key=='goetia_de_laurence_1916' else node.find_parent('td')
            with_brackets,maintext=clean(element)
            matches=list(re.finditer(r'(\d+)\s+Legions?',maintext,re.I))
            assert len(matches)==(2 if i==9 else 1),(key,i,maintext)
            count=int(matches[0].group(1))
            if i==9:assert count==200 and int(matches[1].group(1))==25
            selector={'catalogue_position':i,'paragraph_id':node.get('id'),'section':'SHEMHAMPHORASH' if key=='goetia_de_laurence_1916' else 'catalog', 'main_cell':key!='goetia_de_laurence_1916'}
            records.append({'position':i,'imported_comparison_name':repository_rows[i-1]['demon'],'legions_primary':count,
                            'additional_accompanying_legions':25 if i==9 else None,'selector':selector,
                            'source_text_with_editorial_brackets':with_brackets,'extracted_main_text_sha256':sha(maintext.encode()),
                            'count_context':maintext[max(0,matches[0].start()-85):matches[0].end()+55],
                            'count_policy':'Remove superscript footnote markers and bracketed editorial alternatives for this main reading; choose first direct legion count. Retain brackets/source separately. Paimon secondary25 remains separately typed.'})
        witness_rows[key]=records; vectors[key]=[r['legions_primary'] for r in records]
        policies[key]={'source':source_by_id[key],'count_unit':'primary legion-command count per catalogue chief','primary_row_count':72,'sum':sum(vectors[key]),'distinct_personnel_total':None,'membership_disjointness':'not established'}
    assert sum(vectors['goetia_de_laurence_1916'])==2645
    assert sum(vectors['goetia_peterson_sloane3825'])==2618
    deltas={key:[{'position':i+1,'name':repository_rows[i]['demon'],'repository':a,'witness':b,'delta':b-a} for i,(a,b) in enumerate(zip(repo,vec)) if a!=b] for key,vec in vectors.items()}
    assert [(r['name'],r['delta']) for r in deltas['goetia_de_laurence_1916']]==[('Ose',27),('Belial',-30)]
    assert [(r['position'],r['delta']) for r in deltas['goetia_peterson_sloane3825']]==[(21,6),(41,-27),(45,-1),(62,-8)]

    soup=soups['goetia_de_laurence_1916']; heading=next(h for h in soup.find_all('h3') if 'CLASSIFIED LIST' in h.get_text())
    paragraphs=[]
    for element in heading.next_elements:
        if getattr(element,'name',None)=='h3':break
        if getattr(element,'name',None)=='p':paragraphs.append(element.get_text(' ',strip=True))
    rank_labels=['Kings','Dukes','Princes and Prelates','Marquises','Presidents','Earls or Counts','Knights']; expected=[9,23,7,15,14,10,1]
    rank_groups=[]; memberships=defaultdict(list)
    for label,text,n in zip(rank_labels,paragraphs[:7],expected):
        positions=[int(x) for x in re.findall(r'\((\d+)\.\)',text)]
        assert len(positions)==n
        rank_groups.append({'native_label':label,'member_positions':positions,'membership_occurrences':len(positions),'exact_extracted_paragraph':text,'quote_sha256':sha(text.encode()),'source':'goetia_de_laurence_1916','section':'CLASSIFIED LIST OF THE72CHIEFSPIRITS, ACCORDING TO RESPECTIVE RANK'})
        for p in positions:memberships[p].append(label)
    assert set(memberships)==set(range(1,73)) and sum(map(len,memberships.values()))==79
    dual=[{'position':p,'imported_comparison_name':repository_rows[p-1]['demon'],'rank_memberships':ranks} for p,ranks in memberships.items() if len(ranks)>1]
    assert len(dual)==7

    pairings=[['Aion Teleos','Propator'],['Proarche','Bythos'],['Ennoea','Sige'],['Charis','Thelesis']]
    primordial=[{'id':'PRIM-A','historical_label':'A — source-identity','structure':'Four role-pairings may cross fewer underlying source principles; not four new independently generated beings.','source_identity_groups_as_historically_compared':[['Proarche','Propator','Bythos'],['Ennoea','Charis','Sige']],'generation_claim':'No primordial-to-primordial birth chain follows from alias/role pairing.','source_spans':['USER-PRIMORDIAL-PAIRINGS','ASSISTANT-ABC-DEFINITIONS','USER-SUPPLIED-ABC-ACCOUNTING'],'status':'retained competing source-identity hypothesis; I.1 identity convention supports a local reading, not a global election'},
                {'id':'PRIM-B','historical_label':'B — functional-unfolding','ordered_boundaries':[{'label':'Proarche','address':0},{'label':'Aion Teleios','address':1},{'label':'Bythos','address':1},{'label':'Sige','address':2}],'generation_claim':'Sequential enabling/functional boundaries are proposed; the numbers are not four newborn entity counts or source-proved Fibonacci stages.','source_spans':['USER-PRIMORDIAL-PAIRINGS','ASSISTANT-ABC-DEFINITIONS','USER-SUPPLIED-ABC-ACCOUNTING'],'status':'retained candidate, no source-independent validation'},
                {'id':'PRIM-C','historical_label':'C — four primordial relational units','proposed_pairings':pairings,'generation_claim':'Four distinguishable configurations jointly condition the Ogdoad; joint causation remains to be tested under each witness.','source_spans':['USER-PRIMORDIAL-PAIRINGS','ASSISTANT-ABC-DEFINITIONS','USER-SUPPLIED-ABC-ACCOUNTING'],'status':'retained relational configuration hypothesis; not eight distinct people or an established historical genealogy'}]
    productions=[{'witness':'Irenaeus I.1','inputs':['Bythos','Sige'],'outputs':['Nous','Aletheia'],'relation':'reported seed/reception/production; first tetrad is sourcepair plus generatedpair'},
                 {'witness':'Irenaeus I.1','inputs':['Nous / Monogenes'],'outputs':['Logos','Zoe'],'relation':'reported production; do not silently add Aletheia as equal co-producer'},
                 {'witness':'Irenaeus I.1','inputs':['Logos','Zoe'],'outputs':['Anthropos','Ecclesia'],'relation':'conjunction/production'},
                 {'witness':'Irenaeus I.1','inputs':['Logos','Zoe'],'outputs':['Decad, five named syzygies'],'relation':'later production, sibling branch to Anthropos/Ecclesia'},
                 {'witness':'Irenaeus I.1','inputs':['Anthropos','Ecclesia'],'outputs':['Dodecad, six named syzygies'],'relation':'conjunction/production'},
                 {'witness':'Irenaeus I.11.1','inputs':['Arrhetus','Sige'],'outputs':['Pater','Aletheia'],'relation':'a different reported first/second Dyad'},
                 {'witness':'Irenaeus I.11.3','inputs':['Monotes','Henotes'],'outputs':['Monas / Monad'],'relation':'reported production qualified as not external emanation; coexisting Hen is same essence, not silently inferred child'},
                 {'witness':'Irenaeus I.11.3','inputs':['Monotes','Henotes','Monas','Hen'],'outputs':['remaining company of aeons'],'relation':'four powers jointly produce; distinct source configuration, no automatic PRIM-C identity'},
                 {'witness':'Irenaeus I.12.1','inputs':['Ennoea','Thelesis'],'outputs':['Monogenes / Nous','Aletheia'],'relation':'complementary source powers; Bythos has both consorts; will enables thought'},
                 {'witness':'Irenaeus I.12.3 Colorbasian report','inputs':['Propator','Ennoea'],'outputs':['initial Ogdoad'],'relation':'reported simultaneous production, with reversed Logos/Zoe versus Anthropos/Ecclesia organization; do not merge with I.1 chain'}]
    aeon_groups={'I1-Ogdoad':[['Bythos','Sige'],['Nous','Aletheia'],['Logos','Zoe'],['Anthropos','Ecclesia']],
                 'I1-Decad':[['Bythius','Mixis'],['Ageratos','Henosis'],['Autophyes','Hedone'],['Acinetos','Syncrasis'],['Monogenes','Macaria']],
                 'I1-Dodecad':[['Paracletus','Pistis'],['Patricos','Elpis'],['Metricos','Agape'],['Ainos','Synesis'],['Ecclesiasticus','Macariotes'],['Theletos','Sophia']]}
    assert sum(2*len(x) for x in aeon_groups.values())==30

    report={'schema':'sunny.hierarchy-origin-witness-recovery.v1','created_utc':datetime.now(timezone.utc).isoformat(),
      'current_assignment':{'source_role':'parent attestation of newest direct user steering','scope':'Recover full hierarchy starting alternatives A/B/C through Monad/aeons/archons/angelic/demonic ranks and legions; keep Western/Chinese native enumeration and counting units separate.','boundary':'This bounded recovery is starting evidence for that graph, not a complete hierarchy atlas.'},
      'method':{'Jev_receipt':'docs/evidence/hierarchy-recovery-jev-result.json','actual_model':'jev-1.14.0','choice':'separate_native_source_gates','research_type':'descriptive source reconstruction; not a controlled experiment or systematic literature review','knowledge_depth':'Working: exact origin labels and exposed native count artifacts recovered; full hierarchy membership and mathematical bridge still partial.','canon':['Rank1 for prior conceptual intent: exact direct user message and preserved contextual records.','Rank1 historical witness text: current New Advent digital translations I.1/I.11/I.12; translator/polemical frame retained.','Rank1 source readings: preserved deLaurence1916 digital edition and Peterson Sloane3825 main transcription, distinct from manuscript originals.','Rank3 direct inspection: source-hashed uploaded72CSV; source-locked Chinese research documents.','Historical assistant tables and derived atlases provide retrieval leads and prior claims, not independent corroboration.'],'research_mode_timing':'Relevant Research Methodology/source-verification skills loaded during retrieval; charter is not falsely represented as preregistered before initial FTS.','scope_filter':'Kept only exact primordial definitions, witness-specific generation, command-count/rank units and Chinese native-order distinctions. No flat numerical alignment or historical culprit inference.','object_filter':'A/B/C origin alternatives, TOL A/B, three-voice A/B/C and three legion witnesses are separate namespaces. Excluded ungrounded pairing, total-personnel extrapolation and universal hierarchy claims.','source_fidelity':'Original bytes hash-checked; exact stored source spans include roles/locators/offsets; public main-reading extraction policy explicitly recorded.','initial_corrected_lookup_error':'An initial FTS table guess source_fts failed; schema inspection identified actual search_index. All subsequent retrieval read-only, no database mutation.'},
      'queries':queries,'source_spans':spans,'public_sources':source_rows,
      'primordial_alternatives':primordial,'user_primordial_pairings':{'pairings':pairings,'source_span':'USER-PRIMORDIAL-PAIRINGS','count_unit':'four proposed relational/functional bundles, not eight independently identified primordial entities'},
      'accounting_correction':{'source_span':'USER-SUPPLIED-ABC-ACCOUNTING','statement':'30attested aeons +4primordial functional units =34 is a mixed functional accounting convention; all three alternatives meet this total, so34does not discriminate or prove new entity count.','scope':'The user later supplied this analytical correction. Do not retain the earlier fouradditionalindividuals formulation as established.'},
      'source_native_productions':productions,'I1_source_groups':aeon_groups,
      'I1_accounting':{'aeon_member_positions':30,'syzygy_occurrences':15,'collective_wholes':3,'native_groups':[8,10,12],'boundary':'Different accounting units and graph depths, not extra independent entities. Reused labels such as Monogenes retain contextual position/alias distinctions.'},
      'legion_witnesses':{'axes_independent_of_primordial_ABC':True,'source_dependency_boundary':'The three Goetic count vectors share textual transmission history. They are distinct readings, not three independent empirical confirmations or confidence votes.','uploaded_repository':{'source_id':csv_source['id'],'path':csv_source['path'],'sha256':csv_source['sha256'],'row_count':72,'primary_command_count_sum':2648,'rank_policy':'One imported primary rank per row, not a full native multiple-rank census.'},'public_main_readings':policies,'vectors':{'uploaded_repository':repo,**vectors},'rows':witness_rows,'deltas_from_uploaded_repository':deltas,'controlled_hybrid':{'Ose_alone_3_to_30_sum':2675,'status':'Controlled hybrid of repository plus one reading, not a third complete witness; do not substitute for the three named sourcevectors.'},'count_boundary':'Legion is a command-count unit. Unique personnel, universal legion size, disjoint memberships and absolute global rank order are not established. Paimon200primary and25accompanying are separately retained.'},
      'native_rank_enumeration':{'source':'goetia_de_laurence_1916','groups':rank_groups,'unique_chief_positions':72,'rank_membership_occurrences':79,'distinct_rank_groups':7,'dual_rank_chiefs':dual,'imported_single_primary_rank_counts':dict(Counter(r['goetic_rank'] for r in repository_rows)),'boundary':'A count of rank memberships differs from a count of entities. Listed sequence is not a source-proved total order of ranks; Prince/Prelate and Earl/Count are witness-label conventions.'},
      'Chinese_native_starting_register':{'sources':['CHINESE-NATIVE-ORDER-VS-ADAPTER','CHINESE-CONDITIONAL-SOURCE-LOCK'],'native_production_sequence':['Dao/nebulous void','space-time','primordialqi / One','clearHeaven and turbidEarth','combinedessences / yin-yang','fourseasons','tenthousandthings'],'other_structures':['wuxing field','sheng operator','ke operator','twelvelu generative standards','ganying distributed resonance','human/sage regulator within wanwu'],'address_projection':{'outer_stations':12,'center':'human/sage regulator; not a thirteenthouterstation'},'boundary':'These are recovered research-document assertions, not freshly verified ancient sources. Native production, horizontal/distributed operations and analytic musical addresses remain distinct. Human is not a later creation outside wanwu; LaoziThree is not forced to HeavenEarthHuman.'},
      'Sethian_starting_material':{'source':'PRIMORDIAL-SOURCE-ATLAS','retained_families':['InvisibleSpirit / Monad','Barbelo / Pronoia','fivefoldgroup','Autogenes','fourLuminaries and associatedaeons','Sophia event','Yaldabaoth / archons'],'boundary':'This overview is a prior source-family register, not the complete named critical-edition graph. Parentage and co-occurrences must be recovered per selected recension; listing order is not itself a birth edge. Do not conflate its Monad with the I.11 Monas occurrence.'},
      'source_gaps':[{'id':'FULL-NAMED-HIERARCHY','status':'partial','detail':'ABC origins, thirty I.1positions, three72-vectors and native79rank memberships recovered here. Complete primordial-to-archon-to-angel/demon/legion graph remains to be built from further source-native rows.'},{'id':'CURRENT-SHARE','url':'https://chatgpt.com/share/6ae6a870-f0ac-83e8-a16d-5131a4b2af8b','status':'root retrieval pending at worker checkpoint; no content inferred from failed retrieval or shareID'},{'id':'NEW36FILES','source':'docs/evidence/hierarchy-supplied-input-inventory.json','status':'Root preserving and inspecting supplied originals; this worker does not call them inaccessible or repeat the old image hunt.'},{'id':'SUPERMEMORY-SEARCH','status':'invocation returned tool unavailable to model','receipt':'docs/evidence/hierarchy-supermemory-retrieval-attempt.json','boundary':'No inference of absent account context; no repeated retry loop.'}],
      'verification':{'source_spans_hash_verified':len(spans),'public_source_hashes_verified':5,'uploaded_vector_rows':72,'public_vector_rows_each':72,'vector_sums':[2648,2645,2618],'vector_deltas_match_prior_atlas':True,'rank_unique_entities':72,'rank_membership_occurrences':79,'dual_rank_chiefs':7,'source_account_claim':'Bounded to named selected records and current publictranscriptions; not exhaustive account semantic processing.','database_mutated':False,'new_service_or_browser_started':False},
      'next_action':'Build alternative-aware source-native graph using these distinct origin/witness/count axes, recover remaining named parents/members and original corpus sources, then test musical constraints rather than selecting by totals.'}
    def preserve_previous(path):
        if path.exists():
            previous=path.read_bytes(); history=ROOT/'docs/evidence/history';history.mkdir(parents=True,exist_ok=True)
            snapshot=history/(path.name+'-'+sha(previous)+'.snapshot')
            if snapshot.exists():assert snapshot.read_bytes()==previous
            else:snapshot.write_bytes(previous)
    out=ROOT/'docs/evidence/hierarchy-origin-witness-recovery.json';preserve_previous(out);out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# Hierarchy source register — recovered origins, witnesses and counting units','',
      'This is a source-bound starting register for the current full hierarchy atlas. It recovers the exact A/B/C alternatives and three separate legion witnesses. It does not elect an origin, pair those axes, or declare the complete hierarchy reconstructed.','',
      '## Recovered A/B/C definitions','',
      '| Alternative | Exact structural distinction retained | Status |','|---|---|---|',
      '| A — source-identity | Fewer source principles appear under several names/roles. Four proposed pairings need not be four independently generated beings. | Retained alternative; local I.1 alias convention is not a global election. |',
      '| B — functional-unfolding | Proarche0 → AionTeleios first1 → Bythos second1 → Sige2; successive functional boundaries. | Direct user candidate; numbering is not an attested birth census. |',
      '| C — four relational units | AionTeleos–Propator; Proarche–Bythos; Ennoea–Sige; Charis–Thelesis as four proposed configurations jointly conditioning the next layer. | Joint causation remains an explicit hypothesis per witness. |','',
      'The direct user pairing/candidate message is `47c97755…`, the assistant definition table `4cdbd1f7…`, and the later user-supplied analytical correction `28af9b9e…`. Full IDs, exact quotes, roles, occurrence histories and original-byte hashes are in the [JSON register](../evidence/hierarchy-origin-witness-recovery.json). A pasted analytical passage retains outer user provenance without inventing its inner authorship.','',
      '**Counting correction:** thirty aeons plus four functional primordial bundles is a mixed accounting convention. All three alternatives meet34; that total does not select an alternative or establish four additional people. TOL A/B and experimental three-voice A/B/C remain separate namespaces.','',
      '## Witness-specific upper production','',
      'The current [Irenaeus I.1 translation](https://www.newadvent.org/fathers/0103101.htm) distinguishes Bythos–Sige, Nous–Aletheia, Logos–Zoe and Anthropos–Ecclesia. Logos–Zoe produce the Decad; Anthropos–Ecclesia produce the Dodecad. Keep those branches separate. Its eight/ten/twelve member positions give thirty, with fifteen syzygies and three collective groups as different units. Repeated names retain their contextual identities.','',
      '[I.11](https://www.newadvent.org/fathers/0103111.htm) reports several other arrangements, including Monotes/Henotes, Monas and coexisting Hen; its Monad occurrence is not silently merged with the Sethian Monad. [I.12](https://www.newadvent.org/fathers/0103112.htm) distinguishes Ennoea/Thelesis and reports a simultaneous-Ogdoad account with changed internal ordering. These are reported historical witnesses with a polemical narrator, not interchangeable canonical judgments. Raw digital source bytes and exact extraction contexts are preserved.','',
      '## The three legion witnesses are a separate axis','',
      '| Complete72-row vector | Primary legion-command sum | Recovery |','|---|---:|---|',
      '| Uploaded repository CSV | 2648 | All72original rows read and source-hash checked. |',
      '| [deLaurence1916 digital edition](https://www.gutenberg.org/files/72679/72679-h/72679-h.htm) | 2645 | All72current main readings independently extracted. |',
      '| [Peterson Sloane3825 transcription](https://www.esotericarchives.com/solomon/goetia.htm) | 2618 | All72current main readings independently extracted. |','',
      'The first comparison changes Ose3→30 and Belial80→50. The second changes Morax30→36, Focalor30→3, Vine36→35 and Valac38→30. All remaining primary counts agree with the uploaded vector. Superscript note numbers and bracketed editorial alternatives are excluded from the selected main reading but retained in source context. Paimon’s200primary and25accompanying legions remain separate. The2675one-edit hybrid is not another complete witness. These readings share textual ancestry; they are not independent empirical confirmations. No total here determines disjoint personnel.','',
      '## Native ranks: entities versus membership','',
      '| deLaurence classified group | Membership occurrences |','|---|---:|',
      *['| '+r['native_label']+' | '+str(r['membership_occurrences'])+' |' for r in rank_groups], '',
      '**72unique chiefs,79rank memberships.** Seven chiefs occupy two rank groups: '+', '.join(r['imported_comparison_name'] for r in dual)+'. The uploaded single-primary-rank column collapses those multiple memberships. Keep both representations and their source conventions; do not infer a total ordering of ranks from this table.','',
      '## Chinese enumeration stays native','',
      'The recovered Chinese source-locked documents retain Dao/void → space-time → primordialqi → clearHeaven/turbidEarth → combinedessences/yin–yang → seasons → wanwu. Wuxing, sheng/ke, twelve lü and ganying include horizontal operators, standards and distributed relations, rather than additional births. Human/sage regulation occurs within wanwu. Twelve analytic outer addresses and a center are a separate adapter projection. The early-source calibration excludes later pantheons; those remain additional source work.','',
      '## Next source gates','',
      '- Recover the complete selected-recension Sethian named graph, retaining parentage, association, appointments and jurisdiction separately. The existing primordial atlas is starting material rather than a completed upper hierarchy.','- Build membership/production/rank/command edges from the recovered native rows; preserve all A/B/C alternatives and the three independent witness vectors.','- Inspect the newly supplied36original files under root’s preserved inventory. Their availability supersedes the earlier acquisition gap for those particular inputs.','- Add exact source coverage for remaining angelic/demonic and Western/Chinese structures before any complete-census claim.','',
      'Actual SuperJev `jev-1.14.0` selected separate native source gates. Supermemory retrieval was attempted once and returned unavailable; that is not absent history. Relevant Sacred Timeline and research source methods guard provenance and native units. No service, browser, account-access loop, database write or orientation election occurred.','',
      'Reproduce this bounded recovery with `python -X utf8 scripts/recover_hierarchy_sources.py`. Current public source bytes are already pinned in `docs/evidence/hierarchy-primary-retrieval.json`; this command itself performs no network requests.','']
    readable=ROOT/'docs/reconstruction/HIERARCHY_SOURCE_REGISTER.md';preserve_previous(readable);readable.write_text('\n'.join(lines),encoding='utf-8')
    connection.close()
    print(json.dumps({'result':'PASS','exit_code':0,'source_spans':len(spans),'public_sources':5,'witness_rows_each':72,'sums':[2648,2645,2618],'rank_unique_chiefs':72,'rank_memberships':79,'dual_rank_chiefs':7,'database_mutated':False,'output_sha256':sha(out.read_bytes())}))


if __name__=='__main__':
    main()
