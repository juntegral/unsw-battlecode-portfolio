import sys,json
from pathlib import Path
from collections import deque,Counter
sys.dont_write_bytecode=True
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'data/analysis/ladder/dossier/local')]
from count_local import Geo
from scoreboard import load_replay
out={}
for gid,folder in [(1497633,'b1497630'),(1497386,'b1497386'),(1497387,'b1497386')]:
 d=json.loads((OUT/f'{gid}-trace.json').read_text());b=json.loads((OUT/f'{gid}-base.json').read_text());root=load_replay(ROOT/'data/online/live-one1'/folder/f'M{gid}.replay').root();w=d['w'];h=d['h'];raw=[tuple(map(int,l.split()[1:4])) for l in root.text(0).splitlines() if l.startswith('EDGE ')];g=Geo(w,h,raw)
 bad=[];moves=0
 for t in d['turns']:
  src=t['start'][0]
  for direction,dest in zip(t['dirs'],t['moves']):
   moves+=1
   if g.moves[src][direction]!=(0,dest) and g.moves[src][direction]!=(2,dest):bad.append([t['round'],t['id'],src,direction,dest,g.moves[src][direction]])
   src=dest
 print(gid,'MOVE VALIDATION',moves,len(bad),bad[:3])
 def comp(src):
  reached={src};q=deque([src])
  while q:
   a=q.popleft()
   for z in g.adj[a]:
    if z not in reached:reached.add(z);q.append(z)
  return reached
 print('queen last moves')
 for q in d['qboards']:
  occ={c:int(i) for i,bb in q['bodies'].items() for c in bb};src=q['body'][0];print(q['round'],[(z,(c%w,c//w),k,occ.get(c)) for z,(k,c) in enumerate(g.moves[src])]);
 if gid==1497633:
  queen_turns=[t for t in d['turns'] if t['id']==1 and t['round']>=211];eqcomp=comp(queen_turns[0]['start'][0]);print('ENEMY QUEEN COMPONENT',len(eqcomp),'bounds',(min(c%w for c in eqcomp),max(c%w for c in eqcomp),min(c//w for c in eqcomp),max(c//w for c in eqcomp)))
  print('queen actual heads',sorted(set((t['start'][0]%w,t['start'][0]//w) for t in queen_turns)))
  qs=[t for t in d['turns'] if t['id']==0 and t['round']<209];seen={c for t in qs for c in g.window(t['start'][0])};print('portal exit previously directly seen',443 in seen)
  out[str(gid)]={'move_count':moves,'move_mismatches':bad,'enemy_queen_component':sorted(eqcomp),'enemy_queen_heads':sorted(set(t['start'][0] for t in queen_turns)),'portal_exit_seen_before':443 in seen}
 else:out[str(gid)]={'move_count':moves,'move_mismatches':bad}
(OUT/'checks.json').write_text(json.dumps(out))
