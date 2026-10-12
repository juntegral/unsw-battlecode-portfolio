import sys,json
from pathlib import Path
from collections import deque,Counter
sys.dont_write_bytecode=True
ROOT=Path.cwd(); OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'data/analysis/ladder/dossier')]
import ladder_replay as lr
from count_dossier import Geo
p=ROOT/'data/online/live-one1/b1495464/M1495468.replay'
meta=json.loads(p.with_name('game-1495468.json').read_text())
scan=lr.scan(p,meta,'b1495464',set()); scan.pop('intervals')
(OUT/'scan.json').write_text(json.dumps(scan,ensure_ascii=False,indent=2))
r=lr.replay.load(p).root(); w,h=map(int,r.text(0).splitlines()[0].split()[1:3]); bodies={}; teams={}; edges=[]
for line in r.text(0).splitlines():
 q=line.split()
 if q[0]=='DRAGON':
  i=len(bodies);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(q[1])
 elif q[0]=='EDGE':edges.append(tuple(map(int,q[1:4])))
g=Geo(w,h,edges);pearls=set();turns=[];turn=None;rnd=-1;actor=None;near=[];minimum=None;queen_positions=Counter();splits=[]
xy=lambda c:[c%w,c//w]
def board(c):
 xs=[(c%w+dx)%w for dx in range(-3,4)];ys=[(c//w+dy)%h for dy in range(-3,4)]
 occ={z:('Q' if i==1 else 'q' if i==0 else 'B' if teams[i] else 'A') if k==0 else ('o' if i==1 else 'b' if teams[i] else 'a') for i,b in bodies.items() for k,z in enumerate(b)}
 lines=[]
 for y in ys:
  lines.append('+'+'+'.join('-' if g.moves[y*w+x][0][0]==1 else ' ' for x in xs)+'+')
  lines.append(''.join(('|' if g.moves[y*w+x][3][0]==1 else ' ')+occ.get(y*w+x,'*' if y*w+x in pearls else '.') for x in xs)+('|' if g.moves[y*w+xs[-1]][1][0]==1 else ' '))
 lines.append('+'+'+'.join('-' if g.moves[ys[-1]*w+x][2][0]==1 else ' ' for x in xs)+'+')
 return dict(xs=xs,ys=ys,ascii='\n'.join(lines),occupants=[dict(id=i,team=teams[i],body=[xy(z) for z in b]) for i,b in bodies.items() if any(z%w in xs and z//w in ys for z in b)])
for idx,ev in enumerate(r.pointer(3)):
 k=ev.u16(0);p=ev.pointer(0)
 if k==0:rnd=p.i32(0);actor=None
 elif k==1:
  actor=p.i32(0);turn=dict(round=rnd,id=actor,event=idx,body=[xy(z) for z in bodies[actor]],actions=[],updates=[],logs=[])
  if 157<=rnd<=162 or actor in (0,1):
   turn['board']=board(bodies[actor][0]);turns.append(turn)
  if 1 not in bodies and 0 in bodies and teams[actor]:
   dist=g.distances(bodies[0][0])[bodies[actor][0]]
   entry=dict(round=rnd,event=idx,id=actor,length=len(bodies[actor]),distance=dist,head=xy(bodies[actor][0]),queen=xy(bodies[0][0]))
   if minimum is None or dist<minimum['distance']:minimum=entry
   if dist<=5:near.append(entry)
  if 1 not in bodies and actor==0:queen_positions[tuple(xy(bodies[0][0]))]+=1
 elif k==3:
  z=lr.replay.point(p.pointer(0));c=z[1]*w+z[0]
  if p.u32(0):pearls.add(c)
  else:pearls.remove(c)
 elif k==4:
  a=p.pointer(0);turn['actions'].append(dict(kind=a.u16(0),dirs=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else [],raw=a.u32(4)))
 elif k==9:
  i=p.i32(0);hd=lr.replay.point(p.pointer(0));tl=lr.replay.point(p.pointer(1));hd=hd[1]*w+hd[0];tl=tl[1]*w+tl[0];b=bodies[i]
  if b[0]!=hd:b.appendleft(hd)
  while len(b)>1 and b[-1]!=tl:b.pop()
  assert b[-1]==tl
  if turn is not None:turn['updates'].append(dict(id=i,body=[xy(z) for z in b]))
 elif k==10:
  splits.append(dict(round=rnd,parent=p.i32(0),child=p.i32(4)))
  for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(pt.i32(4)*w+pt.i32(0) for pt in p.pointer(z));teams[i]=p.u16(8)
 elif k==11:bodies.pop(p.i32(0))
 elif k==6:
  if turn is not None:turn['logs'].append(p.text(0))
result=dict(turns=turns,near=near,minimum=minimum,queen_positions=[dict(xy=k,turns=v) for k,v in queen_positions.items()],splits=splits,final={i:[xy(z) for z in b] for i,b in bodies.items()})
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print('min',minimum,'near turns',len(near),'near ids',sorted({z['id'] for z in near}));print('queen positions',result['queen_positions']);print('queen splits',[s for s in splits if s['parent']==1]);
for t in turns:
 if t['id']==1 and t['round']>=157:
  print(json.dumps({k:v for k,v in t.items() if k!='board'}));print(t['board']['ascii']);print(t['board']['occupants'])
print('EVENTS',lr.replay.EVENT_NAMES)
