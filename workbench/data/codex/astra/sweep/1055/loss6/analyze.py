import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,'data/analysis/ladder/dossier/work')
sys.path.insert(0,'tools')
import o1_scan
import ladder_replay as lr
sys.path.insert(0,'data/analysis/ladder/dossier/local')
import scoreboard
OUT=Path('data/codex/astra/sweep/1055/loss6')
for gid in (1503502,1503503,1503504):
 p=Path(f'data/online/smoke/one12-p1-old/M{gid}.replay'); j=json.loads(p.with_name(f'game-{gid}.json').read_text())
 root=scoreboard.load_replay(p).root()
 lr.replay.load=lambda _: type('Loaded',(),{'root':lambda _:root})()
 g=o1_scan.scan('one12-p1-old',p,j)
 d=lr.scan(p,j,'one12-p1-old',set())
 (OUT/f'{gid}-ledger.json').write_text(json.dumps(g))
 (OUT/f'{gid}-detail.json').write_text(json.dumps({k:v for k,v in d.items() if k!='intervals'}))
 print(gid,g['bot'],g['how'],g['last'],g['ends'])
 print('queens',d['queens'],'deaths',[v for v in d['deaths'] if v['id'] in d['queens'].values()])
 print('eats',d['eats'],'qeats',d['q_eats'],'qsplits',d['q_splits'])
 print('snaps',g['snaps'])
