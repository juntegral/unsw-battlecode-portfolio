import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
sys.path[:0]=['data/codex/astra/approach','data/analysis/ladder/dossier/local']
from scan import Board,replay,edge_id
from scoreboard import load_replay
replay.load=load_replay
p=Path(__file__).resolve().parent;b=Board(Path('data/online/live-one1/b1479873/M1479875.replay'));rows=[];cur=None
for ev in b.root.pointer(3):
 k=ev.u16(0)
 if k not in (0,1,3,4,9,10,11):continue
 x=ev.pointer(0)
 if k in (0,1):cur=None
 if k==4 and cur is not None:
  a=x.pointer(0);cur['action']=a.u16(0);cur['dirs']=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else []
 b.update(k,x)
 if k!=1:continue
 i=b.actor
 if not ((i in (0,8) and 111<=b.rnd<=116) or (i in (1033,951) and 474<=b.rnd<=478)):continue
 h=b.bodies[i][0];window=[((h[0]+dx)%b.W,(h[1]+dy)%b.H) for dy in range(-3,4) for dx in range(-3,4)]
 cur=dict(r=b.rnd,id=i,head=h,body=list(b.bodies[i]),teams=b.teams.copy(),
  bodies={z:list(bb) for z,bb in b.bodies.items()},pearls=list(b.pearls),
  window=window,edges=[(c,b.adj[c]) for c in window],
  options=[dict(dir=d,dest=n,occupants=[z for z,bb in b.bodies.items() if n in bb]) for d,n in enumerate(b.adj[h])])
 rows.append(cur)
(p/'moments.json').write_text(json.dumps(rows))
for r in rows:
 print(r['r'],r['id'],r['head'],len(r['body']),r.get('dirs'),r['options'])
