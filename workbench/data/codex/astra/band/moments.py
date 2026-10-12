import json,collections
from pathlib import Path
G=list(map(json.loads,Path('data/codex/astra/band/games.jsonl').read_text().splitlines()))
for name in sorted({g['opp'] for g in G}):
 print('\nTEAM',name)
 for g in G:
  if g['opp']!=name:continue
  nr=[sum(d[4]=='rammed' and d[1]==s for d in g['deaths']) for s in (0,1)]
  e=[sum(z[0]<=50 and z[1]==s for z in g['eats']) for s in (0,1)]
  qd=[(d['side'],d['round'],d['length'],d['cause'],d['actor']) for d in g['queen_deaths']]
  print(g['gid'],g['map'],g['bot'],'R' if g['ranked'] else 'U',g['result'],g['how'],'turn',g['turn_round'],'Qend',[g['ends'][s][3] for s in (0,1)],'long',[g['ends'][s][2] for s in (0,1)],'rammed us/them',nr,'P50',e,'Qdeaths',qd)
  if g['result']=='loss':
   for d in g['deaths']:
    if d[1]==0 and (d[6] or (d[2]>=15 and d[0]>=300)):
     print(' death',d)
