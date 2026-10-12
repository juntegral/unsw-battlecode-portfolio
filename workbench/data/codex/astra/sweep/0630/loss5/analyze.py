import sys,json
from pathlib import Path
from collections import deque,Counter
sys.dont_write_bytecode=True
ROOT=Path.cwd(); OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'data/analysis/ladder/dossier/local')]
import ladder_replay as lr
from count_local import Geo
from scoreboard import load_replay
GAMES=[(1497633,'b1497630'),(1497386,'b1497386'),(1497387,'b1497386')]
for gid,folder in GAMES:
 p=ROOT/'data/online/live-one1'/folder/f'M{gid}.replay'; meta=json.loads(p.with_name(f'game-{gid}.json').read_text())
 root=load_replay(p).root(); lr.replay.load=lambda _: type('Loaded',(),{'root':lambda _:root})()
 base=lr.scan(p,meta,folder,set()); (OUT/f'{gid}-base.json').write_text(json.dumps({k:v for k,v in base.items() if k!='intervals'},ensure_ascii=False))
 print(gid,'bots',base['bots'],'queens',base['queens'],'end',base['last_round'],base['final'])
 print('queen deaths', [{k:v for k,v in d.items() if k not in ('pearls','body')} for d in base['deaths'] if d['id'] in base['queens'].values()])
 print('snaps',[(r,base['snapshots'][r]) for r in [0,20,50,100,150,200,300,400,499] if r in base['snapshots']])
