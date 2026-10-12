import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
sys.path[:0]=['tools','data/analysis/ladder/dossier/work','data/analysis/ladder/dossier/local']
import o1_scan,ladder_replay
OUT=Path('data/codex/astra/sweep/1055/loss2')
D=Path('data/online/smoke/one12-c1-old')
for gid in [1501666,1501667,1501668]:
 j=json.loads((D/f'game-{gid}.json').read_text())
 a=o1_scan.scan('one12-c1-old',D/f'M{gid}.replay',j)
 b=ladder_replay.scan(D/f'M{gid}.replay',j,str(D),set())
 (OUT/f'{gid}-counts.json').write_text(json.dumps(a))
 (OUT/f'{gid}-ledger.json').write_text(json.dumps({k:v for k,v in b.items() if k!='intervals'}))
 print(gid,a['how'],a['bot'],a['ends'])
 print('QUEENS',b['queens'],'deaths',[d for d in b['deaths'] if d['id'] in b['queens'].values()])
 print('SNAPS',a['snaps'])
 print('Qeats/splits',b['q_eats'],b['q_splits'])
