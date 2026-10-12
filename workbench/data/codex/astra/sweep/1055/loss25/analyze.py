import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter,defaultdict
sys.path.insert(0,str(Path('tools').resolve()))
import ladder_replay as lr
OUT=Path(__file__).parent
jobs=[(1508916,1508916),(1510463,1510461),(1512747,1512747)]
for gid,bid in jobs:
 p=Path(f'data/online/live-one1/b{bid}/M{gid}.replay'); meta=json.loads(p.with_name(f'game-{gid}.json').read_text())
 s=lr.scan(p,meta,'loss25',set())
 root=lr.replay.load(p).root(); W,H=map(int,s['text'].splitlines()[0].split()[1:3]); bodies={}; teams={}; edges=[]
 for line in s['text'].splitlines():
  a=line.split()
  if a[0]=='DRAGON':
   i=len(bodies); bodies[i]=deque((int(a[3+2*k]),int(a[4+2*k])) for k in range(int(a[2])));teams[i]='AB'[int(a[1])]
  if a[0]=='EDGE': edges.append(tuple(map(int,a[1:4])))
 edges=lr.canonical_edges(W,H,edges); portals=defaultdict(list)
 for e,(k,pid) in edges.items():
  if k==2:portals[pid].append(e)
 def dest(h,d):
  e=lr.edge_id(W,H,*h,d);k,pid=edges.get(e,(0,-1))
  if k==1:return None
  if k==2:
   partner=next(z for z in portals[pid] if z!=e);row,x=divmod(partner,W+1);y=row//2
   return ((x-(d==3))%W,(y-(d==0))%H)
  dx,dy=lr.base.STEP[d];return ((h[0]+dx)%W,(h[1]+dy)%H)
 adj={(x,y):[v for d in range(4) if (v:=dest((x,y),d)) is not None] for x in range(W) for y in range(H)}
 nearcache={}
 def near(target):
  if target not in nearcache:
   # Directed portal-aware distances TO the queen.
   rev=defaultdict(list)
   for u,vs in adj.items():
    for v in vs:rev[v].append(u)
   ds={target:0};q=deque([target])
   while q:
    u=q.popleft()
    if ds[u]==5:continue
    for v in rev[u]:
     if v not in ds:ds[v]=ds[u]+1;q.append(v)
   nearcache[target]=ds
  return nearcache[target]
 qid=s['queens']['us'];eq=s['queens']['them'];ours=s['ours']; rnd=-1;actor=None;present=set();turn=None;qt=[];allturn=[];close=[];positions=Counter();splits=[]
 def board(h):
  rows=[]
  for dy in range(-3,4):
   row=''
   for dx in range(-3,4):
    c=((h[0]+dx)%W,(h[1]+dy)%H);ch='*' if c in present else '.'
    for i,b in bodies.items():
     if c in b:ch=('Q' if i==qid else 'E' if i==eq else 'A' if teams[i]==ours else 'X') if c==b[0] else ('a' if teams[i]==ours else 'x')
    row+=ch
   rows.append(row)
  return rows
 def finish():
  if turn is not None:
   turn['end']=list(bodies[actor]) if actor in bodies else [];allturn.append(turn)
   if actor in (qid,eq):qt.append(turn)
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);v=ev.pointer(0)
  if k==0:finish();turn=None;rnd=v.i32(0);actor=None
  elif k==1:
   finish();actor=v.i32(0);h=bodies[actor][0]
   turn=dict(r=rnd,id=actor,event=idx,L=len(bodies[actor]),head=h,eats=0,steps=[],split=False)
   if actor in (qid,eq):turn.update(board=board(h),bodies={i:list(b) for i,b in bodies.items() if any(min(abs(c[0]-h[0]),W-abs(c[0]-h[0]))<=3 and min(abs(c[1]-h[1]),H-abs(c[1]-h[1]))<=3 for c in b)},pearls=list(present),units=sum(t==ours and i in bodies for i,t in teams.items()))
   if qid not in bodies and eq in bodies:
    positions[bodies[eq][0]]+=1
    if teams[actor]==ours and h in near(bodies[eq][0]):close.append(dict(r=rnd,id=actor,L=len(bodies[actor]),head=h,queen=bodies[eq][0],distance=near(bodies[eq][0])[h]))
  elif k==3:
   c=lr.replay.point(v.pointer(0))
   if v.u32(0):present.add(c)
   else:present.discard(c);turn['eats']+=1
  elif k==4:
   a=v.pointer(0);turn['action']=a.u16(0) if a else None;turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
  elif k==9:
   i=v.i32(0);h=lr.replay.point(v.pointer(0));tail=lr.replay.point(v.pointer(1));b=bodies[i]
   if b[0]!=h:b.appendleft(h);turn['steps'].append(h)
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
  elif k==10:
   parent,child=v.i32(0),v.i32(4);turn['split']=True;splits.append(dict(r=rnd,parent=parent,child=child,before=len(bodies[parent])))
   for z,i in enumerate((parent,child)):bodies[i]=deque(lr.replay.point(c) for c in v.pointer(z));teams[i]='AB'[v.u16(8)]
  elif k==11:bodies.pop(v.i32(0))
 finish()
 s.update(queen_turns=qt,close_after_death=close,enemy_positions=positions.most_common(),splits=splits,allturns=allturn,final_bodies={i:list(b) for i,b in bodies.items()},teams=teams)
 s['intervals']={str(k):v for k,v in s['intervals'].items()}
 (OUT/f'{gid}.json').write_text(json.dumps(s))
 print(gid, 'bots',s['bots'],'queens',s['queens'],'final',s['final'],'end',s['last_round'],s['end_reason'])
 print('queen deaths', [d for d in s['deaths'] if d['id'] in (qid,eq)])
 print('last own queen turns', [{k:v for k,v in t.items() if k not in ('bodies','pearls')} for t in qt if t['id']==qid][-3:])
 print('near after death',len(close),close[:3], 'enemy positions',positions.most_common(4))
 print('checkpoints', {r:s['snapshots'][r] for r in (0,50,100,200,300,400,499) if r in s['snapshots']})
