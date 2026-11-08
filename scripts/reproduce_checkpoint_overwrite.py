"""Reproduce only actual context assignments, without running DB or services."""
from pathlib import Path
import ast, copy, hashlib, json
root=Path(__file__).resolve().parents[1]
path=root/'scripts/refresh_reconstruction_checkpoint.py'
raw=path.read_bytes()
tree=ast.parse(raw)
function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
keys={'current_priority','latest_user_priority_exact','next_actions','completion'}
assignments=[]
for node in function.body:
    if not isinstance(node,ast.Assign): continue
    for target in node.targets:
        if isinstance(target,ast.Subscript) and isinstance(target.value,ast.Name) and target.value.id=='state' and isinstance(target.slice,ast.Constant) and target.slice.value in keys:
            assignments.append(node);break
before={'current_priority':'CURRENT USER MANDATE','latest_user_priority_exact':'CURRENT EXACT INPUT','next_actions':['DERIVE ACTUAL MATHEMATICS'],'completion':'CURRENT EVIDENCE'}
after=copy.deepcopy(before)
code=ast.fix_missing_locations(ast.Module(body=assignments,type_ignores=[]))
exec(compile(code,str(path),'exec'),{}, {'state':after})
changed=[key for key in keys if before[key]!=after[key]]
report={'schema':'sunny.checkpoint-overwrite-reproduction.v1','source_sha256':hashlib.sha256(raw).hexdigest(),'direct_context_assignments':len(assignments),'overwritten_fields':sorted(changed),'before':before,'after':after,'bug_reproduced':bool(changed),'scope':'Only selected assignments from actual main(); no database, checkpoint or service execution.'}
print(json.dumps(report,indent=2))
