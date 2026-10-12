import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
from datetime import datetime
sys.path.insert(0,'tools')
from ladder_replay import replay
O=Path('data/codex/astra/longest');games=[json.loads(l) for name in ('games.jsonl','local.jsonl') for l in (O/name).read_text().splitlines()]; rows=[]
for g in games:
 p=Path(g['path']); root=replay.load(p).root(); fin=root.pointer(4)
 if g['label'].startswith('mA'):own=int(g['gid'][-1])
 else:own=0 if root.text(1)==g['bot'] else 1
 end=g['snapshots'][str(g['last'])]
 for s in (0,1):
  z=fin.pointer(own if s==0 else 1-own)
  assert (end[s]['alive'],end[s]['length'],end[s]['total'])==(z.i32(0),z.i32(4),z.i32(8)),g['gid']
 assert len({d['id'] for d in g['deaths']})==len(g['deaths']),g['gid']
 for d in g['deaths']:
  assert len(d['eaters'])<=(d['length']+1)//2
 for k,ss in g['snapshots'].items():
  if int(k)%25!=0:assert int(k)==g['last']
  for s in ss:assert s['role']!='fed' or s['stop_drop']>0
 rows.append(dict(gid=g['gid'],label=g['label'],path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),last=g['last'],queen_lengths=[fin.pointer(own).i32(12),fin.pointer(1-own).i32(12)]))
(O/'verification.json').write_text(json.dumps(dict(time=datetime.now().astimezone().isoformat(),checked=len(rows),terminal_mismatches=0,inputs=rows),ensure_ascii=False,indent=2))
print('verified terminal alive/longest/total, unique deaths, drop bounds:',len(rows))
