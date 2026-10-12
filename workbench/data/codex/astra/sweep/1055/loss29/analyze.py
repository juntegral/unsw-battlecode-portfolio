import sys,json
from pathlib import Path
from collections import deque,Counter
sys.dont_write_bytecode=True
ROOT=Path.cwd(); OUT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'tools'))
import ladder_replay as lr
sys.path.insert(0,str(ROOT/'data/analysis/ladder/dossier'))
from count_dossier import Geo

def scan(gid):
 p=ROOT/f'data/online/smoke/one13-p1-old/M{gid}.replay'; meta=json.loads(p.with_name(f'game-{gid}.json').read_text())
 base=json.loads((OUT/f'{gid}.json').read_text()) if (OUT/f'{gid}.json').exists() else lr.scan(p,meta,'one13-p1-old',set()); root=lr.replay.load(p).root()
 W,H=map(int,root.text(0).splitlines()[0].split()[1:3]); bodies={}; teams={}; raw=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if q and q[0]=='DRAGON':
   i=len(bodies); bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 geo=Geo(W,H,raw); tile=lambda p:p[1]*W+p[0]
 oq=base['queens']['us']; eq=base['queens']['them']; rnd=-1;actor=None;pearls=set();turns=[];qt=[];near=[];snaps={};splits=[];dead=False;ts=None
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);v=ev.pointer(0)
  if k==0:
   rnd=v.i32(0)
  elif k==1:
   actor=v.i32(0)
   ts=dict(r=rnd,id=actor,L=len(bodies[actor]),head=bodies[actor][0],steps=[],eats=0,act=None)
   turns.append(ts)
   if actor==oq:
    ts['bodies']={i:list(b) for i,b in bodies.items()};ts['pearls']=list(pearls);qt.append(ts)
   if dead and eq in bodies and teams[actor]==0:
    d=geo.distances(tile(bodies[eq][0]))[tile(bodies[actor][0])]
    near.append(dict(r=rnd,id=actor,d=d,head=bodies[actor][0],q=bodies[eq][0]))
  elif k==3:
   xy=lr.replay.point(v.pointer(0))
   if v.u32(0):pearls.add(xy)
   else:pearls.remove(xy);ts['eats']+=1
  elif k==4:
   a=v.pointer(0); ts['act']={'kind':a.u16(0),'dirs':list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else []}
  elif k==9:
   i=v.i32(0);h=lr.replay.point(v.pointer(0));tail=lr.replay.point(v.pointer(1));b=bodies[i]
   if h!=b[0]:b.appendleft(h);ts['steps'].append(h)
   while len(b)>1 and b[-1]!=tail:b.pop()
  elif k==10:
   par,child=v.i32(0),v.i32(4);before=len(bodies[par])
   for z,i in enumerate((par,child)):bodies[i]=deque(lr.replay.point(pt) for pt in v.pointer(z));teams[i]=v.u16(8)
   splits.append(dict(r=rnd,id=par,child=child,before=before,after=len(bodies[par])))
  elif k==11:
   i=v.i32(0)
   if i==oq:dead=True
   bodies.pop(i)
  if k in (0,9,10,11):snaps[rnd]={s:dict(q=len(bodies.get(oq if s==0 else eq,())),n=sum(teams[i]==s for i in bodies),total=sum(len(b) for i,b in bodies.items() if teams[i]==s),long=max([len(b) for i,b in bodies.items() if teams[i]==s] or [0])) for s in (0,1)}
 base.pop('intervals',None);base['teams']=teams;base['final_bodies']={i:list(b) for i,b in bodies.items()};base['qt']=qt;base['splits']=splits;base['near']=near;base['turns']=turns;base['geometry']={'W':W,'H':H,'edges':raw};base['states']=snaps
 (OUT/f'{gid}.json').write_text(json.dumps(base,ensure_ascii=False,default=list))
 print(gid,base['bots'],base['final'],'last',rnd,'queenDeaths',[d for d in base['deaths'] if d['id'] in (0,1)],'near',min(near,key=lambda x:x['d']) if near else None)
 print('qt last', [{k:v for k,v in t.items() if k not in ('bodies','pearls')} for t in qt[-3:]])
 print('snapshots',[(r,base['snapshots'].get(r)) for r in (0,25,50,100,200,300,400,499)])
for gid in (1507918,1507919,1507921):scan(gid)
