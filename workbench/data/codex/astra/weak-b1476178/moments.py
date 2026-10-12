import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
sys.path[:0]=['data/codex/astra/approach','data/analysis/ladder/dossier/local']
from scan import Board,replay
from scoreboard import load_replay
replay.load=load_replay
OUT=Path(__file__).resolve().parent

def audit(path,own,full=False):
 B=Board(Path(path));last={};deaths=[];turns=[];cur=None
 def close():
  nonlocal cur
  if cur:
   cur['end']=list(B.bodies[cur['id']][0]) if cur['id'] in B.bodies else None
   cur=None
 for ev in B.root.pointer(3):
  k=ev.u16(0);p=ev.pointer(0)
  if k in (0,1):close()
  if k==11 and B.teams[p.i32(0)]==own:
   i=p.i32(0)
   deaths.append(dict(r=B.rnd,id=i,L=len(B.bodies[i]),h=list(B.bodies[i][0]),reason=p.u16(4),actor=B.actor,last=last.get(i),attacker=cur))
  B.update(k,p)
  if k==1:
   i=B.actor;h=B.bodies[i][0]
   cur=dict(r=B.rnd,id=i,L=len(B.bodies[i]),h=list(h),body=list(B.bodies[i]),dirs=[],split=False,steps=[],eaten=[])
   if B.teams[i]==own:
    cur.update(bodies={z:list(b) for z,b in B.bodies.items()},teams=B.teams.copy(),pearls=list(B.pearls),visible=[z for z,b in B.bodies.items() if B.view(h,b[0])],adj=B.adj[h])
    last[i]=cur
    if full:turns.append(cur)
  elif cur:
   if k==4:
    a=p.pointer(0);cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) else [];cur['action']=a.u16(0) if a else None
   if k==9:cur['steps'].append(list(replay.point(p.pointer(0))))
   if k==10:cur['split']=True
   if k==3 and not p.u32(0):cur['eaten'].append(list(replay.point(p.pointer(0))))
 close()
 return dict(deaths=deaths,turns=turns)
if __name__=='__main__':
 x=audit('data/online/live-one1/b1476178/M1476178.replay',0,True)
 (OUT/'moments.json').write_text(json.dumps(x,indent=2))
 for d in x['deaths']:
  t=d['last'];a=d['attacker']
  print(d['r'],d['id'],'last',t['r'],t['h'],t['dirs'],t.get('end'),'ram',a['id'],a['L'],a['h'],a['dirs'],'seen',a['id'] in t['visible'])
 for t in x['turns']:
  if t['id']==0 and t['r']>=84:
   print('queen',t['r'],t['body'],t['dirs'],'adj',t['adj'],'visible bodies',[(i,b) for i,b in t['bodies'].items() if i in t['visible']], 'pearls',t['pearls'])
