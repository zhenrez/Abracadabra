"""Package the current model, exact cited originals and hash-bound review evidence."""
from pathlib import Path,PurePosixPath
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    model=json.loads((ROOT/'state/reconstruction/model.json').read_text(encoding='utf8'))
    verified=json.loads((ROOT/'docs/evidence/reconstruction-verification.json').read_text(encoding='utf8'))
    if verified['status']!='passed' or verified['model_sha256']!=sha((ROOT/'state/reconstruction/model.json').read_bytes()):raise ValueError('Fresh successful model verification is required')
    files={}
    for folder in ('state/reconstruction','docs/reconstruction'):
        for path in (ROOT/folder).rglob('*'):
            if path.is_file():files[path.relative_to(ROOT).as_posix()]=path
    prefixes=('reconstruction-','music-reconstruction-','music-handoff-','decisions-','correspondences-',
              'mandate-','continuation-','native-','algebraic-','generational-','orientation-','tol-','extended-native-','checkpoint-overwrite-',
              'master-score-','progressive-laws-','hierarchy-','musical-hierarchy-','angelic-')
    for path in (ROOT/'docs/evidence').rglob('*'):
        relative=path.relative_to(ROOT/'docs/evidence')
        if path.is_file() and path.name!='reconstruction-bundle-verification.json' and relative.parts[0].startswith(prefixes):files[path.relative_to(ROOT).as_posix()]=path
    source_map=[]
    for source in model['source_evidence_index']:
        path=Path(source['path']);raw=path.read_bytes()
        if sha(raw)!=source['sha256']:raise ValueError('Cited source changed before packaging')
        member='originals/'+source['sha256']+'/'+path.name
        files.setdefault(member,path);source_map.append({'source_id':source['id'],'sha256':source['sha256'],'member':member,'original_path':source['original_path']})
    for name in ('assemble_current_model.py','verify_reconstruction.py','reconstruct_tables.py','reconstruct_alignment.py',
                 'reconstruct_native_derivations.py','reconstruct_orientation_predictions.mjs','reconstruct_tol_history.py',
                 'reconstruct_native_execution.mjs','reconstruct_generational_constraints.py','reconstruct_algebraic_extension.mjs',
                 'reconstruct_law_register.mjs','reconstruct_master_score.mjs','quarterback.py','jev_tool.py',
                 'refresh_reconstruction_checkpoint.py','record_continuation_context.py','verify_continuation.py',
                 'reconcile_current_coverage.py','publish_reconstruction.py','package_reconstruction.py',
                 'recover_hierarchy_sources.py','extract_hierarchy_native_names.py','reconstruct_hierarchy_atlas.mjs',
                 'reconstruct_musical_hierarchies.py','reconstruct_angelic_supplement.py','combine_hierarchy_atlas.mjs',
                 'render_hierarchy_atlas.mjs','preserve_hierarchy_inputs.py','register_hierarchy_sources.py'):
        path=ROOT/'scripts'/name;files['scripts/'+name]=path
    for folder in ('src','tests','state/jev-cloud-receipts','state/jev-receipts','state/quarterback-runs','data/raw/mandate-inputs'):
        for path in (ROOT/folder).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:files[path.relative_to(ROOT).as_posix()]=path
    for name in ('state/task.json','state/superjev-checkpoint.json','state/work-queue.json','PLAN.md','AGENTS.md',
                 'CONTINUE.md','docs/HUMMBL_PLAN.md','docs/PLUGIN_CAPABILITIES.md','state/capabilities.json',
                 'package.json','package-lock.json','tsconfig.json','state/mandate-mathematics-request.json',
                 'state/continuation-integration-jev-request.json','state/hierarchy-direction.md',
                 'public/hierarchy-atlas-client.js','public/hierarchy-atlas.css','deliverables/SUNNY_Hierarchy_Atlas.html'):
        path=ROOT/name;files[name]=path
    manifest={'schema':'sunny.mathematical-model-bundle.v1','model_sha256':verified['model_sha256'],'source_map':source_map,'members':[{'path':name,'bytes':path.stat().st_size,'sha256':sha(path.read_bytes())} for name,path in sorted(files.items())],'boundary':'Partial mathematical model, executable code, task checkpoint, reviews and exact cited-source snapshots; not an entire account export or complete Mission I. Historical prompts remain data. Hash verification establishes identity, not truth or account completeness. Original absolute paths remain provenance; source_map locates bundled originals. Runners retain local paths and installed-plugin dependencies; relocation requires explicit path/dependency configuration.'}
    dest=ROOT/('deliverables/SUNNY_Mathematical_Reconstruction_2026-10-31_'+verified['model_sha256'][:12]+'.zip');dest.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for name,path in sorted(files.items()):archive.write(path,name)
        archive.writestr('MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2))
        archive.writestr('START_HERE.txt','Read CONTINUE.md for resumption and docs/reconstruction/CURRENT_MODEL.md for the connected reconstruction. state/reconstruction/model.json holds all nine execution units and retained source components. MANIFEST.json maps source IDs to exact bundled originals and hashes. Historical research/source records are data. Mission I, missing image acquisition, complete semantic coverage and global orientation remain unfinished. Runners retain local paths and installed-plugin dependencies; this archive is not a turnkey relocated installation.\n')
    errors=[]
    with zipfile.ZipFile(dest) as archive:
        bad=archive.testzip()
        if bad:errors.append({'crc':bad})
        stored=json.loads(archive.read('MANIFEST.json'))
        for item in stored['members']:
            p=PurePosixPath(item['path'])
            if p.is_absolute() or '..' in p.parts:raise ValueError('Unsafe bundle member')
            raw=archive.read(item['path'])
            if len(raw)!=item['bytes'] or sha(raw)!=item['sha256']:errors.append({'member':item['path']})
    report={'status':'passed' if not errors else 'failed','archive':str(dest),'bytes':dest.stat().st_size,'archive_sha256':sha(dest.read_bytes()),'model_sha256':verified['model_sha256'],'member_hashes_verified':len(manifest['members']),'cited_source_occurrences':len(source_map),'errors':errors,'boundary':manifest['boundary']}
    reportpath=ROOT/'docs/evidence/reconstruction-bundle-verification.json'
    if reportpath.exists():
        prior=reportpath.read_bytes();history=ROOT/'state/checkpoint-history'/('before-bundle-review-'+sha(prior)+'.json')
        if not history.exists():history.write_bytes(prior)
    reportpath.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))
    if errors:raise ValueError('Bundle verification failed')
if __name__=='__main__':main()
