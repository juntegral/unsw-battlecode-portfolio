"""Mechanism counts for local arms, our side (side 0 in the scan), rounds 0-100.  python3 -B mech.py <arm> ..."""
import sys
sys.dont_write_bytecode=True
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import local,summ
def heading(t,W,H):
 if len(t['moves'])!=1 or t['end'] is None:return None
 dx=(t['end'][0]-t['h'][0]+W//2)%W-W//2;dy=(t['end'][1]-t['h'][1]+H//2)%H-H//2
 return (dx,dy) if abs(dx)+abs(dy)==1 else None
def mech(g,s=0):
 C=Counter();prev={};streak=Counter();W,H=g['size']
 for t in g['turns']:
  if t['side']!=s:continue
  hd=heading(t,W,H);p=prev.get(t['id']);prev[t['id']]=(t['r'],hd)
  if t['queen']:continue
  if t['L']<=3 and t['d0']<99:
   C['short']+=1;C['far9']+=t['d0']>=9;C['adj']+=t['d0']==1
   C['narrow']+=t.get('deg',9)<=2;C['narrow_eat']+=sum(t['eats'].values()) if t.get('deg',9)<=2 else 0
   if t['d0']>=9 and p and p[0]==t['r']-1 and p[1] and hd:C['fh']+=1;C['fstraight']+=p[1]==hd
   if t['d0']>=9 and t['d1'] is not None:C['fn']+=1;C['fcloser']+=t['d1']<t['d0']
  if t['L']>=4:
   if t['split']:C['split']+=1;C['split0']+=streak[t['id']]==0;streak[t['id']]=0
   else:C['hold']+=1;streak[t['id']]+=1
 return C
if __name__=='__main__':
 arms={a:local.rows(a) for a in sys.argv[1:]}
 common=sorted(set.intersection(*[set(v) for v in arms.values()]))
 print('games in every arm:',len(common),common)
 for a,gs in arms.items():
  T=Counter();M=Counter();res=Counter()
  for n in common:
   T.update(mech(gs[n]));m=summ.measure(gs[n],0)
   for k in ('eat50','eat100','nat100','heads100','len100','deaths','q100'):M[k]+=m[k]
   r=gs[n]['result'];res['win' if 'winner=0' in r else 'loss' if 'winner=1' in r else 'draw']+=1
  n=max(len(common),1)
  print('%-6s results(as A) %s | eat50 %.1f eat100 %.1f nat100 %.1f heads100 %.1f len100 %.1f deaths %.1f q100 %.1f | short far9+ %.1f%% | pearl-adjacent turns/game %.1f | far: straight %.1f%% closer %.1f%% | narrow cells: %.1f%% of short turns, %.1f pearls/game eaten there | non-queen 4+: hold turns/game %.1f, splits/game %.1f, first-turn splits %.0f%%'%(a,dict(res),M['eat50']/n,M['eat100']/n,M['nat100']/n,M['heads100']/n,M['len100']/n,M['deaths']/n,M['q100']/n,100*T['far9']/max(T['short'],1),T['adj']/n,100*T['fstraight']/max(T['fh'],1),100*T['fcloser']/max(T['fn'],1),100*T['narrow']/max(T['short'],1),T['narrow_eat']/n,T['hold']/n,T['split']/n,100*T['split0']/max(T['split'],1)))
