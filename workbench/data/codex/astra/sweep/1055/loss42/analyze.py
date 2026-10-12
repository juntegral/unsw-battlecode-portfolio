import sys,json
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/work']
import ladder_replay as lr
sys.path.insert(0,"data/analysis/ladder/dossier/local")
import scoreboard
lr.replay.load=scoreboard.load_replay

from pathlib import Path
from collections import deque,Counter
OUT=Path('data/codex/astra/sweep/1055/loss42')
FOLDER=Path('data/online/live-one1/b1514288')
for gid in (1514288,1514290,1514291):
 meta=json.loads((FOLDER/f'game-{gid}.json').read_text());path=FOLDER/f'M{gid}.replay'
 s=lr.scan(path,meta,str(FOLDER),set())
 s.pop('intervals',None)
 (OUT/f'{gid}-base.json').write_text(json.dumps(s))
 print(gid, 'bots',s['bots'],'final',s['final'],'q',s['queens'],'qeats',s['q_eats'],'qsplits',s['q_splits'])
 print('queen deaths',[d for d in s['deaths'] if d['id'] in s['queens'].values()])
 print('snapshots', {r:s['snapshots'][r] for r in (50,100,200,300,400,499) if r in s['snapshots']})
