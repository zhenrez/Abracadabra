"""Execute the final-day native/evidence delivery without certifying unknown history."""
from pathlib import Path
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib,json,os,re,subprocess,sys,tempfile

ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[1];OUT=ROOT/'results'
for directory in (ROOT,ROOT/'integration',ROOT/'western',ROOT/'native-east',PROJECT/'work/unit001'):
    if str(directory) not in sys.path:sys.path.insert(0,str(directory))
import baseline,controls,comparisons,inverse_controls,mathematical_sources
from evidence import import_matrix,verify_g0_conservation,serialize
from contracts import CrossOrientationRegistry
from sefer import SeferModel,Profile
from western_model import WesternOrientation
from east_models import ChineseModel,GramaModel,MelakartaModel
from common_models import CommonOrientation

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(name,value):
    path=OUT/name;path.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as file:file.write(raw);temporary=Path(file.name)
    os.replace(temporary,path)
    if path.read_bytes()!=raw:raise RuntimeError('Written artifact failed byte readback: '+str(path))

def command(name,args,timeout=180):
    process=subprocess.run(args,cwd=PROJECT,capture_output=True,text=True,encoding='utf-8',errors='backslashreplace',timeout=timeout)
    output=process.stdout+process.stderr
    save('checks/'+name+'.json',{'command':args,'exit_code':process.returncode,'output':output})
    if process.returncode:raise RuntimeError('Required check failed: '+name)
    count=re.search(r'Ran (\d+) tests?',output)
    if 'unittest' in args and (count is None or int(count.group(1)) <= 0):
        raise RuntimeError('Required unit suite collected no verifiable tests: '+name)
    if name == 'original-Sefer' and int(count.group(1)) != 6:
        raise RuntimeError('Frozen original Sefer suite did not execute its six tests')
    return {'name':name,'command':args,'exit_code':process.returncode,'observed_tests':int(count.group(1)) if count else None,
            'output_ref':'checks/'+name+'.json'}

def cluster(label):
    if label in ('Proto-Sinaitic (proxy)','Phoenician','Paleo-Hebrew','Imperial Aramaic','Square Hebrew','Syriac'):
        return 'northwest-semitic-related-witness-control'
    if label in ('Ugaritic','Sabaic / South Arabian','Old Arabic (28-letter proxy)'):
        return 'other-semitic-related-witness-control'
    if label=='Old Persian':return 'old-persian-sign-model-control'
    return 'european-alphabet-related-witness-control'

def coding_report(records,field):
    values=tuple(r[field] for r in records);fitted=baseline.infer_basis(values)
    literal=baseline.encode_literal(values)
    selected=baseline.encode_literal(values) if fitted['selected_model']=='literal' else baseline.encode_dictionary(values,fitted['basis'])
    if baseline.decode(selected['bits'])!=values:raise RuntimeError('Full source target did not roundtrip')
    folds=[]
    index={r['record_id']:r for r in records}
    for fold in baseline.grouped_folds(records):
        train=tuple(index[rid][field] for rid in fold['train_ids']);test=tuple(index[rid][field] for rid in fold['test_ids'])
        fit=baseline.infer_basis(train)
        encoded=baseline.encode_literal(test) if fit['selected_model']=='literal' else baseline.encode_dictionary(test,fit['basis'])
        if baseline.decode(encoded['bits'])!=test:raise RuntimeError('Held-cluster code did not roundtrip')
        folds.append({**fold,'fit_model':fit['selected_model'],'fit_basis_size':len(fit['basis']),
            'training_bits':fit['selected_bits'],'held_cluster_model_bits':encoded['model_bits'],
            'held_cluster_data_bits':encoded['data_bits'],'held_cluster_total_bits':encoded['total_bits'],
            'held_cluster_literal_bits':baseline.encode_literal(test)['total_bits'],'held_cluster_escapes':encoded['escaped_values']})
    return {'target':field,'positions':len(values),'literal_bits':literal['total_bits'],
        'selected_model':fitted['selected_model'],'selected_bits':selected['total_bits'],
        'model_bits':selected['model_bits'],'data_given_model_bits':selected['data_bits'],
        'basis_size':len(fitted['basis']),'basis':fitted['basis'],'search':fitted,'folds':folds,
        'lossless_roundtrip':True,'adapter_cost_scope':'Raw type/string pair already observed; no musical-to-script adapter was fitted',
        'scientific_limits':['Code family is explicit and finite; global MDL optimality not claimed',
            'Literal escapes are residual storage, not successful historical predictions',
            'Order-blind coding cannot establish cyclic, liturgical or cryptographic ordering',
            'Source-family independence is not certified; all supplied material was already exposed'],
        'historical_model_comparison':'NOT_EVALUATED'}

def main():
    OUT.mkdir(exist_ok=True);checks=[]
    for name,directory,pattern in (
        ('new-core',ROOT,'test_*.py'),('common-contracts',ROOT/'integration','test_common_models.py'),
        ('adversarial',ROOT/'independent-review','test_*.py'),
        ('canonical-features',ROOT/'canonical-features','test_canonical_features.py'),
        ('dashboard',ROOT/'dashboard','test_dashboard.py'),
        ('accepted-G0-G1',PROJECT/'work/unit001','test_*.py'),
        ('original-Sefer',PROJECT/'work/unit001/frozen/sefer','test_harmonic_verifier.py'),
        ('preserved-linguistic-pipeline',PROJECT/'work/ariadne-inverse','test_*.py'),
        ('earlier-four-orientations',PROJECT/'work/four-orientations','test_models.py')):
        checks.append(command(name,[sys.executable,'-B','-m','unittest','discover','-s',str(directory),'-p',pattern,'-v']))
    checks.append(command('western-native',[sys.executable,'-B',str(ROOT/'western/run_native.py'),
                         '--output',str(OUT/'western-native.json')]))
    checks.append(command('east-native',[sys.executable,'-B',str(ROOT/'native-east/verify_native_east.py')]))
    manifest=json.loads((PROJECT/'work/unit001/source-manifest.json').read_text(encoding='utf-8'))
    frozen_integrity=[]
    for group in ('baseline','earlier_derived','context'):
        for item in manifest[group].values():
            actual=sha(PROJECT/'work/unit001'/item['path'])
            if actual!=item['sha256']:raise RuntimeError('Frozen artifact changed: '+item['path'])
            frozen_integrity.append({'group':group,'path':item['path'],'sha256':actual,'matched':True})
    for label,item in [('source-event',manifest['source']['event']),('orientation-attachment',manifest['attachment'])]:
        actual=sha(PROJECT/'work/unit001'/item['path'])
        if actual!=item['sha256']:raise RuntimeError('Original source artifact changed: '+label)
        frozen_integrity.append({'group':label,'path':item['path'],'sha256':actual,'matched':True})
    protected={**manifest['src_hashes'],**manifest['existing_work_hashes']};intentional=[]
    for name,digest in protected.items():
        if sha(PROJECT/name)!=digest:
            change=ROOT/'runtime/approved-source-change.json'
            if name.replace('\\','/')!='src/worker.ts' or not change.exists():raise RuntimeError('Protected source changed: '+name)
            record=json.loads(change.read_text(encoding='utf-8'))
            if record['before_sha256']!=digest or record['after_sha256']!=sha(PROJECT/name) or sha(PROJECT/record['preserved_before'])!=digest:
                raise RuntimeError('Operational runtime supersession lacks exact source binding')
            intentional.append(record)
    source=PROJECT/'work/unit001/frozen/source/matrix-message.txt'
    if sha(source)!=manifest['source']['sha256']:raise RuntimeError('Original matrix bytes changed')
    graph=import_matrix(source.read_bytes(),manifest['source']['locator']);g0=verify_g0_conservation(graph)
    if g0['status']!='PASSED':raise RuntimeError('G0 conservation failed')
    witnesses={w.raw_cell_id:w for w in graph.witnesses};records=[];matrix=[]
    for cell in graph.cells:
        witness=witnesses.get(cell.cell_id);kind=witness.phonetic_type.value if witness else 'BLANK_GLYPH_POSITION'
        records.append({'record_id':cell.cell_id,'cluster':cluster(cell.script_label),'phonetic':(kind,cell.ipa),
            'joint':(kind,json.dumps({'glyph':cell.glyph,'ipa':cell.ipa,'english':cell.english},ensure_ascii=False,sort_keys=True,separators=(',',':')))})
        matrix.append({'record_id':cell.cell_id,'script':cell.script_label,'ordinal':cell.ordinal,
            'glyph':cell.glyph,'ipa':cell.ipa,'english':cell.english,'phonetic_type':kind,
            'proxy':bool(witness and 'PROXY' in witness.glyph_type.value)})
    phonetic=coding_report(records,'phonetic');joint=coding_report(records,'joint')
    save('coding-baselines.json',{'phonetic':phonetic,'joint':joint})
    observed=tuple((row['record_id'],row['joint'][1]) for row in records)
    distinct=tuple(dict.fromkeys(value for _,value in observed))
    inverse_certificate=inverse_controls.countermodels(observed,'unobserved:witness:new-position',distinct[:2])
    proxy={str(cell.ordinal):cell.ipa for cell in graph.cells if cell.script_label==graph.grid.script_labels[0] and cell.glyph}
    inverse_certificate['latent_relabeling']=inverse_controls.relabeling_certificate(proxy,{key:'latent:'+str(len(proxy)-i) for i,key in enumerate(proxy)})
    save('inverse-identifiability.json',inverse_certificate)
    scale=WesternOrientation();mode=scale.core.mode('ionian')
    west_input={'kind':'scale','mode':'ionian','source_ref':'engineering:explicit-Pythagorean-native-profile',
        'observations':[{'record_id':'degree:'+str(i),'ratio':str(value),'onset':str(i),'voice':'single'} for i,value in enumerate(mode['ratios'])]}
    native_objects={'western':scale,'chinese':ChineseModel(),'grama':GramaModel(),'melakarta':MelakartaModel()}
    descriptions={};encodings={};native_validations={}
    for name,native in native_objects.items():
        wrapped=CommonOrientation(native);encoded=wrapped.encode(west_input if name=='western' else None)
        validation=wrapped.validate_native(encoded)
        if validation.status!='VALID':raise RuntimeError('Common native validation failed: '+name)
        if wrapped.to_json(wrapped.from_json(wrapped.to_json(encoded)))!=wrapped.to_json(encoded):raise RuntimeError('Common serialization changed')
        descriptions[name]=wrapped.description_measurement(encoded)
        encodings[name]=json.loads(serialize(encoded));native_validations[name]=json.loads(serialize(validation))
    save('common-encodings.json',encodings);save('native-description-measurements.json',descriptions)
    sefer=SeferModel();sefer_encoded=sefer.encode(graph,Profile('final-day:proto',graph.grid.script_labels[0],sefer.baseline_hash))
    if sefer.validate_native(sefer_encoded).status!='VALID':raise RuntimeError('Preserved Sefer projection failed')
    demo_cmd=[sys.executable,'-B',str(PROJECT/'work/unit001/frozen/sefer/harmonic_verifier.py')]
    demo=subprocess.run(demo_cmd,cwd=PROJECT,capture_output=True,text=True,timeout=60)
    if demo.returncode:raise RuntimeError('Frozen demonstration execution failed')
    demo_expected=json.loads((PROJECT/'work/unit001/frozen/sefer/harmonic-demo.json').read_text(encoding='utf-8'))
    demo_actual=json.loads(demo.stdout)
    if demo_actual!=demo_expected:raise RuntimeError('Full frozen demonstration output changed')
    original_input=[token for group in sefer.legacy_module.GROUPS.values() for token in group]
    demo_inputs={'complete':original_input,'missing_m':[token for token in original_input if token!='m'],'duplicate':original_input[:-1]+['b']}
    demo_cases=[]
    for name,tokens in demo_inputs.items():
        actual=sefer.legacy(tokens)
        if actual!=demo_expected[name]:raise RuntimeError('Legacy demonstration adapter changed: '+name)
        demo_cases.append({'case':name,'input':tokens,'expected':demo_expected[name],'observed':actual,'passed':True})
    save('original-demonstrations.json',{'command':demo_cmd,'exit_code':demo.returncode,'full_json_equal':True,'cases':demo_cases})
    save('sefer-native.json',{'pair_counts':sefer.pair_counts(),'legacy_complete':sefer.legacy(list(sefer.legacy_module.HarmonicPhoneticVerifier().slots)),
        'description':json.loads(serialize(sefer.describe(None,None))),
        'scope':'Stipulated model projection; no musical correspondence inferred'})
    examples=[comparisons.commutation(comparisons.ScalarOperator('Chinese D','length_ratio',Q(2,3)),
        comparisons.ScalarOperator('frequency fifth','frequency_ratio',Q(3,2)),
        comparisons.QuantityAdapter('length_ratio','frequency_ratio','reciprocal',Q(1)),(Q(7,11),Q(13,17))),
        comparisons.commutation(comparisons.ScalarOperator('SUN RL','length_ratio',Q(1,2)),
        comparisons.ScalarOperator('Chinese DU','length_ratio',Q(8,9)),
        comparisons.QuantityAdapter('length_ratio','length_ratio','identity',Q(1)),(Q(7,11),Q(13,17)))]
    save('mathematical-comparisons.json',examples)
    registry=CrossOrientationRegistry()
    if registry.adapters:raise RuntimeError('Historical registry populated unexpectedly')
    try:comparisons.historical_reconstruct({'glyph':'א','pitch':'A'})
    except PermissionError:historical_denied=True
    else:raise RuntimeError('Unsupported historical reconstruction accepted')
    save('phonetic-numeric-controls.json',{'sanskrit_varga':controls.sanskrit_stop_table(),
        'documented_numeric_examples':[controls.decode_katapayadi(text) for text in ('dhīra','māyā','nāgā','naṭanara')],
        'numeric_inverse_example':controls.encode_katapayadi(29),'historical_music_or_glyph_mapping':'NOT_ASSIGNED'})
    census=json.loads((ROOT/'audit/deliverables.json').read_text(encoding='utf-8'))
    version_path=ROOT/'audit/mathematical-source-versions/version-manifest.json'
    versions=mathematical_sources.load_registry(version_path,census,PROJECT)
    outputs=[]
    for requirement in census['requirements']:
        if requirement['scope']!='original_mathematical_output':continue
        source_versions=[mathematical_sources.resolve_source(item,versions,PROJECT,requirement['id']) for item in requirement['evidence']]
        entry={**requirement,'source_versions':source_versions,'version_manifest':'work/final-day-2026-11-07/audit/mathematical-source-versions/version-manifest.json','new_connected_outputs':['common-encodings.json','native-description-measurements.json','mathematical-comparisons.json',
                'coding-baselines.json','phonetic-numeric-controls.json'],
            'full_research_scope_status':requirement['status'],'completion_note':'Existing executable source-scoped work is linked; unresolved source/geometry/global-law dependencies remain open'}
        save('eight-outputs/'+requirement['id']+'.json',entry);outputs.append({'id':requirement['id'],'requirement':requirement['requirement'],
            'status':requirement['status'],'artifact':'eight-outputs/'+requirement['id']+'.json'})
    gates={'G0':'PASSED_PRESERVED_ENGINEERING','G1':'PASSED_PRESERVED_SEFER',
        'G2':'PASSED_BOUNDED_NATIVE_PROFILE; HISTORICAL_PROFILE_COMPLETENESS_PARTIAL',
        'G3':'PASSED_BOUNDED_NATIVE_PROFILE','G4':'PASSED_SEPARATE_BOUNDED_NATIVE_PROFILES',
        'G5':'PASSED_SOURCE_DEFINED_CONTROLS; NO_ACOUSTIC_OR_HISTORICAL_ROOT_CERTIFICATION',
        'G6':'MEASURED_CONDITIONAL_CODES; HISTORICAL_CROSS_MODEL_SELECTION_NOT_EVALUATED',
        'G7':'MATHEMATICAL_CONTROLS_VERIFIED; HISTORICAL_RECONSTRUCTION_LOCKED'}
    limitations=['Full parent transcript is unavailable; current-chat snapshots and available preview retained',
        'No independently attested historical glyph-stroke corpus or ancient sound recording supplied',
        'Raw field conservation and exact native-model tests do not establish intended historical meanings',
        'Conditional byte/program costs depend on the declared coding language and shared side information',
        'No source-family-independent prospective historical prediction trial has been performed',
        'The original wider106requirements include unresolved scientific, calendar, zodiac and global-geometry dependencies']
    east=json.loads((ROOT/'native-east/native-results.json').read_text(encoding='utf-8'))
    west=json.loads((OUT/'western-native.json').read_text(encoding='utf-8'))
    runtime_path=ROOT/'runtime/project-final-checks.json'
    runtime=json.loads(runtime_path.read_text(encoding='utf-8'))
    runtime_counts=runtime['observed_counts']
    if runtime['exit_code']!=0 or runtime_counts.get('tests',0)<99 or runtime_counts.get('pass')!=runtime_counts['tests'] or any(runtime_counts.get(name)!=0 for name in ('fail','cancelled','skipped')) or not runtime.get('inputs_unchanged'):
        raise RuntimeError('Final full-project acceptance is not verified')
    for name,digest in runtime['checked_inputs'].items():
        if sha(PROJECT/name)!=digest:raise RuntimeError('Project acceptance source changed: '+name)
    data={'counts':{'positions':len(matrix),'populated':len(graph.witnesses),'empty':sum(not row['glyph'] for row in matrix)},
        'matrix':matrix,'native':{'western':west,'east':east},'coding':{'phonetic':phonetic,'joint':joint,'native_descriptions':descriptions},
        'comparisons':examples,'gates':gates,'requirements':census['requirements'],
        'source_links':[{'label':'Original requirement census','path':'../audit/deliverables.json'},
            {'label':'Original mathematical outputs','path':'eight-outputs/'},
            {'label':'Exact source conservation','path':'../../unit001/list-completion/HANDOFF.md'}],
        'limitations':limitations,'full_mission_complete':False}
    save('dashboard-data.json',data)
    summary={'timestamp_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'g0':g0,'native_validations':native_validations,
        'counts':data['counts'],'matrix_sha256':sha(source),'gates':gates,'protected_source_exceptions':intentional,
        'frozen_artifact_integrity':frozen_integrity,'original_demo_equal':True,'original_demo_cases':len(demo_cases),
        'runtime_acceptance':{'path':'runtime/project-final-checks.json','sha256':sha(runtime_path),'exit_code':0,'observed_counts':runtime['observed_counts']},
        'mathematical_source_versions':{'manifest':'audit/mathematical-source-versions/version-manifest.json','sha256':sha(version_path),
            'unique_paths':len(versions['sources']),'changed_paths':[row['original_path'] for row in versions['sources'] if row['version_relation']=='NEWLY_OBSERVED_VERSION']},
        'historical_registry_empty':True,'unsupported_historical_call_denied':historical_denied,
        'eight_mathematical_outputs':outputs,'requirements_count':len(census['requirements']),
        'conditional_compression':{'phonetic_literal_bits':phonetic['literal_bits'],'phonetic_selected_bits':phonetic['selected_bits'],
            'joint_literal_bits':joint['literal_bits'],'joint_selected_bits':joint['selected_bits']},
        'limitations':limitations,'full_mission_complete':False,
        'outputs':{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*.json') if p.name!='delivery-receipt.json'}}
    save('delivery-receipt.json',summary)
    print(json.dumps({'checks':[{k:c[k] for k in ('name','exit_code','observed_tests')} for c in checks],
                      'counts':data['counts'],'gates':gates,'conditional_compression':summary['conditional_compression'],
                      'requirements':len(census['requirements']),'full_mission_complete':False},indent=2))

if __name__=='__main__':main()
