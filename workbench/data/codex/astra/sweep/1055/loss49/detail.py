import sys,json
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/local']
import ladder_replay as lr
import scoreboard as sb
from collections import deque,defaultdict,Counter
from pathlib import Path
OUT=Path(__file__).resolve().parent
for bp in sorted(OUT.glob('*-base.json')):
 z=json.loads(bp.read_text()); gid=z['gid']; root=sb.load_replay(Path(z['folder'])/f'M{gid}.replay').root(); lines=root.text(0).splitlines()
 W,H=map(int,lines[0].split()[1:3]); bodies={};teams={};raw=[]
 for line in lines:
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]='AB'[int(q[1])]
  if q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 edges=lr.canonical_edges(W,H,raw);portals=defaultdict(list)
 for e,(k,p) in edges.items():
  if k==2:portals[p].append(e)
 def dest(c,d):
  e=lr.edge_id(W,H,*c,d);k,p=edges.get(e,(0,-1))
  if k==1:return None
  if k==2:
   t=next(t for t in portals[p] if t!=e);row,x=divmod(t,W+1);return ((x-(d==3))%W,(row//2-(d==0))%H)
  dx,dy=((0,-1),(1,0),(0,1),(-1,0))[d];return ((c[0]+dx)%W,(c[1]+dy)%H)
 rev=defaultdict(list)
 for y in range(H):
  for x in range(W):
   for d in range(4):
    n=dest((x,y),d)
    if n is not None:rev[n].append((x,y))
 cache={}
 def distances(t):
  if t not in cache:
   ds={t:0};queue=deque([t])
   while queue:
    c=queue.popleft()
    for n in rev[c]:
     if n not in ds:ds[n]=ds[c]+1;queue.append(n)
   cache[t]=ds
  return cache[t]
 queen=z['queens']['us'];enemyq=z['queens']['them'];death=next(d for d in z['deaths'] if d['id']==queen);dr=death['round'];attacker=death['actor']
 pearls=set();rnd=-1;actor=None;turn=None;turns=[];near=[];minimum=None;enemyqpos={};qturns=[]
 def view(c):
  occ={p:(i,k) for i,b in bodies.items() for k,p in enumerate(b)};board=[];edge_rows=[]
  for dy in range(-3,4):
   row=''
   for dx in range(-3,4):
    p=((c[0]+dx)%W,(c[1]+dy)%H);ch='o' if p in pearls else '.'
    if p in occ:
     i,k=occ[p];ch=('Q' if k==0 else 'q') if i==queen else ('M' if k==0 else 'm') if teams[i]==z['ours'] else ('E' if k==0 else 'e')
    row+=ch
   board.append(row)
  for d in range(4):
   edge_rows.append({'dir':'NESW'[d],'kind':edges.get(lr.edge_id(W,H,*c,d),(0,-1)),'dest':dest(c,d),'occupants':[(i,len(b),list(b).index(dest(c,d))) for i,b in bodies.items() if dest(c,d) in b]})
  return board,edge_rows
 def observe(idx):
  global minimum
  if queen in bodies or enemyq not in bodies:return
  target=bodies[enemyq][0];ds=distances(target);enemyqpos[rnd]=target
  best=min(((ds.get(b[0],99999),i,b[0]) for i,b in bodies.items() if teams[i]==z['ours']),default=(99999,None,None))
  rec={'round':rnd,'event':idx,'distance':best[0],'id':best[1],'head':best[2],'queen':target}
  if minimum is None or best[0]<minimum['distance']:minimum=rec
  if best[0]<=5 and (not near or near[-1]['round']!=rnd):near.append(rec)
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:rnd=p.i32(0);actor=None
  elif k==1:
   actor=p.i32(0);turn={'round':rnd,'id':actor,'body':list(bodies[actor]),'actions':[],'updates':[],'logs':[],'eats':0}
   if actor==queen:
    turn['board'],turn['edges']=view(bodies[actor][0]);
    if rnd>=dr-3:turn['scene']={'bodies':{str(i):list(b) for i,b in bodies.items()},'pearls':list(pearls),'edges':raw};
    turn['nearby']=[{'id':i,'team':teams[i],'body':list(b)} for i,b in bodies.items() if any(min(abs(c[0]-bodies[actor][0][0]),W-abs(c[0]-bodies[actor][0][0]))<=3 and min(abs(c[1]-bodies[actor][0][1]),H-abs(c[1]-bodies[actor][0][1]))<=3 for c in b)];qturns.append(turn)
   if actor in (queen,attacker,8) and dr-4<=rnd<=dr:turns.append(turn)
  elif k==3:
   c=lr.replay.point(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:
    pearls.discard(c)
    if turn:turn['eats']+=1
  elif k==4:
   a=p.pointer(0);turn['actions'].append({'kind':a.u16(0),'dirs':list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else [],'split':a.i32(4)})
  elif k in (5,6):
   if turn:turn['logs'].append(p.text(0))
  elif k==9:
   i=p.i32(0);h=lr.replay.point(p.pointer(0));tail=lr.replay.point(p.pointer(1));b=bodies[i]
   if h!=b[0]:b.appendleft(h)
   while len(b)>1 and b[-1]!=tail:b.pop()
   if turn:turn['updates'].append({'id':i,'head':h,'length':len(b)})
  elif k==10:
   for no,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(lr.replay.point(v) for v in p.pointer(no));teams[i]='AB'[p.u16(8)]
  elif k==11:bodies.pop(p.i32(0))
  if k in (1,9,10,11):observe(idx)
 result={'gid':gid,'W':W,'H':H,'death':death,'turns':turns,'queen_last3':qturns[-3:],'after_min':minimum,'after_near':near,'enemyq_positions':enemyqpos,'queen_turns':qturns}
 (OUT/f'{gid}-detail.json').write_text(json.dumps(result,ensure_ascii=False))
 print(gid,'min',minimum,'near rounds',len(near),'last3',[(t['round'],t['body'][0],t['actions'],t['logs']) for t in qturns[-3:]],flush=True)
