import sys,json
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/work']
import ladder_replay as lr
from pathlib import Path
OUT=Path('data/codex/astra/sweep/1055/loss1')
JOBS=[('data/online/live-one1/b1501017',1501019),('data/online/live-one1/b1501017',1501020),('data/online/smoke/one12-c1-old',1501665)]
for folder,gid in JOBS:
 p=Path(folder);j=json.loads((p/f'game-{gid}.json').read_text());g=lr.scan(p/f'M{gid}.replay',j,folder,set())
 g['intervals']={str(k):v for k,v in g['intervals'].items()}
 (OUT/f'{gid}-base.json').write_text(json.dumps(g,ensure_ascii=False))
 print(gid,'bots',g['bots'],'queens',g['queens'],'final',g['final'],'round',g['last_round'],'reason',g['end_reason'])
 print('queen deaths',[d for d in g['deaths'] if d['id'] in g['queens'].values()])
 print('checkpoints',[(r,s) for r,s in g['snapshots'].items() if r%50==0])
