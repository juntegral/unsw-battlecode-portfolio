import sys,json
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/local']
from ladder_replay import edge_id,canonical_edges
from replay_format import load,point
from collections import deque,defaultdict
from pathlib import Path
OUT=Path(__file__).resolve().parent
STEP=((0,-1),(1,0),(0,1),(-1,0))
def scan(gid):
 root=load(Path(f'data/online/smoke/one10-c1-old/M{gid}.replay')).root()
 W,H=map(int,root.text(0).splitlines()[0].split()[1:3]); bodies={};teams={};raw=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 edges=canonical_edges(W,H,raw);ports=defaultdict(list)
 for e,(k,p) in edges.items():
  if k==2:ports[p].append(e)
 queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
 def dest(h,d):
  e=edge_id(W,H,*h,d);k,p=edges.get(e,(0,-1))
  if k==1:return None
  if k==2:
   row,x=divmod(next(z for z in ports[p] if z!=e),W+1)
   return ((x-(d==3))%W,(row//2-(d==0))%H)
  dx,dy=STEP[d];return ((h[0]+dx)%W,(h[1]+dy)%H)
 def distances(h,occ=set(),limit=9999):
  seen={h:0};queue=deque([h])
  while queue:
   c=queue.popleft()
   if seen[c]>=limit:continue
   for d in range(4):
    n=dest(c,d)
    if n is not None and n not in seen:
     seen[n]=seen[c]+1
     if n not in occ:queue.append(n)
  return seen
 def man(a,b):
  dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1]);return min(dx,W-dx)+min(dy,H-dy)
 def state():
  return [dict(n=sum(teams[i]==s for i in bodies),total=sum(len(b) for i,b in bodies.items() if teams[i]==s),long=max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),q=len(bodies.get(queens[s],())),eats=eats[s]) for s in (0,1)]
 pearls=set();eats=[0,0];turns=[];deaths=[];snaps={};splits=[];r=-1;actor=None;t=None;post=[];qdead=False;nearest=None
 def finish():
  if t is not None:t['end']=list(bodies[actor]) if actor in bodies else []
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   finish()
   if r>=0:snaps[r]=state()
   r=p.i32(0);actor=None;t=None
  elif k==1:
   finish();actor=p.i32(0)
   t=dict(r=r,i=actor,L=len(bodies[actor]),h=bodies[actor][0],bodies={i:list(b) for i,b in bodies.items()},pearls=list(pearls),steps=[],eat=0,logs=[],event=idx)
   turns.append(t)
   if qdead and queens[1] in bodies and teams[actor]==0:
    h=bodies[actor][0];qh=bodies[queens[1]][0];ds=distances(h,limit=5)
    md=man(h,qh)
    if nearest is None or md<nearest['man']:nearest=dict(r=r,i=actor,h=h,qh=qh,man=md)
    if ds.get(qh,999)<=5:
     occ={c for b in bodies.values() for c in b};free=distances(h,occ,5).get(qh,999)
     post.append(dict(r=r,i=actor,L=len(bodies[actor]),h=h,qh=qh,steps=ds[qh],free=free,man=md))
  elif k==3:
   c=point(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:
    pearls.remove(c);eats[teams[actor]]+=1;t['eat']+=1
  elif k==4:
   a=p.pointer(0);t['action']=a.u16(0) if a else None
   t['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) else []
   if a and a.u16(0)==1:t['childSize']=a.i32(4)
  elif k==6:
   if t is not None:t['logs'].append(p.text(0))
  elif k==9:
   i=p.i32(0);h=point(p.pointer(0));tail=point(p.pointer(1));b=bodies[i]
   if b[0]!=h:b.appendleft(h);t['steps'].append(h)
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
  elif k==10:
   par,ch=p.i32(0),p.i32(4)
   for z,i in enumerate((par,ch)):bodies[i]=deque(point(x) for x in p.pointer(z));teams[i]=p.u16(8)
   splits.append(dict(r=r,parent=par,child=ch,lens=[len(bodies[par]),len(bodies[ch])]))
  elif k==11:
   i=p.i32(0);deaths.append(dict(r=r,i=i,reason=p.u16(4),actor=actor,L=len(bodies[i]),body=list(bodies[i]),turn=len(turns)-1,event=idx))
   if i==queens[0]:qdead=True
   bodies.pop(i)
 finish();snaps[r]=state()
 res=root.pointer(4);final=[dict(zip(('n','long','total','q'),[res.pointer(s).i32(o) for o in (0,4,8,12)])) for s in (0,1)]
 assert all(all(final[s][k]==snaps[r][s][k] for k in final[s]) for s in (0,1))
 qturns=[t for t in turns if t['i']==queens[0]]
 summary=dict(gid=gid,W=W,H=H,botA=root.text(1),botB=root.text(2),queens=queens,end=r,final=final,qdeath=[d for d in deaths if d['i'] in queens],lastq=[{k:v for k,v in t.items() if k!='bodies' and k!='pearls'} for t in qturns[-3:]],post=post,nearest=nearest,snaps=snaps)
 (OUT/f'{gid}-summary.json').write_text(json.dumps(summary,indent=2))
 (OUT/f'{gid}-turns.json').write_text(json.dumps(dict(turns=turns,deaths=deaths,teams=teams,edges=raw,splits=splits)))
 print(json.dumps({k:v for k,v in summary.items() if k not in ('snaps','post')}));print('post',len(post),post[:3]);print('snaps',[(k,v) for k,v in snaps.items() if k%50==0])
for g in (1492099,1492102,1492103):scan(g)
