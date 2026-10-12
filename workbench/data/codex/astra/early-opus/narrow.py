"""Narrow ground: share of non-queen length 2-3 turns that start on a cell with at most 2 open sides (corridor or dead end),
and what they eat there. r0-100, both sides."""
import sys
sys.dont_write_bytecode=True
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from summ import games
for label in sys.argv[1:]:
 T=[Counter(),Counter()];lo=hi=0;per=[];n=0
 for g in games(label):
  n+=1;row=[]
  for s in (0,1):
   c=Counter()
   for t in g['turns']:
    if t['side']!=s or t['queen'] or t['L']>3:continue
    k='narrow' if t['deg']<=2 else 'open';c[k]+=1;c[k+' eat']+=sum(t['eats'].values())
    if t['r']<=30:c[k+'30']+=1
   T[s].update(c);row.append(100*c['narrow']/max(c['narrow']+c['open'],1))
  if abs(row[0]-row[1])>=1:lo+=row[0]<row[1];hi+=row[0]>row[1]
  per.append('%s %.0f/%.0f'%(g['map'][:8],row[0],row[1]))
 f=lambda s:100*T[s]['narrow']/max(T[s]['narrow']+T[s]['open'],1)
 f30=lambda s:100*T[s]['narrow30']/max(T[s]['narrow30']+T[s]['open30'],1)
 e=lambda s,k:100*T[s][k+' eat']/max(T[s][k],1)
 print('%-9s short non-queen turns on narrow cells: us %.1f%% / them %.1f%% (r0-30: %.1f%% / %.1f%%) | maps us lower %d, higher %d | turns per game on narrow cells %.0f / %.0f | pearls per 100 turns there %.1f / %.1f, on open cells %.1f / %.1f | pearls per game eaten on narrow cells %.1f / %.1f'%(label,f(0),f(1),f30(0),f30(1),lo,hi,T[0]['narrow']/n,T[1]['narrow']/n,e(0,'narrow'),e(1,'narrow'),e(0,'open'),e(1,'open'),T[0]['narrow eat']/n,T[1]['narrow eat']/n))
 print('     per map %:',' '.join(per))
