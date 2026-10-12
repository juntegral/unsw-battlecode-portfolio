import sys,json
sys.dont_write_bytecode=True
sys.path.insert(0,'tools')
import ladder_replay as lr
from pathlib import Path
OUT=Path('data/codex/astra/sweep/1055/loss36')
SRC=Path('data/online/smoke/one13-q1-old')
for gid in (1515658,1515660,1515661):
 j=json.loads((SRC/f'game-{gid}.json').read_text())
 g=lr.scan(SRC/f'M{gid}.replay',j,str(SRC),set())
 # intervals use tuple keys
 g.pop('intervals')
 (OUT/f'{gid}-ledger.json').write_text(json.dumps(g))
 print(gid,{k:g[k] for k in ('bots','queens','q_eats','q_splits','final','last_round','eats','anomalies')})
 print('queen deaths',[d for d in g['deaths'] if d['id'] in g['queens'].values()])
 print('snaps',{r:g['snapshots'][r] for r in (50,100,200,300,400,499) if r in g['snapshots']})
