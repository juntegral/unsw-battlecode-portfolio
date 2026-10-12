import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path[:0]=['data/analysis/ladder/dossier/local','data/analysis/ladder/losses/counts']
import replay_format as rf
from count_replays import Geometry
OUT=Path(__file__).parent
JOBS=[(1507926,'one13-p1-old'),(1512558,'one13-p2-old'),(1512559,'one13-p2-old')]
def scan(gid,folder):
 root=rf.load(f'data/online/smoke/{folder}/M{gid}.replay').root(); lines=root.text(0).splitlines(); w,h=map(int,lines[0].split()[1:]); bodies={};teams={};raw=[]
 for l in lines:
  q=l.split()
  if q[0]=='DRAGON':
   i=len(bodies);teams[i]=int(q[1]);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
  if q[0]=='EDGE':raw.append(tuple(map(int,q[1:])))
 geo=Geometry(w,h,raw); queens=[min(i for i in teams if teams[i]==s) for s in (0,1)]
 pearls=set();eats=Counter();qt=[];turns=[];deaths=[];snaps={};splits=[];near=[];rnd=-1;actor=None;t=None;idx=-1
 def state():
  return [dict(queen=len(bodies.get(queens[s],[])),longest=max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),total=sum(len(b) for i,b in bodies.items() if teams[i]==s),alive=sum(teams[i]==s for i in bodies),eats=sum(v for i,v in eats.items() if teams[i]==s)) for s in (0,1)]
 def snapshot():return {str(i):list(b) for i,b in bodies.items()}
 def close():
  if t is not None:
   t['end']=list(bodies.get(t['id'],[]));t['state_end']=state()
 def observe():
  if queens[0] not in bodies and queens[1] in bodies:
   q=bodies[queens[1]][0];ds=geo.distances(q)
   found=[(ds[b[0]],i,b[0]) for i,b in bodies.items() if teams[i]==0]
   if found:
    d,i,p=min(found)
    if d<=5:near.append(dict(r=rnd,event=idx,id=i,d=d,p=p,q=q))
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   close()
   if rnd>=0:snaps[rnd]=state()
   rnd=p.i32(0);actor=None;t=None
  elif k==1:
   close();actor=p.i32(0);t=dict(r=rnd,event=idx,id=actor,L=len(bodies[actor]),head=bodies[actor][0],eats=0,steps=[],action=None)
   turns.append(t)
   if actor in queens:
    t['bodies']=snapshot();t['pearls']=sorted(pearls);qt.append(t)
  elif k==3:
   x,y=rf.point(p.pointer(0));c=y*w+x
   if p.u32(0):pearls.add(c)
   else:pearls.discard(c);eats[actor]+=1;t['eats']+=1
  elif k==4:
   a=p.pointer(0);kind=a.u16(0) if a else None
   t['action']={'kind':kind,'dirs':list(a.pointer(0)) if a and kind==0 and a.pointer(0) is not None else [],'raw':[a.u32(z) for z in range(0,a.dwords*8,4)] if a else []}
  elif k==9:
   i=p.i32(0);x,y=rf.point(p.pointer(0));hd=y*w+x;x,y=rf.point(p.pointer(1));tail=y*w+x;b=bodies[i]
   if b[0]!=hd:t['steps'].append([b[0],hd]);b.appendleft(hd)
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
  elif k==10:
   parent,child=p.i32(0),p.i32(4);before=len(bodies[parent])
   for z,i in enumerate((parent,child)):
    bodies[i]=deque(rf.point(pt)[1]*w+rf.point(pt)[0] for pt in p.pointer(z));teams[i]=p.u16(8)
   sp=dict(r=rnd,id=parent,child=child,before=before,after=len(bodies[parent]),childL=len(bodies[child]),units=sum(teams[i]==teams[parent] for i in bodies));splits.append(sp);t['split']=sp
  elif k==11:
   i=p.i32(0);d=dict(r=rnd,event=idx,id=i,side=teams[i],actor=actor,reason=p.u16(4),body=list(bodies[i]),action=t['action'],actor_start=t['head'],actor_steps=t['steps'][:]);
   if i in queens:d['bodies']=snapshot();d['pearls']=sorted(pearls)
   deaths.append(d);del bodies[i]
  if k in (0,1,9,10,11):observe()
 close();snaps[rnd]=state();final=state()
 result=root.pointer(4)
 for s in (0,1):
  st=result.pointer(s);assert [st.i32(z) for z in (0,4,8)]==[final[s][z] for z in ('alive','longest','total')]
 out=dict(gid=gid,bot=root.text(1),w=w,h=h,queens=queens,final=final,last=rnd,queen_deaths=[d for d in deaths if d['id'] in queens],deaths=deaths,queen_turns=qt,splits=splits,snaps=snaps,turns=turns,near=near,final_bodies=snapshot(),teams=teams,raw_edges=raw)
 (OUT/f'{gid}.json').write_text(json.dumps(out,separators=(',',':')))
 print(gid,'bot',out['bot'],'final',final,'queen deaths',[(d['id'],d['r'],d['actor'],d['reason']) for d in out['queen_deaths']],'near',near[:1])
for job in JOBS:scan(*job)
