import sys,json
sys.dont_write_bytecode=True
sys.path.insert(0,'tools')
import ladder_replay as LR
from pathlib import Path
OUT=Path('data/codex/astra/sweep/1055/loss47')
SM=Path('data/online/smoke/one13-k2-old')
for gid in (1513836,1513839,1513840):
 j=json.loads((SM/f'game-{gid}.json').read_text())
 a=LR.scan(SM/f'M{gid}.replay',j,str(SM),set())
 a['intervals']={str(k):v for k,v in a['intervals'].items()}
 (OUT/f'{gid}-ledger.json').write_text(json.dumps(a,ensure_ascii=False))
 print(gid,a['bots'],a['final'],'queens',a['queens'],'end',a['end_reason'],a['last_round'])
 print('queen deaths',[d for d in a['deaths'] if d['id'] in a['queens'].values()])
 print('checkpoints',{r:a['snapshots'][r] for r in (0,25,50,100,200,300,400,499) if r in a['snapshots']})
 print('last deaths',a['deaths'][-8:])
