import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
sys.path.insert(0, 'tools')
import ladder_replay as lr

OUT = Path(__file__).resolve().parent
JOBS = [(1504731,1504730),(1504016,1504016),(1504017,1504016)]

for gid,bid in JOBS:
    folder = Path(f'data/online/live-one1/b{bid}')
    meta = json.loads((folder/f'game-{gid}.json').read_text())
    result = lr.scan(folder/f'M{gid}.replay',meta,str(folder),set())
    result.pop('intervals')
    (OUT/f'{gid}-ledger.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(gid, result['bots'], 'queens',result['queens'],'final',result['final'],'end',result['end_reason'],result['last_round'])
    print('Q deaths', [{k:v for k,v in d.items() if k not in ('pearls',)} for d in result['deaths'] if d['id'] in result['queens'].values()])
    print('Q eats/splits',result['q_eats'],result['q_splits'])
    print('checkpoints', {r:v for r,v in result['snapshots'].items() if r in (0,10,25,50,100,200,300,400,499)})
