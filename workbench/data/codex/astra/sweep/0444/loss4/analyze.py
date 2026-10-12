import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path.insert(0,str(Path('tools').resolve()))
import ladder_replay as lr
sys.path.insert(0,str(Path('data/analysis/ladder/dossier/local').resolve()))
from scoreboard import load_replay
from replay_format import point
from count_local import Geo
OUT=Path('data/codex/astra/sweep/0444/loss4')
for gid in (1488842,1488844):
 p=Path(f'data/online/live-one1/b1488840/M{gid}.replay');meta=json.loads(p.with_name(f'game-{gid}.json').read_text())
 s=lr.scan(p,meta,'b1488840',set())
 # JSON-safe shared counter output.
 (OUT/f'{gid}-summary.json').write_text(json.dumps({k:v for k,v in s.items() if k not in ('intervals','text')},ensure_ascii=False,indent=2))
 print(gid,{k:s[k] for k in ('bots','queens','final','last_round','end_reason','q_eats','q_splits','eats','anomalies')})
 print('queen deaths',[d for d in s['deaths'] if d['id'] in s['queens'].values()])
 print('snapshots', {r:s['snapshots'][r] for r in (0,10,20,30,50,100,150,200,300,400,499) if r in s['snapshots']})
 root=load_replay(p).root();w,h=map(int,root.text(0).splitlines()[0].split()[1:]);b={};teams={};edges=[];pearls=set();turns=[];snaps={};round=-1;cur=None
 for line in root.text(0).splitlines():
  q=line.split()
  if q and q[0]=='DRAGON':
   i=len(b);b[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q and q[0]=='EDGE':edges.append(tuple(map(int,q[1:4])))
 geo=Geo(w,h,edges);tile=lambda p:point(p)[1]*w+point(p)[0]
 def snapshot():return {i:list(bb) for i,bb in b.items()}
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:round=p.i32(0)
  elif k==1:
   cur=dict(round=round,event=idx,id=p.i32(0),b=snapshot(),pearls=list(pearls),steps=[],eats=[],deaths=[],splits=[]);turns.append(cur)
  elif k==3:
   t=tile(p.pointer(0))
   if p.u32(0):pearls.add(t)
   else:pearls.remove(t);cur['eats'].append(t)
  elif k==4:
   a=p.pointer(0);cur['action']=a.u16(0);cur['dirs']=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0)!=None else []
  elif k==9:
   i=p.i32(0);hd,tail=tile(p.pointer(0)),tile(p.pointer(1));bb=b[i]
   if hd!=bb[0]:bb.appendleft(hd);cur['steps'].append([i,hd])
   while len(bb)>1 and bb[-1]!=tail:bb.pop()
   assert bb[-1]==tail
  elif k==10:
   cur['splits'].append([p.i32(0),p.i32(4)])
   for z,i in enumerate((p.i32(0),p.i32(4))):b[i]=deque(tile(pt) for pt in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:cur['deaths'].append([p.i32(0),p.u16(4)]);b.pop(p.i32(0))
  if cur:cur['end']=snapshot()
 (OUT/f'{gid}-turns.json').write_text(json.dumps(dict(w=w,h=h,teams=teams,edges=edges,turns=turns),separators=(',',':')))
