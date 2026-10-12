import sys,json
sys.dont_write_bytecode=True
sys.path.insert(0,'tools')
import ladder_replay as lr
from pathlib import Path
from collections import deque,defaultdict
OUT=Path(__file__).parent
FOLDER=Path('data/online/smoke/one8-p1-old')
STEP=((0,-1),(1,0),(0,1),(-1,0))
def run(gid):
 meta=json.loads((FOLDER/f'game-{gid}.json').read_text())
 raw=lr.scan(FOLDER/f'M{gid}.replay',meta,str(FOLDER),set());raw.pop('intervals')
 (OUT/f'{gid}-scan.json').write_text(json.dumps(raw))
 root=lr.replay.load(FOLDER/f'M{gid}.replay').root()
 lines=root.text(0).splitlines(); W,H=map(int,lines[0].split()[1:3]);bodies={};teams={};edges=[]
 for line in lines:
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(q[1])
  if q[0]=='EDGE': edges.append(tuple(map(int,q[1:4])))
 edges=lr.canonical_edges(W,H,edges);ports=defaultdict(list)
 for e,(k,p) in edges.items():
  if k==2:ports[p].append(e)
 def dest(c,d):
  x,y=c;e=lr.edge_id(W,H,x,y,d);k,p=edges.get(e,(0,-1))
  if k==1:return None
  if k==2:
   other=next(z for z in ports[p] if z!=e);row,x=divmod(other,W+1);y=row//2
   return ((x-(d==3))%W,(y-(d==0))%H)
  dx,dy=STEP[d];return ((x+dx)%W,(y+dy)%H)
 rev=defaultdict(list)
 for y in range(H):
  for x in range(W):
   for d in range(4):
    n=dest((x,y),d)
    if n is not None:rev[n].append((x,y))
 cache={}
 def distances(target):
  if target not in cache:
   seen={target:0};q=deque([target])
   while q:
    c=q.popleft()
    for n in rev[c]:
     if n not in seen:seen[n]=seen[c]+1;q.append(n)
   cache[target]=seen
  return cache[target]
 def board(i):
  h=bodies[i][0]; grid=[]
  for dy in range(-3,4):
   row=[]
   for dx in range(-3,4):
    c=((h[0]+dx)%W,(h[1]+dy)%H); ch='o' if c in pearls else '.'
    for z,b in bodies.items():
     if c in b:ch=('Q' if z==i else 'M' if teams[z]==0 else 'E') if c==b[0] else ('b' if z==i else 'm' if teams[z]==0 else 'e')
    walls=''.join('NESW'[d] if edges.get(lr.edge_id(W,H,*c,d),(0,-1))[0]==1 else 'nesw'[d] if edges.get(lr.edge_id(W,H,*c,d),(0,-1))[0]==2 else '' for d in range(4))
    row.append(ch+walls)
   grid.append(row)
  return grid
 def view(c,h):return min((c[0]-h[0])%W,(h[0]-c[0])%W)<=3 and min((c[1]-h[1])%H,(h[1]-c[1])%H)<=3
 queens=raw['queens']; qid=queens['us'];eq=queens['them']; pearls=set();rnd=-1;actor=None;turn=None;turns=[];qturns=[];near=[];qpos={};minimum=None;event_minimum=None
 def close():
  if turn is not None:turn['end']=list(bodies.get(actor,[]))
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:close();turn=None;rnd=p.i32(0)
  elif k==1:
   close();actor=p.i32(0);turn={'r':rnd,'i':actor,'event':idx,'body':list(bodies[actor]),'steps':[],'eats':[],'splits':[],'deaths':[]};turns.append(turn)
   if actor==qid or (gid==1494955 and actor==1209 and rnd>=480):
    turn['board']=board(actor);turn['others']={i:list(b) for i,b in bodies.items() if i!=actor and any(view(c,bodies[actor][0]) for c in b)}
    if actor==qid:qturns.append(turn)
   if qid not in bodies and eq in bodies:
    h=bodies[eq][0];dd=distances(h);qpos[rnd]=h
    choices=sorted((dd.get(b[0],99999),i,b[0],len(b)) for i,b in bodies.items() if teams[i]==0)
    if choices:
     record=[rnd,idx,*choices[0],h]
     if minimum is None or record[2]<minimum[2]:minimum=record
    if teams[actor]==0 and dd.get(bodies[actor][0],99999)<=5:near.append([rnd,actor,dd[bodies[actor][0]],bodies[actor][0],len(bodies[actor]),h,idx])
  elif k==4:
   a=p.pointer(0);turn['action']={'kind':a.u16(0) if a else None,'dirs':list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []}
  elif k==3:
   c=lr.replay.point(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:pearls.discard(c);turn['eats'].append(c)
  elif k==9:
   i=p.i32(0);h=lr.replay.point(p.pointer(0));t=lr.replay.point(p.pointer(1));b=bodies[i]
   if b[0]!=h:b.appendleft(h);turn['steps'].append([i,h])
   while len(b)>1 and b[-1]!=t:b.pop()
  elif k==10:
   ids=(p.i32(0),p.i32(4));turn['splits'].append(ids)
   for z,i in enumerate(ids):bodies[i]=deque(lr.replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:
   i=p.i32(0);turn['deaths'].append([i,p.u16(4)]);bodies.pop(i)
  if k in (9,10,11) and qid not in bodies and eq in bodies:
   h=bodies[eq][0];dd=distances(h)
   choices=sorted((dd.get(b[0],99999),i,b[0],len(b)) for i,b in bodies.items() if teams[i]==0)
   if choices and (event_minimum is None or choices[0][0]<event_minimum[2]):event_minimum=[rnd,idx,*choices[0],h]
 close()
 data={'W':W,'H':H,'queens':queens,'qturns':qturns,'turns':turns,'near':near,'minimum':minimum,'event_minimum':event_minimum,'enemy_positions':qpos,'final_bodies':bodies,'teams':teams}
 data['final_bodies']={i:list(b) for i,b in bodies.items()}
 (OUT/f'{gid}-detail.json').write_text(json.dumps(data))
 print(gid,'lastq',qturns[-3:],'near_n',len(near),'minimum',minimum,'firstnear',near[:3])
 print('long deaths after400',[d for d in raw['deaths'] if d['round']>=400 and d['length']>=15])
if __name__=='__main__':
 for gid in [1494953,1494954,1494955]:run(gid)
