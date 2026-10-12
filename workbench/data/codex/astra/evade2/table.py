import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
from collections import Counter
from datetime import datetime
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'evade'))
import analyze as a
OUT=Path(__file__).resolve().parent
inventory=[];rows=[]
for label in ('one5-w1','one5-c1','one7-w1','one7-c1'):
 inv=a.label_report.inventory(label,'old')
 inventory.append(dict(label=label,planned=inv['planned'],games=len(inv['jobs']),ids=[m['id'] for p,m in inv['jobs']],notes=inv['notes']))
 for p,m in inv['jobs']:
  cache=OUT/f'table-{m["id"]}.json'
  if cache.exists(): game=json.loads(cache.read_text())
  elif label.startswith('one5'):
   game=json.loads((a.OUT/f'g{m["id"]}.json').read_text())
  else:
   game=a.scan(p,m,label)
   cache.write_text(json.dumps(game,separators=(',',':')))
  g=a.Geo(a.lr.replay.load(p).root().text(0))
  for row in game['rows']:
   if row['side']!='us':continue
   rec={k:v for k,v in row.items() if k not in ('safe','safe_all','known_safe')}
   rec['basic_status']=row['status'];safe=[];cap=0
   if row['status']=='avoidable':
    bs={i:tuple(tuple(c) for c in b) for i,s,b in row['start_bodies']}
    for op in row['safe']:
     try: hit=a.hits(g,bs,row['attacker'],row['victim'],tuple(tuple(c) for c in op['body']),set(tuple(c) for c in op['remaining_pearls']),extra_budget=True)
     except RuntimeError:cap+=1;continue
     if not hit:safe.append(op)
    rec['status']='avoidable' if safe else 'unresolved' if cap else 'not avoidable'
   rec['safe']=safe;rec['capped']=cap;rows.append(rec)
  print(label,m['id'],dict(Counter(r['status'] for r in rows if r['gid']==m['id'])),flush=True)
  (OUT/'table-rows.json').write_text(json.dumps(rows,separators=(',',':')))
(OUT/'inventory.json').write_text(json.dumps(dict(time=datetime.now().astimezone().isoformat(),sets=inventory),indent=2))
summary={l:dict(Counter(r['status'] for r in rows if r['label']==l)) for l in ('one5-w1','one5-c1','one7-w1','one7-c1')}
(OUT/'table-summary.json').write_text(json.dumps(summary,indent=2));print(summary,flush=True)
