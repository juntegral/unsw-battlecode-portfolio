import sys,json,importlib.util
from pathlib import Path
from collections import deque,Counter
sys.dont_write_bytecode=True
ROOT=Path.cwd();OUT=ROOT/'data/codex/astra/sweep/0559/loss2'
sys.path.insert(0,str(ROOT/'tools'));import ladder_replay as lr
spec=importlib.util.spec_from_file_location('cr',ROOT/'data/analysis/ladder/losses/counts/count_replays.py');cr=importlib.util.module_from_spec(spec);spec.loader.exec_module(cr)
for gid in (1494957,1494958,1494959):
 base=json.loads((OUT/f'{gid}-base.json').read_text());root=lr.replay.load(ROOT/f'data/online/smoke/one8-p1-old/M{gid}.replay').root()
 w,h=map(int,root.text(0).splitlines()[0].split()[1:3]);bodies={};teams={};edges=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q[0]=='EDGE':edges.append(tuple(map(int,q[1:4])))
 geo=cr.Geometry(w,h,edges);qu=base['queens']['us'];qt=base['queens']['them'];pearls=set();turns=[];queen=[];near=[];rnd=-1;actor=None;turn=None;detail=[]
 qd=next(d for d in base['deaths'] if d['id']==qu);focus=set(range(qd['round']-3,qd['round']+1))
 def snap():return {str(i):list(b) for i,b in bodies.items()}
 def close():
  if turn is not None:
   turn['end']=list(bodies.get(actor,()));turns.append(turn)
 def nearcheck(idx):
  if qu not in bodies and qt in bodies:
   dist=geo.distances(bodies[qt][0]);pairs=[(dist[b[0]],i,b[0]) for i,b in bodies.items() if teams[i]==0]
   if pairs:
    dd,i,hd=min(pairs)
    if not near or dd<min(z['distance'] for z in near):near.append(dict(round=rnd,event=idx,distance=dd,id=i,head=hd,queen=bodies[qt][0]))
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:close();turn=None;rnd=p.i32(0);actor=None
  elif k==1:
   close();actor=p.i32(0);turn=dict(round=rnd,event=idx,id=actor,side=teams[actor],start=list(bodies[actor]),eats=0,steps=[],action=None)
   if actor==qu or (rnd in focus and actor==qd['actor']):turn['bodies']=snap();turn['pearls']=list(pearls)
   if actor==qu:queen.append(turn)
   if rnd in focus and actor==qd['actor']:detail.append(turn)
  elif k==3:
   pt=lr.replay.point(p.pointer(0));c=pt[1]*w+pt[0]
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c);turn['eats']+=1
  elif k==4:
   a=p.pointer(0);turn['action']=dict(type=a.u16(0),dirs=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else [])
  elif k==9:
   i=p.i32(0);hd=lr.replay.point(p.pointer(0));tl=lr.replay.point(p.pointer(1));hd=hd[1]*w+hd[0];tl=tl[1]*w+tl[0];b=bodies[i]
   if b[0]!=hd:b.appendleft(hd);turn['steps'].append(hd)
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(lr.replay.point(c)[1]*w+lr.replay.point(c)[0] for c in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:bodies.pop(p.i32(0))
  if k in (1,9,10,11):nearcheck(idx)
 close()
 final={str(i):list(b) for i,b in bodies.items()};totals={}
 for lo,hi in ((0,20),(21,50),(51,100),(101,300),(301,419),(420,499)):
  totals[f'{lo}-{hi}']=[dict(turns=len(ts:=[t for t in turns if t['side']==s and lo<=t['round']<=hi]),eats=sum(t['eats'] for t in ts),splits=sum(t['action']['type']==1 for t in ts),stop=sum(t['action']['type']==0 and not t['action']['dirs'] for t in ts)) for s in (0,1)]
 out=dict(w=w,h=h,teams=teams,queen=queen[-3:],attacker=detail,near=near,final=final,totals=totals,turns=[{k:v for k,v in t.items() if k not in ('bodies','pearls')} for t in turns])
 (OUT/f'{gid}-detail.json').write_text(json.dumps(out))
 print(gid,'size',w,h,'near',near,'final top',sorted([(len(b),i,teams[i]) for i,b in bodies.items()],reverse=True)[:10])
 for t in queen[-3:]+detail:print({k:v for k,v in t.items() if k not in ('bodies','pearls')})
 print('TOTALS',totals)
