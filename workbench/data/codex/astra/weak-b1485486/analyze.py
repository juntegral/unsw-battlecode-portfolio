import sys,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
sys.path[:0]=['data/analysis/ladder/dossier/local','data/codex/astra/kraken']
import scoreboard,importlib.util
spec=importlib.util.spec_from_file_location("kraken_shared", "data/codex/astra/kraken/analyze.py")
shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared)
shared.lr.replay.load=scoreboard.load_replay
OUT=Path('data/codex/astra/weak-b1485486')
def run(mp):
 m=json.loads(mp.read_text()); rp=mp.with_name(f"M{m['id']}.replay"); out=OUT/f"M{m['id']}.json"
 if not rp.exists():return
 if out.exists():d=json.loads(out.read_text())['detail']
 else:
  d=shared.detail(rp,m); out.write_text(json.dumps({'meta':m,'path':str(rp),'sha256':hashlib.sha256(rp.read_bytes()).hexdigest(),'detail':d},separators=(',',':')))
 print(m['id'],m['mapName'],d['bots'],[(x['r'],x['id'],x['reason'],x['actor'],x['actorL'],x['step']) for x in d['deaths'] if x['id'] in d['queens']],d['snaps'].get('499',d['snaps'].get(499)),flush=True)
if __name__=='__main__':
 for gid in (1485486,1485489,1485490):run(Path(f'data/online/live-one1/b1485486/game-{gid}.json'))
