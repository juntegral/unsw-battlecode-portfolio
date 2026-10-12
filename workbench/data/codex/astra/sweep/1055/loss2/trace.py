import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path[:0]=['tools','data/analysis/ladder/dossier/local']
from ladder_replay import replay
from count_local import Geo
OUT=Path('data/codex/astra/sweep/1055/loss2');D=Path('data/online/smoke/one12-c1-old')
for gid in [1501666,1501667,1501668]:
 root=replay.load(D/f'M{gid}.replay').root();lines=root.text(0).splitlines();w,h=map(int,lines[0].split()[1:3]);bodies={};teams={};raw=[]
 for line in lines:
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(q[3+2*k])+w*int(q[4+2*k]) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 geo=Geo(w,h,raw);qs=[min(i for i in bodies if teams[i]==s) for s in (0,1)];pearls=set();rnd=-1;actor=None;turn=None;turns=[];deaths=[];qhist=[];near=[];qpos=Counter();snaps={};splits=[]
 xy=lambda c:[c%w,c//w]
 tile=lambda p:replay.point(p)[0]+w*replay.point(p)[1]
 def snap():
  return [[len([i for i in bodies if teams[i]==s]),sum(len(b) for i,b in bodies.items() if teams[i]==s),max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),len(bodies.get(qs[s],[])),sorted([[i,len(b),xy(b[0])] for i,b in bodies.items() if teams[i]==s],key=lambda v:-v[1])[:5]] for s in (0,1)]
 def distance(src,target,maxdist=5):
  seen={src:0};todo=deque([src])
  while todo:
   c=todo.popleft()
   if c==target:return seen[c]
   if seen[c]==maxdist:continue
   for t in geo.adj[c]:
    if t not in seen:seen[t]=seen[c]+1;todo.append(t)
  return None
 def board(qid):
  hd=bodies[qid][0];win=geo.window(hd);occ={c: ('Q' if i==qid else 'E' if teams[i]!=teams[qid] and c==b[0] else 'e' if teams[i]!=teams[qid] else 'A' if c==b[0] else 'a') for i,b in bodies.items() for c in b}
  for c in bodies[qid]:occ[c]='q'
  occ[hd]='Q'
  cells=[[(hd//w+dy)%h*w+(hd%w+dx)%w for dx in range(-3,4)] for dy in range(-3,4)]
  return dict(head=xy(hd),grid=[''.join(occ.get(c,'*' if c in pearls else '.') for c in row) for row in cells],edges=[dict(at=xy(c),dirs=''.join('NESW'[d] for d,(k,t) in enumerate(geo.moves[c]) if k==1),portals=['NESW'[d] for d,(k,t) in enumerate(geo.moves[c]) if k==2]) for row in cells for c in row if any(k for k,t in geo.moves[c])],dragons=[dict(id=i,side=teams[i],length=len(b),head=xy(b[0]),visible=[xy(c) for c in b if c in win]) for i,b in bodies.items() if any(c in win for c in b)])
 def close():
  if turn:
   turn['end']=xy(bodies[actor][0]) if actor in bodies else None;turn['endL']=len(bodies.get(actor,[]));turns.append(turn)
 for index,ev in enumerate(root.pointer(3)):
  k=ev.u16(0)
  if k not in (0,1,3,4,9,10,11):continue
  p=ev.pointer(0)
  if k in (0,1):
   close();turn=None
  if k==0:
   if rnd>=0:snaps[rnd]=snap()
   rnd=p.i32(0);actor=None
   if qs[0] not in bodies and qs[1] in bodies:qpos[tuple(xy(bodies[qs[1]][0]))]+=1
  elif k==1:
   actor=p.i32(0);turn=dict(r=rnd,event=index,id=actor,side=teams[actor],L=len(bodies[actor]),head=xy(bodies[actor][0]),steps=[],eat=[],units=sum(teams[i]==teams[actor] for i in bodies))
   if actor in qs:
    turn['board']=board(actor);qhist.append(turn)
   if qs[0] not in bodies and qs[1] in bodies and teams[actor]==0:
    dd=distance(bodies[actor][0],bodies[qs[1]][0])
    if dd is not None:near.append(dict(r=rnd,event=index,id=actor,L=len(bodies[actor]),distance=dd,head=xy(bodies[actor][0]),queen=xy(bodies[qs[1]][0])))
  elif k==4:
   a=p.pointer(0);typ=a.u16(0) if a else 0;turn['action']=['move','split','suicide'][typ] if typ<3 else str(typ)
   turn['dirs']=''.join('NESW'[d] for d in a.pointer(0)) if typ==0 and a and a.pointer(0) else '';turn['splitSize']=a.i32(4) if typ==1 else None
  elif k==3:
   c=tile(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c);turn['eat'].append(xy(c))
  elif k==9:
   i=p.i32(0);hd,tl=tile(p.pointer(0)),tile(p.pointer(1));b=bodies[i]
   if b[0]!=hd:
    b.appendleft(hd)
    if i==actor:turn['steps'].append(xy(hd))
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
  elif k==10:
   par,ch=p.i32(0),p.i32(4);splits.append(dict(r=rnd,id=par,child=ch,side=teams[par],before=len(bodies[par])))
   for z,i in enumerate((par,ch)):bodies[i]=deque(tile(t) for t in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:
   i=p.i32(0);dd=dict(r=rnd,event=index,id=i,side=teams[i],L=len(bodies[i]),head=xy(bodies[i][0]),actor=actor,reason=p.u16(4),turn=dict(turn));deaths.append(dd);bodies.pop(i)
 close();snaps[rnd]=snap()
 result=dict(gid=gid,w=w,h=h,queens=qs,snaps=snaps,turns=turns,deaths=deaths,splits=splits,near=near,qpos=[[list(k),v] for k,v in qpos.items()])
 (OUT/f'{gid}-trace.json').write_text(json.dumps(result))
 print(gid,'queens',[(d['id'],d['r'],d['reason'],d['actor']) for d in deaths if d['id'] in qs], 'near',len(near),flush=True)
