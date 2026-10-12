import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path[:0]=['tools','data/analysis/ladder/dossier/local']
import ladder_replay as lr
from count_local import Geo
OUT=Path(__file__).resolve().parent
F=Path('data/online/smoke/one13-k1-old')
for gid in (tuple(map(int,sys.argv[1:])) or (1509102,1509107,1509108)):
 root=lr.replay.load(F/f'M{gid}.replay').root()
 w,h=map(int,root.text(0).splitlines()[0].split()[1:3]);bodies={};teams={};raw=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if q and q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 ours=min(i for i in bodies if teams[i]==0);theirs=min(i for i in bodies if teams[i]==1)
 geo=Geo(w,h,raw);pearls=set();rnd=-1;actor=None;cur=None;turns=[];qdead=False;close=[];minimum=None;cache={};deathstates=[]
 def tile(p):
  x,y=lr.replay.point(p);return y*w+x
 def state():return {i:list(b) for i,b in bodies.items()}
 def finish():
  global cur
  if cur is not None:
   cur['end']={i:[len(b),b[0]] for i,b in bodies.items()};turns.append(cur);cur=None
 def near():
  global minimum
  if not qdead or theirs not in bodies:return
  target=bodies[theirs][0]
  for i,b in bodies.items():
   if teams[i]!=0:continue
   src=b[0]
   if src not in cache:
    ds={src:0};todo=deque([src])
    while todo:
     c=todo.popleft()
     for nxt in geo.adj[c]:
      if nxt not in ds:ds[nxt]=ds[c]+1;todo.append(nxt)
    cache[src]=ds
   d=cache[src].get(target,9999)
   row=[rnd,i,d,src,target]
   if minimum is None or d<minimum[2]:minimum=row
   if d<=5:close.append(row)
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:finish();rnd=p.i32(0);actor=None
  elif k==1:
   finish();actor=p.i32(0);near();cur={'r':rnd,'id':actor,'event':idx,'bodies':state(),'pearls':sorted(pearls),'steps':[],'eats':0,'logs':[]}
  elif k==3:
   c=tile(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:
    pearls.remove(c)
    if cur:cur['eats']+=1
  elif k==4:
   a=p.pointer(0)
   if cur:cur['action']={'kind':a.u16(0) if a else None,'dirs':list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) else []}
  elif k==9:
   i=p.i32(0);hd=tile(p.pointer(0));tl=tile(p.pointer(1));b=bodies[i]
   if b[0]!=hd:
    b.appendleft(hd)
    if cur:cur['steps'].append(hd)
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
   near()
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(tile(c) for c in p.pointer(z));teams[i]=p.u16(8)
   if cur:cur['split']=[p.i32(0),p.i32(4)]
   near()
  elif k==11:
   i=p.i32(0)
   if i in (0,1):deathstates.append({'r':rnd,'id':i,'actor':actor,'bodies':state(),'pearls':sorted(pearls)})
   bodies.pop(i)
   if i==ours:qdead=True
   near()
  elif k==8 and cur:
   cur['logs'].append(p.text(0))
 finish()
 # Store all turns for exact audits, and succinct preview.
 output={'gid':gid,'w':w,'h':h,'teams':teams,'edges':raw,'turns':turns,'queen_death_states':deathstates,'closest_after_qdeath':minimum,'near5_first':close[:1],'near5_distinct':sorted(set((x[0],x[1]) for x in close))}
 (OUT/f'{gid}-details.json').write_text(json.dumps(output,separators=(',',':')))
 qt=[t for t in turns if t['id']==ours]
 print(gid,'queen last',[(t['r'],len(t['bodies'][ours]),t['bodies'][ours],t.get('action'),t['steps'],t['eats'],t.get('split')) for t in qt[-5:]],'near',minimum,close[:1],flush=True)
 print('deathstates',deathstates,flush=True)
