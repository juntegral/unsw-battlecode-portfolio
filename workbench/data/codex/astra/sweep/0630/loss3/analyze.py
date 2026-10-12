import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json
ROOT = Path.cwd()
OUT = ROOT/'data/codex/astra/sweep/0630/loss3'
sys.path.insert(0, str(ROOT/'tools'))
import ladder_replay as lr

for gid in (1496851,1496852,1496857):
    folder=ROOT/'data/online/smoke/one11-c1-old'
    meta=json.loads((folder/f'game-{gid}.json').read_text())
    result=lr.scan(folder/f'M{gid}.replay',meta,str(folder),set())
    result['intervals']={str(k):v for k,v in result['intervals'].items()}
    (OUT/f'{gid}-scan.json').write_text(json.dumps(result,ensure_ascii=False))
    print(gid, json.dumps({k:result[k] for k in ('bots','queens','final','last_round','end_reason','q_eats','q_splits','eats','anomalies')},ensure_ascii=False))
    print('QUEEN DEATHS', [d for d in result['deaths'] if d['id'] in result['queens'].values()])
    print('SNAPS', {r:result['snapshots'][r] for r in (0,50,100,150,200,300,400) if r in result['snapshots']})
