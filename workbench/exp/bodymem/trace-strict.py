from pathlib import Path
import subprocess,json,concurrent.futures
p=Path('exp/bodymem')
jobs=[]
for arm in ('on','off'):
 rows={}
 for line in (p/arm/'rows.jsonl').read_text().splitlines():
  r=json.loads(line)
  if r.get('exit')==0 and 'G' in r and not r.get('error') and not r.get('botProblem'):rows[r['key']]=r
 for key,r in rows.items(): jobs.append((arm,key,r['side']))
def trace(job):
 arm,key,side=job
 prefix=p/'memory-strict'/arm/key.replace(':','_')
 f=p/arm/'games'/key.replace(':','_')/'game.replay'
 q=subprocess.run(['node',str(p/'memory-trace-strict.js'),str(f),side,str(prefix)],capture_output=True,text=True)
 if q.returncode:raise RuntimeError(str(job)+' '+q.stderr)
 print(q.stdout.strip(),flush=True)
 return {'arm':arm,'key':key,'file':str(prefix)+'.json'}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
 rows=list(ex.map(trace,jobs))
(p/'memory-strict-index.json').write_text(json.dumps(rows,indent=2)+'\n')
