import sys
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque
import json
sys.path.insert(0,'data/analysis/ladder/dossier/local')
import replay_format as rf
from count_local import Geo
OUT=Path('data/codex/astra/sweep/0436/loss1')
results={}
for gid in [1487474,1487486]:
 root=rf.load(f'data/online/smoke/one9-k1-old/M{gid}.replay').root();w,h=map(int,root.text(0).splitlines()[0].split()[1:3]);bodies={};teams={};raw=[];pearls=set();rnd=-1;actor=None;current=None
 for line in root.text(0).splitlines():
  z=line.split()
  if z and z[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(z[4+2*k])*w+int(z[3+2*k]) for k in range(int(z[2])));teams[i]=int(z[1])
  elif z and z[0]=='EDGE':raw.append(tuple(map(int,z[1:4])))
 g=Geo(w,h,raw);xy=lambda c:[c%w,c//w];out=[]
 def legal(body,dirs,other):
  b=list(body);p=set(pearls);free=(len(b)+3)//4
  for j,d in enumerate(dirs):
   k,dst=g.moves[b[0]][d]
   if k==1 or dst in b or dst in other or (j>=free and len(b)<=2):return None
   b.insert(0,dst)
   if dst in p:p.remove(dst)
   else:b.pop()
   if j>=free:b.pop()
  return b
 def ram_can(att, target, others):
  b=list(bodies[att]);free=(len(b)+3)//4;stack=[(b,0,set(pearls))]
  while stack:
   bb,n,pp=stack.pop()
   if n>=8 or (n>=free and len(bb)<=2):continue
   for k,dest in g.moves[bb[0]]:
    if k==1 or dest in bb:continue
    if dest==target:return n+1
    if dest in others:continue
    cc=[dest]+bb;qq=set(pp)
    if dest in qq:qq.remove(dest)
    else:cc.pop()
    if n>=free:cc.pop()
    stack.append((cc,n+1,qq))
  return None
 for e in root.pointer(3):
  k=e.u16(0);p=e.pointer(0);tile=lambda ptr:(lambda t:t[1]*w+t[0])(rf.point(ptr))
  if k==0:rnd=p.i32(0)
  elif k==1:
   actor=p.i32(0);current=None
   if gid==1487474 and rnd==130 and actor==0:
    other={c for i,b in bodies.items() if i!=0 for c in b};paths=[]
    for dirs in [[2],[2,3],[2,3,3]]:
     nb=legal(bodies[0],dirs,other)
     reach={str(i):ram_can(i,nb[0],{c for j,b in bodies.items() if j not in (0,i) for c in b}|set(nb[1:])) for i in (7,78)} if nb else {}
     paths.append(dict(dirs=dirs,body=list(map(xy,nb)) if nb else None,visible_attacker_reach=reach))
    out.append(dict(round=rnd,paths=paths))
   if (gid==1487474 and rnd==441 and actor==25) or (gid==1487486 and rnd in (4,5,9,10) and actor in (0,9,10)):
    current=dict(round=rnd,actor=actor,length=len(bodies[actor]),body=list(map(xy,bodies[actor])),heads={str(i):[len(b),xy(b[0])] for i,b in bodies.items()},path=[]);out.append(current)
  elif k==4 and current is not None:
   a=p.pointer(0);current['kind']=a.u16(0);current['dirs']=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else []
  elif k==3:
   c=tile(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c)
  elif k==9:
   i=p.i32(0);hd=tile(p.pointer(0));tail=tile(p.pointer(1));b=bodies[i]
   if b[0]!=hd:
    b.appendleft(hd)
    if current is not None:current['path'].append(xy(hd))
   while len(b)>1 and b[-1]!=tail:b.pop()
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(tile(t) for t in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:bodies.pop(p.i32(0))
 results[str(gid)]=out
(OUT/'moments.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print(json.dumps(results,ensure_ascii=False))
