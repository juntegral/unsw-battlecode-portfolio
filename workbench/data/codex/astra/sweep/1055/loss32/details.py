import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path.insert(0,str(Path('data/analysis/ladder/dossier/local').resolve()))
from scoreboard import load_replay
from count_local import Geo
from replay_format import point
OUT=Path(__file__).resolve().parent
for gid in (1512561,1512562,1512563):
 root=load_replay(Path(f'data/online/smoke/one13-p2-old/M{gid}.replay')).root()
 base=json.loads((OUT/f'{gid}-scan.json').read_text()); qid=base['queens']['us']; eq=base['queens']['them']
 W,H=map(int,root.text(0).splitlines()[0].split()[1:3]); bodies={}; teams={}; raw=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies); bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2]))); teams[i]=int(q[1])
  if q[0]=='EDGE': raw.append(tuple(map(int,q[1:4])))
 geo=Geo(W,H,raw); pearls=set(); turns=[]; cur=None; rnd=-1; contacts=[]; mincontact=None; seen_contacts=set(); snapshots={}; dists={}
 def tile(p):return p[1]*W+p[0]
 def distmap(pos):
  src=tile(pos)
  if src not in dists:
   d={src:0}; queue=deque([src])
   while queue:
    a=queue.popleft()
    for b in geo.adj[a]:
     if b not in d:d[b]=d[a]+1;queue.append(b)
   dists[src]=d
  return dists[src]
 def contact(idx):
  global mincontact
  if qid in bodies or eq not in bodies:return
  ds=distmap(bodies[eq][0])
  for i,b in bodies.items():
   if teams[i]!=0:continue
   dist=ds.get(tile(b[0]),99999)
   item=dict(round=rnd,event=idx,id=i,length=len(b),head=b[0],queen=bodies[eq][0],distance=dist)
   if mincontact is None or dist<mincontact['distance']:mincontact=item
   if dist<=5 and (rnd,i) not in seen_contacts:
    seen_contacts.add((rnd,i));contacts.append(item)
 def finish():
  if cur:
   cur['end']=list(bodies.get(cur['id'],[]));cur['endlength']=len(cur['end'])
 def snapshot():
  snapshots[rnd]={str(i):dict(length=len(b),head=b[0],side=teams[i]) for i,b in bodies.items()}
 for idx,ev in enumerate(root.pointer(3)):
  kind=ev.u16(0);p=ev.pointer(0)
  if kind==0:
   finish();cur=None
   if rnd>=0:snapshot()
   rnd=p.i32(0)
  elif kind==1:
   finish();i=p.i32(0)
   cur=dict(round=rnd,event=idx,id=i,side=teams[i],length=len(bodies[i]),body=list(bodies[i]),moves=[],eats=[],splits=[],logs=[])
   if i==qid or (gid==1512561 and 166<=rnd<=169) or (gid==1512562 and 58<=rnd<=60) or (gid==1512563 and 100<=rnd<=103):
    cur['board']={str(z):list(b) for z,b in bodies.items()};cur['pearls']=list(pearls)
   turns.append(cur)
  elif kind==3:
   xy=point(p.pointer(0))
   if p.u32(0):pearls.add(xy)
   else:
    pearls.discard(xy)
    if cur:cur['eats'].append(xy)
  elif kind==4:
   a=p.pointer(0)
   if cur:
    cur['action']=dict(kind=a.u16(0),value=a.i32(4),dirs=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else [])
  elif kind==6:
   if cur:cur['logs'].append(p.text(0))
  elif kind==9:
   i=p.i32(0);hd=point(p.pointer(0));tail=point(p.pointer(1));b=bodies[i]
   if hd!=b[0]:
    b.appendleft(hd)
    if cur:cur['moves'].append(hd)
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
   contact(idx)
  elif kind==10:
   if cur:cur['splits'].append(dict(parent=p.i32(0),child=p.i32(4)))
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(point(pt) for pt in p.pointer(z));teams[i]=p.u16(8)
   contact(idx)
  elif kind==11:
   bodies.pop(p.i32(0));contact(idx)
 finish();snapshot()
 out=dict(gid=gid,W=W,H=H,teams=teams,turns=turns,contacts=contacts,mincontact=mincontact,snapshots=snapshots)
 (OUT/f'{gid}-details.json').write_text(json.dumps(out,ensure_ascii=False))
 print(gid,'size',W,H,'mincontact',mincontact,'contacts',len(contacts),'first',contacts[:3])
 qt=[t for t in turns if t['id']==qid]
 for t in qt[-5:]:print('Q', {k:v for k,v in t.items() if k not in ('board','pearls')})
 print('long deaths',[(d['round'],d['id'],d['length'],d['cause'],d['actor']) for d in base['deaths'] if d['side']=='us' and d['length']>=8])
