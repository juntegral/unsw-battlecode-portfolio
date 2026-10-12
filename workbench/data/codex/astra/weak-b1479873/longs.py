import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
sys.path[:0]=['data/analysis/ladder/dossier/work','data/analysis/ladder/dossier/local']
import o1_long
from scoreboard import load_replay
o1_long.replay.load=load_replay
out=Path(__file__).resolve().parent
rows=json.loads((out/'samples.json').read_text());paths={int(p.stem[5:]):p for p in Path('data/online/live-one1').glob('b*/game-*.json')}
for p in Path('data/online/smoke').glob('one6-*-old/game-*.json'):paths[int(p.stem[5:])]=p
result=[]
for r in rows:
 p=paths[r['game']];c=out/f"long-{r['game']}.json"
 if c.exists():x=json.loads(c.read_text())
 else:
  x=o1_long.scan(r['group'],p.with_name(f"M{r['game']}.replay"),json.loads(p.read_text()));c.write_text(json.dumps(x))
 result.append(x);print(r['game'],len([z for z in x['rams'] if z['s']==0]),flush=True)
(out/'longs.json').write_text(json.dumps(result))
