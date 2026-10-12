import sys,json
from pathlib import Path
from collections import deque,Counter
sys.dont_write_bytecode=True
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'data/analysis/ladder/dossier/local')]
import ladder_replay as lr
from scoreboard import load_replay
from count_local import Geo
GAMES=[(1497633,'b1497630'),(1497386,'b1497386'),(1497387,'b1497386')]
for gid,folder in GAMES:
 root=load_replay(ROOT/'data/online/live-one1'/folder/f'M{gid}.replay').root();base=json.loads((OUT/f'{gid}-base.json').read_text());own='AB'.index(base['ours']); w,h=map(int,root.text(0).splitlines()[0].split()[1:3]);bodies={};teams={};raw=[]
 for line in root.text(0).splitlines():
  v=line.split()
  if v[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(v[4+2*k])*w+int(v[3+2*k]) for k in range(int(v[2])));teams[i]=int(v[1])
  elif v[0]=='EDGE':raw.append(tuple(map(int,v[1:4])))
 g=Geo(w,h,raw);oq=base['queens']['us'];eq=base['queens']['them']; qd=next(d for d in base['deaths'] if d['id']==oq);r=-1;actor=None;cur=None;turns=[];pearls=set();qboards=[];near=[];minimum=None;distances={};per_round={}
 def bfs(src):
  if src not in distances:
   dd={src:0};todo=deque([src])
   while todo:
    a=todo.popleft()
    for b in g.adj[a]:
     if b not in dd:dd[b]=dd[a]+1;todo.append(b)
   distances[src]=dd
  return distances[src]
 def nearcheck(idx):
  global minimum
  if oq in bodies or eq not in bodies:return
  for i,b in bodies.items():
   if teams[i]!=own:continue
   d=bfs(b[0]).get(bodies[eq][0],99999)
   item=dict(round=r,event=idx,id=i,head=b[0],queen=bodies[eq][0],distance=d)
   if minimum is None or d<minimum['distance']:minimum=item
   if d<=5 and (not near or (r,i,b[0],bodies[eq][0]) != tuple(near[-1][k] for k in ('round','id','head','queen'))):near.append(item)
 def close():
  if cur is not None:
   cur['end']=list(bodies.get(actor,[]));turns.append(cur)
 def board():
  cx,cy=bodies[oq][0]%w,bodies[oq][0]//w
  occ={c: ('Q' if i==oq else 'X' if i==qd['actor'] else 'A' if teams[i]==own else 'E') if j==0 else ('q' if i==oq else 'x' if i==qd['actor'] else 'a' if teams[i]==own else 'e') for i,b in bodies.items() for j,c in enumerate(b)}
  lines=[]
  for dy in range(-3,4):
   row='';top=''
   for dx in range(-3,4):
    c=((cy+dy)%h)*w+(cx+dx)%w
    top+='+'+('-' if g.moves[c][0][0]==1 else 'P' if g.moves[c][0][0]==2 else ' ')
    row+=('|' if g.moves[c][3][0]==1 else 'P' if g.moves[c][3][0]==2 else ' ')+occ.get(c,'*' if c in pearls else '.')
   c=((cy+dy)%h)*w+(cx+3)%w
   lines.extend([top+'+',row+('|' if g.moves[c][1][0]==1 else 'P' if g.moves[c][1][0]==2 else ' ')])
  lines.append(''.join('+'+('-' if g.moves[((cy+3)%h)*w+(cx+dx)%w][2][0]==1 else 'P' if g.moves[((cy+3)%h)*w+(cx+dx)%w][2][0]==2 else ' ') for dx in range(-3,4))+'+')
  return '\n'.join(lines)
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:close();cur=None;r=p.i32(0);actor=None
  elif k==1:
   close();actor=p.i32(0);cur=dict(round=r,event=idx,id=actor,side=teams[actor],start=list(bodies[actor]),moves=[],eats=[],splits=[],deaths=[])
   if actor==oq and r<=qd['round']:
    qboards.append(dict(round=r,event=idx,body=list(bodies[oq]),bodies={i:list(b) for i,b in bodies.items()},board=board(),pearls=list(pearls)));qboards=qboards[-3:]
   if actor==eq:cur['our_nearest']=min(((bfs(b[0]).get(bodies[eq][0],99999),i,b[0]) for i,b in bodies.items() if teams[i]==own),default=None)
  elif k==4:
   a=p.pointer(0);cur['action_kind']=a.u16(0);cur['dirs']=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) else [];cur['split_n']=a.i32(4) if a.u16(0)==1 else None
  elif k==3:
   x,y=lr.replay.point(p.pointer(0));c=y*w+x
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c);cur['eats'].append(c)
  elif k==9:
   i=p.i32(0);x,y=lr.replay.point(p.pointer(0));hd=y*w+x;x,y=lr.replay.point(p.pointer(1));tail=y*w+x;b=bodies[i]
   if b[0]!=hd:
    if i==actor:cur['moves'].append(hd)
    b.appendleft(hd)
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
  elif k==10:
   cur['splits'].append([p.i32(0),p.i32(4)])
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(lr.replay.point(pt)[1]*w+lr.replay.point(pt)[0] for pt in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:
   i=p.i32(0);cur['deaths'].append(dict(id=i,reason=p.u16(4),body=list(bodies[i])));bodies.pop(i)
  if k in (1,9,10,11):nearcheck(idx)
 close()
 result=dict(w=w,h=h,own=own,teams=teams,qboards=qboards,turns=turns,near=near,minimum=minimum,final_bodies={i:list(b) for i,b in bodies.items()})
 (OUT/f'{gid}-trace.json').write_text(json.dumps(result))
 print(gid,'minimum',minimum,'near records',len(near),'unique turns',len(set((n['round'],n['id']) for n in near)))
 print('LAST Q TURNS',[(t['round'],t['start'],t['moves'],t.get('dirs'),t['eats']) for t in turns if t['id']==oq][-3:])
 print('ATTACK',[(t['round'],t['id'],t['start'],t['moves'],t.get('dirs'),t['eats'],t['deaths']) for t in turns if t['round']==qd['round'] and t['id']==qd['actor']])
 print('FINAL',[(i,len(b),b[0]) for i,b in bodies.items()])
