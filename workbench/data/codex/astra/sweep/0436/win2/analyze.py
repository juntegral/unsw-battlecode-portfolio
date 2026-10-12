import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
from collections import deque, Counter, defaultdict
sys.path[:0]=['data/analysis/ladder/dossier/work','data/analysis/ladder/dossier/online','data/analysis/ladder/dossier/local','tools']
import o1_scan, o1_qdef, label_report as lr
from ladder_replay import edge_id, canonical_edges
OUT=Path('data/codex/astra/sweep/0436/win2')
F=Path('data/online/live-one1/b1488287')
def scan(gid):
 path=F/f'M{gid}.replay'; meta=json.loads((F/f'game-{gid}.json').read_text())
 root=lr.agg.sb.load_replay(path).root()
 assert root.text(1)=='21165'
 ledger=o1_scan.scan('win2',path,meta)
 W,H=map(int,root.text(0).splitlines()[0].split()[1:3]); bodies={};teams={};raw=[]
 for q in map(str.split,root.text(0).splitlines()):
  if q and q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
 edges=canonical_edges(W,H,raw);ports=defaultdict(list)
 for e,(k,p) in edges.items():
  if k==2:ports[p].append(e)
 def dest(c,d):
  e=edge_id(W,H,*c,d);k,p=edges.get(e,(0,-1))
  if k==1:return None
  if k==2:
   other=next(e2 for e2 in ports[p] if e2!=e);row,x=divmod(other,W+1);return ((x-(d==3))%W,(row//2-(d==0))%H)
  dx,dy=o1_scan.STEP[d];return ((c[0]+dx)%W,(c[1]+dy)%H)
 def gap(a,b):
  x,y=abs(a[0]-b[0]),abs(a[1]-b[1]);return min(x,W-x)+min(y,H-y)
 def view(a,b):
  x,y=abs(a[0]-b[0]),abs(a[1]-b[1]);return min(x,W-x)<=3 and min(y,H-y)<=3
 def snap():
  out=[]
  for s in (0,1):
   ls=[len(b) for i,b in bodies.items() if teams[i]==s]
   out.append([len(bodies.get(queens[s],())),max(ls,default=0),sum(ls),len(ls)])
  return out
 def bodycopy():return {i:list(b) for i,b in bodies.items()}
 rounds={};turns=[];deaths=[];splits=[];pearls={};r=-1;actor=None;t=None;eindex=-1
 def close():
  nonlocal t
  if t is not None:
   t['end']=list(bodies[t['id']]) if t['id'] in bodies else []
   t['after']=snap();turns.append(t);t=None
 for eindex,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   close()
   if r>=0:rounds[r]=snap()
   r=p.i32(0);actor=None
  elif k==1:
   close();actor=p.i32(0);b=bodies[actor];h=b[0]
   occ={c:i for i,bb in bodies.items() for c in bb}
   adj=[]
   for d in range(4):
    n=dest(h,d)
    if n is not None and n not in occ:adj.append([d,list(n),n in pearls])
   enemies=[(i,list(bb[0]),len(bb)) for i,bb in bodies.items() if teams[i]!=teams[actor] and view(h,bb[0])]
   mates=[(i,list(bb[0]),len(bb)) for i,bb in bodies.items() if i!=actor and teams[i]==teams[actor] and view(h,bb[0])]
   t=dict(r=r,id=actor,L=len(b),h=list(h),s=teams[actor],before=snap(),body=list(b),adj=adj,enemies=enemies,mates=mates,eats=[],steps=[],actions=[],event=eindex)
   if actor in queens:t['pearls']=[list(c) for c in pearls]
   if actor in queens or any(n in queens for n,_,_ in enemies) or (gid==1488288 and 97<=r<=102 and actor==62):t['bodies']=bodycopy()
  elif k==4:
   a=p.pointer(0);z=a.u16(0)
   t['actions'].append([z,list(a.pointer(0)) if z==0 and a.pointer(0) is not None else a.i32(4)])
  elif k==3:
   c=lr.agg.sb.replay_format.point(p.pointer(0))
   if p.u32(0):pearls[c]=[r,actor is not None]
   else:
    origin=pearls.pop(c)
    if t is not None:t['eats'].append([list(c),origin])
  elif k==9:
   i=p.i32(0);hd=lr.agg.sb.replay_format.point(p.pointer(0));tl=lr.agg.sb.replay_format.point(p.pointer(1));b=bodies[i]
   if b[0]!=hd:
    if t is not None and i==actor:t['steps'].append(list(hd))
    b.appendleft(hd)
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
  elif k==10:
   parent,child=p.i32(0),p.i32(4);old=list(bodies[parent]);tail=old[-1]
   sp=dict(r=r,parent=parent,child=child,L=len(old),s=teams[parent],tail=list(tail),portal_tail=any(edges.get(edge_id(W,H,*tail,d),(0,-1))[0]==2 for d in range(4)))
   for z,i in enumerate((parent,child)):
    bodies[i]=deque(lr.agg.sb.replay_format.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
   sp['sizes']=[len(bodies[parent]),len(bodies[child])];splits.append(sp)
  elif k==11:
   i=p.i32(0);deaths.append(dict(r=r,id=i,L=len(bodies[i]),s=teams[i],cause=p.u16(4),actor=actor,at=list(bodies[i][0]),actor_L0=t['L'] if t else None,actor_h=t['h'] if t else None,event=eindex,prior=snap()))
   bodies.pop(i)
 close();rounds[r]=snap()
 result=root.pointer(4)
 for s in (0,1):
  expected=[result.pointer(s).i32(o) for o in (12,4,8,0)]
  assert snap()[s]==expected
 signs={r:(x[0][:3]>x[1][:3])-(x[0][:3]<x[1][:3]) for r,x in rounds.items()}
 last_not_win=max((r for r,z in signs.items() if z<=0),default=-1)
 lead=last_not_win+1 if last_not_win<r else None
 data=dict(game=gid,map=meta['mapName'],bot=root.text(1),queen_ids=queens,last=r,final=snap(),ahead_for_good=lead,rounds=rounds,turns=turns,deaths=deaths,splits=splits,ledger=ledger)
 (OUT/f'{gid}.json').write_text(json.dumps(data,separators=(',',':')))
 print(gid,meta['mapName'],'queens',queens,'final Q/max/total/count',snap(),'last',r,'ahead',lead)
 print('queen deaths',[d for d in deaths if d['id'] in queens])
 print('splits',Counter((z['s'],z['portal_tail']) for z in splits),'own queen splits',[z for z in splits if z['parent']==queens[0]])
 print('death counts',Counter((d['s'],d['cause']) for d in deaths))
 print('peak/count',max(x[0][3] for x in rounds.values()),'round checkpoints',{r:rounds[r] for r in (0,1,5,10,20,50,100,200,350,400,450,499) if r in rounds})
 print('own queen rams',[d for d in deaths if d['s']==1 and d['cause']==3 and d['id']==queens[1]])
 return data
if __name__=='__main__':
 for gid in (1488288,1488289,1488291):scan(gid)
