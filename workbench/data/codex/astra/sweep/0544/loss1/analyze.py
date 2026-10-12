import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path.insert(0,str(Path('data/analysis/ladder/dossier/local').resolve()))
from scoreboard import load_replay
from count_local import Geo
from replay_format import point
OUT=Path(__file__).parent

def scan(gid):
 root=load_replay(Path(f'data/online/smoke/one8-c2-old/M{gid}.replay')).root()
 b={};team={};edges=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if q[0]=='MAP': w,h=map(int,q[1:3])
  if q[0]=='EDGE': edges.append(tuple(map(int,q[1:4])))
  if q[0]=='DRAGON':
   i=len(b);team[i]=int(q[1]);b[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
 geo=Geo(w,h,edges); tile=lambda p:point(p)[1]*w+point(p)[0]
 qs=[min(i for i in b if team[i]==s) for s in (0,1)]
 pearls={};rounds={};qt=[];turns=[];deaths=[];near=[];rnd=-1;actor=None;cur=None;distcache={}
 rev=[[] for _ in range(w*h)]
 for c,adj in enumerate(geo.adj):
  for d in adj:rev[d].append(c)
 def dist(dest):
  if dest not in distcache:
   ds={dest:0};todo=deque([dest])
   while todo:
    c=todo.popleft()
    for d in rev[c]:
     if d not in ds:ds[d]=ds[c]+1;todo.append(d)
   distcache[dest]=ds
  return distcache[dest]
 def state():return [dict(n=sum(team[i]==s for i in b),q=len(b.get(qs[s],())),longest=max([len(bb) for i,bb in b.items() if team[i]==s],default=0),total=sum(len(bb) for i,bb in b.items() if team[i]==s)) for s in (0,1)]
 def close():
  if cur is not None:cur['end']=list(b.get(actor,()));turns.append(cur)
 for idx,e in enumerate(root.pointer(3)):
  k=e.u16(0);p=e.pointer(0)
  if k==0:
   close();cur=None
   if rnd>=0:rounds[rnd]=state()
   rnd=p.i32(0);actor=None
  elif k==1:
   close();actor=p.i32(0)
   cur=dict(r=rnd,id=actor,L=len(b[actor]),start=list(b[actor]),steps=[],eat=[],split=[],event=idx,units=sum(team[j]==team[actor] for j in b))
   if team[actor]==0:
    window=geo.window(b[actor][0])
    cur['enemy10']=[j for j,bb in b.items() if team[j]==1 and sum(c in window for c in bb)>=10]
   if actor in qs:
    cur['bodies']={i:list(bb) for i,bb in b.items()};cur['pearls']=list(pearls);qt.append(cur)
   if qs[0] not in b and qs[1] in b and team[actor]==0:
    d=dist(b[qs[1]][0]).get(b[actor][0],999)
    if d<=5:near.append(dict(r=rnd,id=actor,L=len(b[actor]),d=d,q=list(b[qs[1]]),head=b[actor][0]))
  elif k==3:
   c=tile(p.pointer(0))
   if p.u32(0):pearls[c]='spawn' if actor is None else 'drop'
   else:cur['eat'].append([c,pearls.pop(c)])
  elif k==4:
   a=p.pointer(0)
   cur['action']={'type':a.u16(0),'dirs':list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else []}
  elif k==9:
   i=p.i32(0);hd=tile(p.pointer(0));tail=tile(p.pointer(1))
   if b[i][0]!=hd:b[i].appendleft(hd);cur['steps'].append(hd)
   while len(b[i])>1 and b[i][-1]!=tail:b[i].pop()
   assert b[i][-1]==tail
  elif k==10:
   parent,child=p.i32(0),p.i32(4);cur['split'].append(child)
   for z,i in enumerate((parent,child)):b[i]=deque(tile(pt) for pt in p.pointer(z));team[i]=p.u16(8)
  elif k==11:
   i=p.i32(0);deaths.append(dict(r=rnd,id=i,actor=actor,reason=p.u16(4),body=list(b[i]),event=idx,actor_turn={kk:vv for kk,vv in cur.items() if kk not in ('bodies','pearls')},heads={j:[len(bb),bb[0]] for j,bb in b.items()}));b.pop(i)
 close();rounds[rnd]=state()
 result=root.pointer(4)
 for s in (0,1):
  st=result.pointer(s);assert list(rounds[rnd][s].values())==[st.i32(0),st.i32(12),st.i32(4),st.i32(8)]
 obj=dict(gid=gid,w=w,h=h,queens=qs,bots=[root.text(1),root.text(2)],final=rounds[rnd],rounds=rounds,deaths=deaths,queen_turns=qt,near=near,teams=team,edges=edges,turns=turns)
 (OUT/f'{gid}.json').write_text(json.dumps(obj,separators=(',',':')))
 qd=[d for d in deaths if d['id'] in qs]
 print(json.dumps(dict(gid=gid,size=[w,h],bots=obj['bots'],final=obj['final'],qdeaths=qd,near_count=len(near),near_first=near[:3],near_last=near[-3:]),ensure_ascii=False))
for gid in (1493878,1493879,1493880):scan(gid)
