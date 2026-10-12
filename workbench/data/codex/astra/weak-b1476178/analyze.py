import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
sys.path.insert(0,'data/codex/astra/weak')
import analyze as prior
OUT=Path(__file__).resolve().parent
rp=Path('data/online/live-one1/b1476178/M1476178.replay')
m=json.loads(rp.with_name('game-1476178.json').read_text())
x=prior.extra(rp,m)
g=prior.o1_scan.scan('one6-live',rp,m)
(OUT/'target.json').write_text(json.dumps(dict(detail=x,scan=g),indent=2))
print('scan keys',g.keys())
print('submission',g.get('bot'),g.get('submission'),g.get('bot_id'))
print('end',x['all_snapshots'][max(x['all_snapshots'])],'turn',x['decisive_retrospective'])
print('queens',x['queens'])
print('queen deaths',json.dumps([d for d in x['deaths'] if d['queen']],indent=2))
print('last queen turns',json.dumps([t for t in x['queen_turns'] if t['side']==0][-4:],indent=2))
