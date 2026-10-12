import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path[:0]=['tools','data/analysis/ladder/dossier/local']
import ladder_replay as lr
from count_local import Geo
D=Path('data/codex/astra/sweep/1055/loss41')
for gid in [1511407,1511409,1511410]:
 root=lr.replay.load(f'data/online/live-one1/b1511406/M{gid}.replay').root();bs={};teams={};raw=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if not q:continue
  if q[0]=='MAP':w,h=map(int,q[1:3])
  elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
  elif q[0]=='DRAGON':i=len(bs);bs[i]=int(q[4])*w+int(q[3]);teams[i]=int(q[1])
 g=Geo(w,h,raw);rev=[[]for _ in g.adj]
 for c,adj in enumerate(g.adj):
  for n in adj:rev[n].append(c)
 us=min(i for i in bs if teams[i]==1);foe=min(i for i in bs if teams[i]==0);dead=False;cache={};near={};nearest=None;pos=Counter();rd=-1;actor=-1
 for ix,e in enumerate(root.pointer(3)):
  k=e.u16(0);p=e.pointer(0)
  if k==0:rd=p.i32(0)
  elif k==1:actor=p.i32(0)
  elif k==9:xy=lr.replay.point(p.pointer(0));bs[p.i32(0)]=xy[1]*w+xy[0]
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):xy=lr.replay.point(next(iter(p.pointer(z))));bs[i]=xy[1]*w+xy[0];teams[i]=p.u16(8)
  elif k==11:i=p.i32(0);bs.pop(i);dead|=i==us
  if not(dead and foe in bs and k in (0,1,9,10,11)):continue
  target=bs[foe]
  if target not in cache:
   ds={target:0};queue=deque([target])
   while queue:
    c=queue.popleft()
    for n in rev[c]:
     if n not in ds:ds[n]=ds[c]+1;queue.append(n)
   cache[target]=ds
  ds=cache[target];best=min(((ds.get(c,99999),i,c) for i,c in bs.items() if teams[i]==1),default=(99999,None,None));row={'r':rd,'distance':best[0],'id':best[1],'head':best[2],'queen':target,'event':ix,'actor':actor}
  if nearest is None or best[0]<nearest['distance']:nearest=row
  if best[0]<=5 and rd not in near:near[rd]=row
  if k==0:pos[target]+=1
 out={'nearest':nearest,'near_rounds':near,'queen_positions':pos,'asymmetric_edges':sum(c not in g.adj[n] for c,a in enumerate(g.adj) for n in a)}
 (D/f'{gid}-proximity.json').write_text(json.dumps(out));print(gid,out,flush=True)
