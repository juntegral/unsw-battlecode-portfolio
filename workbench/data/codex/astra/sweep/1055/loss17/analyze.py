import sys,json
from pathlib import Path
from collections import deque,Counter
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier','data/analysis/ladder/dossier/local']
import ladder_replay as lr
from count_dossier import Geo
import scoreboard
OUT=Path(__file__).resolve().parent
JOBS=[(1502776,1502774),(1502778,1502774),(1507592,1507592)]
for gid,battle in JOBS:
 pth=Path(f'data/online/live-one1/b{battle}/M{gid}.replay'); meta=json.loads(pth.with_name(f'game-{gid}.json').read_text())
 base=lr.scan(pth,meta,'loss17',set()); root=scoreboard.load_replay(pth).root(); W,H=map(int,root.text(0).splitlines()[0].split()[1:3]); bodies={}; teams={}; raw=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies); bodies[i]=deque(int(q[4+2*k])*W+int(q[3+2*k]) for k in range(int(q[2]))); teams[i]='AB'[int(q[1])]
  elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 geo=Geo(W,H,raw); own=base['ours']; queen=base['queens']['us']; foe=base['queens']['them']; rnd=-1; actor=None; pearls=set(); turns=[]; turn=None; near=[]; first_near=None; min_near=65535; unique=set(); qs=[]
 def xy(c): return [c%W,c//W]
 def finish():
  if turn is not None:
   turn['end']={str(i):list(b) for i,b in bodies.items() if i in [queen,foe,actor]}; turns.append(turn)
 def check_near(idx):
  global first_near,min_near
  if queen in bodies or foe not in bodies:return
  ds=geo.distances(bodies[foe][0]); d,i=min(((ds[b[0]],i) for i,b in bodies.items() if teams[i]==own),default=(65535,-1)); min_near=min(min_near,d)
  if d<=5:
   unique.add(i)
   if first_near is None:first_near=dict(round=rnd,event=idx,id=i,distance=d,head=xy(bodies[i][0]),foe=xy(bodies[foe][0]))
 for idx,e in enumerate(root.pointer(3)):
  k=e.u16(0); p=e.pointer(0)
  if k==0:finish();turn=None;rnd=p.i32(0);actor=None
  elif k==1:
   finish();actor=p.i32(0); turn=dict(round=rnd,event=idx,id=actor,side=teams[actor],length=len(bodies[actor]),body=list(bodies[actor]),steps=[],eats=0,split=None)
   if actor in (queen,foe):
    turn['scene']={str(i):list(b) for i,b in bodies.items()};turn['pearls']=list(pearls)
   if actor==queen:qs.append(turn)
   if queen not in bodies and foe in bodies and teams[actor]==own:
    d=geo.distances(bodies[foe][0])[bodies[actor][0]]
    if d<=5:near.append(dict(round=rnd,id=actor,distance=d,foe=xy(bodies[foe][0])))
  elif k==3:
   c=lr.replay.point(p.pointer(0));c=c[1]*W+c[0]
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c);turn['eats']+=1
  elif k==4:
   a=p.pointer(0);turn['action']={'kind':a.u16(0),'dirs':list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else [],'split':a.i32(4)}
  elif k==9:
   i=p.i32(0); h=lr.replay.point(p.pointer(0));t=lr.replay.point(p.pointer(1));h=h[1]*W+h[0];t=t[1]*W+t[0];b=bodies[i]
   if b[0]!=h:b.appendleft(h);turn['steps'].append(h)
   while len(b)>1 and b[-1]!=t:b.pop()
   assert b[-1]==t
   check_near(idx)
  elif k==10:
   parent,child=p.i32(0),p.i32(4);turn['split']=child
   for z,i in enumerate((parent,child)):bodies[i]=deque(lr.replay.point(pt)[1]*W+lr.replay.point(pt)[0] for pt in p.pointer(z));teams[i]='AB'[p.u16(8)]
   check_near(idx)
  elif k==11:
   i=p.i32(0)
   if i==queen:
    turn['queen_death_scene']={str(j):list(b) for j,b in bodies.items()};turn['death_pearls']=list(pearls)
   bodies.pop(i);check_near(idx)
 finish()
 slim={k:v for k,v in base.items() if k not in ('text','intervals','natural','pearls')}
 slim.update(width=W,height=H,teams=teams,queen_turns=qs,turns=turns,near=dict(first=first_near,min=min_near,own_turns=len(near),examples=near[:20],unique_ids=sorted(unique)),final_bodies={i:list(b) for i,b in bodies.items()})
 (OUT/f'{gid}.json').write_text(json.dumps(slim))
 print(gid,base['bots'],base['final'],'q deaths',[d for d in base['deaths'] if d['id'] in [queen,foe]],'near',slim['near'])
