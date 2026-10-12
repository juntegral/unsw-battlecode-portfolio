import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'data/codex/astra/weak')
import analyze as prior
from ladder_replay import scan
OUT=Path(__file__).resolve().parent
for gid in (1492096,1492097,1492098):
 rp=Path(f'data/online/smoke/one10-c1-old/M{gid}.replay'); m=json.loads(rp.with_name(f'game-{gid}.json').read_text())
 x=prior.extra(rp,m); g=scan(rp,m,'one10-c1-old',set())
 g.pop('intervals',None)
 (OUT/f'{gid}.json').write_text(json.dumps(dict(detail=x,scan=g),ensure_ascii=False))
 print(gid,g['bots'],g['final'],'turn',x['decisive_retrospective'])
 print('queen deaths',json.dumps([d for d in g['deaths'] if d['id'] in g['queens'].values()]))
 print('last turns',json.dumps([t for t in x['queen_turns'] if t['side']==0][-3:]))
 print('checkpoints',[(r,g['snapshots'].get(r)) for r in (0,20,50,100,200,300,400,499)])
