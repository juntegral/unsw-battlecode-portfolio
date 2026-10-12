import sys
sys.dont_write_bytecode = True
import json
import importlib.util
from pathlib import Path
from collections import deque, Counter
from functools import lru_cache
ROOT=Path.cwd(); OUT=ROOT/'data/codex/astra/sweep/1055/loss55'
sys.path.insert(0,str(ROOT/'tools'))
import ladder_replay as lr
path=ROOT/'data/online/live-one1/b1516554/M1516558.replay'
meta=json.loads(path.with_name('game-1516558.json').read_text())
if (OUT/'summary.json').exists():
 summary=json.loads((OUT/'summary.json').read_text())
else:
 summary=lr.scan(path,meta,'loss55',set())
 (OUT/'summary.json').write_text(json.dumps({k:v for k,v in summary.items() if k not in ('text','pearls','natural','intervals','eaten_rounds')},indent=2))
rp=lr.replay; root=rp.load(path).root()
spec=importlib.util.spec_from_file_location('sonar_decoder', ROOT.parent/'battlecode/work/card_42_check.py')
codec=importlib.util.module_from_spec(spec); spec.loader.exec_module(codec)
W,H=map(int,root.text(0).splitlines()[0].split()[1:3])
key=codec.make_key(W,H,1); streams={}; sonar=[]; scout=[]
bodies={}; teams={}; raw_edges=[]
for line in root.text(0).splitlines():
 q=line.split()
 if q[0]=='DRAGON':
  i=len(bodies); bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2]))); teams[i]=int(q[1])
 elif q[0]=='EDGE': raw_edges.append(tuple(map(int,q[1:4])))
edges=lr.canonical_edges(W,H,raw_edges)
portals={}
for e,(k,p) in edges.items():
 if k==2: portals.setdefault(p,[]).append(e)
def dest(c,d):
 e=lr.edge_id(W,H,*c,d); kind,pid=edges.get(e,(0,-1))
 if kind==2:
  partner=next(z for z in portals[pid] if z!=e); row,x=divmod(partner,W+1); y=row//2
  return ((x-(d==3))%W,(y-(d==0))%H)
 dx,dy=lr.base.STEP[d]; return ((c[0]+dx)%W,(c[1]+dy)%H)
def wall(c,d): return edges.get(lr.edge_id(W,H,*c,d),(0,-1))[0]==1
rev={(x,y):[] for x in range(W) for y in range(H)}
for c in rev:
 for d in range(4):
  if not wall(c,d): rev[dest(c,d)].append(c)
@lru_cache(None)
def distances(c):
 ds={c:0}; queue=deque([c])
 while queue:
  h=queue.popleft()
  for n in rev[h]:
   if n not in ds: ds[n]=ds[h]+1; queue.append(n)
 return ds
def view(a,b):
 dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1]); return min(dx,W-dx)<=3 and min(dy,H-dy)<=3
pearls=set(); rnd=-1; actor=None; current=None
turns=[]; near=[]; closest=None; post_samples=0; queen_positions=Counter(); qchanges=[]
def board(h):
 cells={c:('Q' if i==1 and k==0 else 'q' if i==1 else 'X' if i==365 and k==0 else 'x' if i==365 else 'A' if teams[i]==1 and k==0 else 'a' if teams[i]==1 else 'E' if k==0 else 'e') for i,b in bodies.items() for k,c in enumerate(b)}
 lines=[]
 for y in range(h[1]-3,h[1]+4):
  top=''; row=''
  for x in range(h[0]-3,h[0]+4):
   c=(x%W,y%H); top+='+'+('-' if wall(c,0) else ' '); row+=('|' if wall(c,3) else ' ')+cells.get(c,'*' if c in pearls else '.')
  lines += [top+'+',row+('|' if wall((x%W,y%H),1) else ' ')]
 lines.append(''.join('+'+('-' if wall((x%W,y%H),2) else ' ') for x in range(h[0]-3,h[0]+4))+'+')
 return '\n'.join(lines)
def snap():
 h=bodies[actor][0]
 return dict(round=rnd,id=actor,event=idx,body=list(bodies[actor]),board=board(h),visible=[dict(id=i,team=teams[i],body=list(b),head_visible=view(h,b[0]),visible_parts=sum(view(h,c) for c in b)) for i,b in bodies.items() if any(view(h,c) for c in b)],attacker=list(bodies.get(365,())),pearls=sorted(c for c in pearls if view(h,c)),actions=[],updates=[],logs=[])
for idx,ev in enumerate(root.pointer(3)):
 kind=ev.u16(0); p=ev.pointer(0)
 if kind==0: rnd=p.i32(0); actor=None; current=None
 elif kind==1:
  actor=p.i32(0); current=None
  if (actor==1 and rnd>=150) or (actor==365 and 150<=rnd<=158) or (actor in (0,1086) and 489<=rnd<=492): current=snap(); turns.append(current)
  if 154<=rnd<=158 and teams[actor]==1 and 365 in bodies and view(bodies[actor][0],bodies[365][0]):
   scout.append(dict(round=rnd,event=idx,id=actor,head=bodies[actor][0],attacker=bodies[365][0],queen=bodies.get(1,[None])[0]))
  if 1 not in bodies and 0 in bodies:
   qh=bodies[0][0]; ds=distances(qh); queen_positions[qh]+=1
   nearest=min(((ds.get(b[0],99999),i,b[0]) for i,b in bodies.items() if teams[i]==1),default=(99999,None,None))
   row=dict(round=rnd,event=idx,distance=nearest[0],id=nearest[1],head=nearest[2],queen=qh); post_samples+=1
   if closest is None or nearest[0]<closest['distance']: closest=row
   if teams[actor]==1 and ds.get(bodies[actor][0],99999)<=5: near.append(dict(round=rnd,event=idx,id=actor,length=len(bodies[actor]),head=bodies[actor][0],queen=qh,distance=ds[bodies[actor][0]],visible=view(bodies[actor][0],qh)))
 elif kind==3:
  c=rp.point(p.pointer(0))
  if p.u32(0): pearls.add(c)
  else: pearls.remove(c)
 elif kind==4 and current is not None:
  a=p.pointer(0); k=a.u16(0); current['actions'].append(dict(kind=k,dirs=list(a.pointer(0)) if k==0 and a.pointer(0) is not None else [],split=a.i32(4) if k==1 else None))
 elif kind==6 and current is not None: current['logs'].append(p.text(0))
 elif kind==9:
  i=p.i32(0); h=rp.point(p.pointer(0)); tail=rp.point(p.pointer(1)); b=bodies[i]
  if b[0]!=h: b.appendleft(h)
  while len(b)>1 and b[-1]!=tail: b.pop()
  assert b[-1]==tail
  if current is not None: current['updates'].append(dict(id=i,body=list(b)))
  if i==0: qchanges.append(dict(round=rnd,head=h,length=len(b)))
 elif kind==10:
  for z,i in enumerate((p.i32(0),p.i32(4))): bodies[i]=deque(rp.point(c) for c in p.pointer(z)); teams[i]=p.u16(8)
 elif kind==11: bodies.pop(p.i32(0))
 elif kind==12 and 150<=rnd<=158 and teams.get(p.i32(0))==1:
  plain=codec.unseal(key,p.u64(16),streams)
  if plain is not None:
   row=dict(round=rnd,event=idx,sender=p.i32(0),hit=p.i32(12) if p.u16(6) else None,origin=rp.point(p.pointer(0)),end=rp.point(p.pointer(1)),kind=(plain>>38)&0x7fff,high=plain>>63)
   if row['high'] and row['kind']==0x5b: row.update(cell=(plain&0x3fff),parts=((plain>>14)&0x3fff)+1,when=(plain>>28)&0x1ff)
   if row['hit']==1 or row['kind']==0x5b: sonar.append(row)
for s in (0,1):
 expected=summary['final']['us' if s==1 else 'them']; ls=[len(b) for i,b in bodies.items() if teams[i]==s]
 assert (len(ls),sum(ls),max(ls))==(expected['alive'],expected['total'],expected['longest'])
facts=dict(size=[W,H],turns=turns,near=near,closest=closest,post_samples=post_samples,sonar=sonar,scout=scout,queen_positions=[dict(head=k,turns=v) for k,v in queen_positions.most_common()],qchanges=qchanges,final_bodies={i:dict(team=teams[i],body=list(b)) for i,b in bodies.items()})
(OUT/'facts.json').write_text(json.dumps(facts,indent=2))
print(json.dumps(dict(final=summary['final'],closest=closest,near_count=len(near),near_first=near[:5]),indent=2))
for t in turns:
 if t['round']>=156:
  print(json.dumps({k:v for k,v in t.items() if k not in ('visible','board')},ensure_ascii=False)); print(t['board'])
