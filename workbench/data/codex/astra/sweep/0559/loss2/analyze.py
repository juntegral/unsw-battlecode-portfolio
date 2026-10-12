import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path.cwd(); OUT=ROOT/'data/codex/astra/sweep/0559/loss2'
sys.path.insert(0,str(ROOT/'tools'))
import ladder_replay as lr
for gid in (1494957,1494958,1494959):
 p=ROOT/f'data/online/smoke/one8-p1-old/M{gid}.replay'
 meta=json.loads(p.with_name(f'game-{gid}.json').read_text())
 d=lr.scan(p,meta,str(p.parent),set())
 d.pop('intervals')
 (OUT/f'{gid}-base.json').write_text(json.dumps(d,ensure_ascii=False))
 print(json.dumps({k:d[k] for k in ('gid','map','bots','final','last_round','end_reason','q_eats','q_splits','eats','anomalies')},ensure_ascii=False))
 print('QUEEN DEATHS',json.dumps([x for x in d['deaths'] if x['id'] in d['queens'].values()]))
 print('LONG DEATHS',json.dumps([{k:x[k] for k in ('id','round','length','cause','actor','hit','destination')} for x in d['deaths'] if x['side']=='us' and x['length']>=8]))
