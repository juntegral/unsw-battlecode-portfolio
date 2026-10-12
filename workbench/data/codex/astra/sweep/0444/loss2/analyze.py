import sys,json
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/work']
from ladder_replay import scan,replay
from pathlib import Path
from collections import deque,Counter
OUT=Path('data/codex/astra/sweep/0444/loss2')
F=Path('data/online/live-one1/b1488845')
for gid in (1488848,1488849):
 meta=json.loads((F/f'game-{gid}.json').read_text())
 z=scan(F/f'M{gid}.replay',meta,str(F),set())
 (OUT/f'{gid}-base.json').write_text(json.dumps({k:v for k,v in z.items() if k != 'intervals'}))
 print(gid,z['bots'],z['final'],'round',z['last_round'],'queens',z['queens'])
 print('queen deaths',[d for d in z['deaths'] if d['id'] in z['queens'].values()])
 print('snapshots',[(r,z['snapshots'].get(r)) for r in (0,25,50,100,150,200,300,400,450,499)])
 print('last deaths',[(d['round'],d['id'],d['length'],d['cause'],d['actor']) for d in z['deaths'][-15:]])
