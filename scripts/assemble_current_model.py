"""Assemble the recovered current research state without electing new correspondences."""
from pathlib import Path
from datetime import datetime,timezone
import collections,hashlib,json,sqlite3
ROOT=Path(__file__).resolve().parents[1];STATE=ROOT/'state/reconstruction';DOC=ROOT/'docs/reconstruction'
def load(path):return json.loads(path.read_text(encoding='utf8'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def md(value):return str(value if value is not None else '').replace('|','\\|').replace('\n',' / ').replace('<','&lt;').replace('>','&gt;')
def table(headers,rows):return '\n'.join(['| '+' | '.join(map(md,headers))+' |','| '+' | '.join('---' for _ in headers)+' |']+['| '+' | '.join(map(md,row))+' |' for row in rows])
def file_link(path,label,line=None):return '['+label+'](<'+str(path.resolve())+((':'+str(line)) if line else '')+'>)'

def main():
    DOC.mkdir(parents=True,exist_ok=True)
    names=['decisions','music-geometry','correspondences','tables','alignment']
    modules={name:load(STATE/(name+'.json')) for name in names}
    execution_names=['coverage','native-derivations','orientation-predictions','tol-history-math',
                     'native-execution','generational-constraints','algebraic-extension',
                     'derived-laws','master-score','hierarchy-atlas-combined','contextual-alignment','symbol-sound-constraints','score-anchor-constraints','phonological-context-constraints','phonological-history-constraints','reading-operations',
                     'indian-hierarchy','western-expanded','chinese-expanded','native-class-constructors','biblical-genealogies','upper-legion-color-constraints']
    execution={name:load(STATE/(name+'.json')) for name in execution_names}
    database=sqlite3.connect((ROOT/'data/sunny.sqlite').as_uri()+'?mode=ro',uri=True);database.row_factory=sqlite3.Row
    indexed={r['id']:dict(r) for r in database.execute('SELECT * FROM sources')}
    source_records=collections.defaultdict(list)
    for r in modules['music-geometry']['records']:
        for sid in r['source_refs']:source_records[sid].append({'module':'music-geometry','record_id':r['id']})
    for r in modules['decisions']['records']:
        for occurrence in r['source_occurrences']:source_records[occurrence['source_id']].append({'module':'decisions','record_id':r['id']})
    for citation in modules['correspondences']['citations']:source_records[citation['source_id']].append({'module':'correspondences','citation_id':citation['id']})
    for v in modules['tables']['versions']:
        for alias in v['aliases']:source_records[alias['id']].append({'module':'native_tables','workbook':v['file']})
    for t in modules['alignment']['tables']:
        for occurrence in t['occurrences']:source_records[occurrence['source_id']].append({'module':'alignment','record_id':t['id']})
    for frame in modules['alignment']['csv_frames']:source_records[frame['source_id']].append({'module':'alignment','frame':frame['name']})
    def referenced_source_ids(value):
        if isinstance(value,str):
            if value in indexed:yield value
        elif isinstance(value,list):
            for item in value:yield from referenced_source_ids(item)
        elif isinstance(value,dict):
            for item in value.values():yield from referenced_source_ids(item)
    for name,value in execution.items():
        # Corpus inventory contact is not a mathematical citation.
        if name=='coverage':continue
        for sid in sorted(set(referenced_source_ids(value))):
            source_records[sid].append({'module':'mathematical_execution','unit':name,'binding':'Exact source identifier in execution artifact; not semantic identity or independent corroboration.'})
    graph_source_ids={s['id'] for s in execution['hierarchy-atlas-combined']['sources']}
    registration=load(ROOT/'docs/evidence/hierarchy-source-registration.json')
    for binding in registration['mapping']:
        if binding['graph_source_id'] in graph_source_ids:
            source_records[binding['database_source_id']].append({'module':'hierarchy-atlas-combined',
              'graph_source_id':binding['graph_source_id'],'binding':'Exact graph-to-database source occurrence; no identity, authorship or historical-truth promotion.'})
    missing=sorted(set(source_records)-set(indexed))
    if missing:raise ValueError('Unresolved source IDs in current model: '+str(missing))
    sources=[{**indexed[sid],'referenced_by':refs} for sid,refs in sorted(source_records.items())]
    native=[load(Path(t['path'])) for t in modules['tables']['tables']]
    alignment=[load(Path(t['path'])) for t in modules['alignment']['tables']]
    asof=datetime.now(timezone.utc).isoformat()
    current={'schema':'sunny.current-reconstructed-model.v1','assembled_utc':asof,'user_deadline':'2026-10-31 America/Phoenix','research_horizon':'Through October29 source events, preserved in October30 exports, plus October30 SUNNY specification and current user corrections.','status':'assembled_pending_independent_fidelity_verification','goal':'Catch the reconstructed model up to the user\'s current progress; preserve retained gains and exact open branches, not a new empty model.','selection_evidence':['docs/evidence/reconstruction-priority-superjev.json','docs/evidence/reconstruction-alignment-superjev.json','docs/evidence/reconstruction-presentation-superjev.json'],'module_snapshots':[{'module':n,'path':str(STATE/(n+'.json')),'sha256':digest(STATE/(n+'.json'))} for n in names],'components':modules,'native_workbook_tables':native,'alignment_source_tables':alignment,'source_evidence_index':sources,'integration_rules':['All original native objects, operators, witnesses and statuses remain intact.','Current explicit user corrections govern the reconstructed research position; inherited assistant results remain reports unless their stronger status is actually sourced.','GEN, MEM, TIME, ADR, FUNC and TRN are recovered axes, not a newly imposed domain ontology.','Each address is qualified by source, frame, register, generation and proposed transformation.','Shared source IDs establish provenance links, not semantic identity or independent corroboration.','No row-index-only join, unique absolute orientation, missing class derivation, historical fact or physical law is invented.','Whole-account semantic completeness and the unretrieved twenty-image extraction remain explicit boundaries.'],'unavailable_latest_inputs':load(ROOT/'docs/evidence/reconstruction-image-search.json'),'image_retrieval_attempt':load(ROOT/'docs/evidence/reconstruction-image-fetch.json')}
    current['status']='accessible_current_state_materialized; fidelity result is a separate hash-bound report'
    current['goal']='Execute the current SUNNY Jev Reconstruction and Predictive Derivation Mandate; reconstruct mathematics and lawful consequences from the retained whole research state.'
    current['mathematical_execution']=execution
    current['current_activity_date']='2026-11-07 America/Phoenix'
    current['user_deadline']='2026-11-07 America/Phoenix'
    current['current_delivery']={'plan':'docs/delivery-2026-11-07/PLAN.md',
      'acceptance':'state/delivery-2026-11-07/acceptance.json',
      'interactive_view':'web/delivery-2026-11-07/index.html',
      'deadline':'2026-11-07 America/Phoenix',
      'boundary':'All sixteen goals and eight complete mathematical deliverables remain required; visual implementation does not establish scientific completion.'}
    current['research_horizon']='Recovered archive through the retained October source events, current sixteen-goal user direction, source-qualified November2 research packets and the November7 source-conditioned timing-anchor extension. New public research is separately snapshot-bound; whole-corpus semantic completeness is not asserted.'
    mission=load(ROOT/'state/mission.json')
    current['current_goal_semantics']={'path':'state/mission.json','schema':mission['schema'],
      'goals':mission['goals'],'governing_dependency':mission['governing_dependency'],
      'working_premises':mission['working_premises'],'musical_bridge_policy':mission['musical_bridge_policy'],
      'boundary':'Latest scientific requirements retained independently of historical source positions and transient process status.'}
    current['execution_module_snapshots']=[{'module':n,'path':str(STATE/(n+'.json')),'sha256':digest(STATE/(n+'.json'))} for n in execution_names]
    current['current_mandate']=load(ROOT/'docs/evidence/mandate-adoption.json')
    current['active_hierarchy_direction']={'path':'state/hierarchy-direction.md','sha256':digest(ROOT/'state/hierarchy-direction.md'),
      'input_occurrences':'state/reconstruction/hierarchy-inputs.json','source_registration':'docs/evidence/hierarchy-source-registration.json',
      'interactive_view':'deliverables/SUNNY_Hierarchy_Atlas.html',
      'status':'Bounded source reconstruction and expandable census; full upper-to-lower universal joins remain unresolved.'}
    current['mathematical_acceptance']='Partial conditional reconstruction; comprehensive Mission I and independent blind Mission II are not complete.'
    current['mandated_output_status']=[
        {'output':'Native mathematical register','status':'partial_executable',
         'units':['native-execution','native-derivations','algebraic-extension','tol-history-math'],
         'remaining':'Every applicable native system and complete compositional/instrumental law.'},
        {'output':'Transformation register','status':'partial_executable',
         'units':['native-derivations','tol-history-math','algebraic-extension','generational-constraints'],
         'remaining':'Literal TOL A/B, all source adapters, domains, inverses and cross-system residuals.'},
        {'output':'Generational reconstruction','status':'conditional_constraints_executable',
         'units':['generational-constraints'],
         'remaining':'Complete class transitions, changing breadth, radius/rebound and four-dimensional realization.'},
        {'output':'Global constraint system','status':'partial_candidate_system',
         'units':['orientation-predictions','generational-constraints','derived-laws'],
         'remaining':'Independent global orientation selectors and all native interacting constraints.'},
        {'output':'Proof and derivation ledger','status':'source_conditional_proofs_and_experiments',
         'units':['native-derivations','orientation-predictions','tol-history-math','algebraic-extension','generational-constraints'],
         'remaining':'Proof or localization of every reconstructed mathematical claim; corpus-wide coverage.'},
        {'output':'Discrepancy and missing-component register','status':'partial_localized_counterexamples',
         'units':['native-derivations','tol-history-math','algebraic-extension','generational-constraints'],
         'remaining':'All manuscript, language, calendar and representation discrepancies with discriminating consequences.'},
        {'output':'Representation-independent prediction mechanism','status':'conditional_finite_family_engine',
         'units':['orientation-predictions'],
         'remaining':'Source-proved adapters for arbitrary anchors and independently preregistered withheld-target evaluation.'},
        {'output':'Complete executable master score','status':'partial_source_views_executable',
         'units':['master-score','native-execution'],
         'remaining':'Complete orchestration, timing, instrumentation, succession and lawful global interactions.'}
    ]
    for output in current['mandated_output_status']:
        if output['output'] in ['Native mathematical register','Transformation register','Generational reconstruction','Proof and derivation ledger','Discrepancy and missing-component register']:
            output['units'].extend(['native-class-constructors','indian-hierarchy','western-expanded','chinese-expanded'])
        if output['output'] in ['Global constraint system','Discrepancy and missing-component register']:
            output['units'].extend(['biblical-genealogies','upper-legion-color-constraints'])
        if output['output']!='Generational reconstruction':
            output['units'].extend(['contextual-alignment','symbol-sound-constraints','phonological-context-constraints','phonological-history-constraints','reading-operations'])
        output['units'].append('score-anchor-constraints')
        if output['output']=='Representation-independent prediction mechanism':
            output['status']='conditional_linear_anchor_and_finite_family_engine'
    current['integration_rules'].append('Recovered, reproduced, extended and predictively discriminating results remain separate; model preferences do not establish mathematical truth.')
    for previous in (STATE/'model.json',DOC/'CURRENT_MODEL.md'):
        if previous.exists():
            raw=previous.read_bytes();sha=hashlib.sha256(raw).hexdigest()
            saved=ROOT/'state/checkpoint-history'/('before-math-'+previous.name+'-'+sha+'.snapshot')
            saved.parent.mkdir(exist_ok=True)
            if saved.exists():
                if saved.read_bytes()!=raw:raise ValueError('Immutable previous-model snapshot mismatch')
            else:saved.write_bytes(raw)
    (STATE/'model.json').write_text(json.dumps(current,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
    def show(identifier,title):
        data=next(t for t in alignment if t['id']==identifier);origin=data['occurrences'][0]
        return '\n'.join(['### '+title,'',table(data['headers'],data['rows']),'',f"Retained {origin['role']} table, {identifier}; "+file_link(Path(origin['source_path']),'exact source',origin['line_start'])+'. Its original frame and status remain attached.',''])
    text='''# SUNNY — reconstructed current model

The current user-adopted Jev Reconstruction and Predictive Derivation Mandate governs this connected reconstruction. The model retains the accessible research and now executes source-bound musical operations, transformations, conditional predictions and generational constraints. Mission I remains incomplete: source fidelity, mathematical reproduction, new derivation and independent blind prediction are distinct accomplishments.

The organizing object is the conductor's master score: parts, performers, instruments, notes, registers, entrances, durations, overlap, sequence, transformations and coordinated generational structure. SUNNY preserves relevant SUN, SOL, SOFI and adjacent branch histories without importing their separate epistemological missions. The current source-backed executable score is a partial instantiation; missing timing, assignments and cross-system laws remain explicit.

Start with the executed mathematical register below and its linked derivations. The older source-native frames and later corrections remain attached. For continuation after a context change, read CONTINUE.md and verify the task checkpoint against the current artifacts.

## Current symbol and sound constraint execution

The active dependency is symbol/sound, language, grammar and reproducible source readings before revised hierarchies and calendrical/zodiacal rectification. All sixteen goals and the complete musical/geometric working premises remain governing. Historical forensics and external prior-art research support this work in parallel.

The new source-conditioned contextual-alignment module is executable via `node scripts/execute_contextual_alignment.mjs`. The proposed common-gong adapter has zero solutions: its three-equation cycle has residue4 modulo12, and deleting any one equation leaves12 solutions. The separate-modal interpretation preserves all12 origin frames across all12 selected ritual prescriptions, with144 modular checks and four ancestral exact rational/register checks. This reuses known interpretive prior art; it does not elect an ancient reading, absolute frequency, global orientation or sacred phonetic system.

Read [the executed result](CONTEXTUAL_ALIGNMENT.md) and `state/reconstruction/contextual-alignment.json`. The module retains native source conditions, the rejected hypothesis, the surviving family, explicit register/comma limits, conditional predictions and a partial score fragment. It contributes to seven connected registers without claiming any comprehensive output complete or substituting a twelve-state carrier for full music. Input bytes are preserved in content-addressed snapshots.

The executable [symbol/sound constraint case](SYMBOL_SOUND_CONSTRAINTS.md) retains two mark-grammar interpretations with an identical seven-context consonantal-realization projection. Those observations alone cannot distinguish the interpretations. Three source-qualified final cases reject the universal dotted-consonant rule under Khan's reconstruction. Four current publisher XML tokens have replayed byte spans and U+05BC marks; shared transcription ancestry does not establish independent manuscript support. Duration, Hz, waveform and original intended sound remain unknown. The alternatives execute as three added score views; membership occurrences and distinct source IDs remain separate. Provider-account attribution of saved Jev responses remains unverified; no new inference was performed for this case.

## Retained hierarchy atlas

The retained hierarchy census remains part of the full deliverables. The offline SUNNY_Hierarchy_Atlas.html exposes A/B/C origin alternatives, the three independently selected legion witnesses, separate Western and Chinese musical source views, angelic classifications and bounded archonic relationships. The underlying graph preserves9,493witness/context records:1,582non-slot records and7,911explicitly generated anonymous legion-command membership slots across22views. Neither count is a global census of unique beings, legions, instruments or personnel.

The three72-chief catalogue vectors reconcile2,648/2,645/2,618primary legion-command attributions. Their pairing with A/B/C remains unestablished. Native deLaurence classification retains79rank memberships across72chiefs; seven chiefs have two ranks. The generated lower slots make every stated command attribution addressable while leaving individual names, cross-command identity and unique personnel unknown.

The musical supplement has1,141typed records, including686explicitly derived context/membership occurrences, and1,608typed relationships. Its Western hierarchy follows identified image witnesses and declared rules. Chinese generation, seasonal order,7/5upper/lower,6/6yin/yang, five tone functions, eight materials and the separately sourced60-context analytical model remain different native relations. This is bounded reconstruction of those witnesses, not a complete census of every Western or Chinese musical tradition.

Production, partnership, membership, command, succession and proposed correspondences retain their relationship types. The viewer's unrestricted trace means upstream relationships; its production-only filter excludes co-generated partners as parents. Unknown Monad/ancestral joins, complete named lower populations and Goetic-to-archonic links remain localized gaps. The two Greek hierarchies remain subsequent work.

## The current connected state

The retained Chinese–Western musical bridge is part of the starting state. Its repeated omission was directly corrected by the user. Scalar construction, Chinese pipe generation, Western realization, Fludd/Kepler relations, the81/80comma and16/15boundary excursion remain available within their documented conditions. They are not discarded because a different global coordinate is still open.

Sophia's upper-registerF, Yaldabaoth's lower-registerF at the octave seam, and Sabaoth's lower-registerC/fifth are retained working locks. Chromatic address, fifth-cycle address, generation, institutional order and heaven numbering are separate coordinates; their unresolved conversions do not erase the pitch/register relation.

The later correction adds Sophia at12→new0/midnight→13. Thirteen is a stacked/Theodorus lift at the Scorpio–Ophiuchus–Sagittarius boundary, not another thirteenth Shem angular slice. The Earth/aether overlap, Chinese Earth-to-Metal handoff and Western Water-to-Fire passage retain their source-specific frames. Earlier descriptions locating the relevant lift at Virgo must not silently return as the current position.

The user's later assertion that Sagittarius is Earth in the cross-system alignment is retained explicitly. The earlier assistant tables below label Western Sagittarius Fire and ChineseShenMetal under their respective frames; those labels do not overwrite the user's Earth association or settle the combined alignment. See DEC-sophia_midnight_correction / C034 and their exact source quotation.

By October30 the user reports a successful three-axis SriYantra integration: the outer square becomes a tesseract, the bindu a Sierpinski tetrahedron at infinitum, the construction yields the sought dodecahedron, and aeons function as enabling fields outward from the bindu. That reported discovery is part of the current model, rather than being reduced to an unworked geometry premise. The reconstruction retains the report and its role; it does not claim a newly reproduced proof. See corr-claim-013 and its exact October30 user source.

The Sophia/Yaldabaoth/Samael/Sakla and Adam/Cain/Abel/Seth comparison retains its generative and functional branches. Phaethon/Yaldabaoth–Cronus, Samael–Zeus and Sakla–Saturn remain a qualified candidate chain; the alternative Gaia/Cronus/Saturn reading is not erased. Names, offices, actors, manifestations, stages and addresses are not flattened into one identity.

The user's earlier Adam0-as-1, Evefirst1, Abelsecond1, Cain2, Seth3 sequence remains exact. The nine-triangle/27-plus-retained3 hunch and possible male/female5+7 versus Chinese6+6 remain questions where the user phrased them conditionally. The later name scratchpad is not falsely presented as the recovery of the thought lost before that list.

## Native music and operations already in the model

The recovered native graph contains364music-native vertices across71source-native systems,117empirical hyperedges,312incidences,67family-projection receipts,10generative mechanisms and12constitutive relation types. The22-entry alphabet retains three constructors, seven transitions and twelve relations; observer expectation stays separate. These are recovered source objects with their original coverage/status fields, not a claim that this run independently proved every historical or physical assertion.

The operational distinctions include scalar multiplication; dihedral pitch action; reversal; partial shared-pitch/address mutation; cyclic rotation; Euclidean onset construction; modular Boolean sieves; local added duration; jointly constituted hyperedges; and conditional next-event kernels. Pitch-ratio operations do not replace duration, address, timbre, rhythm or joint-constitution operations.

Chinese length generation81→54→72 and corresponding frequency order8→12→9 remain process ordered; sorting the8:9:12sonority does not erase how it was generated. Twelve pipes, five tone-position functions, rotatinggong, distinctT/ttransforms and eight material/sound classes remain separate. Their12×5formal contexts are not relabeled60historical pipes.

The source-locked Chinese functional Tree adapter retains Dao; primordialqi; Heaven/yang; Earth/yin; yin-yang relation; sheng; ke; harmonizedwuxing; seasonal recurrence; twelvelü; ganying; wanwu; and human/sage regulation. Its conditional functional result survives alongside the rejected universal ten-rank ladder and retained pitch-closure residual. A failed universal ladder is not a failure of the usable functional bridge.

## Class, address, time and instrumentation

GEN / MEM / TIME / ADR / FUNC / TRN are the existing register. A placement can retain biological generation, succession, age, role, note/register, cumulative phase, entrance and transformation separately. Every systemic/generational class retains two turns/720degrees before its lift; a360degree visual return does not erase the second-turn distinction. The vortex/torus and Sierpinski-tetrahedral Monad remain the governing SUNNY geometry premise. Radius, rebound, class growth and fourth-axis assignments are not filled by visual convenience.

The retained elemental sections are aether—strings/harp; air—woodwinds; fire—brass; water—shimmering metals; earth—heavy percussion. Section follows the source-qualified position; particular instrument can also depend on generation. The primordial→Titan→Olympian→demi→hero distinctions remain available rather than being replaced by one flat note list.

Age is a participant's elapsed temporal position; a year is a source-defined periodic reference; rhythm concerns events and performance. No recovered approval turns one historical year into one beat, bar, note or physical frequency. Exact proportional chronological/rhythmic results remain usable without that unsupported unit conversion.

## Recovered alignment frames

These are populated source frames, accompanied by later correction records. They are not silently merged by matching row numbers. The workingC/Aries convention below is a source-qualified frame, not a new election of the global orientation.

'''
    for identifier,title in [('alignment-table-0e2dfd3dca876eaf','Directional/instrumental anchor frame'),('alignment-table-0871a4976f9bba9a','Working fifth-cycle / zodiac frame'),('alignment-table-42cb520ba2696910','Chinese–Western corridor under the stated overlay'),('alignment-table-b871faeaf57586d3','The proposed lift interval retains its internal handoff'),('alignment-table-47b2dbc91a0423db','Planetary phase and musical functions'),('alignment-table-779bc29285b26db4','Retained upper/lower register placement'),('alignment-table-d548ca1ae9dae3d2','The21–24 solar-term/mountain frame')]:text+=show(identifier,title)
    text+='''## Usable narrative results and their conditions

The Cainan branch preserves the same8:9:12harmonic configuration under competing genealogies, with a changed central-reference person. The chord alone therefore did not elect a textual lineage. Later work retained the unequal proportional timing, five-year divergence and different overlap windows. The Samaritan control matters: a five-year offset or27:26relation is not automatically unique evidence for an inserted Cainan. GEN, musicalADR and institutional succession remain different axes.

The Eldad–Medad continuation carries three identity branches and the all-four-camp control forward rather than treating a favored tribal placement as a unique consequence. The quail/sacred-symbol branch preserves the EMET→MET/Aleph-deletion reading, repeatedעלי שלו, Gog→Magog/Mem addition, the years/two reading, and two prophets/one prophecy as source-reported candidate operations. The subsequent correction separating generation, activation and deletion is retained; a blanket one-toggle or zombie interpretation is not silently reinstated.

Those are recovered usable conditional results and exclusions. Their exact witness tables, reported-result status, quotations and competing readings are in the correspondence and decision modules. This reconstruction does not mislabel them as newly rerun experiments.

## Complete inspectable registers

'''
    text+='\n'.join('- '+file_link(DOC/name,label) for name,label in [('DECISIONS.md','Current decisions, corrections, chronology and exact source trail'),('MUSIC_GEOMETRY.md','Complete recovered native music, bridge, register and geometry state'),('CORRESPONDENCES.md','Cross-system relationships, class/generation attributions and narrative results')])+'\n\n'
    text+='The '+file_link(STATE/'model.json','consolidated machine-readable current model')+' preserves all three modules, their hashes, every recovered native workbook table and every recovered transcript alignment table. It contains a shared evidence index; source links are not mislabeled semantic identity.\n\n'
    text+=f"The native workbook register preserves{modules['tables']['unique_workbook_bytes']}versions,{modules['tables']['distinct_sheet_contents']}distinct worksheet contents and{modules['tables']['distinct_sheet_cells']}nonempty/formula-bearing native cells. The transcript register retains{modules['alignment']['distinct_markdown_tables']}distinct tables with{modules['alignment']['table_rows']}rows, plus the72-gate and216-letter CSVframes. These counts describe preserved material, not independent support or a claim that every older table was approved.\n\n"
    text+='''## Localized retrieval and research boundaries

The October29 response reports a completed twenty-image music extraction with395indexed entries, transcriptions, diagrams and original pixels. The named workbook/archive have not been retrieved in the searched local and connected scopes; a source-linked original-image request returned403. The earlier reported completion and counts are preserved as a report. This missing package is not converted into an empty musical input or fabricated OCR.

The exact earlier10–12Jev proposal list is still not retrieved;52original repository proposals are a different recovered object. Full current-account census, deleted/unexported branches and every inaccessible attachment cannot be certified from these exports. The full generational radius/rebound/fourth-axis law and a uniquely selected absolute orientation remain unresolved. The current mandate expressly directs progressively derived type laws; the old blanket assertion that this policy question is unanswered is superseded, with its history preserved.

The present deliverable is the source-linked reconstruction of the accessible current research state. New universal alignment, new prospective predictions and inaccessible inputs remain distinct obligations. The source records and their contradictions survive so the next investigation starts from these retained relations rather than forgetting them.
'''
    text+='\n## Executed mathematical reconstruction under the current mandate\n\n'
    text+='The current direct user mandate requires complete musical-relational reconstruction and derived global consequences. Source ingestion and the earlier current-state catalog are inputs to that mission, not its completion. The complete previous model and readable report are retained by hash before this assembly.\n\n'
    units=[('NATIVE_DERIVATIONS.md','native musical bridge and path derivations'),
           ('ORIENTATION_PREDICTIONS.md','source-family orientation consequences'),
           ('TOL_HISTORY_MATH.md','TOL history and inverse constraints'),
           ('NATIVE_EXECUTION.md','ten native operational mechanism interfaces'),
           ('GENERATIONAL_CONSTRAINTS.md','joint temporal/generational constraints'),
           ('ALGEBRAIC_EXTENSION.md','exact Zhu root extension and octave quotients'),
           ('DERIVED_LAWS.md','progressively derived conditional law register'),
           ('MASTER_SCORE.md','source-backed executable partial master score'),
           ('SYMBOL_SOUND_CONSTRAINTS.md','source-qualified phonetic constraints and unresolved interpretation fibre'),
           ('HIERARCHY_ATLAS.md','source-scoped A/B/C and legion census'),
           ('MUSICAL_HIERARCHIES.md','separate reconstructed native musical hierarchies'),
           ('ANGELIC_HIERARCHY_SUPPLEMENT.md','angelic and archonic source views'),
           ('COVERAGE.md','exact corpus processing boundaries')]
    text+='The connected execution contains '+', '.join(file_link(DOC/name,label) for name,label in units)+'. Each artifact retains its source conditions, mathematical steps, actual Jev decisions and applicable independent checks. Coverage inventory is not mathematical citation or semantic adjudication.\n\n'
    text+='Computed constraints include the exact reverse-five/forward-seven tuning distinction; finite-address versus rational-pitch information loss; common addresses across all twelve recovered transitive completions; the minimum ordered phase observations needed to separate that family; and the failure of scalar or normalized-pitch outputs to recover full operation histories. These constrain progressively attained type distinctions rather than imposing a universal taxonomy.\n\n'
    text+='The optional twelve-completion family is one test case within SUNNY. Other native musical systems, the phase-preserving profile, full generational geometry, restoration objectives and missing sources remain in scope. These are conditional reproduced/extended results, not a claim of global completion or independent blind predictive success.\n'
    text+='\nThe recovered scalar group and Zhu root extension distinguish H/G=C12 from H/<2>=C12×Z. The latter retains unbounded prime-3 information. The exact difference between q^7 and3/2 has twelfth power524288/531441; matching finite dial labels cannot establish exact pitch equality.\n\n'
    text+='Fourteen recorded aligned witness shifts generate the lattice <(50,0),(130,1)> and preserve I=t−130g mod50. An ordinary genealogical step changes this value: it describes the tested changes between witnesses, not conservation along genealogy. The five-stage lifespan system leaves two independent overlap freedoms. No historical year-to-beat conversion or global class-growth law follows from these results.\n\n'
    text+='The master score executes the known native construction and chronology views while retaining unknown musical timing and instrumentation. Its representation separates participants, roles, registers, entrances, durations, overlaps, transitions and qualified addresses. It does not fabricate the missing complete orchestration.\n'
    text+='\nNovember7 extension: '+file_link(ROOT/'docs/delivery-2026-11-07/SCORE_ANCHORS.md','minimal sufficient score observations')+' classifies all ten two-stage duration-anchor pairs. Eight recover both timing freedoms; pairs1+4 and2+5 remain redundant. Fifty exposed witness replays and forty invertible-coordinate replays are retained, with independent symbolic verification. Exact linear-observable prediction and minimal-conflict localization are conditional capabilities, not a historical sound or calendar reconstruction. The canonical score-anchor-constraints module retains immutable inputs and code bindings.\n'
    text+='\nAssembly evidence: '+file_link(ROOT/'docs/evidence/reconstruction-priority-superjev.json','earlier source work selection')+', '+file_link(ROOT/'docs/evidence/mandate-mathematics-superjev.json','current Jev mathematical direction')+'.\n'
    (DOC/'CURRENT_MODEL.md').write_text(text,encoding='utf8')
    print(json.dumps({'status':'assembled_pending_fidelity_verification','model_path':str(STATE/'model.json'),'model_sha256':digest(STATE/'model.json'),'source_files':len(sources),'semantic_music_records':len(modules['music-geometry']['records']),'decision_records':len(modules['decisions']['records']),'correspondence_claims':len(modules['correspondences']['claims']),'current_doc':str(DOC/'CURRENT_MODEL.md')},indent=2))
if __name__=='__main__':main()
