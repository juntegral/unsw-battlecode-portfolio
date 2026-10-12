import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
from collections import Counter
from moments import audit,Board
OUT=Path(__file__).resolve().parent

def inspect(d,B,own):
 t=d['last'];a=d['attacker']
 if t is None or d['reason']!=3 or a['id']==d['id'] or d['id']==own or t['L']>4 or not t.get('end') or t['split']:return None
 bodies={int(i):[tuple(c) for c in b] for i,b in t['bodies'].items()};teams={int(i):s for i,s in t['teams'].items()};h=tuple(t['h']);end=tuple(t['end']);occ={c for b in bodies.values() for c in b}
 # Mimic the small-unit threat radius on the observed geometry; not the entire bot score.
 old=set();new=set();attackdist=None
 for i in t['visible']:
  if teams[i]==own:continue
  parts=sum(B.view(h,c) for c in bodies[i])
  if parts>=5:continue
  ds=B.flood(bodies[i][0],max(1,parts-1),occ-{bodies[d['id']][-1]})
  old.update(c for c,dist in ds.items() if dist==1)
  new.update(c for c,dist in ds.items() if 1<=dist<=max(1,parts-1))
  if i==a['id']:attackdist=ds.get(end)
 safe=[list(c) for c in B.adj[h] if c is not None and c not in occ and c not in new]
 return dict(r=d['r'],turn=t['r'],id=d['id'],actor=a['id'],old_danger=end in old,new_danger=end in new,safe=safe,attackdist=attackdist,newly_marked=end in new and end not in old,whole_attacker=a['id'] in t['visible'] and all(B.view(h,c) for c in bodies.get(a['id'],[])))
if __name__=='__main__':
 jobs=json.loads((OUT/'inventory.json').read_text())['games'];out=[]
 for job in jobs:
  p=Path(job['path']);m=json.loads(p.with_name('game-%s.json'%job['gid']).read_text());own=int(m['teamAId']!=1119)
  a=audit(p,own);B=Board(p)
  rows=[v for d in a['deaths'] if (v:=inspect(d,B,own))]
  out.append(dict(label=job['label'],gid=job['gid'],rows=rows));print(job['gid'],flush=True)
 (OUT/'radius.json').write_text(json.dumps(out,indent=2))
