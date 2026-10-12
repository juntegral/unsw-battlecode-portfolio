import sys
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque, Counter
import json
sys.path.insert(0,'data/analysis/ladder/dossier/local')
from scoreboard import load_replay
from replay_format import point
from count_local import Geo
OUT=Path(__file__).parent
JOBS=[(1496858,'data/online/smoke/one11-c1-old',0),(1496859,'data/online/smoke/one11-c1-old',0),(1497630,'data/online/live-one1/b1497630',1)]

def scan(gid,folder,own):
 r=load_replay(Path(folder)/f'M{gid}.replay').root()
 B={}; teams={}; raw=[]
 for line in r.text(0).splitlines():
  p=line.split()
  if not p:continue
  if p[0]=='MAP':w,h=map(int,p[1:3])
  if p[0]=='EDGE':raw.append(tuple(map(int,p[1:4])))
  if p[0]=='DRAGON':
   i=len(B);teams[i]=int(p[1]);B[i]=deque(int(p[4+2*k])*w+int(p[3+2*k]) for k in range(int(p[2])))
 g=Geo(w,h,raw); qs=[min(i for i in B if teams[i]==s) for s in (own,1-own)]
 rev=[[] for _ in range(w*h)]
 for c,adj in enumerate(g.adj):
  for d in adj:rev[d].append(c)
 cache={}
 def distances(dst):
  if dst not in cache:
   ds={dst:0};queue=deque([dst])
   while queue:
    c=queue.popleft()
    for z in rev[c]:
     if z not in ds:ds[z]=ds[c]+1;queue.append(z)
   cache[dst]=ds
  return cache[dst]
 side=lambda i:int(teams[i]!=own)
 tile=lambda p:point(p)[1]*w+point(p)[0]
 pearls={}; stats=[Counter(),Counter()];snaps={};turns=[];qturns=[];deaths=[];births=[];qt=None;cur=None;rnd=-1;actor=None;close=[]
 def state():
  return [dict(alive=sum(side(i)==s for i in B),total=sum(len(b) for i,b in B.items() if side(i)==s),longest=max((len(b) for i,b in B.items() if side(i)==s),default=0),queen=len(B.get(qs[s],[])),**stats[s]) for s in (0,1)]
 def finish():
  if cur is not None:
   cur['end']=list(B.get(actor,[]));cur['Lend']=len(cur['end'])
 def proximity(ev):
  if qs[0] in B or qs[1] not in B:return
  ds=distances(B[qs[1]][0]);m=min(((ds.get(b[0],99999),i,b[0]) for i,b in B.items() if side(i)==0),default=(99999,-1,-1))
  if not close or m[0]<close[-1]['distance'] or (m[0]<=5 and close[-1]['round']!=rnd):
   close.append(dict(round=rnd,event=ev,distance=m[0],dragon=m[1],head=m[2],queen_head=B[qs[1]][0]))
 for ei,e in enumerate(r.pointer(3)):
  k=e.u16(0);p=e.pointer(0)
  if k==0:
   finish()
   if rnd>=0:snaps[rnd]=state()
   rnd=p.i32(0);actor=None;cur=None
  elif k==1:
   finish();actor=p.i32(0);stats[side(actor)]['turns']+=1
   cur=dict(round=rnd,event=ei,id=actor,side=side(actor),start=list(B[actor]),steps=[],eats=[],action=None)
   turns.append(cur)
   if actor in qs:
    cur['bodies']={i:list(b) for i,b in B.items()};cur['pearls']=list(pearls);qturns.append(cur)
  elif k==4:
   a=p.pointer(0);cur['action']=a.u16(0) if a else None
   if a and a.u16(0)==0:cur['directions']=list(a.pointer(0)) if a.pointer(0) else []
   if a and a.u16(0)==1:cur['split_size']=a.i32(4)
  elif k==3:
   c=tile(p.pointer(0))
   if p.u32(0):pearls[c]='natural' if actor is None else 'drop'
   else:
    origin=pearls.pop(c);stats[side(actor)][origin]+=1;cur['eats'].append([c,origin])
  elif k==9:
   i=p.i32(0);hd=tile(p.pointer(0));tail=tile(p.pointer(1));b=B[i]
   if b[0]!=hd:b.appendleft(hd);cur['steps'].append(hd)
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
   proximity(ei)
  elif k==10:
   parent,child=p.i32(0),p.i32(4)
   for j,i in enumerate((parent,child)):B[i]=deque(tile(pt) for pt in p.pointer(j));teams[i]=p.u16(8)
   stats[side(parent)]['splits']+=1;births.append(dict(round=rnd,parent=parent,child=child,body=list(B[child])))
   proximity(ei)
  elif k==11:
   i=p.i32(0);deaths.append(dict(round=rnd,event=ei,id=i,side=side(i),reason=p.u16(4),actor=actor,body=list(B[i]),attacker_start=cur['start'],directions=cur.get('directions'),steps=list(cur['steps'])))
   del B[i];proximity(ei)
 finish();snaps[rnd]=state()
 final=[]
 for s in (own,1-own):
  p=r.pointer(4).pointer(s);final.append(dict(zip(('alive','longest','total','queen'),(p.i32(o) for o in (0,4,8,12)))))
 assert all(all(snaps[rnd][s][k]==final[s][k] for k in final[s]) for s in (0,1))
 out=dict(game=gid,own=own,bot=r.text(own+1),w=w,h=h,queens=qs,final=final,round=rnd,snaps=snaps,qturns=qturns,deaths=deaths,births=births,close=close,teams=teams,edges=raw,turns=turns)
 (OUT/f'{gid}.json').write_text(json.dumps(out,separators=(',',':')))
 qdeaths=[d for d in deaths if d['id'] in qs]
 print(gid,'bot',out['bot'],'final',final,'Qdead',qdeaths,'close',close[:3],flush=True)
 print('checkpoints',[(k,snaps[k]) for k in [0,25,50,100,150,200,300,400,499] if k in snaps],flush=True)
for args in JOBS:scan(*args)
