import sys,json,importlib.util
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,defaultdict
ROOT=Path.cwd(); OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('weak',ROOT/'data/codex/astra/weak/analyze.py'); weak=importlib.util.module_from_spec(spec);spec.loader.exec_module(weak)
replay=weak.replay
for gid,bid in [(1516988,1516986),(1516990,1516986),(1516554,1516554)]:
 folder=ROOT/f'data/online/live-one1/b{bid}'; path=folder/f'M{gid}.replay';m=json.loads((folder/f'game-{gid}.json').read_text())
 base=weak.extra(path,m);root=replay.load(path).root(); bodies={};teams={};raw=[]
 lines=root.text(0).splitlines();W,H=map(int,lines[0].split()[1:3])
 for line in lines:
  p=line.split()
  if p[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque((int(p[3+2*k]),int(p[4+2*k])) for k in range(int(p[2])));teams[i]=int(p[1])
  elif p[0]=='EDGE':raw.append(tuple(map(int,p[1:4])))
 edges=weak.canonical_edges(W,H,raw);ports=defaultdict(list)
 for e,(k,p) in edges.items():
  if k==2:ports[p].append(e)
 def dest(c,d):
  e=weak.edge_id(W,H,*c,d);k,p=edges.get(e,(0,-1))
  if k==1:return None
  if k==2:
   z=next(x for x in ports[p] if x!=e);y,x=divmod(z,W+1);return ((x-(d==3))%W,(y//2-(d==0))%H)
  dx,dy=((0,-1),(1,0),(0,1),(-1,0))[d];return ((c[0]+dx)%W,(c[1]+dy)%H)
 adj={(x,y):[v for d in range(4) if (v:=dest((x,y),d)) is not None] for y in range(H) for x in range(W)}
 distcache={}
 def distances(c):
  if c not in distcache:
   dd={c:0};q=deque([c])
   while q:
    a=q.popleft()
    for b in adj[a]:
     if b not in dd:dd[b]=dd[a]+1;q.append(b)
   distcache[c]=dd
  return distcache[c]
 def visible(a,b):
  dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1]);return min(dx,W-dx)<=3 and min(dy,H-dy)<=3
 def board(c):
  occ={v:('Q' if i==base['queens'][0] else 'K' if i==base['queens'][1] else 'A' if teams[i]==1 else 'E') if j==0 else ('q' if i==base['queens'][0] else 'k' if i==base['queens'][1] else 'a' if teams[i]==1 else 'e') for i,b in bodies.items() for j,v in enumerate(b)}
  cells=[];ed=[]
  for y in range(c[1]-3,c[1]+4):
   row=[];er=[]
   for x in range(c[0]-3,c[0]+4):
    p=(x%W,y%H);row.append(occ.get(p,'*' if p in pearls else '.'));er.append(''.join('NESW'[d] for d in range(4) if dest(p,d) is None) or '-')
   cells.append(''.join(row));ed.append(er)
  return dict(rows=cells,walls=ed,origin=[(c[0]-3)%W,(c[1]-3)%H])
 turns=[];pearls=set();cur=None;r=-1;post=[];qdead=False
 def finish():
  global cur
  if cur:
   cur['end']=list(bodies[cur['id']]) if cur['id'] in bodies else [];turns.append(cur);cur=None
 for ix,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k in (0,1):finish()
  if k==0:r=p.i32(0)
  elif k==1:
   i=p.i32(0);h=bodies[i][0]
   cur=dict(r=r,id=i,team=teams[i],body=list(bodies[i]),action=None,logs=[],eats=0,opts=[dict(d='NESW'[d],to=dest(h,d),owner=next((z for z,b in bodies.items() if dest(h,d) in b),None)) for d in range(4)])
   if i==base['queens'][0]:cur['board']=board(h);cur['others']={z:list(b) for z,b in bodies.items() if z!=i and any(visible(h,c) for c in b)}
   if qdead and teams[i]==1 and base['queens'][1] in bodies:
    eq=bodies[base['queens'][1]][0];dd=distances(h).get(eq,9999)
    if dd<=5:post.append(dict(r=r,id=i,L=len(bodies[i]),head=h,eq=eq,d=dd))
  elif k==4:
   a=p.pointer(0);ak=a.u16(0) if a else 2;cur['action']=[ak,list(a.pointer(0)) if ak==0 and a.pointer(0) is not None else a.i32(4) if ak==1 else None]
  elif k in (5,6):
   if cur:cur['logs'].append(p.text(0))
  elif k==3:
   c=replay.point(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:pearls.discard(c);cur['eats']+=1
  elif k==9:
   i=p.i32(0);h,t=replay.point(p.pointer(0)),replay.point(p.pointer(1));b=bodies[i]
   if b[0]!=h:b.appendleft(h)
   while len(b)>1 and b[-1]!=t:b.pop()
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:
   i=p.i32(0);qdead|=i==base['queens'][0];bodies.pop(i)
 finish()
 output=dict(meta=m,bots=[root.text(1),root.text(2)],W=W,H=H,base=base,turns=turns,post=post,final={i:list(b) for i,b in bodies.items()})
 (OUT/f'{gid}.json').write_text(json.dumps(output,separators=(',',':')))
 print(gid,output['bots'],'q',base['queens'],'final',base['all_snapshots'][max(base['all_snapshots'])],'turn',base['decisive_retrospective'],'qdeath',[(d['id'],d['r'],d['reason'],d['actor']) for d in base['deaths'] if d['queen']],'post',len(post),post[:2],flush=True)
