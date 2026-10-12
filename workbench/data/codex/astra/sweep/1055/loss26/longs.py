import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
sys.path[:0]=['data/analysis/ladder/dossier/work']
import o1_long
O=Path('data/codex/astra/sweep/1055/loss26')
for g in (1507572,1507575):
 p=Path(f'data/online/live-one1/b1507572/M{g}.replay');m=json.loads(p.with_name(f'game-{g}.json').read_text());x=o1_long.scan('loss26',p,m)
 (O/f'{g}-longs.json').write_text(json.dumps(x));print(g,[r for r in x['rams'] if r['s']==0],flush=True)
