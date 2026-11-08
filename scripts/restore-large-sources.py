"""Restore verified large-source bytes without replacing an existing user file.

The manifest is data, not permission to escape the chosen output/payload roots.
All compressed parts, the complete gzip stream and decompressed bytes are checked.
"""
from __future__ import annotations
import argparse,gzip,hashlib,io,json,os,re,stat,sys,tempfile
from pathlib import Path,PurePosixPath

CHUNK=1024*1024
MAX_PART=64*1024*1024
RESERVED={'con','prn','aux','nul',*[f'com{i}' for i in range(1,10)],*[f'lpt{i}' for i in range(1,10)]}
class IntegrityError(ValueError):pass

def relative(value):
    if not isinstance(value,str) or not value or '\\' in value or ':' in value:raise ValueError('Unsafe relative path')
    pieces=value.split('/')
    if any(x in {'','.','..'} or x.rstrip(' .')!=x or x.split('.')[0].casefold() in RESERVED for x in pieces):raise ValueError('Unsafe relative path component')
    p=PurePosixPath(value)
    if p.is_absolute():raise ValueError('Absolute path rejected')
    return p

def safe_path(root,value):
    rel=relative(value);path=root.joinpath(*rel.parts);at=root
    for piece in rel.parts:
        at=at/piece
        if at.is_symlink():raise ValueError('Symlink path rejected')
    if not path.resolve().is_relative_to(root.resolve()):raise ValueError('Path escapes root')
    return path

def digest_file(path):
    h=hashlib.sha256();n=0
    with path.open('rb') as f:
        for b in iter(lambda:f.read(CHUNK),b''):h.update(b);n+=len(b)
    return h.hexdigest(),n

def digest(value):
    if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{64}',value):raise ValueError('Invalid SHA256')
    return value

def number(value,minimum=0):
    if type(value) is not int or value<minimum:raise ValueError('Invalid byte/count value')
    return value

def validate_manifest(manifest):
    if manifest.get('schema')!='sunny.large-source-manifest.v1' or manifest.get('status')!='complete':raise ValueError('A complete supported manifest is required')
    files=manifest.get('files')
    if not isinstance(files,list) or not files:raise ValueError('No source files listed')
    seen=set();limit=number(manifest['maxPartBytes'],1)
    if limit>MAX_PART:raise ValueError('Declared part size exceeds64MiB')
    for row in files:
        name=str(relative(row['sourcePath']));key=name.casefold()
        if key in seen:raise ValueError('Duplicate/case-aliased output path')
        seen.add(key);source_sha=digest(row['originalSha256']);digest(row['gzipSha256']);number(row['originalBytes'])
        parts=row['parts']
        if not isinstance(parts,list) or not parts or number(row['partCount'],1)!=len(parts):raise ValueError('Invalid part count')
        for index,part in enumerate(parts,1):
            if number(part['index'],1)!=index:raise ValueError('Nonconsecutive part index')
            if not 1<=number(part['bytes'],1)<=limit:raise ValueError('Invalid part length')
            digest(part['sha256']);expected=f'archives/large-files/{source_sha}/part-{index:04d}.gzpart'
            if part['repositoryPath']!=expected:raise ValueError('Unexpected or escaping repository part path')
        if number(row['gzipBytes'],1)!=sum(p['bytes'] for p in parts):raise ValueError('Gzip length differs from sum of parts')
    if manifest.get('fileCount',len(files))!=len(files):raise ValueError('File count mismatch')
    return files

class PartsReader(io.RawIOBase):
    def __init__(self,row,payload_root):
        self.row=row;self.root=payload_root;self.index=0;self.file=None;self.path=None
        self.total=0;self.sha=hashlib.sha256();self.checked=[]
    def readable(self):return True
    def _open(self):
        part=self.row['parts'][self.index]
        name=f"{self.row['originalSha256']}/part-{self.index+1:04d}.gzpart"
        self.path=safe_path(self.root,name)
        if not self.path.is_file() or not stat.S_ISREG(self.path.stat().st_mode):raise IntegrityError('Missing/nonregular compressed part')
        self.file=self.path.open('rb');self.before=os.fstat(self.file.fileno());self.part_sha=hashlib.sha256();self.count=0
    def _finish_part(self):
        after=os.fstat(self.file.fileno());self.file.close();self.file=None;p=self.row['parts'][self.index]
        if (self.before.st_size,self.before.st_mtime_ns,self.before.st_ino)!=(after.st_size,after.st_mtime_ns,after.st_ino):raise IntegrityError('Compressed part changed while read')
        if self.count!=p['bytes'] or self.part_sha.hexdigest()!=p['sha256']:raise IntegrityError(f'Compressed part integrity mismatch at index{self.index+1}')
        self.checked.append(self.index+1);self.index+=1
    def readinto(self,buffer):
        view=memoryview(buffer).cast('B');written=0
        while written<len(view) and self.index<len(self.row['parts']):
            if self.file is None:self._open()
            n=self.file.readinto(view[written:])
            if not n:self._finish_part();continue
            b=view[written:written+n];self.part_sha.update(b);self.sha.update(b);self.count+=n;self.total+=n;written+=n
        return written
    def close(self):
        if self.file:self.file.close();self.file=None
        super().close()

def verify_stream(row,payload_root,output=None):
    raw=PartsReader(row,Path(payload_root).resolve());h=hashlib.sha256();n=0
    try:
        with io.BufferedReader(raw,buffer_size=CHUNK) as buffered,gzip.GzipFile(fileobj=buffered,mode='rb') as zipped:
            while True:
                block=zipped.read(CHUNK)
                if not block:break
                n+=len(block)
                if n>row['originalBytes']:raise IntegrityError('Decompressed length exceeds declared original')
                h.update(block)
                if output is not None:output.write(block)
        if raw.checked!=list(range(1,row['partCount']+1)):raise IntegrityError('Not all parts were verified')
        if raw.total!=row['gzipBytes'] or raw.sha.hexdigest()!=row['gzipSha256']:raise IntegrityError('Complete gzip integrity mismatch')
        if n!=row['originalBytes'] or h.hexdigest()!=row['originalSha256']:raise IntegrityError('Restored original integrity mismatch')
        return {'partsVerified':len(raw.checked),'gzipBytesVerified':raw.total,'originalBytesVerified':n,'originalSha256':h.hexdigest()}
    finally:raw.close()

def restore(manifest,repository_root,output_root=None,payload_root=None,verify_only=False,progress=None):
    rows=validate_manifest(manifest);repository_root=Path(repository_root).resolve()
    output_root=Path(output_root).resolve() if output_root else repository_root
    payload_root=Path(payload_root).resolve() if payload_root else repository_root/'archives/large-files'
    # Validate the entire path set before any output is created.
    paths=[safe_path(output_root,row['sourcePath']) for row in rows]
    for row,path in zip(rows,paths):
        if path.exists():
            if not path.is_file() or path.is_symlink():raise ValueError('Existing target is not a regular user file')
            if digest_file(path)!=(row['originalSha256'],row['originalBytes']):raise FileExistsError(f'Preserving mismatching existing file: {row["sourcePath"]}')
    results=[]
    for row,target in zip(rows,paths):
        existed=target.exists();temporary=None
        try:
            if verify_only or existed:
                verified=verify_stream(row,payload_root)
                status='verified-only' if verify_only else 'already-present-and-verified'
            else:
                target.parent.mkdir(parents=True,exist_ok=True);safe_path(output_root,row['sourcePath'])
                fd,name=tempfile.mkstemp(prefix='.sunny-restore-',suffix='.partial',dir=target.parent);temporary=Path(name)
                with os.fdopen(fd,'wb') as stream:
                    verified=verify_stream(row,payload_root,stream);stream.flush();os.fsync(stream.fileno())
                # Hard-link publication is atomic and refuses an existing destination.
                # It never uses replace/rename-over-target, even if a file appeared mid-read.
                safe_path(output_root,row['sourcePath'])
                try:os.link(temporary,target,follow_symlinks=False)
                except FileExistsError:
                    if target.is_symlink() or digest_file(target)!=(row['originalSha256'],row['originalBytes']):raise FileExistsError('A target appeared during restore; its bytes were preserved')
                status='restored-missing-file'
            if existed and digest_file(target)!=(row['originalSha256'],row['originalBytes']):raise FileExistsError('Existing user file changed during verification; it was not overwritten')
            results.append({'sourcePath':row['sourcePath'],'status':status,**verified})
            if progress:progress({'completedFiles':len(results),'totalFiles':len(rows),**results[-1]})
        finally:
            if temporary is not None and temporary.exists():temporary.unlink()
    return {'schema':'sunny.large-source-restore.v1','status':'verified','verifyOnly':verify_only,'existingFilesOverwritten':False,'files':results}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',default=str(Path(__file__).resolve().parents[1]));parser.add_argument('--manifest',default='state/publication/large-files-manifest.json');parser.add_argument('--output-root');parser.add_argument('--payload-root');parser.add_argument('--verify-only',action='store_true');args=parser.parse_args()
    root=Path(args.root).resolve();manifest_path=Path(args.manifest)
    if not manifest_path.is_absolute():manifest_path=safe_path(root,args.manifest)
    manifest=json.loads(manifest_path.read_text(encoding='utf-8-sig'));result=restore(manifest,root,args.output_root,args.payload_root,args.verify_only,progress=lambda row:print(json.dumps(row),file=sys.stderr,flush=True))
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({'status':'failed','errorType':type(exc).__name__,'error':str(exc)}),file=sys.stderr);raise SystemExit(1)
