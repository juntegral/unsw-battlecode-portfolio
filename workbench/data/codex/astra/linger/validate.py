import sys
sys.dont_write_bytecode=True
sys.path[:0]=['data/analysis/ladder/dossier/work']
from o1_scan import scan
from pathlib import Path
import json
from collections import Counter
OUT=Path('data/codex/astra/linger')
rows=[]
for gid in (1460555,1460561,1471457,1471458,1471462):
 g=json.loads((OUT/f'g{gid}.json').read_text());folder=Path('data/online/smoke')/(g['label']+'-old')
 m=json.loads((folder/f'game-{gid}.json').read_text());old=scan(g['label'],folder/f'M{gid}.replay',m)
 counted=Counter(x[1] for x in old['eats'] if x[3]=='n')
 assert [counted[s] for s in (0,1)]==g['natural_eats']
 counts=Counter((x[0],x[1]) for x in old['eats'] if x[3]=='n' and 0<=x[0]<=300)
 assert counts==Counter((x['r'],x['s']) for x in g['meals'])
 rows.append(dict(gid=gid,natural_eats=g['natural_eats'],per_round_side_matched=True))
(OUT/'validation.json').write_text(json.dumps(rows,indent=2));print(rows)
