import sys
sys.dont_write_bytecode=True
sys.path.insert(0,'data/codex/astra/approach')
from scan import Board,replay
from collections import Counter
from pathlib import Path
import json
O=Path(__file__).resolve().parent
G=[json.loads(l) for l in (O/'games.jsonl').read_text().splitlines()]
assert len(G)==len({g['game'] for g in G})==90
assert all(g['bot'] in ('20980','21033') for g in G)
assert all(g['event_counts'].get('2',0)==0 for g in G)
def state(gid,actor,r):
 b=Board(f'data/online/live-one1/b1477038/M{gid}.replay')
 for e in b.root.pointer(3):
  k=e.u16(0);p=e.pointer(0);b.update(k,p)
  if k==1 and b.actor==actor and b.rnd==r:return b

def path(b,i,dirs,paid=False):
 body=list(b.bodies[i]);occ={c:z for z,bb in b.bodies.items() if z!=i for c in bb};pearls=set(b.pearls);free=(len(body)+3)//4;steps=[]
 for k,d in enumerate(dirs):
  cost=paid and k>=free
  assert not cost or len(body)>2
  n=b.adj[body[0]][d];assert n is not None and n not in body
  if n in occ:
   z=occ[n];assert b.bodies[z][0]==n
   steps.append(dict(to=n,ram=z));return steps
  eat=n in pearls
  body.insert(0,n)
  if not eat:body.pop()
  if cost:body.pop()
  pearls.discard(n);steps.append(dict(to=n,eat=eat,L=len(body)))
 return steps
b=state(1477042,6,20)
a=path(b,6,[1,2,3,2,1]);assert sum(x.get('eat',False) for x in a)==3
b=state(1477048,2,16)
c=path(b,2,[2,1],True);assert c[-1]['ram']==1 and c[0]['eat']
d=path(b,2,[1,2],True);assert d[-1]['ram']==1
# Independent re-count of #6's no-eat near-mouth run from raw turn starts.
b=Board('data/online/live-one1/b1477038/M1477042.replay');heads=[];eats=[]
for e in b.root.pointer(3):
 k=e.u16(0);p=e.pointer(0)
 if k==3 and not p.u32(0) and b.actor==6:eats.append(b.rnd)
 b.update(k,p)
 if k==1 and b.actor==6:heads.append((b.rnd,b.bodies[6][0]))
near=[r for r,h in heads if 15<=r<=159 and min(abs(h[0]-x)+abs(h[1]-y) for x,y in [(16,8),(17,8)])<=2]
assert len(near)==145 and not set(eats)&set(near)
result=dict(games=90,dedup=True,all_final_scores_verified_by_scan=True,portal_run_verified=145,portal_alternative_frozen_other_dragons=a,trophy_SE=c,trophy_ES=d,scope='Alternative paths freeze other dragons; not a counterfactual match.')
(O/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
