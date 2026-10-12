import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path('tools').resolve()))
import ladder_replay as lr
OUT=Path(__file__).resolve().parent
for gid in (1512561,1512562,1512563):
 p=Path(f'data/online/smoke/one13-p2-old/M{gid}.replay')
 meta=json.loads(p.with_name(f'game-{gid}.json').read_text())
 d=lr.scan(p,meta,'one13-p2-old',set())
 d.pop('intervals')
 (OUT/f'{gid}-scan.json').write_text(json.dumps(d,ensure_ascii=False))
 print(gid, 'bots',d['bots'],'final',d['final'],'round',d['last_round'],'queens',d['queens'],'eats',d['q_eats'],'splits',d['q_splits'])
 print('queen deaths',[x for x in d['deaths'] if x['id'] in d['queens'].values()])
 print('snapshots',{r:s for r,s in d['snapshots'].items() if r in (0,25,50,100,150,200,300,400,499,500)})
