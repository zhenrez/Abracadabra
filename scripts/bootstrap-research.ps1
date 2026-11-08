[CmdletBinding()]
param(
    [switch]$VerifyOnly,
    [string]$Python = 'python',
    [string]$EnvironmentPath = '.venv-research',
    [switch]$RestoreJevSource,
    [switch]$CheckJevSource,
    [string]$ReportPath = 'docs/publication/bootstrap-verification.json'
)
$ErrorActionPreference = 'Stop'
$bootstrapRoot = Split-Path -Parent $PSScriptRoot
$bootstrapManifest = Join-Path $bootstrapRoot 'docs/publication/bootstrap-manifest.json'
$bootstrapRequirements = Join-Path $bootstrapRoot 'requirements-research.txt'
$bootstrapEnvironment = if ([IO.Path]::IsPathRooted($EnvironmentPath)) { $EnvironmentPath } else { Join-Path $bootstrapRoot $EnvironmentPath }
$bootstrapReport = if ([IO.Path]::IsPathRooted($ReportPath)) { $ReportPath } else { Join-Path $bootstrapRoot $ReportPath }
$bootstrapPython = $Python

if ($VerifyOnly -and $RestoreJevSource) { throw '-VerifyOnly never clones or installs. Run source restoration separately.' }
if (-not $VerifyOnly) {
    $bootstrapVenvPython = Join-Path $bootstrapEnvironment 'Scripts/python.exe'
    if (-not (Test-Path -LiteralPath $bootstrapVenvPython -PathType Leaf)) {
        & $Python -m venv $bootstrapEnvironment
        if ($LASTEXITCODE -ne 0) { throw 'Could not create the isolated research environment.' }
    }
    $bootstrapPython = $bootstrapVenvPython
    & $bootstrapPython -m pip install -r $bootstrapRequirements
    if ($LASTEXITCODE -ne 0) { throw 'Research dependency installation failed.' }
    & $bootstrapPython -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'Installed dependency consistency check failed.' }
}
if ($RestoreJevSource) {
    $bootstrapSpec = Get-Content -LiteralPath $bootstrapManifest -Raw | ConvertFrom-Json
    $bootstrapJev = Join-Path $bootstrapRoot 'runtime/agent-jev'
    if (-not (Test-Path -LiteralPath $bootstrapJev)) {
        & git clone --no-checkout $bootstrapSpec.jevSource.repository $bootstrapJev
        if ($LASTEXITCODE -ne 0) { throw 'Public Jev source clone failed.' }
        & git -C $bootstrapJev checkout --detach $bootstrapSpec.jevSource.commit
        if ($LASTEXITCODE -ne 0) { throw 'Pinned Jev source checkout failed.' }
    }
    $CheckJevSource = $true
}
$bootstrapProbe = @'
import datetime,hashlib,importlib,importlib.metadata as metadata,json,pathlib,subprocess,sys
root=pathlib.Path(sys.argv[1]); manifest=json.loads(pathlib.Path(sys.argv[2]).read_text(encoding='utf-8-sig'))
report_path=pathlib.Path(sys.argv[3]); check_jev=sys.argv[4]=='1'
rows=[]
for spec in manifest['researchDependencies']:
    row={'distribution':spec['distribution'],'expected':spec['version'],'installed':None,'import_ok':False,'functional_smoke':None}
    try:
        row['installed']=metadata.version(spec['distribution'])
        module=importlib.import_module(spec['importModule'])
        row['import_ok']=True
        name=spec['distribution'].lower()
        if name=='pillow':
            image=module.new('RGB',(1,1),(12,34,56)); assert image.getpixel((0,0))==(12,34,56); image.close()
            row['functional_smoke']='one-pixel memory image'
        elif name=='sympy':
            assert module.Matrix([[1,2],[3,4]]).det()==-2
            row['functional_smoke']='exact 2x2 determinant'
        elif name=='openpyxl':
            book=module.Workbook();book.active['A1']=7;assert book.active['A1'].value==7;book.close()
            row['functional_smoke']='in-memory workbook cell'
        elif name=='pypdf':
            writer=module.PdfWriter();writer.add_blank_page(width=72,height=72);assert len(writer.pages)==1
            row['functional_smoke']='in-memory one-page PDF'
        else: row['functional_smoke']='module/native-library import only; no source PDF opened'
    except Exception as exc:
        row['error']=type(exc).__name__+': '+str(exc)
    row['passed']=row['installed']==row['expected'] and row['import_ok'] and 'error' not in row
    rows.append(row)
jev={'requested':check_jev,'model_loaded':False,'model_weights_rehashed':False}
if check_jev:
    checks=[]
    for item in manifest['jevSource']['criticalFiles']:
        path=root/item['path']; actual=hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        checks.append({'path':item['path'],'sha256':actual,'expected':item['sha256'],'passed':actual==item['sha256']})
    repo=root/'runtime/agent-jev'
    if (repo/'.git').exists():
        run=subprocess.run(['git','-C',str(repo),'rev-parse','HEAD'],capture_output=True,text=True,timeout=10)
        jev['git_commit']=run.stdout.strip() if run.returncode==0 else None
        jev['git_pin_matches']=jev['git_commit']==manifest['jevSource']['commit']
    else:
        jev['git_pin_matches']=None
        jev['source_scope']='Vendored critical-file hashes only; no Git identity independently verified.'
    jev['critical_file_checks']=checks
    jev['passed']=all(c['passed'] for c in checks) and jev.get('git_pin_matches') is not False
passed=all(r['passed'] for r in rows) and (not check_jev or jev['passed'])
report={'schema':'sunny.research-bootstrap-verification.v1','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'passed' if passed else 'dependency-gap','python':sys.version,'executable':sys.executable,'packages':rows,'jev_source':jev,
 'manifest_sha256':hashlib.sha256(pathlib.Path(sys.argv[2]).read_bytes()).hexdigest(),
 'model_downloaded':False,'new_environment_full_suite_run':False,
 'boundary':'Pinned direct dependencies, available imports/smokes and optional public Jev source identity only. Not archive restoration, live model inference or scientific completion.'}
report_path.parent.mkdir(parents=True,exist_ok=True);report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=True,indent=2))
sys.exit(0 if passed else 2)
'@
$bootstrapCheckFlag = if ($CheckJevSource) { '1' } else { '0' }
$bootstrapProbe | & $bootstrapPython -X utf8 -B - $bootstrapRoot $bootstrapManifest $bootstrapReport $bootstrapCheckFlag
exit $LASTEXITCODE
