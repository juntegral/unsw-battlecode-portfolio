import sys,json,importlib.util
from pathlib import Path
from collections import deque,Counter
sys.dont_write_bytecode=True
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'));import ladder_replay as lr
sys.path.insert(0,str(ROOT/'data/analysis/ladder/dossier/local'));import scoreboard
spec=importlib.util.spec_from_file_location('cr',ROOT/'data/analysis/ladder/losses/counts/count_replays.py');cr=importlib.util.module_from_spec(spec);spec.loader.exec_module(cr)
JOBS={1506915:'b1506911',1506149:'b1506148',1506150:'b1506148'}
for gid,folder in JOBS.items():
 base=json.loads((OUT/f'{gid}-base.json').read_text());root=scoreboard.load_replay(ROOT/f'data/online/live-one1/{folder}/M{gid}.replay').root()
 w,h=map(int,root.text(0).splitlines()[0].split()[1:3]);bodies={};teams={};edges=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q[0]=='EDGE':edges.append(tuple(map(int,q[1:4])))
 geo=cr.Geometry(w,h,edges);qu=base['queens']['us'];qt=base['queens']['them'];own=teams[qu]
 qd=next(d for d in base['deaths'] if d['id']==qu);focus=range(qd['round']-4,qd['round']+1)
 turns=[];queen=[];attacker=[];near=[];pearls=set();rnd=-1;actor=None;turn=None;rounds={};minnear=65536;nearids=set();nearturns=0
 def close():
  if turn is not None:turn['end']=list(bodies.get(actor,()));turns.append(turn)
 def proximity(idx):
  global minnear,nearturns
  if qu not in bodies and qt in bodies:
   dist=geo.distances(bodies[qt][0]);pairs=[(dist[b[0]],i,b[0]) for i,b in bodies.items() if teams[i]==own]
   if pairs:
    dd,i,hd=min(pairs)
    if dd<minnear:near.append(dict(round=rnd,event=idx,distance=dd,id=i,head=hd,queen=bodies[qt][0]));minnear=dd
    nearids.update(i for dd,i,hd in pairs if dd<=5)
    if idx>=0 and actor in bodies and teams[actor]==own and dist[bodies[actor][0]]<=5:nearturns+=1
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   close();turn=None
   if rnd>=0:rounds[rnd]={str(i):[len(b),b[0]] for i,b in bodies.items()}
   rnd=p.i32(0);actor=None
  elif k==1:
   close();actor=p.i32(0);turn=dict(round=rnd,event=idx,id=actor,side=teams[actor],start=list(bodies[actor]),eats=0,steps=[],action=None)
   if actor==qu or (rnd in focus and actor==qd['actor']):turn.update(bodies={str(i):list(b) for i,b in bodies.items()},pearls=list(pearls))
   if actor==qu:queen.append(turn)
   if rnd in focus and actor==qd['actor']:attacker.append(turn)
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
  if k in (1,9,10,11):proximity(idx)
 close();rounds[rnd]={str(i):[len(b),b[0]] for i,b in bodies.items()}
 out=dict(w=w,h=h,own=own,teams=teams,queen=queen[-3:],focusqueen=[t for t in queen if (gid==1506915 and 160<=t['round']<=178) or (gid==1506149 and 15<=t['round']<=40)],attacker=attacker,near=near,nearids=sorted(nearids),final={str(i):list(b) for i,b in bodies.items()},rounds=rounds,turns=[{k:v for k,v in t.items() if k not in ('bodies','pearls')} for t in turns])
 (OUT/f'{gid}-detail.json').write_text(json.dumps(out))
 print(gid,'size',w,h,'own',own,'near',near,'nearids',sorted(nearids))
 for t in queen[-3:]+attacker:print({k:v for k,v in t.items() if k not in ('bodies','pearls')})
