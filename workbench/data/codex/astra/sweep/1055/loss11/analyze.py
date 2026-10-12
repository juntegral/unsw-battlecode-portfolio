import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
ROOT=Path.cwd(); OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'))
import ladder_replay as lr
sys.path.insert(0,str(ROOT/'data/analysis/ladder/dossier'))
from count_dossier import Geo
GAMES=[(1504150,'data/online/live-one1/b1504147'),(1504151,'data/online/live-one1/b1504147'),(1504479,'data/online/smoke/one12-k1-old')]
for gid,folder in GAMES:
 p=ROOT/folder/f'M{gid}.replay'; meta=json.loads((p.parent/f'game-{gid}.json').read_text())
 out=lr.scan(p,meta,folder,set())
 out.pop('intervals',None)
 (OUT/f'{gid}-ledger.json').write_text(json.dumps(out))
 print(gid,'bots',out['bots'],'final',out['final'],'q_eats',out['q_eats'],'q_splits',out['q_splits'])
 print('queen deaths',[d for d in out['deaths'] if d['id'] in out['queens'].values()])
 print('snaps',{r:s for r,s in out['snapshots'].items() if r%50==0 or r==499})
