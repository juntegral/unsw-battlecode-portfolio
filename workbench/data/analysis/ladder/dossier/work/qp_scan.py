import sys,json,math
sys.dont_write_bytecode=True
sys.path.insert(0,'tools')
from ladder_replay import replay,canonical_edges,edge_id
from collections import deque,defaultdict
from pathlib import Path
D=Path('data/analysis/ladder/dossier'); OUT=D/'work'; TIMES=[0,10,20,30,40,60,80,100,150]
def scan(row,who):
 root=replay.load(Path(row['replay'])).root(); text=root.text(0); W,H=map(int,text.splitlines()[0].split()[1:3]);bodies={};teams={};raw=[]
 for line in text.splitlines():
  q=line.split()
  if q and q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]='AB'[int(q[1])]
  elif q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 mine=row['side']; queen=min(i for i in bodies if teams[i]==mine);assert queen==row['queen']['id']
 def dist(a,b):
  dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1]);return min(dx,W-dx)+min(dy,H-dy)
 centre=(W//2,H//2);maxd=W//2+H//2;start=bodies[queen][0];d0=dist(start,centre)
 edges=canonical_edges(W,H,raw);ports=defaultdict(list)
 for e,(k,p) in edges.items():
  if k==2:ports[p].append(e)
 steps=((0,-1),(1,0),(0,1),(-1,0));paths={start:0};todo=deque([start])
 while todo:
  xy=todo.popleft();x,y=xy
  for di,(dx,dy) in enumerate(steps):
   e=edge_id(W,H,x,y,di);k,p=edges.get(e,(0,-1))
   if k==1:continue
   if k==2:
    other=next(z for z in ports[p] if z!=e);ry,px=divmod(other,W+1);z=((px-(di==3))%W,(ry//2-(di==0))%H)
   else:z=((x+dx)%W,(y+dy)%H)
   if z not in paths:paths[z]=paths[xy]+1;todo.append(z)
 snaps={};turns=defaultdict(lambda:[0]*8);rnd=0;cur=None;death=None;walk=0
 def proximity(i):
  head=bodies[i][0];friends=[dist(head,b[0]) for z,b in bodies.items() if z!=i and teams[z]==mine]; enemies=[dist(head,b[0]) for z,b in bodies.items() if teams[z]!=mine]
  nf=min(friends,default=None);ne=min(enemies,default=None)
  targets=[b[0] for z,b in bodies.items() if teams[z]!=mine and dist(head,b[0])==ne]
  screen=int(any(dist(b[0],e)<ne for z,b in bodies.items() if z!=i and teams[z]==mine for e in targets)) if ne is not None else None
  return [sum(d<=3 for d in friends),sum(d<=5 for d in friends),sum(d<=8 for d in friends),int(not any(d<=5 for d in friends)),nf,screen,sum(d<=5 for d in enemies)]
 def snapshot(r):
  live=queen in bodies;v={'alive':int(live)}
  if live:
   h=bodies[queen][0];v.update(centre=dist(h,centre)/maxd,path=paths.get(h),walk=walk,nearer=int(dist(h,centre)<d0),length=len(bodies[queen]),prox=proximity(queen))
   same=[i for i,b in bodies.items() if i!=queen and teams[i]==mine and len(b)==len(bodies[queen])]
   v['other_prox']=[proximity(i) for i in same]
  snaps[str(r)]=v
 def finish():
  nonlocal cur
  if cur is None:return
  i,h,L,f,cls=cur;cur=None
  if i not in bodies:return
  end=bodies[i][0];win='0-30' if rnd<=30 else '31-60' if rnd<=60 else '61-150';v=turns[win+'|'+cls];v[0]+=1;v[1]+=dist(end,centre)<dist(h,centre)
  nf=min((dist(h,z) for z in f),default=999)
  if nf<=8:v[2]+=1;v[3]+=min(dist(end,z) for z in f)>nf
  v[4]+=1;v[5]+=nf if f else 0;v[6]+=bool(f);v[7]+=not any(dist(h,z)<=5 for z in f)
 snapshot(0)
 for ev in root.pointer(3):
  k=ev.u16(0)
  if k not in (0,1,4,9,10,11):continue
  p=ev.pointer(0)
  if k in (0,1):finish()
  if k==0:
   nxt=p.i32(0)
   if nxt>rnd and rnd in TIMES and rnd!=0:snapshot(rnd)
   rnd=nxt
   if rnd>150:break
  elif k==1:
   i=p.i32(0)
   if teams[i]==mine and queen in bodies and (i==queen or len(bodies[i])==len(bodies[queen])):
    cur=(i,bodies[i][0],len(bodies[i]),[b[0] for z,b in bodies.items() if z!=i and teams[z]==mine],'Q' if i==queen else 'D')
  elif k==9:
   i=p.i32(0);h=replay.point(p.pointer(0));tail=replay.point(p.pointer(1));b=bodies[i]
   if b[0]!=h:
    b.appendleft(h)
    if i==queen:walk+=1
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(replay.point(c) for c in p.pointer(z));teams[i]='AB'[p.u16(8)]
  elif k==11:
   i=p.i32(0)
   if i==queen:death={'round':rnd,'reason':p.u16(4)}
   bodies.pop(i)
 else:
  finish()
  if rnd in TIMES and rnd!=0:snapshot(rnd)
 # Once a game ends, live positions are unobserved; deaths remain known.
 if queen not in bodies:
  for t in TIMES:
   if str(t) not in snaps:snaps[str(t)]={'alive':0}
 expected=row['queen']['death'];assert (death is None)==(expected is None or expected['round']>150)
 if death:assert death['round']==expected['round'] and death['reason']==expected['reason'];death['cause']=expected['cause']
 return dict(who=who,game=row['game'],layout=row['layout_key'],cells=W*H,snaps=snaps,turns=dict(turns),death=death,last=row['last_round'])
def main():
 shard=int(sys.argv[1]);nsh=int(sys.argv[2]);rows=[]
 for who,f in [('O','per-game.jsonl'),('R','target/per-game-top1.jsonl')]:
  for line in (D/f).open():
   r=json.loads(line)
   if r['relation']=='us':rows.append((who,r))
 assert len(rows)==1097
 out=OUT/f'qp_games_{shard}.jsonl'
 with out.open('w') as f:
  for n,(who,r) in enumerate(rows):
   if n%nsh!=shard:continue
   f.write(json.dumps(scan(r,who))+'\n');f.flush()
   if n%30==shard:print(n,who,r['game'],flush=True)
 print('done',shard,flush=True)
main()
