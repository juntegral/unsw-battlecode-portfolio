import sys,json
sys.dont_write_bytecode=True
sys.path.insert(0,'tools')
import ladder_replay as lr
from pathlib import Path
OUT=Path(__file__).resolve().parent
JOBS=[(1513846,'data/online/smoke/one13-k2-old'),(1513847,'data/online/smoke/one13-k2-old'),(1512824,'data/online/live-one1/b1512823')]
for gid,folder in JOBS:
 p=Path(folder)/f'M{gid}.replay'; meta=json.loads(p.with_name(f'game-{gid}.json').read_text())
 z=lr.scan(p,meta,folder,set())
 z.pop('intervals')
 (OUT/f'{gid}-base.json').write_text(json.dumps(z,ensure_ascii=False))
 print(gid, 'bots',z['bots'],'final',z['final'],'queens',z['queens'],'eats',z['q_eats'],'splits',z['q_splits'])
 print('qdeath',[d for d in z['deaths'] if d['id'] in z['queens'].values()])
 print('snapshots',[(r,z['snapshots'][r]) for r in (0,50,100,200,300,400,499) if r in z['snapshots']])
