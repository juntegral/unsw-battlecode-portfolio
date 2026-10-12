"""Maps where the centre rule is on (cells <= 1000 and (width >= 2*height or cells <= 700)) against the rest. Online labels."""
import sys
sys.dont_write_bytecode=True
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from summ import games,measure
agg=defaultdict(lambda:defaultdict(list))
for label in sys.argv[1:]:
 for g in games(label):
  W,H=g['size'];cells=W*H;on=cells<=1000 and (W>=2*H or cells<=700);rounds=(60 if W>=2*H else 30) if on else 0
  u=measure(g,0);t=measure(g,1)
  fe=[min((e['r'] for e in g['eats'] if e['side']==s and e['origin']=='natural' and e['r']>3),default=101) for s in (0,1)]
  e3=[sorted(e['r'] for e in g['eats'] if e['side']==s and e['origin']=='natural')[2:3] or [101] for s in (0,1)]
  key='centre rule ON ' if on else 'centre rule off'
  for k,v in (('eat50',(u['eat50'],t['eat50'])),('eat100',(u['eat100'],t['eat100'])),('len100',(u['len100'],t['len100'])),('third natural pearl round',(e3[0][0],e3[1][0])),('heads50',(u['heads50'],t['heads50']))):agg[key][k].append(v)
  agg[key]['maps'].append('%s %dx%d %s e100 %d/%d third %d/%d'%(g['map'][:10],W,H,label[-6:],u['eat100'],t['eat100'],e3[0][0],e3[1][0]))
for key,d in sorted(agg.items()):
 n=len(d['eat100']);print(key,'games',n,'| '+' | '.join('%s us %.1f / them %.1f (us lower in %d, higher in %d)'%(k,sum(a for a,b in v)/n,sum(b for a,b in v)/n,sum(a<b for a,b in v),sum(a>b for a,b in v)) for k,v in d.items() if k!='maps'))
 if 'ON' in key:
  for m in d['maps']:print('     ',m)
