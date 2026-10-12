import sys,json
from pathlib import Path
from collections import deque,Counter
sys.dont_write_bytecode=True
ROOT=Path.cwd(); OUT=Path(__file__).parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'data/analysis/ladder/dossier/local')]
import ladder_replay as lr
from count_local import Geo

def run(gid):
 p=ROOT/f'data/online/smoke/one13-k2-old/M{gid}.replay'
 meta=json.loads(p.with_name(f'game-{gid}.json').read_text())
 full=json.loads((OUT/f'{gid}-scan.json').read_text()) if (OUT/f'{gid}-scan.json').exists() else lr.scan(p,meta,'one13-k2-old',set())
 (OUT/f'{gid}-scan.json').write_text(json.dumps({k:v for k,v in full.items() if k != 'intervals'},default=list))
 root=lr.replay.load(p).root(); lines=root.text(0).splitlines(); W,H=map(int,lines[0].split()[1:3]); bodies={}; teams={}; raw=[]
 for q in map(str.split,lines):
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(lr.replay.point(None) for _ in [])
   bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(q[1])
  if q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 geo=Geo(W,H,raw);edges=lr.canonical_edges(W,H,raw)
 queens=[min(i for i in bodies if teams[i]==s) for s in range(2)]
 rev=[[] for _ in geo.adj]
 for a, row in enumerate(geo.adj):
  for b in row:rev[b].append(a)
 cache={}
 def dist(target):
  t=target[1]*W+target[0]
  if t not in cache:
   d={t:0}; queue=deque([t])
   while queue:
    a=queue.popleft()
    for b in rev[a]:
     if b not in d:d[b]=d[a]+1;queue.append(b)
   cache[t]=d
  return cache[t]
 def man(a,b):
  dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1]);return min(dx,W-dx)+min(dy,H-dy)
 pearls=set();rnd=0;actor=None;turn=None; turns=[];qturns=[[],[]];near=[];qpositions=[]; closest=None; near_events=[]
 def close():
  if turn is not None:
   turn['end']=list(bodies.get(actor,[]));turn['after_len']=len(turn['end']);turn['end_units']=sum(teams[i]==teams[actor] for i in bodies)
 def board(hd):
  cells={c:('Q' if i==queens[0] else 'K' if i==queens[1] else 'A' if teams[i]==0 else 'B') if k==0 else ('q' if i==queens[0] else 'k' if i==queens[1] else 'a' if teams[i]==0 else 'b') for i,b in bodies.items() for k,c in enumerate(b)}
  return [''.join(cells.get(((hd[0]+dx)%W,(hd[1]+dy)%H),'*' if ((hd[0]+dx)%W,(hd[1]+dy)%H) in pearls else '.') for dx in range(-3,4)) for dy in range(-3,4)]
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:close();turn=None;rnd=p.i32(0)
  elif k==1:
   close();actor=p.i32(0);hd=bodies[actor][0]
   turn=dict(r=rnd,id=actor,side=teams[actor],event=idx,body=list(bodies[actor]),L=len(bodies[actor]),units=sum(teams[i]==teams[actor] for i in bodies),dirs=[],moves=[],eats=0,splits=[],deaths=[])
   turns.append(turn)
   if actor in queens:
    turn['board']=board(hd);turn['nearby']=[dict(id=i,L=len(b),body=list(b),d=man(hd,b[0])) for i,b in bodies.items() if man(hd,b[0])<=9]
    turn['edges']=[(dx,dy,[geo.moves[((hd[1]+dy)%H)*W+(hd[0]+dx)%W][z][0] for z in range(4)]) for dy in range(-3,4) for dx in range(-3,4)]
    qturns[teams[actor]].append(turn)
    if actor==queens[1] and queens[0] not in bodies:qpositions.append([rnd,hd,len(bodies[actor])])
   if queens[0] not in bodies and queens[1] in bodies and teams[actor]==0:
    qh=bodies[queens[1]][0];dd=dist(qh).get(hd[1]*W+hd[0],999)
    if dd<=5:near.append(dict(r=rnd,id=actor,L=len(bodies[actor]),head=hd,qhead=qh,d=dd,man=man(hd,qh)))
  elif k==4:
   a=p.pointer(0);turn['action']=a.u16(0) if a else None;turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else [];turn['timeout']=p.bit(32)
  elif k==3:
   c=lr.replay.point(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c);turn['eats']+=1
  elif k==9:
   i=p.i32(0);hd=lr.replay.point(p.pointer(0));tail=lr.replay.point(p.pointer(1));b=bodies[i]
   if hd!=b[0]:b.appendleft(hd);turn['moves'].append([i,hd])
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
  elif k==10:
   parent,child=p.i32(0),p.i32(4);turn['splits'].append([parent,child])
   for z,i in enumerate((parent,child)):bodies[i]=deque(lr.replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:
   i=p.i32(0);turn['deaths'].append([i,p.u16(4)]);bodies.pop(i)
  if k in (1,9,10,11) and queens[0] not in bodies and queens[1] in bodies:
   qh=bodies[queens[1]][0];dd=dist(qh)
   for z,b in bodies.items():
    if teams[z]!=0:continue
    gap=dd.get(b[0][1]*W+b[0][0],999)
    rec=dict(r=rnd,event=idx,id=z,d=gap,head=b[0],qhead=qh)
    if closest is None or gap<closest['d']:closest=rec
    if gap<=5:near_events.append(rec)
 close()
 result=dict(gid=gid,W=W,H=H,queens=queens,bots=full['bots'],final=full['final'],qturns=qturns,near=near,qpositions=qpositions,turns=turns,closest=closest,near_events=near_events)
 (OUT/f'{gid}-detail.json').write_text(json.dumps(result))
 print(gid,full['bots'], 'FINAL',full['final'],'QDEATHS', [d for d in full['deaths'] if d['id'] in queens], 'Qeats',full['q_eats'],'Qsplits',full['q_splits'],'NEAR',len(near),near[:3])
 for side in range(2):
  print('Q',side,'last',[(t['r'],t['body'],t['dirs'],t['eats'],t['splits']) for t in qturns[side][-5:]])
for gid in [1513842,1513844,1513845]:run(gid)
