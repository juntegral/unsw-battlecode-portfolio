import sys,json
sys.dont_write_bytecode=True
from collections import deque,defaultdict
from functools import lru_cache
from analyze import lr,FILES,OUT

def scan(path):
 root=lr.replay.load(path).root();W,H=map(int,root.text(0).splitlines()[0].split()[1:3]);bodies={};teams={};raw=[]
 own=0 if root.text(1)=='21330' else 1
 for line in root.text(0).splitlines():
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)];edges=lr.canonical_edges(W,H,raw);portals=defaultdict(list)
 for e,(k,p) in edges.items():
  if k==2:portals[p].append(e)
 rev=defaultdict(list)
 def step(c,d):
  e=lr.edge_id(W,H,*c,d);kind,p=edges.get(e,(0,-1))
  if kind==1:return None
  if kind==2:
   partner=next(x for x in portals[p] if x!=e);row,x=divmod(partner,W+1);return ((x-(d==3))%W,(row//2-(d==0))%H)
  dx,dy=((0,-1),(1,0),(0,1),(-1,0))[d];return ((c[0]+dx)%W,(c[1]+dy)%H)
 for y in range(H):
  for x in range(W):
   for d in range(4):
    dest=step((x,y),d)
    if dest is not None:rev[dest].append((x,y))
 @lru_cache(None)
 def dist(goal):
  seen={goal:0};q=deque([goal])
  while q:
   a=q.popleft()
   for n in rev[a]:
    if n not in seen:seen[n]=seen[a]+1;q.append(n)
  return seen
 rnd=-1;actor=None;first=None;best=None;post=False;qpositions=set();positions=[];last_qpos=None;checks=0;own_turns_near=[]
 def check(ix,turn=False):
  nonlocal best,first,checks,last_qpos
  if not post or queens[1-own] not in bodies:return
  qp=bodies[queens[1-own]][0];qpositions.add(qp)
  if qp!=last_qpos:positions.append([rnd,*qp]);last_qpos=qp
  ds=dist(qp)
  for i,bb in bodies.items():
   if teams[i]!=own:continue
   dd=ds.get(bb[0],99999);checks+=1
   rec=dict(r=rnd,event=ix,id=i,distance=dd,head=bb[0],queen=qp,length=len(bb))
   if best is None or dd<best['distance']:best=rec
   if first is None and dd<=5:first=rec
   if turn and actor==i and dd<=5:own_turns_near.append(rec)
 for ix,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:rnd=p.i32(0)
  elif k==1:actor=p.i32(0);check(ix,True)
  elif k==9:
   i=p.i32(0);hd=lr.replay.point(p.pointer(0));tail=lr.replay.point(p.pointer(1));b=bodies[i]
   if b[0]!=hd:b.appendleft(hd)
   while len(b)>1 and b[-1]!=tail:b.pop()
   check(ix)
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(lr.replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
   check(ix)
  elif k==11:
   i=p.i32(0);bodies.pop(i)
   if i==queens[own]:post=True
   check(ix)
 return dict(first=first,best=best,checks=checks,own_turns_near=own_turns_near,enemy_queen_positions=positions,enemy_queen_last=last_qpos,unique_queen_positions=len(qpositions),definition='Shortest directed terrain path, kelp excluded, portals and wrap included; bodies ignored. Check after every movement/split/death and at turn start.')
if __name__=='__main__':
 for path in FILES:
  d=scan(path);(OUT/f'{path.stem[1:]}-proximity.json').write_text(json.dumps(d));print(path.stem,{k:v for k,v in d.items() if k not in ('enemy_queen_positions','own_turns_near')},'near turns',len(d['own_turns_near']),flush=True)
