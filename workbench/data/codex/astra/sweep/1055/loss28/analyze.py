import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path.insert(0,'data/analysis/ladder/dossier/local')
import scoreboard as sb
sys.path.insert(0,'data/analysis/ladder/dossier')
from count_dossier import Geo
OUT=Path(__file__).resolve().parent

def scan(gid):
 p=Path(f'data/online/smoke/one13-p1-old/M{gid}.replay')
 root=sb.load_replay(p).root(); txt=root.text(0); w,h=map(int,txt.splitlines()[0].split()[1:3])
 bodies={};teams={};raw=[]
 for line in txt.splitlines():
  q=line.split()
  if q and q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 geo=Geo(w,h,raw);queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
 pearls=set();turns=[];qt=[];near=[];death=[];splits=[];snaps={};r=-1;t=None;actor=None;after=False;mind=99999;minrec=None
 tile=lambda p: sb.replay_format.point(p)[1]*w+sb.replay_format.point(p)[0]
 def snap():
  return [dict(n=sum(teams[i]==s for i in bodies),total=sum(len(b) for i,b in bodies.items() if teams[i]==s),long=max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),queen=len(bodies.get(queens[s],[]))) for s in (0,1)]
 def close():
  if t is not None:t['end']=list(bodies.get(actor,[]))
 def check(idx):
  nonlocal mind,minrec
  if not after or queens[1] not in bodies:return
  dst=bodies[queens[1]][0];ds=geo.distances(dst)
  best=min(((ds[b[0]],i) for i,b in bodies.items() if teams[i]==0),default=(99999,-1))
  if best[0]<mind:
   mind=best[0];minrec=dict(round=r,event=idx,d=best[0],id=best[1],head=bodies[best[1]][0] if best[1]>=0 else None,enemy_head=dst)
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);v=ev.pointer(0)
  if k==0:
   close()
   if r>=0:snaps[r]=snap()
   r=v.i32(0);t=None;actor=None
  elif k==1:
   close();actor=v.i32(0)
   t=dict(r=r,id=actor,event=idx,side=teams[actor],body=list(bodies[actor]),steps=[],eats=[],action=None)
   turns.append(t)
   if actor in queens:
    t['bodies']={i:list(b) for i,b in bodies.items()};t['pearls']=sorted(pearls);qt.append(t)
   if after and queens[1] in bodies and teams[actor]==0:
    dst=bodies[queens[1]][0];d=geo.distances(bodies[actor][0])[dst]
    if d<=5:
     t['eq']=dict(head=dst,body=list(bodies[queens[1]]),d=d,visible=geo.visible(bodies[actor][0],dst));near.append(t)
  elif k==3:
   cell=tile(v.pointer(0))
   if v.u32(0):pearls.add(cell)
   else:pearls.remove(cell);t['eats'].append(cell)
  elif k==4:
   a=v.pointer(0);kind=a.u16(0)
   t['action']=dict(kind=kind,dirs=list(a.pointer(0)) if kind==0 and a.pointer(0) is not None else [],data=a.i32(4),timeout=v.bit(32))
  elif k==9:
   i=v.i32(0);hd,tail=tile(v.pointer(0)),tile(v.pointer(1));b=bodies[i]
   if b[0]!=hd:
    b.appendleft(hd)
    if i==actor:t['steps'].append(hd)
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
  elif k==10:
   parent,child=v.i32(0),v.i32(4);splits.append(dict(r=r,id=parent,child=child,pre=list(bodies[parent])))
   for z,i in enumerate((parent,child)):
    bodies[i]=deque(tile(c) for c in v.pointer(z));teams[i]=v.u16(8)
  elif k==11:
   i=v.i32(0);death.append(dict(r=r,id=i,reason=v.u16(4),actor=actor,body=list(bodies[i]),event=idx,turn=t))
   if i==queens[0]:after=True
   bodies.pop(i)
  if k in (9,10,11):check(idx)
 close();snaps[r]=snap();final=snaps[r]
 for s in (0,1):
  st=root.pointer(4).pointer(s);assert list(final[s].values())==[st.i32(o) for o in (0,8,4,12)]
 rec=dict(gid=gid,w=w,h=h,bots=[root.text(1),root.text(2)],queens=queens,teams=teams,turns=turns,queen_turns=qt,deaths=death,splits=splits,snapshots=snaps,final=final,near=near,min_after=minrec,edges=raw)
 (OUT/f'detail-{gid}.json').write_text(json.dumps(rec,separators=(',',':')))
 print(gid,'final',final,'mind',minrec,'near turns',len(near),'q deaths',[(d['r'],d['id'],d['reason'],d['actor']) for d in death if d['id'] in queens],flush=True)
 for q in queens:
  ts=[a for a in qt if a['id']==q]
  print('queen',q,'last',[(a['r'],a['body'],a['action'],a['steps'],a['eats']) for a in ts[-3:]],flush=True)
for gid in (1507915,1507916,1507917):scan(gid)
