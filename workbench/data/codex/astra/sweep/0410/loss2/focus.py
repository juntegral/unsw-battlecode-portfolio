import sys,json
from pathlib import Path
from collections import deque
sys.dont_write_bytecode=True
sys.path[:0]=['data/analysis/ladder/dossier/local','data/analysis/ladder/losses/counts','tools']
from scoreboard import load_replay
from count_replays import Geometry
from replay_format import point
OUT=Path(__file__).resolve().parent
allout={}
for gid,folder in [(1485169,'data/online/smoke/one8-k1-old'),(1485180,'data/online/smoke/one8-k1-old')]:
 root=load_replay(Path(folder)/f'M{gid}.replay').root();w,h=map(int,root.text(0).splitlines()[0].split()[1:3]);bodies={};teams={};raw=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if q and q[0]=='DRAGON':
   i=len(bodies);teams[i]=int(q[1]);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
  elif q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 g=Geometry(w,h,raw);r=-1;out=[];tile=lambda p:point(p)[1]*w+point(p)[0]
 for ev in root.pointer(3):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:r=p.i32(0)
  elif k==1:
   i=p.i32(0)
   if gid==1485180 and r>=301 and i!=0 and teams[i]==teams[0] and len(bodies[i])==2 and 0 in bodies:
    c=bodies[i][0];qh=bodies[0][0];dx=abs(c%w-qh%w);dy=abs(c//w-qh//w);dist=min(dx,w-dx)+min(dy,h-dy)
    if dist<=5:out.append(dict(r=r,id=i,L=2,qL=len(bodies[0]),manhattan=dist,head=[c%w,c//w],qhead=[qh%w,qh//w]))
   if gid==1485169 and r==412 and i==371:
    occ={c for bb in bodies.values() for c in bb};start=bodies[i][0];end=bodies[0][0];parents={start:None};todo=deque([start])
    while todo:
     c=todo.popleft()
     if c==end:break
     for n in g.adj[c]:
      if n not in parents and (n not in occ or n==end):parents[n]=c;todo.append(n)
    path=[];cur=end
    while cur is not None:path.append([cur%w,cur//w]);cur=parents[cur]
    out.append(dict(r=r,id=i,L=len(bodies[i]),enemy_q_L=len(bodies[0]),free_ram_path=path[::-1]))
  elif k==9:
   i=p.i32(0);hd,tl=tile(p.pointer(0)),tile(p.pointer(1));b=bodies[i]
   if b[0]!=hd:b.appendleft(hd)
   while len(b)>1 and b[-1]!=tl:b.pop()
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(tile(pt) for pt in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:bodies.pop(p.i32(0))
 allout[gid]=out;print(gid,'count',len(out),'sample',out[:8])
(OUT/'focus.json').write_text(json.dumps(allout))
