import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,defaultdict
sys.path.insert(0,str(Path('tools').resolve()))
import ladder_replay as lr
O=Path(__file__).parent
out={}
for gid,bid,lo,hi in ((1508916,1508916,390,396),(1510463,1510461,264,269),(1512747,1512747,117,120)):
 s=json.loads((O/f'{gid}.json').read_text());W,H=map(int,s['text'].splitlines()[0].split()[1:3]);edges=lr.canonical_edges(W,H,[tuple(map(int,l.split()[1:4])) for l in s['text'].splitlines() if l.startswith('EDGE ')]);portals=defaultdict(list)
 for e,(k,pid) in edges.items():
  if k==2:portals[pid].append(e)
 rev=defaultdict(list)
 for y in range(H):
  for x in range(W):
   for d,(dx,dy) in enumerate(lr.base.STEP):
    e=lr.edge_id(W,H,x,y,d);k,pid=edges.get(e,(0,-1))
    if k==1:continue
    if k==2:
     partner=next(z for z in portals[pid] if z!=e);row,px=divmod(partner,W+1);v=((px-(d==3))%W,(row//2-(d==0))%H)
    else:v=((x+dx)%W,(y+dy)%H)
    rev[v].append((x,y))
 cache={}
 def dist(target):
  if target not in cache:
   ds={target:0};queue=deque([target])
   while queue:
    u=queue.popleft()
    for v in rev[u]:
     if v not in ds:ds[v]=ds[u]+1;queue.append(v)
   cache[target]=ds
  return cache[target]
 bodies={};teams={}
 for l in s['text'].splitlines():
  a=l.split()
  if a[0]=='DRAGON':i=len(bodies);bodies[i]=(int(a[3]),int(a[4]));teams[i]='AB'[int(a[1])]
 q=s['queens']['us'];eq=s['queens']['them'];root=lr.replay.load(f'data/online/live-one1/b{bid}/M{gid}.replay').root();r=-1;logs=[];closest=None;checks=0;closecount=0;positions=set()
 def check(idx):
  global closest,checks,closecount
  if q in bodies or eq not in bodies:return
  positions.add(bodies[eq]);ds=dist(bodies[eq]);checks+=1
  for i,h in bodies.items():
   if teams[i]!=s['ours']:continue
   d=ds.get(h,999999)
   if closest is None or d<closest['distance']:closest=dict(distance=d,r=r,event=idx,id=i,head=h,queen=bodies[eq])
   if d<=5:closecount+=1
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:r=p.i32(0)
  elif k==6 and lo<=r<=hi and p.i32(0)==q:logs.append((r,p.text(0)))
  elif k==9:bodies[p.i32(0)]=lr.replay.point(p.pointer(0));check(idx)
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=lr.replay.point(next(iter(p.pointer(z))));teams[i]='AB'[p.u16(8)]
   check(idx)
  elif k==11:bodies.pop(p.i32(0));check(idx)
 out[gid]=dict(logs=logs,closest=closest,checks=checks,closecount=closecount,positions=sorted(positions))
 print(gid,json.dumps(out[gid]),flush=True)
(O/'event-checks.json').write_text(json.dumps(out))
