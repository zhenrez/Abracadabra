"""Prepare byte-bound GitHub payloads; no network, source mutation, or account access."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,base64,hashlib,json,os,sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'work/publication'
SKIP_DIRS={'.git','node_modules','__pycache__','.ruff_cache','.pytest_cache'}
SKIP_NAMES={'.env','auth.json','credentials.json','github-known-hosts'}
MUTABLE_PUBLICATION={'state/publication/ready.json','state/publication/push-result.json','state/publication/upload-progress.json','state/publication/file-index.json','state/publication/worker-checkpoint.json'}
def digest(raw):return hashlib.sha256(raw).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def contained(rel):
    if not isinstance(rel,str) or not rel or '\\' in rel or ':' in rel:raise ValueError('Use a relative project path')
    p=Path(rel)
    if p.is_absolute() or '..' in p.parts:raise ValueError('Path escapes project')
    full=(ROOT/p).resolve(strict=True)
    if not full.is_relative_to(ROOT) or not full.is_file() or (ROOT/p).is_symlink():raise ValueError('Regular project file required')
    if any(x in SKIP_DIRS or x.startswith('.venv') for x in p.parts) or full.name in SKIP_NAMES or full.name.startswith('.env.'):
        raise ValueError('Excluded runtime configuration or dependency path')
    return full
def fingerprints(p):
    before=p.stat();sha=hashlib.sha256();git=hashlib.sha1(b'blob '+str(before.st_size).encode()+b'\0')
    with p.open('rb') as f:
        while chunk:=f.read(4*1024*1024):sha.update(chunk);git.update(chunk)
    after=p.stat()
    if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise ValueError('Source changed while hashing: '+str(p.relative_to(ROOT)))
    return {'bytes':after.st_size,'sha256':sha.hexdigest(),'gitBlobSha':git.hexdigest(),'mtimeNs':after.st_mtime_ns}
def inventory():
    prior_path=OUT/'file-index.json'
    prior={r['sourcePath']:r for r in load(prior_path)['files']} if prior_path.is_file() else {}
    large=load(ROOT/'state/publication/large-files-manifest.json')
    # The packager's manifest is the authority for original paths and actual parts.
    records=large.get('files',large.get('entries',[]))
    if not records:raise ValueError('Completed large-source manifest required')
    archived={r.get('sourcePath',r.get('originalPath',r.get('path'))):r for r in records}
    rows=[];omitted=[]
    for current,dirs,files in os.walk(ROOT):
        base=Path(current);relbase=base.relative_to(ROOT).as_posix()
        dirs[:]=sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith('.venv') and not (relbase=='work' and d=='publication'))
        for name in sorted(files):
            p=base/name;rel=p.relative_to(ROOT).as_posix()
            if p.is_symlink():raise ValueError('Symbolic file needs an explicit publication decision: '+rel)
            if name in SKIP_DIRS:continue
            if name in SKIP_NAMES or name.startswith('.env.') or p.suffix.lower() in {'.pem','.key'}:
                omitted.append({'path':rel,'reason':'Runtime configuration excluded without reading its contents','bytes':p.stat().st_size});continue
            if rel in MUTABLE_PUBLICATION or rel.startswith('state/publication/uploads/') or rel.startswith('work/publication/'):
                continue
            if rel.startswith('runtime/agent-jev/models/') and p.suffix.lower() in {'.safetensors','.bin','.pt','.pth'}:
                omitted.append({'path':rel,'reason':'Reproducible upstream model weight; pinned identity and bootstrap retained','bytes':p.stat().st_size});continue
            if rel in archived:
                omitted.append({'path':rel,'reason':'Bytes retained in manifest-bound gzip parts; restore to original path','bytes':p.stat().st_size});continue
            if p.stat().st_size>100*1024*1024:raise ValueError('Unpackaged file exceeds ordinary GitHub blob limit: '+rel)
            old=prior.get(rel);stat=p.stat()
            info={k:old[k] for k in ['bytes','sha256','gitBlobSha','mtimeNs']} if old and (old['bytes'],old['mtimeNs'])==(stat.st_size,stat.st_mtime_ns) else fingerprints(p)
            kind=old['kind'] if old and old['sha256']==info['sha256'] else 'blob'
            if info['bytes']<=160000:
                try:p.read_text(encoding='utf8');kind='inline-text'
                except (UnicodeError,OSError):pass
            rows.append({'path':rel,'sourcePath':rel,'kind':kind,**info})
    # Large parts are explicitly supplied by the completed manifest rather than a recursive scratch-folder copy.
    for r in records:
        for part in r['parts']:
            source=part.get('localPath',part.get('path'))
            repo=part.get('repositoryPath',part.get('repoPath'))
            if not source and repo and r.get('originalSha256'):
                source='work/publication/large/'+r['originalSha256']+'/'+Path(repo).name
            if not source or not repo:raise ValueError('Part needs localPath and repositoryPath')
            p=contained(source);old=prior.get(source);stat=p.stat()
            info={k:old[k] for k in ['bytes','sha256','gitBlobSha','mtimeNs']} if old and (old['bytes'],old['mtimeNs'])==(stat.st_size,stat.st_mtime_ns) else fingerprints(p)
            if info['sha256']!=part['sha256']:raise ValueError('Large part changed: '+source)
            rows.append({'path':repo,'sourcePath':source,'kind':'blob',**info})
    names=[r['path'] for r in rows]
    if len(set(names))!=len(names):raise ValueError('Duplicate repository path')
    out={'schema':'sunny.publication-files.v1','generatedAt':datetime.now(timezone.utc).isoformat(),
         'files':sorted(rows,key=lambda r:r['path']),'excludedOrRelocated':omitted,
         'scope':'All project files outside reproducible environments, upstream weights, private runtime configuration and this publication scratch tree. Large originals remain byte-preserved in reconstructible parts.'}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'file-index.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'inventoried','exit_code':0,'files':len(rows),'bytes':sum(r['bytes'] for r in rows),
      'uniqueBlobIds':len({r['gitBlobSha'] for r in rows}),'inlineTextFiles':sum(r['kind']=='inline-text' for r in rows),'manifest':'work/publication/file-index.json'}))
def packetize():
    index=load(OUT/'file-index.json');packets=[];current=[];size=0
    folder=OUT/'packets';folder.mkdir(parents=True,exist_ok=True)
    def flush():
        nonlocal current,size
        if not current:return
        raw=json.dumps(current,ensure_ascii=False,separators=(',',':')).encode('utf8')
        p=folder/f'inline-{len(packets):05d}.json';p.write_bytes(raw)
        packets.append({'path':p.relative_to(ROOT).as_posix(),'bytes':len(raw),'sha256':digest(raw),'entries':len(current)})
        current=[];size=0
    for row in index['files']:
        if row['kind']!='inline-text':continue
        p=contained(row['sourcePath']);raw=p.read_bytes()
        if digest(raw)!=row['sha256']:raise ValueError('Indexed source changed: '+row['sourcePath'])
        entry={'path':row['path'],'mode':'100644','type':'blob','content':raw.decode('utf8')}
        encoded=json.dumps(entry,ensure_ascii=False).encode('utf8')
        if current and size+len(encoded)>360000:flush()
        current.append(entry);size+=len(encoded)
    flush()
    out={'packets':packets,'blobFiles':[r for r in index['files'] if r['kind']=='blob'],
         'fileIndexSha256':digest((OUT/'file-index.json').read_bytes())}
    (OUT/'upload-plan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'packetized','exit_code':0,'inlinePackets':len(packets),'blobPaths':len(out['blobFiles']),
      'uniqueBinaryBlobs':len({r['gitBlobSha'] for r in out['blobFiles']}),'plan':'work/publication/upload-plan.json'}))
def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('inventory');sub.add_parser('packets')
    p=sub.add_parser('info');p.add_argument('--path',required=True)
    sub.add_parser('receipts')
    p=sub.add_parser('record');p.add_argument('--base64',required=True)
    p=sub.add_parser('read');p.add_argument('--path',required=True);p.add_argument('--offset',type=int,default=0);p.add_argument('--length',type=int,default=524286)
    args=parser.parse_args()
    if args.command=='inventory':inventory()
    elif args.command=='packets':packetize()
    elif args.command=='info':print(json.dumps({'bytes':contained(args.path).stat().st_size}))
    elif args.command=='receipts':
        folder=ROOT/'state/publication/uploads'
        rows=[load(p) for p in folder.rglob('*.json')] if folder.is_dir() else []
        raw=json.dumps({'records':rows},ensure_ascii=False).encode('utf8')
        p=OUT/'receipt-index.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        print(json.dumps({'path':'work/publication/receipt-index.json','bytes':len(raw),'records':len(rows)}))
    elif args.command=='record':
        import re
        row=json.loads(base64.b64decode(args.base64,validate=True));kind=row.get('kind','blob')
        identity=row.get('gitBlobSha') if kind=='blob' else row.get('packetSha256')
        if kind not in {'blob','tree'} or not re.fullmatch('[a-f0-9]{40,64}',str(identity)):raise ValueError('Invalid object receipt identity')
        p=ROOT/'state/publication/uploads'/('objects' if kind=='blob' else 'trees')/(identity+'.json')
        p.parent.mkdir(parents=True,exist_ok=True)
        if p.exists():
            previous=load(p)
            if previous.get('gitBlobSha')!=row.get('gitBlobSha') or previous.get('treeSha')!=row.get('treeSha'):raise ValueError('Conflicting preserved object receipt')
        else:p.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(json.dumps({'status':'recorded','exit_code':0,'path':p.relative_to(ROOT).as_posix()}))
    else:
        if args.offset<0 or not 1<=args.length<=524286:raise ValueError('Invalid byte range')
        with contained(args.path).open('rb') as f:f.seek(args.offset);raw=f.read(args.length)
        sys.stdout.write(base64.b64encode(raw).decode('ascii'))
    return 0
if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,OSError,KeyError) as e:
        print(json.dumps({'status':'invalid','exit_code':1,'error':str(e)}),file=sys.stderr);raise SystemExit(1)
