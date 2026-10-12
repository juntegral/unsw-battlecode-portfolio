import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path[:0]=['tools','data/analysis/ladder/dossier','data/analysis/ladder/dossier/work']
import ladder_replay as lr
from count_dossier import Geo
import o1_scan
OUT=Path(__file__).resolve().parent
for gid in (1494961,1494962,1494964):
 p=Path(f'data/online/smoke/one8-p1-old/M{gid}.replay'); meta=json.loads(p.with_name(f'game-{gid}.json').read_text())
 r=lr.scan(p,meta,'one8-p1-old',set())
 o=o1_scan.scan('one8-p1-old',p,meta)
 (OUT/f'{gid}-economy.json').write_text(json.dumps(o))
 r['intervals']={str(k):v for k,v in r['intervals'].items()}
 (OUT/f'{gid}-ledger.json').write_text(json.dumps(r,ensure_ascii=False))
 print(gid,r['map'],'FINAL',r['final'],'DEATHS',[(d['id'],d['round'],d['cause'],d['actor'],d['length'],d['body'][0]) for d in r['deaths'] if d['id'] in (0,1)],'EATS',r['eats'])
 root=lr.replay.load(p).root(); txt=root.text(0); w,h=map(int,txt.splitlines()[0].split()[1:3]); raw=[]; bodies={};teams={}
 for line in txt.splitlines():
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 geo=Geo(w,h,raw); queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
 qdeath=next((d for d in r['deaths'] if d['id']==queens[0]),None)
 tile=lambda p: lr.replay.point(p)[1]*w+lr.replay.point(p)[0]
 coord=lambda t:[t%w,t//w]
 rnd=-1;actor=None;pearls=set();turn=None;turns=[];close=[];lastq=[];events=[];qpositions=Counter()
 def snap():return {i:list(b) for i,b in bodies.items()}
 def proximity(idx):
  if queens[0] in bodies or queens[1] not in bodies:return
  q=bodies[queens[1]][0]; ds=geo.distances(q); candidates=[(ds[b[0]],i,b[0],len(b)) for i,b in bodies.items() if teams[i]==0]
  if candidates:
   d,i,c,L=min(candidates);close.append(dict(round=rnd,event=idx,distance=d,id=i,length=L,head=coord(c),queen=coord(q)))
 def finish():
  if turn is not None:
   turn['after']=snap();turns.append(turn.copy())
 for idx,e in enumerate(root.pointer(3)):
  k=e.u16(0);p=e.pointer(0)
  if k==0:finish();turn=None;rnd=p.i32(0);actor=None
  elif k==1:
   finish();actor=p.i32(0);turn=dict(round=rnd,event=idx,id=actor,before=snap(),pearls=list(pearls),steps=[],eaten=0,action=None)
  elif k==3:
   t=tile(p.pointer(0))
   if p.u32(0):pearls.add(t)
   else:
    pearls.discard(t)
    if turn is not None:turn['eaten']+=1
  elif k==4:
   a=p.pointer(0);turn['action']=dict(kind=a.u16(0),dirs=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else [],data=a.i32(4)) if a else None
  elif k==9:
   i=p.i32(0);hd,tail=tile(p.pointer(0)),tile(p.pointer(1));b=bodies[i]
   if b[0]!=hd:b.appendleft(hd);turn['steps'].append(coord(hd))
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(tile(pt) for pt in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:
   events.append(dict(round=rnd,event=idx,id=p.i32(0),actor=actor,reason=p.u16(4),before=snap()));bodies.pop(p.i32(0))
  if k in (0,1,9,10,11):proximity(idx)
 finish()
 qt=[t for t in turns if t['id']==queens[0]]
 details=dict(all_turns=turns,edges=raw,gid=gid,w=w,h=h,queens=queens,teams=teams,queen_turns=qt,death_events=[e for e in events if e['id'] in queens],close=close,final=snap())
 if qdeath:
  at=qdeath['actor'];details['attacker_turns']=[t for t in turns if t['id']==at and qdeath['round']-3<=t['round']<=qdeath['round']]
 targets=[x for x in r['deaths'] if x['side']=='us' and x['length']>=10]
 details['long_turns']=[t for t in turns if any(t['id'] in (x['id'],x['actor']) and x['round']-2<=t['round']<=x['round'] for x in targets)]
 (OUT/f'{gid}-detail.json').write_text(json.dumps(details))
 print('LASTQ',[(t['round'],coord(t['before'][queens[0]][0]),len(t['before'][queens[0]]),t['action'],t['steps']) for t in qt[-3:]])
 print('PROX',min(close,key=lambda t:t['distance']) if close else None,'FIRST5',next((c for c in close if c['distance']<=5),None))
 if qdeath: print('ATTACK',[(t['round'],coord(t['before'][at][0]),len(t['before'][at]),t['action'],t['steps']) for t in details['attacker_turns']])
 print('CURVE',[(rr,r['snapshots'].get(rr)) for rr in (0,50,100,200,300,400,499)])
