"""Read-only one6 replay audit; outputs are confined to this folder."""
import sys
sys.dont_write_bytecode=True
sys.path[:0]=['data/codex/astra/approach']
from scan import Board,replay
from pathlib import Path
from collections import deque,Counter
import json,hashlib
from datetime import datetime
OUT=Path(__file__).resolve().parent

def scan(path,m,label):
 B=Board(path);own=int(m['teamAId']!=1119)
 if B.root.text(1+own)!='21033':return None
 qs=[min(i for i in B.bodies if B.teams[i]==s) for s in [own,1-own]]
 hist=[];cur=None;death=None;snaps={};last=None
 def snapshot():
  return [[len(bs:= [b for i,b in B.bodies.items() if B.teams[i]==s]),sum(map(len,bs)),max(map(len,bs),default=0),len(B.bodies.get(q,()))] for s,q in zip([own,1-own],qs)]
 def close():
  nonlocal cur
  if cur:
   cur['end']=list(B.bodies[qs[0]][0]) if qs[0] in B.bodies else None
   hist.append(cur);cur=None
 for ev in B.root.pointer(3):
  k=ev.u16(0);p=ev.pointer(0)
  if k in (0,1):close()
  if k==0 and B.rnd>=0:snaps[B.rnd]=snapshot()
  if k==11 and p.i32(0)==qs[0]:
   death=dict(r=B.rnd,reason=p.u16(4),actor=B.actor,body=list(B.bodies[qs[0]]),attacker=list(B.bodies.get(B.actor,[])),last3=hist[-3:])
  if cur and k==4:
   a=p.pointer(0);cur['action']=a.u16(0);cur['dirs']=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) else []
  B.update(k,p)
  if k==1 and B.actor==qs[0]:
   b=B.bodies[B.actor];h=b[0];occ={c for bb in B.bodies.values() for c in bb}
   opts=[{'dir':d,'dest':n} for d,n in enumerate(B.adj[h]) if n is not None and (n not in occ or n==b[-1])]
   cur=dict(r=B.rnd,body=list(b),options=opts,visible={i:list(bb) for i,bb in B.bodies.items() if i!=qs[0] and B.view(h,bb[0])},pearls=[c for c in B.pearls if B.view(h,c)])
 close();snaps[B.rnd]=snapshot()
 end=snaps[B.rnd]
 assert end[0][1]==m['scores'+'AB'[own]] and end[1][1]==m['scores'+'AB'[1-own]]
 result=B.root.pointer(4)
 for z in [0,1]:
  st=result.pointer([own,1-own][z]);assert st.i32(0)==end[z][0] and st.i32(4)==end[z][2] and st.i32(8)==end[z][1] and st.i32(12)==end[z][3]
 score=lambda s:(s[3],s[2],s[1])
 last=max((r for r,s in snaps.items() if s[0][0] and (not s[1][0] or score(s[0])>=score(s[1]))),default=-1)
 return dict(game=m['id'],map=m['mapName'],label=label,bot=21033,path=str(path),queen=qs[0],enemy_queen=qs[1],death=death,end=end,last_not_behind=last,snapshots=snaps if m['id']==1478190 else {},win=m['winner']=='ab'[own])

def main():
 jobs=[];seen=set()
 for label in ['one6-w1','one6-c1']:
  for p in sorted(Path('data/online/smoke',label+'-old').glob('game-*.json')):jobs.append((label,p))
 for p in sorted(Path('data/online/live-one1').glob('b*/game-*.json')):
  m=json.loads(p.read_text())
  if m.get('startedAt','')>='2026-10-08T16:34' and m.get('ranked'):jobs.append(('ranked' if m.get('ranked') else 'other',p))
 rows=[]
 for label,mp in jobs:
  m=json.loads(mp.read_text());gid=m['id']
  if gid in seen:continue
  seen.add(gid);p=mp.with_name(f'M{gid}.replay')
  if not p.exists():continue
  dest=OUT/f'game-{gid}.json'
  g=json.loads(dest.read_text()) if dest.exists() else scan(p,m,label)
  if not g:continue
  dest.write_text(json.dumps(g));rows.append(g);print(label,gid,g['map'],g['death'] and (g['death']['r'],g['death']['reason']),flush=True)
 (OUT/'inventory.json').write_text(json.dumps([{k:g[k] for k in ['game','label','path','bot']} for g in rows],indent=2))
 (OUT/'verification.json').write_text(json.dumps({'time':datetime.now().astimezone().isoformat(),'games':len(rows),'checks':'Each final N,total,longest,queen matched replay result; totals matched metadata.','source_sha256':hashlib.sha256(Path('data/online/smoke/one6-bot/main.cpp').read_bytes()).hexdigest()},indent=2))
if __name__=='__main__':main()
