import sys,json
from pathlib import Path
from collections import deque,defaultdict
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/work']
from ladder_replay import replay,edge_id,canonical_edges
OUT=Path('data/codex/astra/sweep/1055/loss26')
for gid,bid in [(1512749,1512747),(1507572,1507572),(1507575,1507572)]:
 x=json.loads((OUT/f'{gid}.json').read_text()); qs=x['queens']; own='AB'.index(x['ours']);root=replay.load(f'data/online/live-one1/b{bid}/M{gid}.replay').root()
 lines=root.text(0).splitlines();W,H=map(int,lines[0].split()[1:3]);bodies={};teams={};raw=[];pearls=set()
 for line in lines:
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 edges=canonical_edges(W,H,raw);portals=defaultdict(list)
 for e,(k,p) in edges.items():
  if k==2:portals[p].append(e)
 def dest(c,d):
  e=edge_id(W,H,*c,d);k,p=edges.get(e,(0,-1))
  if k==1:return None
  if k==2:
   partner=next(z for z in portals[p] if z!=e);row,px=divmod(partner,W+1);return ((px-(d==3))%W,(row//2-(d==0))%H)
  dx,dy=((0,-1),(1,0),(0,1),(-1,0))[d];return ((c[0]+dx)%W,(c[1]+dy)%H)
 def board(i):
  h=bodies[i][0];rows=[]
  for dy in range(-3,4):
   row=[]
   for dx in range(-3,4):
    c=((h[0]+dx)%W,(h[1]+dy)%H);ch='o' if c in pearls else '.'
    for j,b in bodies.items():
     if c in b:ch=('Q' if i==j else 'M' if teams[j]==teams[i] else 'E') if c==b[0] else ('b' if i==j else 'm' if teams[j]==teams[i] else 'e')
    wall=''.join('NESW'[d] if edges.get(edge_id(W,H,*c,d),(0,-1))[0]==1 else 'nesw'[d] if edges.get(edge_id(W,H,*c,d),(0,-1))[0]==2 else '' for d in range(4))
    row.append(ch+wall)
   rows.append(row)
  return rows
 rnd=-1;t=None;turns=[];qturns=[];contacts=[];qdeath=None;contexts=[]
 def close():
  if t is not None:
   t['after']={str(i):len(b) for i,b in bodies.items() if i==t['id'] or i in t['children']};turns.append(t)
 def contact():
  if qs['us'] in bodies or qs['them'] not in bodies:return
  target=bodies[qs['them']][0]
  for i,b in bodies.items():
   if teams[i]!=own:continue
   seen={b[0]:0};qu=deque([b[0]])
   while qu:
    c=qu.popleft()
    if c==target:
     contacts.append([rnd,i,seen[c],b[0],target]);return
    if seen[c]>=5:continue
    for d in range(4):
     v=dest(c,d)
     if v is not None and v not in seen:seen[v]=seen[c]+1;qu.append(v)
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0)
  if k not in (0,1,3,4,9,10,11):continue
  p=ev.pointer(0)
  if k==0:close();t=None;rnd=p.i32(0)
  elif k==1:
   close();i=p.i32(0);t=dict(r=rnd,id=i,side=teams[i],body=list(bodies[i]),eats=[],moves=[],children=[],deaths=[])
   if i==qs['us']:
    t['board']=board(i);t['near']={str(j):list(b) for j,b in bodies.items() if abs((b[0][0]-bodies[i][0][0]+W//2)%W-W//2)<=5 and abs((b[0][1]-bodies[i][0][1]+H//2)%H-H//2)<=5};qturns.append(t)
   contact()
  elif k==4:
   a=p.pointer(0);t['action']=a.u16(0) if a else None;t['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
  elif k==3:
   c=replay.point(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:pearls.discard(c);t['eats'].append(c)
  elif k==9:
   i=p.i32(0);hd,tl=replay.point(p.pointer(0)),replay.point(p.pointer(1));b=bodies[i]
   if b[0]!=hd:b.appendleft(hd);t['moves'].append([i,hd])
   while len(b)>1 and b[-1]!=tl:b.pop()
  elif k==10:
   t['split_before']=len(bodies[p.i32(0)]);t['children'].append(p.i32(4))
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:
   i=p.i32(0);t['deaths'].append([i,len(bodies[i]),p.u16(4)])
   if i==qs['us']:contexts.append(dict(r=rnd,bodies={j:list(b) for j,b in bodies.items()},teams=teams.copy()))
   bodies.pop(i)
 close()
 snaps=x['snapshots'];keys=sorted(map(int,snaps));cmp=lambda s:tuple(s[z] for z in ('queen_length','longest','total'))
 last_nonloss=max((r for r in keys if cmp(snaps[str(r)]['us'])>=cmp(snaps[str(r)]['them'])),default=-1)
 result=dict(size=[W,H],queen_turns=qturns,turns=turns,contacts=contacts,death_contexts=contexts,final_bodies={j:list(b) for j,b in bodies.items()},teams=teams,last_nonloss=last_nonloss)
 (OUT/f'{gid}-trace.json').write_text(json.dumps(result))
 print(gid,'last_nonloss',last_nonloss,'q last',[(z['r'],len(z['body']),z['action'],z['dirs'],z['after']) for z in qturns[-4:]],'contacts',contacts[:3],flush=True)
