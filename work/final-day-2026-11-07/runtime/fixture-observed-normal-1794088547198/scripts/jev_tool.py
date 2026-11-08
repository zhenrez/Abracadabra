import json,os,sys,subprocess,time
from pathlib import Path
payload=json.loads(sys.stdin.read())
mode=payload['mode']
child=subprocess.Popen([sys.executable,'-c','import time;time.sleep('+('0.05' if mode=='normal' else '60')+')'])
Path(__file__).resolve().parents[1].joinpath('owned.json').write_text(json.dumps({'interpreter':os.getpid(),'child':child.pid}))
if mode=='normal':
 child.wait()
 print(json.dumps({'status':'invalid','error':'Synthetic lifecycle transport; no inference'}),file=sys.stderr)
 sys.exit(1)
print('x'*20000,flush=True)
time.sleep(60)
