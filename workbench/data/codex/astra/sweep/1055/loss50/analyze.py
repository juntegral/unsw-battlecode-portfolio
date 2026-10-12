import sys, ast, types, json
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,'tools')
import ladder_replay as lr
p=Path('data/analysis/ladder/dossier/work/tq2_scan.py')
tree=ast.parse(p.read_text()); tree.body=tree.body[:-1]
tq=types.ModuleType('tq'); exec(compile(tree,str(p),'exec'),tq.__dict__)
OUT=Path('data/codex/astra/sweep/1055/loss50')
JOBS=[(1512825,'data/online/live-one1/b1512823','B'),(1517686,'data/online/smoke/one14-c1-old','A'),(1517687,'data/online/smoke/one14-c1-old','A')]
for gid,folder,side in JOBS:
    rp=Path(folder)/f'M{gid}.replay'; meta=json.loads((Path(folder)/f'game-{gid}.json').read_text())
    a=lr.scan(rp,meta,folder,set()); b=tq.scan(rp,side,dict(game=gid),{})
    (OUT/f'{gid}-ledger.json').write_text(json.dumps({k:v for k,v in a.items() if k!='intervals'},ensure_ascii=False,indent=1))
    (OUT/f'{gid}-queens.json').write_text(json.dumps(b,ensure_ascii=False,indent=1))
    print(gid,a['bots'], 'final',a['final'],'decision',b['decided'],'fate',b['fate'],'qeats',a['q_eats'],'splits',b['splits'])
    print('snapshots',b['snaps'])
    print('last own queen turns',b['recs'][0][-5:])
