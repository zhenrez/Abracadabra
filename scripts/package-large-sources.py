"""Stream only explicitly inventoried large sources into bounded, byte-verifiable parts.

Originals are opened read-only. This preserves raw SQLite bytes, not a transactional
database backup. No database connection, checkpoint, or WAL mutation is performed.
"""
from __future__ import annotations
import argparse,datetime,gzip,hashlib,json,os,re,stat,sys,time,uuid
from pathlib import Path,PurePosixPath

CHUNK=1024*1024
MAX_PART=64*1024*1024
DEFAULT_PART=8*1024*1024
RESERVED={'con','prn','aux','nul',*[f'com{i}' for i in range(1,10)],*[f'lpt{i}' for i in range(1,10)]}

def relative(value):
    if not isinstance(value,str) or not value or '\\' in value or ':' in value:
        raise ValueError(f'Unsafe relative path: {value!r}')
    pieces=value.split('/')
    if any(x in {'','.','..'} or x.rstrip(' .')!=x or x.split('.')[0].casefold() in RESERVED for x in pieces):
        raise ValueError(f'Unsafe path component: {value!r}')
    p=PurePosixPath(value)
    if p.is_absolute():raise ValueError('Absolute source path rejected')
    return p

def contained(root,value,require_file=False):
    p=relative(value);candidate=root.joinpath(*p.parts)
    at=root
    for piece in p.parts:
        at=at/piece
        if at.is_symlink():raise ValueError(f'Symlink path rejected: {value}')
    if not candidate.resolve().is_relative_to(root.resolve()):raise ValueError('Path escapes root')
    if require_file and (not candidate.is_file() or not stat.S_ISREG(candidate.stat().st_mode)):
        raise ValueError(f'Not a regular file: {value}')
    return candidate

def fingerprint(path):
    s=path.stat()
    return {'bytes':s.st_size,'mtimeNs':s.st_mtime_ns,'ctimeNs':s.st_ctime_ns,'device':s.st_dev,'inode':s.st_ino}

def sha_file(path,progress=None):
    h=hashlib.sha256();n=0
    with path.open('rb') as f:
        for block in iter(lambda:f.read(CHUNK),b''):
            h.update(block);n+=len(block)
            if progress:progress(n)
    return h.hexdigest(),n

def save_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.writing')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    os.replace(temp,path)

def sqlite_sidecars(path):
    result={}
    if path.suffix.lower() not in {'.sqlite','.sqlite3','.db'}:return None
    for suffix in ['-wal','-shm','-journal']:
        side=Path(str(path)+suffix)
        if side.is_symlink():raise ValueError('SQLite sidecar symlink rejected')
        if side.exists():
            before=fingerprint(side);digest,n=sha_file(side);after=fingerprint(side)
            if before!=after:raise RuntimeError('SQLite sidecar changed while read')
            result[suffix]={'exists':True,'stat':after,'sha256':digest,'bytes':n}
        else:result[suffix]={'exists':False}
    return result

class SplitGzipSink:
    def __init__(self,folder,original_sha,part_bytes):
        if not 1<=part_bytes<=MAX_PART:raise ValueError('Part size must be1..64MiB')
        self.folder=folder;self.original_sha=original_sha;self.limit=part_bytes
        self.parts=[];self.file=None;self.count=0;self.total=0;self.sha=hashlib.sha256();self.part_sha=None
    def tell(self):return self.total
    def flush(self):
        if self.file:self.file.flush()
    def _open(self):
        self.name=f'part-{len(self.parts)+1:04d}.gzpart'
        self.file=(self.folder/self.name).open('xb');self.count=0;self.part_sha=hashlib.sha256()
    def _close(self):
        if self.file:
            self.file.flush();os.fsync(self.file.fileno());self.file.close();self.file=None
            self.parts.append({'index':len(self.parts)+1,'bytes':self.count,'sha256':self.part_sha.hexdigest(),
                'repositoryPath':f'archives/large-files/{self.original_sha}/{self.name}'})
    def write(self,block):
        block=memoryview(block);original=len(block);self.sha.update(block);self.total+=original
        while block:
            if self.file is None:self._open()
            n=min(len(block),self.limit-self.count);piece=block[:n];self.file.write(piece);self.part_sha.update(piece)
            self.count+=n;block=block[n:]
            if self.count==self.limit:self._close()
        return original
    def finish(self):self._close()

def package_files(root,source_paths,work_root,manifest_path,part_bytes=DEFAULT_PART,level=1,inventory_bytes=None,progress_path=None):
    root=Path(root).resolve();work_root=Path(work_root).resolve();manifest_path=Path(manifest_path).resolve()
    if not work_root.is_relative_to(root):raise ValueError('Payload work root must remain inside project')
    if manifest_path.exists():raise FileExistsError('Preserving existing manifest; choose a new manifest/work root or use --rechunk-existing explicitly')
    if len(set(p.casefold() for p in source_paths))!=len(source_paths):raise ValueError('Duplicate or case-aliased source path')
    if level not in {1,3}:raise ValueError('Compression level must be1or3')
    work_root.mkdir(parents=True,exist_ok=True)
    report={'schema':'sunny.large-source-manifest.v1','status':'packing','startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'originalsModified':False,'compression':'one deterministic gzip stream per original, split across bounded parts',
        'compressionLevel':level,'maxPartBytes':part_bytes,'sourceRootConvention':'repository relative paths',
        'payloadRepositoryPrefix':'archives/large-files','payloadWorkRoot':work_root.relative_to(root).as_posix(),
        'scope':'Raw byte preservation only; no publication or SQLite transaction-consistency claim','files':[]}
    save_json(manifest_path,report)
    last_progress=[0.0]
    def emit(source,phase,n,total):
        now=time.monotonic()
        if now-last_progress[0]<2 and n!=total:return
        last_progress[0]=now
        value={'sourcePath':source,'phase':phase,'sourceBytesProcessed':n,'sourceBytes':total,'completedFiles':len(report['files']),'totalFiles':len(source_paths),'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        if progress_path:save_json(Path(progress_path),value)
        print(json.dumps(value),flush=True)
    for name in source_paths:
        src=contained(root,name,True);before=fingerprint(src)
        if inventory_bytes is not None and before['bytes']!=inventory_bytes[name]:raise RuntimeError(f'Inventory size changed: {name}')
        sides_before=sqlite_sidecars(src)
        original_sha,n=sha_file(src,lambda n:emit(name,'hash-original',n,before['bytes']))
        if n!=before['bytes'] or fingerprint(src)!=before:raise RuntimeError(f'Original changed during first read: {name}')
        folder=work_root/original_sha
        alias=next((f for f in report['files'] if f['originalSha256']==original_sha),None)
        if alias:
            packed={k:alias[k] for k in ['gzipSha256','gzipBytes','partCount','parts']};packed['samePayloadAs']=alias['sourcePath']
        else:
            if folder.exists():raise FileExistsError(f'Preserving existing payload directory; not overwriting: {folder}')
            folder.mkdir();sink=SplitGzipSink(folder,original_sha,part_bytes);check=hashlib.sha256();read_bytes=0
            try:
                with src.open('rb') as original,gzip.GzipFile(filename='',mode='wb',fileobj=sink,compresslevel=level,mtime=0) as zipped:
                    for block in iter(lambda:original.read(CHUNK),b''):
                        check.update(block);read_bytes+=len(block);zipped.write(block);emit(name,'gzip-and-split',read_bytes,before['bytes'])
                sink.finish()
            except BaseException:
                sink.finish();raise
            if check.hexdigest()!=original_sha or read_bytes!=before['bytes']:raise RuntimeError(f'Original bytes changed between hash and compression reads: {name}')
            packed={'gzipSha256':sink.sha.hexdigest(),'gzipBytes':sink.total,'partCount':len(sink.parts),'parts':sink.parts}
        after=fingerprint(src);sides_after=sqlite_sidecars(src)
        if before!=after or sides_before!=sides_after:raise RuntimeError(f'Original or SQLite sidecars changed while packaging: {name}')
        row={'sourcePath':name,'originalBytes':n,'originalSha256':original_sha,'sourceStatBefore':before,'sourceStatAfter':after,'sourceStable':True,**packed}
        if sides_before is not None:
            row['sqlite']={'sidecarsBefore':sides_before,'sidecarsAfter':sides_after,'sidecarsStable':True,
                'assessment':('WAL present: stable raw main/sidecar bytes were observed, but a transaction-consistent SQLite snapshot is NOT established; retain matching sidecars separately.' if sides_before['-wal']['exists'] else 'No WAL sidecar was present before or after reading. Main bytes were stable; SQLite logical integrity was not tested.'),
                'databaseOpenedBySQLite':False,'checkpointOrMutationPerformed':False}
        report['files'].append(row);save_json(manifest_path,report);emit(name,'complete',n,n)
    report.update({'status':'complete','finishedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fileCount':len(report['files']),
        'totalOriginalBytes':sum(f['originalBytes'] for f in report['files']),
        'uniquePayloadBytes':sum(f['gzipBytes'] for f in report['files'] if 'samePayloadAs' not in f),
        'uniquePartCount':sum(f['partCount'] for f in report['files'] if 'samePayloadAs' not in f)})
    save_json(manifest_path,report)
    return report

def rechunk_manifest(manifest_path,work_root,part_bytes=DEFAULT_PART):
    """Re-segment existing gzip bytes; preserve prior parts and all original files."""
    manifest_path=Path(manifest_path);work_root=Path(work_root).resolve()
    report=json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    if report.get('schema')!='sunny.large-source-manifest.v1' or report.get('status')!='complete':raise ValueError('Completed packaging required before re-segmentation')
    if not 1<=part_bytes<=DEFAULT_PART:raise ValueError('Publication parts must be at most8MiB')
    previous_limit=report['maxPartBytes']
    if previous_limit==part_bytes:return report
    save_json(work_root/'manifest-before-rechunk.json',report)
    converted={};retained=[]
    for row in report['files']:
        sha=row['originalSha256']
        if sha in converted:continue
        if not re.fullmatch('[0-9a-f]{64}',sha):raise ValueError('Invalid original SHA')
        old=work_root/sha;fresh=work_root/('_rechunk-'+sha+'-'+uuid.uuid4().hex)
        if not old.resolve().is_relative_to(work_root) or old.is_symlink():raise ValueError('Unsafe old payload path')
        fresh.mkdir();sink=SplitGzipSink(fresh,sha,part_bytes)
        for index,part in enumerate(row['parts'],1):
            expected=f'archives/large-files/{sha}/part-{index:04d}.gzpart'
            if part['repositoryPath']!=expected:raise ValueError('Unexpected old part path')
            path=old/f'part-{index:04d}.gzpart'
            if path.is_symlink():raise ValueError('Part symlink rejected')
            h=hashlib.sha256();count=0
            with path.open('rb') as stream:
                for block in iter(lambda:stream.read(CHUNK),b''):h.update(block);count+=len(block);sink.write(block)
            if count!=part['bytes'] or h.hexdigest()!=part['sha256']:raise RuntimeError('Old compressed part changed')
        sink.finish()
        if sink.total!=row['gzipBytes'] or sink.sha.hexdigest()!=row['gzipSha256']:raise RuntimeError('Re-segmentation changed gzip bytes')
        prior=work_root/('_previous-parts-'+sha+'-'+uuid.uuid4().hex)
        # Both directory move targets are resolved and confined to owned payload work.
        for candidate in [old,fresh,prior]:
            if not candidate.resolve().is_relative_to(work_root):raise ValueError('Payload directory move escapes work root')
        old.rename(prior);fresh.rename(old);retained.append(prior.name)
        converted[sha]=sink.parts
        print(json.dumps({'phase':'rechunk-complete','originalSha256':sha,'partBytes':part_bytes,'partCount':len(sink.parts)}),flush=True)
    for row in report['files']:row['parts']=converted[row['originalSha256']];row['partCount']=len(row['parts'])
    report.update({'maxPartBytes':part_bytes,'rechunkedFromPartBytes':previous_limit,'rechunkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'uniquePartCount':sum(f['partCount'] for f in report['files'] if 'samePayloadAs' not in f),
        'previousPartsRetainedOnlyInWork':retained})
    save_json(manifest_path,report);return report

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',default=str(Path(__file__).resolve().parents[1]));parser.add_argument('--inventory',default='state/publication/inventory-review.json');parser.add_argument('--work-root',default='work/publication/large');parser.add_argument('--manifest',default='state/publication/large-files-manifest.json');parser.add_argument('--level',type=int,choices=[1,3],default=1);parser.add_argument('--rechunk-existing',action='store_true');args=parser.parse_args()
    root=Path(args.root).resolve()
    if args.rechunk_existing:
        report=rechunk_manifest(contained(root,args.manifest,True),contained(root,args.work_root))
        print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2));return 0
    inventory_path=contained(root,args.inventory,True);inventory=json.loads(inventory_path.read_text(encoding='utf-8-sig'))
    rows=[r for r in inventory['files'] if int(r['bytes'])>90*1024*1024]
    if len(rows)!=6:raise ValueError(f'Expected exactly6 inventoried files over90MiB; found{len(rows)}')
    report=package_files(root,[r['path'] for r in rows],contained(root,args.work_root),contained(root,args.manifest),level=args.level,inventory_bytes={r['path']:int(r['bytes']) for r in rows},progress_path=contained(root,args.work_root)/'progress.json')
    print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2));return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({'status':'failed','errorType':type(exc).__name__,'error':str(exc)}),file=sys.stderr,flush=True);raise SystemExit(1)
