import sys
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
import json,hashlib
sys.path[:0]=['tools','data/analysis/ladder/losses/counts','data/analysis/ladder/dossier/work']
import ladder_replay as lr
from count_replays import Geometry
import o1_scan
OUT=Path(__file__).resolve().parent
F=Path('data/online/live-one1/b1490796')
for gid in (1490798,1490799,1490800):
 p=F/f'M{gid}.replay';meta=json.loads((F/f'game-{gid}.json').read_text())
 g=lr.scan(p,meta,'loss3',set()); ledger=o1_scan.scan('loss3',p,meta)
 root=lr.replay.load(p).root();w,h=map(int,g['text'].splitlines()[0].split()[1:3]);raw=[];bodies={};teams={}
 for line in g['text'].splitlines():
  a=line.split()
  if a[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(a[4+2*k])*w+int(a[3+2*k]) for k in range(int(a[2])));teams[i]='AB'[int(a[1])]
  elif a[0]=='EDGE':raw.append(tuple(map(int,a[1:4])))
 geo=Geometry(w,h,raw);q=g['queens']['us'];eq=g['queens']['them'];pearls=set();rnd=-1;actor=None;turn=None;turns=[];qturns=[];qdead=False;near=[];closest=None;deathframes={};eqpositions=Counter()
 tile=lambda p: lr.replay.point(p)[1]*w+lr.replay.point(p)[0]
 def frame():return dict(bodies={i:list(b) for i,b in bodies.items()},pearls=list(pearls))
 def approach(index):
  global closest
  if not qdead or eq not in bodies:return
  dh=geo.distances(bodies[eq][0]);poss=[(dh[b[0]],i,b[0]) for i,b in bodies.items() if teams[i]=='B']
  if not poss:return
  d,i,c=min(poss)
  if closest is None or d<closest['distance']:closest=dict(distance=d,round=rnd,event=index,id=i,head=c,enemy_head=bodies[eq][0])
  if d<=5 and (not near or near[-1]['round']!=rnd):near.append(dict(round=rnd,event=index,id=i,distance=d,head=c,enemy_head=bodies[eq][0]))
 def close():
  if turn is not None:
   turn['end']=list(bodies.get(actor,()));turns.append(turn)
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);e=ev.pointer(0)
  if k==0:
   close();turn=None;rnd=e.i32(0);actor=None
   if qdead and eq in bodies:eqpositions[bodies[eq][0]]+=1
  elif k==1:
   close();actor=e.i32(0);turn=dict(round=rnd,event=idx,id=actor,side=teams[actor],body=list(bodies[actor]),moves=[],eats=[],splits=[])
   if actor==q:turn['frame']=frame();qturns.append(turn)
  elif k==3:
   c=tile(e.pointer(0))
   if e.u32(0):pearls.add(c)
   else:pearls.remove(c);turn['eats'].append(c)
  elif k==4:
   a=e.pointer(0);turn['action']=a.u16(0) if a else None;turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
  elif k==9:
   i=e.i32(0);hd=tile(e.pointer(0));tail=tile(e.pointer(1));b=bodies[i]
   if b[0]!=hd:
    if turn is not None:turn['moves'].append([i,b[0],hd])
    b.appendleft(hd)
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
  elif k==10:
   for z,i in enumerate((e.i32(0),e.i32(4))):bodies[i]=deque(tile(c) for c in e.pointer(z));teams[i]='AB'[e.u16(8)]
   turn['splits'].append(dict(parent=e.i32(0),child=e.i32(4),kept=len(bodies[e.i32(0)])))
  elif k==11:
   i=e.i32(0)
   if i in (q,eq) or len(bodies[i])>=10:deathframes[idx]=dict(round=rnd,id=i,actor=actor,frame=frame(),turn=dict(turn))
   if i==q:qdead=True
   bodies.pop(i)
  if k in (0,1,9,10,11):approach(idx)
 close()
 assert g['final']['us']['alive']==sum(t=='B' and i in bodies for i,t in teams.items())
 for r,s in ledger['snaps'].items():
  for side,v in zip(('us','them'),s):assert v[:4]==[g['snapshots'][int(r)][side][k] for k in ('alive','total','longest','queen_length')]
 how='wiped out' if not g['final']['us']['alive'] else 'queen' if g['final']['us']['queen_length']!=g['final']['them']['queen_length'] else 'longest' if g['final']['us']['longest']!=g['final']['them']['longest'] else 'total'
 metric={'wiped out':'total','queen':'queen_length','longest':'longest','total':'total'}[how]
 lastlevel=max((r for r,s in g['snapshots'].items() if s['us'][metric]>=s['them'][metric]),default=-1)
 g.update(how=how,lastlevel=lastlevel,width=w,height=h,closest=closest,near=near,enemy_queen_positions=eqpositions.most_common(),teams=teams,final_bodies={i:list(b) for i,b in bodies.items()},qturns=qturns,turns=turns,deathframes=deathframes,ledger=ledger,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 g.pop('intervals')
 (OUT/f'{gid}.json').write_text(json.dumps(g,ensure_ascii=False))
 print(json.dumps({k:g[k] for k in ('gid','map','bots','queens','how','lastlevel','last_round','final','q_eats','q_splits','closest','anomalies')},ensure_ascii=False))
 print('queen deaths',json.dumps([d for d in g['deaths'] if d['id'] in (q,eq)]))
 print('long deaths',[(d['round'],d['id'],d['length'],d['cause'],d['actor']) for d in g['deaths'] if d['side']=='us' and d['length']>=10])
