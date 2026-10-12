import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path[:0]=['tools','data/analysis/ladder/dossier/work']
import ladder_replay as lr
import ast
_geo=ast.parse(Path('data/analysis/ladder/dossier/work/tq2_chase.py').read_text())
_geo.body=[n for n in _geo.body if not isinstance(n,ast.Expr)]
_ns={}
exec(compile(_geo,'tq2_chase.py','exec'),_ns)
Geo=_ns['Geo']
OUT=Path(__file__).parent

def run(gid):
 root=lr.replay.load(Path(f'data/online/smoke/one8-c2-old/M{gid}.replay')).root()
 W,H=map(int,root.text(0).splitlines()[0].split()[1:3]); bodies={};teams={};raw=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if q and q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(q[4+2*k])*W+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
 geo=Geo(W,H,raw);pearls=set();rnd=-1;actor=None;turn=None;turns=[];qturns=[];dead=[];near=[];snaps={};postchecks=0;postmin=999999;posthits=[];qpositions=set();distcache={};splits=[]
 def xy(c):return [c%W,c//W]
 def snap():return {str(i):{'side':teams[i],'L':len(b),'head':xy(b[0])} for i,b in bodies.items()}
 def proximity():
  nonlocal postchecks,postmin
  if queens[0] in bodies or queens[1] not in bodies:return
  q=bodies[queens[1]][0];qpositions.add(q)
  if q not in distcache:
   rev=[[] for _ in range(W*H)]
   for c,ns in enumerate(geo.nxt):
    for n in ns:
     if n>=0:rev[n].append(c)
   dist={q:0};queue=deque([q])
   while queue:
    c=queue.popleft()
    for n in rev[c]:
     if n not in dist:dist[n]=dist[c]+1;queue.append(n)
   distcache[q]=dist
  ds=[(distcache[q].get(b[0],999999),i) for i,b in bodies.items() if teams[i]==0]
  postchecks+=1
  d,i=min(ds,default=(999999,-1));postmin=min(postmin,d)
  if d<=5:posthits.append([rnd,idx,i,d,xy(q)])
 def close():
  if turn is not None:
   turn['end']=list(bodies.get(actor,[]));turns.append(turn)
 def board(center):
  lines=[]; occ={c:('Q' if i==queens[0] and n==0 else 'q' if i==queens[0] else 'K' if i==queens[1] and n==0 else 'A' if teams[i]==0 and n==0 else 'a' if teams[i]==0 else 'B' if n==0 else 'b') for i,b in bodies.items() for n,c in enumerate(b)}
  cx,cy=center%W,center//W
  for dy in range(-3,4):
   cells=[((cy+dy)%H)*W+(cx+dx)%W for dx in range(-3,4)]
   lines.append(''.join('+'+('-' if geo.edges.get(lr.edge_id(W,H,c%W,c//W,0),(0,-1))[0]==1 else 'P' if geo.edges.get(lr.edge_id(W,H,c%W,c//W,0),(0,-1))[0]==2 else ' ') for c in cells)+'+')
   lines.append(''.join(('|' if geo.edges.get(lr.edge_id(W,H,c%W,c//W,3),(0,-1))[0]==1 else 'P' if geo.edges.get(lr.edge_id(W,H,c%W,c//W,3),(0,-1))[0]==2 else ' ')+occ.get(c,'*' if c in pearls else '.') for c in cells)+('|' if geo.edges.get(lr.edge_id(W,H,cells[-1]%W,cells[-1]//W,1),(0,-1))[0]==1 else 'P' if geo.edges.get(lr.edge_id(W,H,cells[-1]%W,cells[-1]//W,1),(0,-1))[0]==2 else ' '))
  cells=[((cy+3)%H)*W+(cx+dx)%W for dx in range(-3,4)]
  lines.append(''.join('+'+('-' if geo.edges.get(lr.edge_id(W,H,c%W,c//W,2),(0,-1))[0]==1 else 'P' if geo.edges.get(lr.edge_id(W,H,c%W,c//W,2),(0,-1))[0]==2 else ' ') for c in cells)+'+')
  return '\n'.join(lines)
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   close();turn=None
   if rnd>=0:snaps[rnd]=snap()
   rnd=p.i32(0);actor=None
  elif k==1:
   close();actor=p.i32(0)
   turn={'r':rnd,'event':idx,'id':actor,'side':teams[actor],'body':list(bodies[actor]),'action':None,'steps':[],'eats':[],'deaths':[]}
   if actor==queens[0]:
    turn['board']=board(bodies[actor][0]);turn['state']=snap();turn['bodies']={str(i):list(b) for i,b in bodies.items()};turn['pearls']=list(pearls)
    turn['neighbors']=[{'direction':'NESW'[d],'tile':xy(c) if c>=0 else 'wall','occupants':[i for i,b in bodies.items() if c in b],'portal':geo.por[bodies[actor][0]][d]} for d,c in enumerate(geo.nxt[bodies[actor][0]])]
    qturns.append(turn)
   if queens[0] not in bodies and queens[1] in bodies and teams[actor]==0:
    q=bodies[queens[1]][0]; dist=geo.ball(bodies[actor][0]).get(q,99)
    if dist<=5:near.append({'r':rnd,'id':actor,'L':len(bodies[actor]),'head':xy(bodies[actor][0]),'qhead':xy(q),'distance':dist})
  elif k==3:
   pt=lr.replay.point(p.pointer(0));c=pt[1]*W+pt[0]
   if p.u32(0):pearls.add(c)
   else:
    pearls.discard(c)
    if turn is not None:turn['eats'].append(c)
  elif k==4:
   a=p.pointer(0)
   turn['action']={'kind':a.u16(0),'dirs':list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) else [],'split':a.i32(4)}
  elif k==9:
   i=p.i32(0);h,t=[lr.replay.point(p.pointer(z)) for z in (0,1)];h=h[1]*W+h[0];t=t[1]*W+t[0];b=bodies[i]
   if b[0]!=h:b.appendleft(h);turn['steps'].append(h)
   while len(b)>1 and b[-1]!=t:b.pop()
   assert b[-1]==t
  elif k==10:
   splits.append({'r':rnd,'parent':p.i32(0),'child':p.i32(4),'lengths':[len(p.pointer(z)) for z in (0,1)]})
   for z,i in enumerate((p.i32(0),p.i32(4))):
    bodies[i]=deque(pt[1]*W+pt[0] for pt in map(lr.replay.point,p.pointer(z)));teams[i]=p.u16(8)
  elif k==11:
   i=p.i32(0);row={'id':i,'r':rnd,'event':idx,'reason':p.u16(4),'actor':actor,'body':list(bodies[i])};dead.append(row);turn['deaths'].append(row);bodies.pop(i)
  if k in (9,10,11):proximity()
 close();snaps[rnd]=snap()
 result={'gid':gid,'W':W,'H':H,'bot':root.text(1),'queens':queens,'qturns':qturns,'near':near,'dead':dead,'final':snap(),'snapshots':snaps,'splits':splits,'proximity':{'checks':postchecks,'min':postmin,'hits':posthits,'qpositions':[xy(c) for c in sorted(qpositions)]}}
 (OUT/f'{gid}-detail.json').write_text(json.dumps(result))
 (OUT/f'{gid}-turns.json').write_text(json.dumps(turns))
 print(gid,'queens',queens,'final',snap(),'postqueen near',len(near),'first',near[:3])
 print('proximity',result['proximity'])

if __name__=='__main__':
 for gid in (1493890,1493891):run(gid)
