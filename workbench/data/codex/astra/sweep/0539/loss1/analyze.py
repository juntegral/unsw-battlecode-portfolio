import sys,json
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/work']
import ladder_replay as lr
import o1_scan
from pathlib import Path
OUT=Path('data/codex/astra/sweep/0539/loss1')
D=Path('data/online/live-one1/b1493690')
for gid in [1493690,1493693,1493694]:
 j=json.loads((D/f'game-{gid}.json').read_text()); p=D/f'M{gid}.replay'
 a=lr.scan(p,j,str(D),set()); b=o1_scan.scan('loss1',p,j)
 a['intervals']={str(k):v for k,v in a['intervals'].items()}
 (OUT/f'{gid}-ledger.json').write_text(json.dumps(a))
 (OUT/f'{gid}-counts.json').write_text(json.dumps(b))
 print(gid,a['bots'],a['final'],'queens',a['queens'],'qdead',[(d['round'],d['id'],d['actor'],d['length'],d['body'],d['cause']) for d in a['deaths'] if d['id'] in a['queens'].values()])
