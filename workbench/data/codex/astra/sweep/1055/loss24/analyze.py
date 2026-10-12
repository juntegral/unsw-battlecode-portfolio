import sys,json
sys.dont_write_bytecode=True
sys.path.insert(0,'data/analysis/ladder/dossier/work')
from o1_scan import replay,canonical_edges,edge_id,STEP
sys.path.insert(0,'data/analysis/ladder/dossier/local')
from scoreboard import load_replay
from collections import deque,defaultdict
from pathlib import Path
OUT=Path(__file__).parent

def scan(gid):
 root=load_replay(Path(f'data/online/smoke/one13-c2-old/M{gid}.replay')).root()
 lines=root.text(0).splitlines();W,H=map(int,lines[0].split()[1:3]);bodies={};teams={};raw=[]
 for line in lines:
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 queens=[min(i for i in teams if teams[i]==s) for s in (0,1)]
 edges=canonical_edges(W,H,raw);portals=defaultdict(list)
 for e,(k,p) in edges.items():
  if k==2:portals[p].append(e)
 def dest(c,d):
  e=edge_id(W,H,*c,d);k,p=edges.get(e,(0,-1))
  if k==1:return None
  if k==2:
   z=next(z for z in portals[p] if z!=e);row,x=divmod(z,W+1);y=row//2
   return ((x-(d==3))%W,(y-(d==0))%H)
  dx,dy=STEP[d];return ((c[0]+dx)%W,(c[1]+dy)%H)
 adjacency={c:[n for d in range(4) if (n:=dest(c,d)) is not None] for c in ((x,y) for y in range(H) for x in range(W))};reverse=defaultdict(list)
 for c,ns in adjacency.items():
  for n in ns:reverse[n].append(c)
 distcache={}
 def distances(target):
  if target in distcache:return distcache[target]
  seen={target:0};q=deque([target])
  while q:
   c=q.popleft()
   for n in reverse[c]:
    if n not in seen:seen[n]=seen[c]+1;q.append(n)
  distcache[target]=seen;return seen
 def board(center):
  occ={c:('Q' if i==queens[0] else 'K' if i==queens[1] else 'A' if teams[i]==0 else 'B') if z==0 else ('q' if i==queens[0] else 'k' if i==queens[1] else 'a' if teams[i]==0 else 'b') for i,b in bodies.items() for z,c in enumerate(b)};rows=[]
  for dy in range(-3,4):
   north='';cells=''
   for dx in range(-3,4):
    c=((center[0]+dx)%W,(center[1]+dy)%H)
    north+='+'+{0:' ',1:'-',2:'P'}[edges.get(edge_id(W,H,*c,0),(0,-1))[0]]
    cells+={0:' ',1:'|',2:'P'}[edges.get(edge_id(W,H,*c,3),(0,-1))[0]]+occ.get(c,'*' if c in pearls else '.')
   east=((center[0]+3)%W,(center[1]+dy)%H);rows += [north+'+',cells+{0:' ',1:'|',2:'P'}[edges.get(edge_id(W,H,*east,1),(0,-1))[0]]]
  bottom=''
  for dx in range(-3,4):
   c=((center[0]+dx)%W,(center[1]+3)%H);bottom+='+'+{0:' ',1:'-',2:'P'}[edges.get(edge_id(W,H,*c,2),(0,-1))[0]]
  return rows+[bottom+'+']
 def state():return [[sum(teams[i]==s for i in bodies),sum(len(b) for i,b in bodies.items() if teams[i]==s),max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),len(bodies.get(queens[s],()))] for s in (0,1)]
 turns=[];deaths=[];snaps={};pearls=set();eats=[0,0];rnd=-1;actor=None;cur=None;near=[];qdead=False;portal_moves=[]
 def close():
  if cur is not None:cur['endbody']=list(bodies.get(actor,()));cur['endstate']=state()
 def proximity(event):
  if not qdead or queens[1] not in bodies:return
  ds=distances(bodies[queens[1]][0]);closest=min(((ds.get(b[0],99999),i,b[0]) for i,b in bodies.items() if teams[i]==0),default=None)
  if closest:near.append([rnd,event,*closest,bodies[queens[1]][0]])
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   close()
   if rnd>=0:snaps[rnd]={'state':state(),'eats':eats.copy()}
   rnd=p.i32(0);actor=None;cur=None
  elif k==1:
   close();actor=p.i32(0);cur={'r':rnd,'event':idx,'id':actor,'side':teams[actor],'body':list(bodies[actor]),'eaten':0,'dirs':[],'steps':[],'split':None}
   if actor in (0,1):
    cur['board']=board(bodies[actor][0]);cur['others']={i:list(b) for i,b in bodies.items() if i!=actor};cur['pearls']=list(pearls)
    cur['neighbors']=[{'dir':d,'dest':dest(bodies[actor][0],d),'edge':edges.get(edge_id(W,H,*bodies[actor][0],d),(0,-1)),'occupants':[i for i,b in bodies.items() if dest(bodies[actor][0],d) in b]} for d in range(4)]
   turns.append(cur)
  elif k==4:
   a=p.pointer(0);cur['actiontype']=a.u16(0) if a else None;cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
  elif k==3:
   c=replay.point(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c);eats[teams[actor]]+=1;cur['eaten']+=1
  elif k==9:
   i=p.i32(0);hd=replay.point(p.pointer(0));tl=replay.point(p.pointer(1));b=bodies[i]
   if b[0]!=hd:
    old=b[0]
    if i==actor:
     n=len(cur['steps']);d=cur['dirs'][n] if n<len(cur['dirs']) else None
     if d is not None and edges.get(edge_id(W,H,*old,d),(0,-1))[0]==2:portal_moves.append([rnd,i,teams[i],len(b),old,hd])
     cur['steps'].append([old,hd])
    b.appendleft(hd)
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
  elif k==10:
   parent,child=p.i32(0),p.i32(4);cur['split']=[child,len(bodies[parent])]
   for z,i in enumerate((parent,child)):bodies[i]=deque(replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:
   i=p.i32(0);d={'r':rnd,'event':idx,'id':i,'side':teams[i],'body':list(bodies[i]),'reason':p.u16(4),'actor':actor,'turn_event':cur['event']}
   if i==queens[0]:d['board']=board(bodies[i][0]);d['others']={j:list(b) for j,b in bodies.items() if j!=i};qdead=True
   deaths.append(d);del bodies[i]
  if k in (0,1,9,10,11):proximity(idx)
 close();snaps[rnd]={'state':state(),'eats':eats.copy()}
 assert all(snaps[rnd]['state'][s][:3]==[root.pointer(4).pointer(s).i32(o) for o in (0,8,4)] for s in (0,1))
 ledger=json.loads((OUT/f'{gid}-ledger.json').read_text());assert all(snaps[rnd]['state'][s]==ledger['ends'][s][:4] for s in (0,1)), (gid,snaps[rnd],ledger['ends'])
 qturn=[t for t in turns if t['id']==queens[0]];qd=next((d for d in deaths if d['id']==queens[0]),None)
 last_good=max((r for r,s in snaps.items() if s['state'][0][3]>=s['state'][1][3]),default=-1)
 summary={'gid':gid,'queens':queens,'bot':root.text(1),'size':[W,H],'final':state(),'qdeath':qd,'last_three':qturn[-3:] if qd else [],'near_min':min(near,key=lambda a:a[2]) if near else None,'near_first5':next((x for x in near if x[2]<=5),None),'last_not_behind_queen':last_good,'checkpoints':{r:s for r,s in snaps.items() if r%25==0 or r==rnd},'portal_first':[next((v for v in portal_moves if v[2]==s),None) for s in (0,1)],'portal_100':[sum(v[2]==s and v[0]<=100 for v in portal_moves) for s in (0,1)]}
 (OUT/f'{gid}-detail.json').write_text(json.dumps({'summary':summary,'turns':turns,'deaths':deaths,'snaps':snaps,'portal_moves':portal_moves},ensure_ascii=False))
 print(json.dumps({k:v for k,v in summary.items() if k not in ('last_three','qdeath','checkpoints')},ensure_ascii=False),flush=True)
 print('qdeath',None if qd is None else {k:v for k,v in qd.items() if k not in ('board','others')},flush=True)
 if qd:
  for t in qturn[-3:]:print('QTURN',{k:v for k,v in t.items() if k not in ('board','others','pearls')},'\n'+'\n'.join(t['board']),flush=True)
  at=next(t for t in turns if t['event']==qd['turn_event']);print('DEATH_ACTION',{k:v for k,v in at.items() if k not in ('board','others','pearls')},flush=True)
for gid in (1510794,1510795,1510796):scan(gid)
