import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'data/analysis/ladder/dossier/work')
import o1_scan
P=Path(__file__).resolve().parent
out=[]
for gid in (1493878,1492097,1494957):
 g=json.loads((P/f'{gid}.json').read_text());base=Path('data/online/smoke',g['label']+'-old');m=json.loads((base/f'game-{gid}.json').read_text());ref=o1_scan.scan(g['label'],base/f'M{gid}.replay',m)
 for side in (0,1):
  for name,k in [('eats','eats'),('splits','splits'),('deaths','deaths')]:
   a=sum(x['side']==side for x in g[k]);b=sum(x[0]<=100 and x[1]==side for x in ref[k]);assert a==b,(gid,name,side,a,b)
  assert sum(t['paid'] for t in g['turns'] if t['side']==side)==sum(x[3] for x in ref['paids'] if x[0]<=100 and x[1]==side)
  for origin in ('natural','corpse'):
   assert sum(e['side']==side and e['origin']==origin for e in g['eats'])==sum(x[0]<=100 and x[1]==side and (x[3]=='n')==(origin=='natural') for x in ref['eats'])
 out.append({'gid':gid,'match':True})
(P/'verification.json').write_text(json.dumps(out,indent=2));print(out)
