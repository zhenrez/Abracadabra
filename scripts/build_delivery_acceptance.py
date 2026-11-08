"""Account for the full SUNNY mission without changing its acceptance conditions."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'state/delivery-2026-11-07'
DOCS=ROOT/'docs/delivery-2026-11-07'

# The requirement text is read unchanged from the governing sixteen-goal register.
# Evidence below is deliberately narrower than the corresponding full requirement.
MAP={
'G01':('partial','Connected native execution and conditional comparison families exist.','Every participating lawful relationship and competing configuration must be reconstructed and tested; no unique global alignment is established.',['state/reconstruction/model.json','state/reconstruction/contextual-alignment.json']),
'G02':('partial','Twenty-three bounded hierarchy views and a shared graph retain source/native units, including a source-qualified reading-example hierarchy.','The native-system census is not exhaustive across all named musical, cultural, scientific, biological, symbolic and numerical systems.',['state/reconstruction/hierarchy-atlas-combined.json','state/reconstruction/reading-operations.json']),
'G03':('partial','Time/generation lattice, distinct axes and class/acoustic-counter restrictions are executed; candidate geometry is visualized.','Exact four-dimensional realization, growth/breadth, rebound, topology-to-acoustics mapping and global orientation remain to derive.',['state/reconstruction/generational-constraints.json','web/delivery-2026-11-07/app.js']),
'G04':('partial','Separate Western/Chinese mechanisms and context-dependent bridges have exact registered executions.','Complete source-native musical/compositional/orchestral structure, literal TOL AB/BA and every applicable/withheld adapter domain remain incomplete.',['state/reconstruction/native-execution.json','state/reconstruction/native-derivations.json','state/reconstruction/tol-history-math.json','state/reconstruction/contextual-alignment.json']),
'G05':('open-dependent','Received witness clocks are preserved in the score and shown separately.','Original symbol/grammar/readings must constrain uninterrupted and selected-calendar-change trajectories; no historical rectification is selected.',['state/reconstruction/master-score.json']),
'G06':('partial','Dated Hebrew/Aramaic witnesses, English controls, contextual Alef alternatives, exact tokens and modern recordings are preserved. Two Molin spelled examples, four comparative IPA strings and twelve analysed syllable occurrences now support conditional finite reading relations; published contextual comparanda remain distinct from bowl attestations.','Original glyph-sound intentions, full inventories, operational grammar and consistent source decoding remain unresolved. The four comparative strings do not reconcile the source-stated four forms. Shaked page213, locator684.14, ink and specimen dating remain unretrieved.',['docs/reconstruction/symbol-sound-census/dated-witnesses.json','state/reconstruction/symbol-sound-constraints.json','state/reconstruction/phonological-context-constraints.json','state/reconstruction/reading-operations.json','docs/delivery-2026-11-07/READING_OPERATIONS.md','docs/delivery-2026-11-07/SHAKED_WITNESS.md','state/research/reactivation/matched-audio/measurements.json']),
'G07':('open-dependent','Ophiuchus alternatives retain implicit, symbolic, non-angular and boundary roles; no thirteenth equal sector is imposed.','Historical positions, orientations, signs and attributions require the symbol/reading dependencies and discriminating source constraints.',['state/mission.json','web/delivery-2026-11-07/app.js']),
'G08':('partial','Raw occurrences, corrections and selected original reasoning spans are linked to current calculations.','Every omitted/rejected/forgotten dependency and pre-nomenclature line has not been semantically reconstructed.',['state/reconstruction/coverage.json','state/reconstruction/generational-constraints.json']),
'G09':('partial','Accessible archive inventory, content hashes and occurrence references are retained.','Inventory/inspection is not semantic completion. Account-wide acquisition, the earlier image package and inaccessible original attachments retain scope gaps.',['data/recovery-report.json','state/reconstruction/coverage.json']),
'G10':('partial','A/B/C alternatives, three catalogue witnesses,23views,9512graph records and10251relations retain distinct units. The reading extension adds19source/analysis records and18edges; generated anonymous memberships remain distinguished from identified beings.','Upper-to-catalogue joins, global person/legion identity, complete subordinate native musical extents and all source-witness organizational links remain unresolved.',['state/reconstruction/hierarchy-atlas-combined.json','state/reconstruction/reading-operations.json','web/delivery-2026-11-07/app.js']),
'G11':('partial','All eight registers exist and contribute to the connected visual workbench.','Each original output requires its complete mathematical/source coverage; populated registers and passing local checks do not establish it.',['state/reconstruction/model.json']),
'G12':('partial','Conditional orientation consequences, timing anchors and finite reading controls execute. The exact two-probe criterion accounts for all 10,296 indexed word pairs in the optional twelve-completion family: 4,608 sufficient pairs and 5,688 explicit collision witnesses. The earlier phase-orbit result is reused.','No independent historical phase constraints are admitted. Source-defined bridges, shared frame/origin, alternative families, withheld-target preregistration and independent blind evaluation remain unresolved; full novelty is not established.',['state/reconstruction/orientation-predictions.json','state/delivery-2026-11-07/global-closure/phase-probe-designs.json','docs/delivery-2026-11-07/PHASE_PROBE_DESIGNS.md','state/delivery-2026-11-07/mathematics/score-anchors.json','state/reconstruction/reading-operations.json']),
'G13':('partial','Actual pinned local AgentJev-0.6B receipts 57–63 direct visual architecture, timing anchors, contextual history, Molin reading operations and the global constraint/dependency extension. Receipt 59 was submitted through the actual browser interface.','Hosted private-payload call was rejected; provider account/billing is unverified. Automatic observers cannot route or certify. Ongoing choices require their own exact receipts.',['state/jev-receipts/000057-95bc223acd84.json','state/jev-receipts/000058-bbb3ab44bbf5.json','state/jev-receipts/000059-6581ee8c1ffa.json','state/jev-receipts/000060-a1b30f75db7d.json','state/jev-receipts/000061-54b57b45fbcd.json','state/jev-receipts/000062-5fcc72f3ccd7.json','state/jev-receipts/000063-298ff24c136a.json','scripts/delivery_server.py']),
'G14':('partial','Reproducible builders, exact calculations, source-preserving checks and local preview exist. Later initialized independent reviewers reproduced bounded calculations and source researchers saved acquisition checkpoints.','Initial workers failed to initialize. Local services stopped across a turn transition and a substantial cadence gap was recorded. Uninterrupted background research is not established by files, timers or a live service.',['scripts/build_delivery.py','scripts/derive_score_anchors.py','scripts/start-delivery.ps1','docs/delivery-2026-11-07/INDEPENDENT_REVIEW.md','state/delivery-2026-11-07/cadence-gap.json','CONTINUE.md']),
'G15':('partial','The full goal register and source-native axes are retained; no date/zodiac rewrite bypasses symbol-first dependencies.','Full corpus semantic incorporation and all progressively derived type/adaptor laws remain incomplete; continuity must keep preserving corrections and counterexamples.',['state/mission.json','state/reconstruction/derived-laws.json','docs/reconstruction/SUNNY_GOALS.md']),
'G16':('partial','Bounded P0-A fourteen-question accounting, source-specific scholarly packets and reused exact linear-algebra prior art exist.','The complete recurring first-order/First &3/4 Order research program, competing positions, negative searches and transfer/reproduction checks remain to complete.',['state/research/reactivation/symbols/p0a-14-baseline.json','docs/reconstruction/symbol-sound-census/reading-tradition-prior-art.json','state/delivery-2026-11-07/mathematics/score-anchors.json'])}

VISUALS=[
('V01','Expandable census: source/native identity, units, position, direct links, distinct reachable IDs and stated extent','atlas'),
('V02','A/B/C alternatives and separate catalogue witnesses without invented pairing','atlas'),
('V03','Search all graph IDs/aliases; expand generated anonymous memberships and inspect complete records','atlas'),
('V04','Separate Western and Chinese native musical trees and operator families','music'),
('V05','Systemic collection wheel with identified members and explicit display-angle semantics','wheels'),
('V06','Generational winding/class counters and candidate toroidal R4 projection','geometry'),
('V07','Finite Sierpinski tetrahedron with explicit infinite-limit boundary','geometry'),
('V08','Symbols, written-token comparisons, contextual alternatives, finite reading relations, real recordings and analytic phase control','symbols'),
('V09','Score entrances, durations, overlaps, source clocks, untimed reading annotations and unknown assignments','score'),
('V10','Bridge domains, exact residuals, candidate alternatives, timing anchors and phase-probe designs','bridges / constraints'),
('V11','Calendar/zodiac dependencies and non-predetermined Ophiuchus roles','time'),
('V12','Eight registers, provenance, discrepancy/missing-join records, data and image exports','proofs'),
('V13','Pinned local Jev metadata, substantive receipts and explicit decision interface','jev')]

def main():
    mission=json.loads((ROOT/'state/mission.json').read_text(encoding='utf-8-sig'))
    model=json.loads((ROOT/'state/reconstruction/model.json').read_text(encoding='utf-8-sig'))
    graph=json.loads((ROOT/'state/reconstruction/hierarchy-atlas-combined.json').read_text(encoding='utf-8-sig'))
    score=json.loads((ROOT/'state/reconstruction/master-score.json').read_text(encoding='utf-8-sig'))
    reading=json.loads((ROOT/'state/reconstruction/reading-operations.json').read_text(encoding='utf-8-sig'))
    probes=json.loads((ROOT/'state/delivery-2026-11-07/global-closure/phase-probe-designs.json').read_text(encoding='utf-8-sig'))
    assert set(MAP)=={g['id'] for g in mission['goals']}
    evidence={}
    def bind(path):
        p=ROOT/path
        if path not in evidence:evidence[path]={'path':path,'available':p.is_file(),
            'sha256':hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None}
        return path
    items=[]
    for goal in mission['goals']:
        status,achieved,remaining,refs=MAP[goal['id']]
        items.append({'id':goal['id'],'requirement':goal['text'],'status':status,'completionProved':False,
            'observedCoverage':achieved,'notYetSatisfied':remaining,'evidence':[bind(p) for p in refs],
            'completionEvidenceNeeded':'Source- and derivation-bound evidence covering the complete requirement, including independent acceptance at its stated scope.'})
    registers=[]
    for i,entry in enumerate(model['mandated_output_status'],1):
        registers.append({'id':'M'+str(i).zfill(2),'requirement':entry['output'],'status':entry['status'],
            'completionProved':False,'units':entry['units'],'notYetSatisfied':entry['remaining']})
    browser_path=ROOT/'docs/evidence/delivery-2026-11-07/browser-check.json'
    browser=json.loads(browser_path.read_text(encoding='utf8')) if browser_path.is_file() else None
    visuals=[{'id':id,'requirement':text,'panel':panel,'status':'implemented; fresh integrated replay required',
        'scientificCoverageInherited':True,'completionBoundary':'Rendering is separate from source completeness and mathematical/historical truth.'} for id,text,panel in VISUALS]
    result={'schema':'sunny.full-scope-acceptance.v1','checkedAt':datetime.now(timezone.utc).isoformat(),
        'authority':mission['authority'],'scopePreserved':True,'status':'partial; full mission incomplete',
        'items':items,'mathematicalDeliverables':registers,'visualDeliverables':visuals,
        'evidence':list(evidence.values()),'priorBrowserCheck':{'status':browser.get('status'),'checks':len(browser['checks']),
            'path':str(browser_path.relative_to(ROOT)).replace('\\','/'),'scope':'Previously rendered build; does not certify later edits'} if browser else None,
        'fullMissionComplete':False,'historicalOrientationSelected':False,'originalSoundsRecovered':False,
        'blindPredictionEstablished':False,'uninterruptedBackgroundExecutionVerified':False,
        'currentExecution':{'moduleCount':len(model['mathematical_execution']),'graphRecords':len(graph['entities']),
            'relations':len(graph['relationships']),'hierarchyViews':len(graph['views']),'scoreViews':len(score['program']['views']),
            'untimedReadingViews':score['counts']['readingAnnotationViews'],'displayedBowlExamples':reading['census']['displayedBowlExamples'],
            'comparativePronunciationForms':reading['census']['comparativePronunciationForms'],'analysedSyllableOccurrences':reading['census']['analysedSyllableOccurrences'],
            'sourceStatedForms':reading['census']['sourceStatedForms'],'fullStatedExtentReconciled':False,
            'phaseProbeDesigns':probes['counts'],'newIndependentHistoricalPhaseConstraints':probes['globalClosure']['newIndependentHistoricalConstraints']},
        'accountingBoundary':'This matrix accounts for the sixteen goals, eight outputs and identified visual requirements. It is not a claim that every archive proposition has been extracted or semantically processed.'}
    STATE.mkdir(parents=True,exist_ok=True);DOCS.mkdir(parents=True,exist_ok=True)
    (STATE/'acceptance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    text=['# SUNNY full-scope acceptance — November7','',
        'The complete original objective remains active. No full goal or mathematical output has sufficient completion evidence. The connected interface is a tangible deliverable; its source and scientific gaps remain attached.','',
        '| Requirement | Current evidence | What remains |','| --- | --- | --- |']
    for item in items:text.append('| '+item['id']+' | '+item['observedCoverage']+' | '+item['notYetSatisfied']+' |')
    text+=['','## Eight mathematical outputs','']
    for item in registers:text+=['- **'+item['requirement']+'** — '+item['status']+'. Remaining: '+item['notYetSatisfied']]
    text+=['','## Visual acceptance','', 'The workbench has thirteen identified visual requirements organized in twelve panels. Fresh integrated browser replay is required after changes; screenshots alone do not verify interactions.','']
    for item in visuals:text+=['- '+item['id']+' — '+item['requirement']+' ('+item['panel']+').']
    text+=['','The dependency order is symbol/sound → grammar/operations → supported readings → changed relationships/hierarchies → global alignment/calendar/zodiac consequences → independent predictions. Native music and targeted historical/prior-art investigation participate throughout.','',
        'Machine-readable requirements, source hashes, current gaps and boundaries: `state/delivery-2026-11-07/acceptance.json`. No unverified state is promoted because of the requested deadline.']
    (DOCS/'ACCEPTANCE.md').write_text('\n'.join(text)+'\n',encoding='utf8')
    print(json.dumps({'status':'accounted','exit_code':0,'fullGoals':len(items),'mathematicalDeliverables':len(registers),'visualRequirements':len(visuals),'fullMissionComplete':False,'missingEvidenceFiles':[p for p,x in evidence.items() if not x['available']]}))

if __name__=='__main__':main()
