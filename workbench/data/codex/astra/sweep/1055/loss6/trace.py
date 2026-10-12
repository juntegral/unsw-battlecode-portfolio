import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,defaultdict,Counter
sys.path.insert(0,'data/analysis/ladder/dossier/local')
import scoreboard as sb
sys.path.insert(0,'tools')
from ladder_replay import edge_id,canonical_edges
OUT=Path('data/codex/astra/sweep/1055/loss6')
for gid in (1503502,1503503,1503504):
 root=sb.load_replay(Path(f'data/online/smoke/one12-p1-old/M{gid}.replay')).root()
 lines=root.text(0).splitlines(); W,H=map(int,lines[0].split()[1:3]); bodies={}; teams={}; raw=[]
 for line in lines:
  z=line.split()
  if z[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque((int(z[3+2*k]),int(z[4+2*k])) for k in range(int(z[2])));teams[i]=int(z[1])
  if z[0]=='EDGE':raw.append(tuple(map(int,z[1:4])))
 edges=canonical_edges(W,H,raw); portals=defaultdict(list)
 for e,(k,p) in edges.items():
  if k==2:portals[p].append(e)
 def dest(c,d):
  e=edge_id(W,H,*c,d);k,p=edges.get(e,(0,-1))
  if k==1:return None
  if k==2:
   other=next(x for x in portals[p] if x!=e);row,x=divmod(other,W+1);y=row//2
   return ((x-(d==3))%W,(y-(d==0))%H)
  dx,dy=((0,-1),(1,0),(0,1),(-1,0))[d];return ((c[0]+dx)%W,(c[1]+dy)%H)
 adj={(x,y):[n for d in range(4) if (n:=dest((x,y),d)) is not None] for x in range(W) for y in range(H)}
 def distances(c):
  ds={c:0};q=deque([c])
  while q:
   c=q.popleft()
   for n in adj[c]:
    if n not in ds:ds[n]=ds[c]+1;q.append(n)
  return ds
 def gap(a,b):
  dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1]);return min(dx,W-dx)+min(dy,H-dy)
 def state():return {str(i):list(b) for i,b in bodies.items()}
 queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)];r=-1;actor=None;turn=None;pearls=set();turns=[];deaths=[];snaps={};splits=[];near=[];qrecent=[];qboards=[];eatrows=[];minnear=None
 def finish():
  global turn
  if turn is not None:
   turn['end']=list(bodies.get(turn['id'],()));turn['afterL']=len(turn['end']);turns.append(turn)
   turn=None
 def proximity(idx):
  global minnear
  if queens[0] in bodies or queens[1] not in bodies:return
  q=bodies[queens[1]][0]
  ds=distances(q)
  for i,b in bodies.items():
   if teams[i]==0:
    dg=ds.get(b[0],99999)
    if minnear is None or dg<minnear['distance']:minnear=dict(round=r,event=idx,id=i,distance=dg,head=b[0],queen=q)
    if dg<=5:near.append(dict(round=r,event=idx,id=i,distance=dg,head=b[0],queen=q))
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0)
  if k not in (0,1,3,4,9,10,11):continue
  p=ev.pointer(0)
  if k==0:
   finish()
   if r>=0:snaps[r]=state()
   r=p.i32(0);actor=None
  elif k==1:
   finish();actor=p.i32(0)
   turn=dict(round=r,id=actor,side=teams[actor],body=list(bodies[actor]),L=len(bodies[actor]),eats=[],updates=[],dirs=[],kind=None)
   if actor==queens[0]:
    qrecent.append(dict(round=r,bodies=state(),pearls=list(pearls)))
    qrecent=qrecent[-3:]
   if actor==queens[1]:turn['qstate']=state()
   proximity(idx)
  elif k==3:
   c=sb.replay_format.point(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:
    pearls.remove(c);turn['eats'].append(c);eatrows.append([r,actor,teams[actor],c])
  elif k==4:
   a=p.pointer(0);turn['kind']=a.u16(0) if a else None
   turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
  elif k==9:
   i=p.i32(0);hd=sb.replay_format.point(p.pointer(0));tl=sb.replay_format.point(p.pointer(1));b=bodies[i]
   if b[0]!=hd:b.appendleft(hd)
   while len(b)>1 and b[-1]!=tl:b.pop()
   if turn:turn['updates'].append([i,hd,len(b)])
  elif k==10:
   parent,child=p.i32(0),p.i32(4);splits.append(dict(round=r,parent=parent,child=child,before=len(bodies[parent]),units=sum(teams[i]==teams[parent] for i in bodies)))
   for z,i in enumerate((parent,child)):bodies[i]=deque(sb.replay_format.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:
   i=p.i32(0);d=dict(round=r,id=i,side=teams[i],actor=actor,reason=p.u16(4),body=list(bodies[i]),actor_turn=turn.copy(),bodies=state(),pearls=list(pearls));deaths.append(d)
   if i==queens[0]:qboards=qrecent.copy()
   del bodies[i]
 finish();snaps[r]=state()
 out=dict(gid=gid,W=W,H=H,queens=queens,teams=teams,edges=list(edges.items()),turns=turns,deaths=deaths,snaps=snaps,qboards=qboards,splits=splits,near=near,minnear=minnear,eats=eatrows)
 (OUT/f'{gid}-trace.json').write_text(json.dumps(out,separators=(',',':')))
 print(gid,'done', 'qdeath',[(d['round'],d['id'],d['actor'],d['reason']) for d in deaths if d['id'] in queens], 'near',minnear,'first',near[:1],flush=True)
