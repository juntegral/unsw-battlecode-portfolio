import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
sys.path[:0]=['tools','data/analysis/ladder/dossier/work','data/analysis/ladder/dossier/local']
import ladder_replay as lr
import o1_scan
from count_local import Geo
OUT=Path(__file__).resolve().parent
F=Path('data/online/smoke/one13-k1-old')
for gid in (1509102,1509107,1509108):
 p=F/f'M{gid}.replay';meta=json.loads((F/f'game-{gid}.json').read_text())
 a=lr.scan(p,meta,str(F),set());b=o1_scan.scan('one13-k1-old',p,meta)
 (OUT/f'{gid}-base.json').write_text(json.dumps({k:v for k,v in a.items() if k != 'intervals'},ensure_ascii=False,default=list))
 (OUT/f'{gid}-ledger.json').write_text(json.dumps(b,ensure_ascii=False))
 print(gid,a['bots'],a['final'],'end',a['last_round'],b['how'])
 print('queens',a['queens'],'queen deaths',[d for d in a['deaths'] if d['id'] in a['queens'].values()])
 print('q eats/splits',a['q_eats'],a['q_splits'])
 print('snaps',b['snaps'])
