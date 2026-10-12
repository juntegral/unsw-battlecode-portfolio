import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path[:0]=['tools','data/analysis/ladder/dossier/work','data/analysis/ladder/dossier/local']
import ladder_replay as lr
import o1_scan
from count_local import Geo
OUT=Path('data/codex/astra/sweep/1055/loss41')
BASE=Path('data/online/live-one1/b1511406')
for gid in [1511407,1511409,1511410]:
 p=BASE/f'M{gid}.replay';j=json.loads((BASE/f'game-{gid}.json').read_text())
 full=lr.scan(p,j,'loss41',set()); ledger=o1_scan.scan('loss41',p,j)
 (OUT/f'{gid}-ledger.json').write_text(json.dumps(ledger))
 (OUT/f'{gid}-scan.json').write_text(json.dumps({k:v for k,v in full.items() if k not in ('intervals',)}))
 print(gid,full['bots'],full['queens'],full['last_round'],full['final'],ledger['how'])
 print('queen deaths', [d for d in full['deaths'] if d['id'] in full['queens'].values()])
 print('snaps', {r:v for r,v in full['snapshots'].items() if r in [25,50,75,100,150,200,300,400,499]})
