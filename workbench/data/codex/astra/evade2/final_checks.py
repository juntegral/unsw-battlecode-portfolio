import sys,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter
from datetime import datetime
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT.parent/'evade'))
import analyze as a
result=[]
for label in ('one5-w1','one5-c1','one7-w1','one7-c1'):
 counts=Counter()
 for p,m in a.label_report.inventory(label,'old')['jobs']:
  root=a.lr.replay.load(p).root()
  assert root.text(1 if m['teamAId']==1119 else 2)==('21086' if label.startswith('one7') else '20980')
  counts.update(a.lr.replay.EVENT_NAMES[e.u16(0)] for e in root.pointer(3))
 result.append(dict(label=label,event_counts=dict(counts)))
 print(label,'logs',counts['dragonLog'],flush=True)
(OUT/'input-audit.json').write_text(json.dumps(dict(time=datetime.now().astimezone().isoformat(),sets=result,sources={str(p.relative_to(a.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.ROOT/'data/online/smoke/one5-bot/main.cpp',a.ROOT/'data/online/smoke/one7-bot/main.cpp']}),indent=2))
