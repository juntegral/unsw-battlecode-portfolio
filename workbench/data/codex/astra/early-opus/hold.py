import sys
sys.dont_write_bytecode=True
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from summ import games
for label in sys.argv[1:]:
 for s in (0,1):
  C=Counter();n=0;ng=0;dl=Counter();dn=Counter();phase=Counter();pn=Counter();eatL=Counter();tl=Counter()
  for g in games(label):
   ng+=1
   for t in [x for x in g['turns'] if x['side']==s]:
    n+=1;Lb=min(t['L'],5);tl[Lb]+=1;dl[Lb]+=min(t['d0'],40);eatL[Lb]+=sum(t['eats'].values())
    ph=min(t['r']//25,3);pn[ph]+=1;phase[ph]+=min(t['d0'],40)
    if t['L']>=4 and not t['split']:
     C[('queen ' if t['queen'] else 'other ')+('L4' if t['L']==4 else 'L5+')+(' tailport' if t['tail_portal'] else ' spans' if t['tail_spans'] else ' tailexit0' if t['tail_exits']==0 else ' room<4' if t['tail_room']<4 else ' free')]+=1
  print(label,'side',s,'turns/game %.0f'%(n/ng),'| turn share by L(2,3,4,5+):',' '.join('%d:%.0f%%'%(k,100*tl[k]/n) for k in sorted(tl)),'| mean dist to pearl by L:',' '.join('%d:%.1f'%(k,dl[k]/tl[k]) for k in sorted(tl)),'| eats/100 turns by L:',' '.join('%d:%.1f'%(k,100*eatL[k]/tl[k]) for k in sorted(tl)),'| dist by 25-round phase:',' '.join('%.1f'%(phase[k]/pn[k]) for k in sorted(pn)))
  print('    L>=4 no-split turns per game:',' , '.join('%s %.1f'%(k,v/ng) for k,v in C.most_common()))
