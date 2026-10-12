import sys
sys.dont_write_bytecode=True
import classify as c
import json
for p in c.O.glob('g*.json'):
 if not p.stem[1:].isdigit():continue
 x=json.loads(p.read_text())
 if x['v']==11:
  y=c.evalrow(x);(c.O/f'livecase{x["gid"]}.json').write_text(json.dumps(y,ensure_ascii=False));print(x['gid'],flush=True)
