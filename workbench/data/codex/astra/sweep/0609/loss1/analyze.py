import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
ROOT=Path(__file__).resolve().parents[6]
sys.path.insert(0,str(ROOT/'tools'))
import ladder_replay as lr
OUT=Path(__file__).parent
P=ROOT/'data/online/live-one1/b1496000/M1496001.replay'
meta=json.loads(P.with_name('game-1496001.json').read_text())
scan=lr.scan(P,meta,'b1496000',set());scan['intervals']={str(k):v for k,v in scan['intervals'].items()}
(OUT/'scan.json').write_text(json.dumps(scan,ensure_ascii=False,indent=2))
root=lr.replay.load(P).root();W,H=map(int,root.text(0).splitlines()[0].split()[1:3])
bodies={};teams={};raw=[]
for line in root.text(0).splitlines():
 q=line.split()
 if q[0]=='DRAGON':
  i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]='AB'[int(q[1])]
 elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
edges=lr.canonical_edges(W,H,raw)
portals={}
for e,(k,p) in edges.items():
 if k==2:portals.setdefault(p,[]).append(e)
def adj(c):
 for d,(dx,dy) in enumerate(((0,-1),(1,0),(0,1),(-1,0))):
  e=lr.edge_id(W,H,*c,d);k,p=edges.get(e,(0,-1))
  if k==1:continue
  if k==2:
   partner=next(z for z in portals[p] if z!=e);row,x=divmod(partner,W+1);y=row//2
   yield ((x-(d==3))%W,(y-(d==0))%H)
  else:yield ((c[0]+dx)%W,(c[1]+dy)%H)
def dist(src):
 seen={src:0};q=deque([src])
 while q:
  c=q.popleft()
  for n in adj(c):
   if n not in seen:seen[n]=seen[c]+1;q.append(n)
 return seen
pearls=set();turns=[];rnd=-1;actor=None;t=None;near=[];qdead=False;near_all=[]
for idx,e in enumerate(root.pointer(3)):
 k=e.u16(0);p=e.pointer(0)
 if k==0:rnd=p.i32(0);actor=None
 elif k==1:
  actor=p.i32(0)
  t=dict(round=rnd,event=idx,id=actor,team=teams[actor],body=list(bodies[actor]),bodies={i:list(b) for i,b in bodies.items()},pearls=sorted(pearls),actions=[],updates=[],eats=[],splits=[],deaths=[],logs=[])
  turns.append(t)
  if qdead and 1 in bodies and teams[actor]=='B':
   dd=dist(bodies[1][0]);gap=dd.get(bodies[actor][0],999)
   near.append(dict(round=rnd,id=actor,gap=gap,head=bodies[actor][0],enemy_queen=bodies[1][0]))
 elif k==3:
  c=lr.replay.point(p.pointer(0))
  if p.u32(0):pearls.add(c)
  else:pearls.remove(c);t['eats'].append(c)
 elif k==4:
  a=p.pointer(0);t['actions'].append(dict(kind=a.u16(0),dirs=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) else [],split=a.i32(4)))
 elif k==6:t['logs'].append(p.text(0))
 elif k==9:
  i=p.i32(0);hd=lr.replay.point(p.pointer(0));tail=lr.replay.point(p.pointer(1));b=bodies[i]
  if b[0]!=hd:b.appendleft(hd)
  while len(b)>1 and b[-1]!=tail:b.pop()
  assert b[-1]==tail
  if t is not None:t['updates'].append(dict(id=i,body=list(b)))
 elif k==10:
  t['splits'].append([p.i32(0),p.i32(4)])
  for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(lr.replay.point(c) for c in p.pointer(z));teams[i]='AB'[p.u16(8)]
 elif k==11:
  i=p.i32(0);t['deaths'].append([i,p.u16(4)]);bodies.pop(i)
  if i==0:qdead=True
 if qdead and 1 in bodies:
  dd=dist(bodies[1][0])
  for i,b in bodies.items():
   if teams[i]=='B':near_all.append(dict(round=rnd,event=idx,id=i,gap=dd.get(b[0],999),head=b[0],enemy_queen=bodies[1][0]))
(OUT/'turns.json').write_text(json.dumps(turns,separators=(',',':')))
(OUT/'near.json').write_text(json.dumps(near,indent=2))
def board(t):
 cx,cy=t['body'][0];occ={c:('Q' if i==0 else 'E' if teams[i]=='A' else 'A') if j==0 else ('q' if i==0 else 'e' if teams[i]=='A' else 'a') for i,b in t['bodies'].items() for j,c in enumerate(b)}
 rows=[]
 for dy in range(-3,4):
  rows.append(''.join(occ.get(((cx+dx)%W,(cy+dy)%H),'*' if ((cx+dx)%W,(cy+dy)%H) in t['pearls'] else '.') for dx in range(-3,4)))
 return '\n'.join(rows)
with (OUT/'detail.txt').open('w') as f:
 for t in turns:
  if t['id']==0 and t['round']>=65:
   f.write(str({k:v for k,v in t.items() if k not in ('bodies','pearls')})+'\n'+board(t)+'\n')
   f.write('near bodies '+str({i:b for i,b in t['bodies'].items() if any(abs(c[0]-t['body'][0][0])<=4 and abs(c[1]-t['body'][0][1])<=4 for c in b)})+'\n')
 print('NEAR after death',near)
 print('DEATHS ours',[(d['round'],d['id'],d['length'],d['cause'],d['actor']) for d in scan['deaths'] if d['side']=='us'])
 print('snapshots',[(r,s['us']['alive'],s['them']['alive'],s['us']['total'],s['them']['total'],s['us']['pearls'],s['them']['pearls']) for r,s in scan['snapshots'].items() if r%5==0 or r>=78])
 print('board size',W,H,'kelp edges',sum(k==1 for k,p in edges.values()))

metrics={}
metrics['closest_after_queen_death']=min(near_all,key=lambda x:x['gap'])
metrics['within5_after_queen_death']=sum(v['gap']<=5 for v in near_all)
def manrow(v):
 dx=abs(v['head'][0]-v['enemy_queen'][0]);dy=abs(v['head'][1]-v['enemy_queen'][1]);return min(dx,W-dx)+min(dy,H-dy)
metrics['closest_manhattan_after_queen_death']=dict(min(near_all,key=manrow))
metrics['closest_manhattan_after_queen_death']['manhattan']=min(map(manrow,near_all))
metrics['bands']=[]
for lo,hi in [(0,24),(25,50),(51,64),(65,88)]:
 row=dict(lo=lo,hi=hi)
 for side in 'BA':
  tt=[t for t in turns if t['team']==side and lo<=t['round']<=hi]
  row[side]=dict(turns=len(tt),eats=sum(len(t['eats']) for t in tt),splits=sum(len(t['splits']) for t in tt))
 metrics['bands'].append(row)
metrics['queen_famine']=dict(rounds=[25,67],turns=sum(t['id']==0 and 25<=t['round']<=67 for t in turns),eats=sum(len(t['eats']) for t in turns if t['id']==0 and 25<=t['round']<=67))
metrics['bodies_final']={i:list(b) for i,b in bodies.items()}
(OUT/'metrics.json').write_text(json.dumps(metrics,indent=2))
print('METRICS',json.dumps(metrics,ensure_ascii=False))
with (OUT/'boards.txt').open('w') as f:
 for t in turns:
  if t['id']==0 and t['round'] in (79,80,81):
   f.write('r'+str(t['round'])+' '+str(t['body'][0])+'\n'+board(t)+'\n')

def dest(c,d):
 e=lr.edge_id(W,H,*c,d);k,p=edges[e]
 if k==1:return None
 if k==2:
  partner=next(z for z in portals[p] if z!=e);row,x=divmod(partner,W+1);y=row//2
  return ((x-(d==3))%W,(y-(d==0))%H)
 dx,dy=((0,-1),(1,0),(0,1),(-1,0))[d];return ((c[0]+dx)%W,(c[1]+dy)%H)

def static_path(t,dirs):
 b=list(t['body']);pp=set(t['pearls']);other={c for i,bb in t['bodies'].items() if i!=t['id'] for c in bb};free=(len(b)+3)//4;path=[]
 for n,d in enumerate(dirs):
  c=dest(b[0],d)
  if c is None or c in b or c in other or n>=free and len(b)<=2:return dict(legal=False,path=path,blocked=c)
  b.insert(0,c)
  if c in pp:pp.remove(c)
  else:b.pop()
  if n>=free:b.pop()
  path.append(c)
 return dict(legal=True,path=path,length=len(b))
alternatives={}
for r,dirs in [(73,[3,3]),(75,[2,2]),(78,[3])]:
 t=next(t for t in turns if t['id']==0 and t['round']==r)
 alternatives[str(r)]=static_path(t,dirs)
(OUT/'alternatives.json').write_text(json.dumps(alternatives,indent=2))
