import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
import analyze
O=analyze.OUT
jobs={}
for f in Path('data/online/smoke').glob('one8-*-old'):
 for mp in f.glob('game-*.json'): jobs[json.loads(mp.read_text())['id']]=mp
for f in Path('data/online/live-one1').glob('b*'):
 for mp in f.glob('game-*.json'):
  m=json.loads(mp.read_text())
  if m.get('startedAt','')>='2026-10-08T18:09:00' and m.get('startedAt','')<='2026-10-08T18:56:00':jobs[m['id']]=mp
for gid,mp in sorted(jobs.items()):
 out=O/f'M{gid}.json'; cache=Path(f'data/codex/astra/kraken/M{gid}.json')
 if not out.exists() and cache.exists():
  c=json.loads(cache.read_text());c.pop('ledger',None);c['path']=str(mp.with_name(f'M{gid}.replay'));out.write_text(json.dumps(c,separators=(',',':')))
 analyze.run(mp)
(O/'inventory.json').write_text(json.dumps({str(k):str(v) for k,v in jobs.items()},indent=2))
