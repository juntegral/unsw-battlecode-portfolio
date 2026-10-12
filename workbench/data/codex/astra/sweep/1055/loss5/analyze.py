import sys,json
sys.dont_write_bytecode=True
sys.path.insert(0,'tools')
from ladder_replay import replay,scan,edge_id,canonical_edges
from collections import deque,defaultdict,Counter
from pathlib import Path
OUT=Path('data/codex/astra/sweep/1055/loss5')
STEP=((0,-1),(1,0),(0,1),(-1,0))
for gid in (1501677,1501678,1501679):
 path=Path(f'data/online/smoke/one12-c1-old/M{gid}.replay')
 meta=json.loads(path.with_name(f'game-{gid}.json').read_text())
 result=scan(path,meta,'one12-c1-old',set())
 root=replay.load(path).root();W,H=map(int,root.text(0).splitlines()[0].split()[1:3])
 bodies={};teams={};er=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q[0]=='EDGE':er.append(tuple(map(int,q[1:4])))
 edges=canonical_edges(W,H,er);portals=defaultdict(list)
 for e,(k,p) in edges.items():
  if k==2:portals[p].append(e)
 def dest(c,d):
  e=edge_id(W,H,*c,d);k,p=edges.get(e,(0,-1))
  if k==1:return None
  if k==2:
   other=next(z for z in portals[p] if z!=e);row,x=divmod(other,W+1);return ((x-(d==3))%W,(row//2-(d==0))%H)
  dx,dy=STEP[d];return ((c[0]+dx)%W,(c[1]+dy)%H)
 adj={ (x,y):[t for d in range(4) if (t:=dest((x,y),d)) is not None] for y in range(H) for x in range(W)}
 rev=defaultdict(list)
 for a,bs in adj.items():
  for b in bs:rev[b].append(a)
 cache={}
 def distances(to):
  if to not in cache:
   dd={to:0};qq=deque([to])
   while qq:
    c=qq.popleft()
    for n in rev[c]:
     if n not in dd:dd[n]=dd[c]+1;qq.append(n)
   cache[to]=dd
  return cache[to]
 qs=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
 pearls=set();rnd=-1;actor=None;turn=None;turns=[];qturns=[];splits=[];close=[];portalcross=[]
 qd=next((d['round'] for d in result['deaths'] if d['id']==qs[0]),None)
 def finish():
  if turn is not None:
   turn['end']=list(bodies[turn['id']]) if turn['id'] in bodies else []
 def board(c):
  occ={xy:('Q' if i==qs[0] and n==0 else 'K' if i==qs[1] and n==0 else ('A' if teams[i]==0 else 'B') if n==0 else ('a' if teams[i]==0 else 'b')) for i,bb in bodies.items() for n,xy in enumerate(bb)}
  rows=[];walls=[]
  for dy in range(-3,4):
   row=''
   for dx in range(-3,4):
    xy=((c[0]+dx)%W,(c[1]+dy)%H);row+=occ.get(xy,'*' if xy in pearls else '.')
    for d in range(4):
     k,p=edges.get(edge_id(W,H,*xy,d),(0,-1))
     if k:walls.append([dx,dy,'NESW'[d],k,p])
   rows.append(row)
  return dict(rows=rows,edges=walls,near={i:list(bb) for i,bb in bodies.items() if any(min(abs(x-c[0]),W-abs(x-c[0]))<=3 and min(abs(y-c[1]),H-abs(y-c[1]))<=3 for x,y in bb)})
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:finish();turn=None;rnd=p.i32(0)
  elif k==1:
   finish();actor=p.i32(0);head=bodies[actor][0]
   turn=dict(r=rnd,event=idx,id=actor,side=teams[actor],body=list(bodies[actor]),moves=[],eats=[],actions=[],units=sum(teams[i]==teams[actor] for i in bodies))
   turns.append(turn)
   if actor==qs[0]:turn['board']=board(head);qturns.append(turn)
   if qs[0] not in bodies and qs[1] in bodies and teams[actor]==0:
    dis=distances(bodies[qs[1]][0]);d=dis.get(head,9999)
    close.append(dict(r=rnd,id=actor,d=d,head=head,qhead=bodies[qs[1]][0],L=len(bodies[actor]),qL=len(bodies[qs[1]])))
  elif k==3:
   c=replay.point(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c);turn['eats'].append(c)
  elif k==4:
   a=p.pointer(0);turn['actions'].append(dict(kind=a.u16(0),dirs=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else []))
  elif k==9:
   i=p.i32(0);h=replay.point(p.pointer(0));tail=replay.point(p.pointer(1));b=bodies[i]
   if h!=b[0]:
    if i==actor:
     turn['moves'].append(h)
     if any(edges.get(edge_id(W,H,*b[0],d),(0,-1))[0]==2 and dest(b[0],d)==h for d in range(4)):portalcross.append([rnd,i,teams[i],list(b[0]),h])
    b.appendleft(h)
   while len(b)>1 and b[-1]!=tail:b.pop()
  elif k==10:
   i,ch=p.i32(0),p.i32(4);splits.append([rnd,i,ch,len(bodies[i])])
   for z,n in enumerate((i,ch)):bodies[n]=deque(replay.point(c) for c in p.pointer(z));teams[n]=p.u16(8)
  elif k==11:bodies.pop(p.i32(0))
 finish()
 result['dimensions']=[W,H];result['queen_last_turns']=qturns[-3:];result['queen_turns']=qturns;result['close_after_qdeath']=close;result['splits_ids']=splits;result['portal_crossings']=portalcross
 # Terrain-only shortest path ignores bodies; record turn starts and movement endpoints for proximity.
 result['turns']=turns
 result.pop('intervals');result.pop('natural');result.pop('text')
 (OUT/f'{gid}.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')))
 print(gid,'final',result['final'],'qdeath',[d for d in result['deaths'] if d['id'] in qs],flush=True)
 print('near after death',min(close,key=lambda x:x['d']) if close else None,flush=True)
 print('last queen turns',[(t['r'],t['body'],t['moves'],t['actions']) for t in qturns[-3:]],flush=True)
 print('q eats',result['q_eats'],'q splits',result['q_splits'],'endround',rnd,flush=True)
