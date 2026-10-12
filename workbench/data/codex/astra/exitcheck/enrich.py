import sys
sys.dont_write_bytecode=True
import classify as c
import json
for p in sorted(c.O.glob('g*.json')):
 if not p.stem[1:].isdigit():continue
 x=json.loads(p.read_text())
 if not x['selected'] or x['v']==11:continue
 f=c.O/f'case{x["gid"]}.json'
 if f.exists():
  old=json.loads(f.read_text())
  if x['death']['reason']==3:continue
 y=c.evalrow(x);f.write_text(json.dumps(y,ensure_ascii=False));print(x['gid'],flush=True)
