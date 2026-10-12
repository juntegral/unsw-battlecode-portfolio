import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
ROOT=Path.cwd(); OUT=Path(__file__).parent
sys.path[:0]=[str(ROOT/'data/analysis/ladder/dossier/local'),str(ROOT/'tools')]
import scoreboard as sb
from count_local import Geo
from replay_format import point
JOBS=[(1506151,1506148),(1506152,1506148),(1511406,1511406)]
for gid,battle in JOBS:
 base=json.loads((OUT/f'{gid}-base.json').read_text()); qs=base['queens']; q=qs['us']; eq=qs['them']
 qd=next(x for x in base['deaths'] if x['id']==q); attacker=qd['actor']
 root=sb.load_replay(ROOT/f'data/online/live-one1/b{battle}/M{gid}.replay').root()
 w,h=map(int,root.text(0).splitlines()[0].split()[1:3]); bodies={};teams={};edges=[]
 for line in root.text(0).splitlines():
  a=line.split()
  if a[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(a[4+2*k])*w+int(a[3+2*k]) for k in range(int(a[2]))); teams[i]=int(a[1])
  elif a[0]=='EDGE':edges.append(tuple(map(int,a[1:4])))
 geo=Geo(w,h,edges); pearls=set();turns=[];focused=[];cur=None;r=-1; actor=None; approach=[];closest=(999,None); qhistory=[];splits=[]
 def xy(c):return [c%w,c//w]
 def man(c,t):
  dx=abs(c%w-t%w);dy=abs(c//w-t//w);return min(dx,w-dx)+min(dy,h-dy)
 reverse=[[] for _ in geo.adj]
 for c,adj in enumerate(geo.adj):
  for t in adj:reverse[t].append(c)
 distances={}
 def ball(t):
  if t not in distances:
   d={t:0}; todo=deque([t])
   while todo:
    c=todo.popleft()
    for n in reverse[c]:
     if n not in d:d[n]=d[c]+1;todo.append(n)
   distances[t]=d
  return distances[t]
 def near(event):
  global closest
  if q not in bodies and eq in bodies:
   target=bodies[eq][0];ds=ball(target)
   candidates=[(ds.get(bb[0],999),i) for i,bb in bodies.items() if teams[i]==1]
   if candidates:
    d,i=min(candidates)
    if d<closest[0]:closest=(d,dict(round=r,event=event,id=i,head=xy(bodies[i][0]),queen=xy(target)))
    if d<=5 and (not approach or approach[-1]['round']!=r):approach.append(dict(round=r,id=i,d=d,head=xy(bodies[i][0]),queen=xy(target)))
 def state():
  center=bodies[q][0];cx,cy=xy(center); grid=[[' ']*15 for _ in range(15)]
  occ={c:(i,k) for i,bb in bodies.items() for k,c in enumerate(bb)}
  for yy in range(7):
   for xx in range(7):
    c=((cy+yy-3)%h)*w+(cx+xx-3)%w; ch='*' if c in pearls else '.'
    if c in occ:
     i,k=occ[c];ch=('Q' if k==0 else 'q') if i==q else ('A' if k==0 else 'a') if teams[i]==1 else ('X' if k==0 else 'x')
    grid[2*yy+1][2*xx+1]=ch
    for direction,(kind,dest) in enumerate(geo.moves[c]):
     dy,dx=[(-1,0),(0,1),(1,0),(0,-1)][direction]
     if kind:grid[2*yy+1+dy][2*xx+1+dx]='P' if kind==2 else ('-' if dy else '|')
  return dict(round=r,event=idx,body=[xy(c) for c in bodies[q]],board=[''.join(row) for row in grid],
    local=[dict(id=i,side=teams[i],length=len(bb),head=xy(bb[0]),man=man(center,bb[0]),visible=bb[0] in geo.window(center),distance=ball(center).get(bb[0])) for i,bb in bodies.items() if man(center,bb[0])<=10],
    bodies={str(i):[xy(c) for c in bb] for i,bb in bodies.items()},pearls=[xy(c) for c in pearls])
 for idx,ev in enumerate(root.pointer(3)):
  kind=ev.u16(0);p=ev.pointer(0)
  if kind==0:r=p.i32(0); actor=None
  elif kind==1:
   actor=p.i32(0);cur=dict(round=r,event=idx,id=actor,side=teams[actor],length=len(bodies[actor]),head=xy(bodies[actor][0]),moves=[],eats=0,action=None);turns.append(cur)
   if actor==q:
    qhistory.append(dict(round=r,length=len(bodies[q]),head=xy(bodies[q][0])))
    if qd['round']-4<=r<=qd['round']:focused.append(state())
   if q not in bodies and eq in bodies and teams[actor]==1:
    d=ball(bodies[eq][0]).get(bodies[actor][0],999)
    if d<=5:cur['enemy_queen_distance']=d
  elif kind==4:
   a=p.pointer(0);cur['action']=dict(kind=a.u16(0),dirs=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) else [],size=a.i32(4)) if a else None
  elif kind==3:
   pos=point(p.pointer(0));c=pos[1]*w+pos[0]
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c);cur['eats']+=1
  elif kind==9:
   i=p.i32(0);hp=point(p.pointer(0));tp=point(p.pointer(1));hd=hp[1]*w+hp[0];tail=tp[1]*w+tp[0];bb=bodies[i]
   if hd!=bb[0]:bb.appendleft(hd);cur['moves'].append(xy(hd))
   while len(bb)>1 and bb[-1]!=tail:bb.pop()
   assert bb[-1]==tail
   near(idx)
  elif kind==10:
   parent,child=p.i32(0),p.i32(4)
   splits.append(dict(round=r,parent=parent,child=child,before=len(bodies[parent])))
   for z,i in enumerate([parent,child]):bodies[i]=deque(point(t)[1]*w+point(t)[0] for t in p.pointer(z));teams[i]=p.u16(8)
  elif kind==11:
   i=p.i32(0);bodies.pop(i);near(idx)
 snapshots=base['snapshots']
 def score(x):return (x['queen_length'],x['longest'],x['total']) if x['alive'] else (-1,-1,-1)
 nonloss=[int(r) for r,v in snapshots.items() if score(v['us'])>=score(v['them'])]
 permanent=max(nonloss,default=-1)+1
 info=dict(gid=gid,bot=root.text(2),size=[w,h],queens=qs,death=qd,final=base['final'],permanent=permanent,focused=focused[-3:],queen_turns=[t for t in turns if t['id']==q],attacker_turns=[t for t in turns if t['id']==attacker],queen_history=qhistory,splits=[s for s in splits if s['parent']==q],approach=approach,closest=closest,close_turns=[t for t in turns if 'enemy_queen_distance' in t],final_bodies={str(i):[xy(c) for c in bb] for i,bb in bodies.items()},turns=turns)
 (OUT/f'{gid}-trace.json').write_text(json.dumps(info,ensure_ascii=False))
 print(gid,'permanent',permanent,'qsplit',info['splits'],'closest',closest,'approach rounds',len(approach),flush=True)
 print('Q LAST',info['queen_turns'][-3:],flush=True)
 print('ATTACKER',info['attacker_turns'][-3:],flush=True)
 print('LAST LOCAL',[dict(round=f['round'],local=f['local']) for f in info['focused']],flush=True)
