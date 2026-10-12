import sys
sys.dont_write_bytecode=True
import analyze as a
import json
jobs=json.loads((a.O/'inventory.json').read_text())['games']
for j in jobs:
 p=a.O/f'g{j["gid"]}.json'
 if not p.exists():continue
 x=json.loads(p.read_text())
 if not x['death'] or x['v']==11 or x['death']['reason']==3 or any(c['team']==x['own'] and c['qvisible'] and c['L']<=3 for c in x['closures']):continue
 f=a.O/f'history{j["gid"]}.json'
 if not f.exists():
  y=a.scan(j);f.write_text(json.dumps(y['history'],ensure_ascii=False));print(j['gid'],flush=True)
