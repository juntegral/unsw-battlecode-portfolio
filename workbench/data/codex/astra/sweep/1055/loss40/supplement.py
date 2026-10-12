import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter
sys.path.insert(0,str(Path.cwd()/'data/analysis/ladder/dossier/local'))
from count_local import Geo
P=Path(__file__).parent
out={}
for gid in (1506151,1506152,1511406):
 b=json.loads((P/f'{gid}-base.json').read_text());d=json.loads((P/f'{gid}-trace.json').read_text());w,h=d['size']
 g=Geo(w,h,[tuple(map(int,l.split()[1:4])) for l in b['text'].splitlines() if l.startswith('EDGE ')])
 a={'permanent_total_deficit':1+max((int(r) for r,s in b['snapshots'].items() if s['us']['total']>=s['them']['total']),default=-1),'windows':[],'legal':[]}
 for lo,hi in [(0,100),(101,300),(301,b['last_round'])]:
  if lo>hi:continue
  ts=[t for t in d['turns'] if t['side']==1 and lo<=t['round']<=hi]
  a['windows'].append(dict(lo=lo,hi=hi,turns=len(ts),eats=sum(t['eats'] for t in ts),move_noeat=sum(bool(t['moves']) and not t['eats'] for t in ts),splits=sum(bool(t['action']) and t['action']['kind']==1 for t in ts)))
 for f in d['focused']:
  occ={y*w+x:i for i,bb in f['bodies'].items() for x,y in bb};x,y=f['body'][0];c=y*w+x
  row={'round':f['round'],'neighbors':[]}
  for dr,(kind,n) in enumerate(g.moves[c]):row['neighbors'].append(dict(direction='NESW'[dr],xy=[n%w,n//w],edge=kind,occupant=occ.get(n)))
  a['legal'].append(row)
 a['queen_growth_after_last_split']={}
 if d['splits']:
  r=d['splits'][-1]['round'];ts=[t for t in d['queen_turns'] if t['round']>r]
  a['queen_growth_after_last_split']=dict(after=r,turns=len(ts),eats=sum(t['eats'] for t in ts),unique_heads=len({tuple(t['head']) for t in ts}))
 out[gid]=a
 print(gid,json.dumps(a,ensure_ascii=False))
(P/'supplement.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
