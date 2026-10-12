import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'data/codex/astra/weak')
import analyze as prior
sys.path.insert(0,'data/analysis/ladder/dossier/work')
import o1_early
OUT=Path(__file__).resolve().parent
for gid in (1492096,1492098):
 rp=Path(f'data/online/smoke/one10-c1-old/M{gid}.replay')
 m=json.loads(rp.with_name(f'game-{gid}.json').read_text())
 (OUT/f'early-{gid}.json').write_text(json.dumps(o1_early.scan('one10-c1-old',rp,m)))
