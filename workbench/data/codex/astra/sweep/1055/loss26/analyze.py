import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/work']
import ladder_replay as lr
import o1_scan
OUT=Path('data/codex/astra/sweep/1055/loss26')
GAMES=[(1512749,1512747),(1507572,1507572),(1507575,1507572)]
for gid,bid in GAMES:
 p=Path(f'data/online/live-one1/b{bid}/M{gid}.replay'); m=json.loads(p.with_name(f'game-{gid}.json').read_text())
 x=lr.scan(p,m,'loss26',set()); y=o1_scan.scan('loss26',p,m)
 x.pop('intervals'); x.pop('text'); x['ledger']=y
 (OUT/f'{gid}.json').write_text(json.dumps(x,ensure_ascii=False))
 print(gid,'bots',x['bots'],'final',x['final'],'how',y['how'],'queens',x['queens'],'q_eats',x['q_eats'],'q_splits',x['q_splits'])
 print('queen deaths',[d for d in x['deaths'] if d['id'] in x['queens'].values()]);print('snapshots',y['snaps'])
