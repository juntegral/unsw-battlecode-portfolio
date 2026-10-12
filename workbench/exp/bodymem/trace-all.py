from pathlib import Path
import subprocess,json,concurrent.futures
p=Path('exp/bodymem')
for arm in ('on','off'):
 b=p/('bot-'+arm)
 subprocess.run(['/usr/bin/clang++','-std=c++20','-O2','-I',str(b),str(p/'memory-world.cpp'),str(b/'world.cpp'),str(b/'mapid.cpp'),str(b/'ptmod.cpp'),'-o',str(p/('memory-world-'+arm))],check=True)
jobs=[]
for arm in ('on','off'):
 rows={}
 for line in (p/arm/'rows.jsonl').read_text().splitlines():
  r=json.loads(line)
  if r.get('exit')==0 and 'G' in r and not r.get('error') and not r.get('botProblem'):rows[r['key']]=r
 for key,r in rows.items(): jobs.append((arm,key,r['side']))
def trace(job):
 arm,key,side=job
 prefix=p/'memory-audit'/arm/key.replace(':','_')
 f=p/arm/'games'/key.replace(':','_')/'game.replay'
 q=subprocess.run(['node',str(p/'memory-trace.js'),str(f),side,str(prefix)],capture_output=True,text=True)
 if q.returncode:raise RuntimeError(str(job)+' '+q.stderr)
 print(q.stdout.strip(),flush=True)
 return {'arm':arm,'key':key,'file':str(prefix)+'.json'}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
 rows=list(ex.map(trace,jobs))
(p/'memory-index.json').write_text(json.dumps(rows,indent=2)+'\n')
