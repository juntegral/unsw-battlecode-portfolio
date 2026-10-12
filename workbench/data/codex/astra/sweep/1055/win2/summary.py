import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
sys.path.insert(0,'tools')
import ladder_replay as lr
OUT=Path(__file__).resolve().parent
JOBS=[(i,'data/online/smoke/one12-k1-old') for i in (1504483,1504485,1504487,1504488,1504490,1504491)]
JOBS += [(i,'data/online/live-one1/b1504730') for i in (1504730,1504732,1504733,1504734)]
JOBS += [(i,'data/online/live-one1/b1501263') for i in (1501263,1501264)]
rows=[]
for gid,folder in JOBS:
    p=Path(folder)/f'M{gid}.replay';meta=json.loads(p.with_name(f'game-{gid}.json').read_text())
    g=lr.scan(p,meta,folder,set())
    def key(s):return (int(s['alive']>0),s['queen_length'],s['longest'],s['total'])
    g['permanent_lead']=1+max((r for r,s in g['snapshots'].items() if key(s['us'])<=key(s['them'])),default=-1)
    g['queen_deaths']={s:next((d for d in g['deaths'] if d['id']==g['queens'][s]),None) for s in ('us','them')}
    g.pop('intervals')
    (OUT/f'{gid}-base.json').write_text(json.dumps(g,separators=(',',':')))
    rows.append({k:g[k] for k in ('gid','map','ours','last_round','final','permanent_lead','queen_deaths','anomalies')})
    print(json.dumps(rows[-1],ensure_ascii=False),flush=True)
(OUT/'base-summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
