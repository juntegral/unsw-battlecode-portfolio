"""Where natural pearls are eaten: distinct tiles per side, eats per tile, and how many dragons do the eating. r0-100."""
import sys
sys.dont_write_bytecode=True
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from summ import games
for label in sys.argv[1:]:
 T=[Counter(),Counter()];lo=hi=0;per=[]
 n=0
 for g in games(label):
  n+=1;row=[]
  for s in (0,1):
   E=[e for e in g['eats'] if e['side']==s and e['origin']=='natural' and e['r']<=100]
   tiles=Counter(tuple(e['xy']) for e in E);r50={tuple(e['xy']) for e in E if e['r']<=50}
   T[s]['eats']+=len(E);T[s]['tiles']+=len(tiles);T[s]['tiles50']+=len(r50);T[s]['repeat']+=sum(v-1 for v in tiles.values());T[s]['eaters']+=len({e['id'] for e in E})
   row.append(len(tiles))
  lo+=row[0]<row[1];hi+=row[0]>row[1];per.append('%s %d/%d'%(g['map'][:8],row[0],row[1]))
 print('%-10s natural pearls r0-100, per game us/them: eaten %.1f/%.1f | different tiles eaten from %.1f/%.1f (by r50 %.1f/%.1f) | repeat eats on a tile %.1f/%.1f | dragons that ate %.1f/%.1f | maps with fewer tiles for us %d, more %d'%(label,T[0]['eats']/n,T[1]['eats']/n,T[0]['tiles']/n,T[1]['tiles']/n,T[0]['tiles50']/n,T[1]['tiles50']/n,T[0]['repeat']/n,T[1]['repeat']/n,T[0]['eaters']/n,T[1]['eaters']/n,lo,hi))
 print('     tiles per map:',' '.join(per))
