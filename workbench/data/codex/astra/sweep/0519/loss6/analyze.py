import sys,json
sys.dont_write_bytecode=True
sys.path.insert(0,'tools')
import ladder_replay as lr
from collections import deque,defaultdict
from pathlib import Path
OUT=Path(__file__).parent
RP=Path('data/online/smoke/one10-c1-old/M1492104.replay')
j=json.loads(RP.with_name('game-1492104.json').read_text())
x=lr.scan(RP,j,'one10-c1-old',set())
x.pop('intervals')
(OUT/'ledger.json').write_text(json.dumps(x,ensure_ascii=False))
root=lr.replay.load(RP).root(); text=root.text(0); W,H=map(int,text.splitlines()[0].split()[1:3]); bodies={};teams={};raw=[]
for line in text.splitlines():
 q=line.split()
 if q and q[0]=='DRAGON':
  i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(q[1])
 elif q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
edges=lr.canonical_edges(W,H,raw); portals=defaultdict(list)
for e,(k,p) in edges.items():
 if k==2:portals[p].append(e)
def dest(h,d):
 e=lr.edge_id(W,H,*h,d);kind,pid=edges.get(e,(0,-1))
 if kind==1:return None
 if kind==2:
  pe=next(z for z in portals[pid] if z!=e);row,px=divmod(pe,W+1)
  return ((px-(d==3))%W,(row//2-(d==0))%H)
 dx,dy=((0,-1),(1,0),(0,1),(-1,0))[d];return ((h[0]+dx)%W,(h[1]+dy)%H)
adj={};rev=defaultdict(list)
for y in range(H):
 for xx in range(W):
  c=(xx,y);adj[c]=[v for d in range(4) if (v:=dest(c,d)) is not None]
  for v in adj[c]:rev[v].append(c)
def bfs(start,graph):
 dist={start:0};todo=deque([start])
 while todo:
  c=todo.popleft()
  for v in graph[c]:
   if v not in dist:dist[v]=dist[c]+1;todo.append(v)
 return dist
cache={}
def distances(q):
 if q not in cache:cache[q]=bfs(q,rev)
 return cache[q]
def visible(a,b):return min(abs(a[0]-b[0]),W-abs(a[0]-b[0]))<=3 and min(abs(a[1]-b[1]),H-abs(a[1]-b[1]))<=3
pearls=set();turns=[];snaps={};near=[];minrow=None;post_positions=set();minman=None;round=-1;actor=None;turn=None
for idx,ev in enumerate(root.pointer(3)):
 kind=ev.u16(0);p=ev.pointer(0)
 if kind==0:round=p.i32(0)
 elif kind==1:
  actor=p.i32(0);turn={'round':round,'event':idx,'actor':actor,'body':list(bodies[actor]),'action':None,'steps':[],'eats':[],'deaths':[]};turns.append(turn)
  if actor==0 or (183<=round<=187 and actor==104):
   turn['state']={i:list(b) for i,b in bodies.items()};turn['pearls']=list(pearls)
 elif kind==4:
  a=p.pointer(0);turn['action']={'kind':a.u16(0),'dirs':list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) else []}
 elif kind==3:
  c=lr.replay.point(p.pointer(0))
  if p.u32(0):pearls.add(c)
  else:pearls.discard(c);turn['eats'].append(c)
 elif kind==9:
  i=p.i32(0);h=lr.replay.point(p.pointer(0));tail=lr.replay.point(p.pointer(1));b=bodies[i]
  if b[0]!=h:b.appendleft(h);turn['steps'].append({'id':i,'head':h})
  while len(b)>1 and b[-1]!=tail:b.pop()
  assert b[-1]==tail
 elif kind==10:
  for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(lr.replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
 elif kind==11:
  i=p.i32(0);turn['deaths'].append({'id':i,'reason':p.u16(4),'body':list(bodies[i])});bodies.pop(i)
 if kind in (0,9,10,11) and 0 not in bodies and 1 in bodies:
  q=bodies[1][0];post_positions.add(q);dist=distances(q)
  for i,b in bodies.items():
   if teams[i]!=0:continue
   dx=abs(b[0][0]-q[0]);dy=abs(b[0][1]-q[1]);man=min(dx,W-dx)+min(dy,H-dy)
   mr={'round':round,'event':idx,'id':i,'head':b[0],'queen':q,'distance':man}
   if minman is None or man<minman['distance']:minman=mr
   row={'round':round,'event':idx,'id':i,'length':len(b),'head':b[0],'queen':q,'distance':dist.get(b[0],9999)}
   if minrow is None or row['distance']<minrow['distance']:minrow=row
   if row['distance']<=5:near.append(row)
 if kind==0 and round in (184,185,186,187,200,300,400,499):snaps[round]={i:list(b) for i,b in bodies.items()}
qturns=[t for t in turns if t['actor']==0]
selected=[t for t in turns if (t['actor']==0 and t['round']>=183) or (t['actor']==104 and 183<=t['round']<=186)]
result={'width':W,'height':H,'teams':teams,'selected':selected,'last3':qturns[-3:],'min_manhattan':minman,'nearest_after_death':minrow,'within5_states':len(near),'near_first':near[:5],'near_last':near[-5:],'queen_positions_after_death':sorted(post_positions),'snapshots':snaps}
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False))
print(json.dumps({k:v for k,v in result.items() if k not in ('teams','selected','last3','snapshots','queen_positions_after_death')}))
for t in selected:
 print(json.dumps({k:v for k,v in t.items() if k not in ('state','pearls')}))
 if 'state' in t:
  h=t['body'][0];print('VISIBLE',[(i,len(b),b[0],sum(visible(h,c) for c in b)) for i,b in t['state'].items() if visible(h,b[0])])
print('queen post positions',sorted(post_positions))
# 7x7 tiles plus edge tables keep walls separate from tile occupancy.
lines=[]
for t in qturns[-3:]:
 h=t['body'][0];occ={tuple(c):(i,k) for i,b in t['state'].items() for k,c in enumerate(b)};pp=set(map(tuple,t['pearls']))
 lines.append(f"r{t['round']} head {h}, action {t['action']}")
 for dy in range(-3,4):
  s=''
  for dx in range(-3,4):
   c=((h[0]+dx)%W,(h[1]+dy)%H);mark='*' if c in pp else '.'
   if c in occ:
    i,k=occ[c];mark=('Q' if k==0 else 'q') if i==0 else ('X' if k==0 else 'x') if i==104 else ('A' if k==0 else 'a') if teams[i]==0 else ('E' if k==0 else 'e')
   s+=mark
  lines.append(s)
 lines.append('Head edges N/E/S/W: '+str([(edges.get(lr.edge_id(W,H,*h,d),(0,-1)),dest(h,d)) for d in range(4)]))
 lines.append('')
(OUT/'boards.txt').write_text('\n'.join(lines));print('\n'.join(lines))

print('graph',len(bfs((9,11),adj)),len(bfs((22,6),adj)),len(bfs((30,12),rev)), 'reach queen',distances((30,12)).get((22,6)))
print('q starts',[(t['round'],t['body'][0]) for t in turns if t['actor']==1 and t['round'] in (186,200,300,400,499)])
mismatch=[];move_count=0
for t in turns:
 h=tuple(t['body'][0]); dirs=(t['action'] or {}).get('dirs',[]);n=0
 for step in t['steps']:
  if step['id']!=t['actor']:continue
  target=tuple(step['head']);d=dirs[n];n+=1;move_count+=1
  if dest(h,d)!=target:mismatch.append([t['round'],t['actor'],h,d,dest(h,d),target])
  h=target
print('movement validation',move_count,'mismatches',len(mismatch),mismatch[:3])
comp=bfs((30,12),rev)
print('all enemy queen post in component',all(c in comp for c in post_positions))
print('last snapshot',snaps[499])
for t in selected:
 if t['round']==186 and t['actor'] in (0,104):
  occ={tuple(c):i for i,b in t['state'].items() for c in b};h=tuple(t['body'][0]);details=[]
  for d in range(4):
   n=dest(h,d);details.append({'dir':d,'dest':n,'occupant':occ.get(n),'edge':edges.get(lr.edge_id(W,H,*h,d),(0,-1))})
  print('last options',t['actor'],details)
  if t['actor']==0:
   start=(9,10);graph={c:[v for v in vs if v not in occ] for c,vs in adj.items()};print('queen north static room',len(bfs(start,graph)))
seen=set();found=[]
for t in turns:
 if t['actor']!=104:continue
 h=tuple(t['body'][0]);seen.update(((h[0]+dx)%W,(h[1]+dy)%H) for dx in range(-3,4) for dy in range(-3,4))
 if visible(h,(9,11)) or visible(h,(8,11)):found.append((t['round'],h))
print('104 observed queen portal mouth before death',found)
(OUT/'validation.json').write_text(json.dumps({'move_count':move_count,'move_mismatches':mismatch,'queen_component_size':len(comp),'queen_post_stays_component':all(c in comp for c in post_positions),'104_mouth_observations':found}))
