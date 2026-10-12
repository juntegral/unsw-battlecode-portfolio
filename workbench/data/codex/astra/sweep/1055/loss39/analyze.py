import sys,json,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'));import ladder_replay as lr
sys.path.insert(0,str(ROOT/'data/analysis/ladder/dossier/local'));import scoreboard
lr.replay.load=scoreboard.load_replay
JOBS={1506915:'b1506911',1506149:'b1506148',1506150:'b1506148'}
for gid,folder in JOBS.items():
 p=ROOT/f'data/online/live-one1/{folder}/M{gid}.replay';m=json.loads(p.with_name(f'game-{gid}.json').read_text())
 d=lr.scan(p,m,str(p.parent),set());d.pop('intervals')
 (OUT/f'{gid}-base.json').write_text(json.dumps(d,ensure_ascii=False))
 print(json.dumps({k:d[k] for k in ('gid','map','bots','final','last_round','end_reason','q_eats','q_splits','eats','anomalies')},ensure_ascii=False))
 print('QUEENS',json.dumps([x for x in d['deaths'] if x['id'] in d['queens'].values()]))
 print('LONGS',json.dumps([{k:x[k] for k in ('id','round','length','cause','actor','hit','destination')} for x in d['deaths'] if x['side']=='us' and x['length']>=8]))
