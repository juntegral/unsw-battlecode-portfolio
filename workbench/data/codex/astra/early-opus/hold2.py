import sys
sys.dont_write_bytecode=True
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from summ import games
for label in sys.argv[1:]:
 for s in (0,1):
  C=Counter();ng=0;run=Counter();after=Counter()
  for g in games(label):
   ng+=1;prev={};streak=Counter()
   for t in g['turns']:
    if t['side']!=s:continue
    i=t['id'];ate=sum(t['eats'].values())>0;p=prev.get(i);prev[i]=(t['r'],ate)
    if t['queen'] or t['L']<4:continue
    if t['split']:
     C['split']+=1;run[min(streak[i],6)]+=1;streak[i]=0;continue
    streak[i]+=1
    foe=any(z[1]!=s for z in t['near_heads']);mate=any(z[1]==s for z in t['near_heads'])
    geo='tailport' if t['tail_portal'] else 'spans' if t['tail_spans'] else 'tailexit0' if t['tail_exits']==0 else 'room<4' if t['tail_room']<4 else 'free'
    C['hold']+=1
    C['hold foe in view']+=foe
    C['hold ate now']+=ate
    C['hold ate now or last turn']+=ate or bool(p and p[0]==t['r']-1 and p[1])
    C['hold died']+=t['dead']
    C['hold free, no foe, no eating']+=(geo=='free' and not foe and not ate and not (p and p[0]==t['r']-1 and p[1]))
    C['hold geo '+geo]+=1
    C['hold paid']+=t['paid']>0
    C['hold moves2+']+=len(t['moves'])>1
  print(label,'side',s,'per game:',' | '.join('%s %.1f'%(k,v/ng) for k,v in sorted(C.items())))
  print('    turns held before each split (0 = split on the first turn at 4+):',' '.join('%d:%.1f'%(k,v/ng) for k,v in sorted(run.items())))
