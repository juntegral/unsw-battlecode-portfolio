import sys,json,importlib.util
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
ROOT=Path.cwd(); OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'))
import ladder_replay as lr
spec=importlib.util.spec_from_file_location('geo',ROOT/'data/analysis/ladder/losses/counts/count_replays.py'); gm=importlib.util.module_from_spec(spec);spec.loader.exec_module(gm)

def analyze(gid):
 folder=ROOT/'data/online/smoke/one12-k1-old'; path=folder/f'M{gid}.replay'; meta=json.loads((folder/f'game-{gid}.json').read_text())
 base=lr.scan(path,meta,'one12-k1-old',set()); root=lr.replay.load(path).root()
 w,h=map(int,base['text'].splitlines()[0].split()[1:3]); bodies={};teams={};edges=[]
 for line in base['text'].splitlines():
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q[0]=='EDGE':edges.append(tuple(map(int,q[1:4])))
 geo=gm.Geometry(w,h,edges); queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
 rnd=0;actor=None;t=None;turns=[];qturns=[];splits=[];near=[];present=set();deaths=[];eats=Counter()
 def close():
  if t is not None:
   t['endL']=len(bodies.get(t['id'],()));t['endhead']=bodies[t['id']][0] if t['id'] in bodies else None
 def proximity(idx):
  if queens[0] not in bodies and queens[1] in bodies:
   q=bodies[queens[1]][0];ds=geo.distances(q);p=min(((ds[b[0]],i,b[0]) for i,b in bodies.items() if teams[i]==0),default=(65535,None,None))
   near.append([rnd,idx,*p,q])
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:close();t=None;rnd=p.i32(0);actor=None
  elif k==1:
   close();actor=p.i32(0);b=bodies[actor];t=dict(r=rnd,event=idx,id=actor,side=teams[actor],L=len(b),head=b[0],eaten=0,steps=[],split=None,owncount=sum(teams[i]==0 for i in bodies));turns.append(t)
   if actor in queens:
    t['bodies']={i:list(bb) for i,bb in bodies.items()};t['pearls']=sorted(present);qturns.append(t)
  elif k==3:
   cell=lr.replay.point(p.pointer(0));c=cell[1]*w+cell[0]
   if p.u32(0):present.add(c)
   else:present.remove(c);t['eaten']+=1;eats[actor]+=1
  elif k==4:
   a=p.pointer(0);t['action']=a.u16(0) if a else None;t['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
  elif k==9:
   i=p.i32(0);hh=lr.replay.point(p.pointer(0));tt=lr.replay.point(p.pointer(1));hd=hh[1]*w+hh[0];tail=tt[1]*w+tt[0];b=bodies[i]
   if b[0]!=hd:b.appendleft(hd);t['steps'].append(hd)
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
  elif k==10:
   parent,child=p.i32(0),p.i32(4);before=len(bodies[parent])
   for z,i in enumerate((parent,child)):bodies[i]=deque(lr.replay.point(pt)[1]*w+lr.replay.point(pt)[0] for pt in p.pointer(z));teams[i]=p.u16(8)
   ss=dict(r=rnd,parent=parent,child=child,before=before,after=len(bodies[parent]),childL=len(bodies[child]),owncount=t['owncount']);splits.append(ss);t['split']=ss
  elif k==11:
   i=p.i32(0);deaths.append(dict(r=rnd,id=i,actor=actor,reason=p.u16(4),L=len(bodies[i]),body=list(bodies[i])));del bodies[i]
  if k in (0,1,9,10,11):proximity(idx)
 close()
 # final standings already validated against result by imported scanner
 simple={k:base[k] for k in ('gid','map','bots','queens','final','eats','q_eats','q_splits','last_round','anomalies')}
 keys=lambda st:(st['queen_length'],st['longest'],st['total'])
 snaps=base['snapshots'];bad=[r for r,ss in snaps.items() if keys(ss['us'])>=keys(ss['them'])]
 simple['permanent_behind']=max(bad)+1 if bad else min(snaps)
 simple['queen_deaths']=[d for d in base['deaths'] if d['id'] in queens]
 simple['checkpoints']={r:ss for r,ss in snaps.items() if r in [0,25,50,100,150,200,250,300,350,400,450,499,500]}
 simple['near_after_qdeath']={'closest':min(near,key=lambda x:x[2]) if near else None,'first5':next((z for z in near if z[2]<=5),None),'queen_range':sorted({z[-1] for z in near})}
 simple['queen_splits']=[s for s in splits if s['parent'] in queens]
 simple['late_long_deaths']=[d for d in base['deaths'] if d['side']=='us' and d['round']>=300 and d['length']>=8]
 (OUT/f'{gid}-summary.json').write_text(json.dumps(simple,indent=2))
 (OUT/f'{gid}-turns.json').write_text(json.dumps(turns,separators=(',',':')))
 (OUT/f'{gid}-base.json').write_text(json.dumps({k:v for k,v in base.items() if k!='intervals'},separators=(',',':')))
 print(json.dumps(simple,ensure_ascii=False))
for gid in [1504482,1504484,1504486]:
 if not (OUT/f'{gid}-base.json').exists():analyze(gid)
