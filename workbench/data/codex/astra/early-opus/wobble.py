"""Blind travel: for non-queen dragons of length 2-3, every 6-turn window in which the nearest pearl stayed 7+ steps away:
net torus displacement over the 6 turns (6 = dead straight). Online labels or local arms (prefix local:)."""
import sys
sys.dont_write_bytecode=True
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from summ import games
def windows(g,s,rmax=100,rmin=0):
 W,H=g['size'];by=defaultdict(list);out=[]
 for t in g['turns']:
  if t['side']==s and not t['queen'] and t['L']<=3 and rmin<=t['r']<=rmax:by[t['id']].append(t)
 for ts in by.values():
  for a in range(0,len(ts)-6,3):
   w=ts[a:a+7]
   if w[6]['r']-w[0]['r']!=6 or any(x['d0']<7 for x in w[:6]) or any(len(x['moves'])!=1 for x in w[:6]):continue
   dx=abs(w[6]['h'][0]-w[0]['h'][0]);dy=abs(w[6]['h'][1]-w[0]['h'][1]);out.append(min(dx,W-dx)+min(dy,H-dy))
 return out
def line(name,rows):
 for lo,hi in ((0,24),(25,100)):
  tot=[[],[]];less=more=0;per=[]
  for g in rows:
   a=windows(g,0,hi,lo);b=windows(g,1,hi,lo);tot[0]+=a;tot[1]+=b
   if a and b:
    ma=sum(a)/len(a);mb=sum(b)/len(b);less+=ma<mb;more+=ma>mb;per.append('%s %.1f/%.1f'%(g['map'][:8],ma,mb))
  f=lambda x:(sum(x)/len(x) if x else float('nan'))
  g2=lambda x:(100*sum(1 for v in x if v<=2)/len(x) if x else float('nan'))
  print('%-10s r%d-%d net cells per 6 blind turns us %.2f (n %d) / them %.2f (n %d) | windows that end within 2 cells of where they began: us %.0f%% / them %.0f%% | maps us<them %d, us>them %d'%(name,lo,hi,f(tot[0]),len(tot[0]),f(tot[1]),len(tot[1]),g2(tot[0]),g2(tot[1]),less,more))
  print('     '+' '.join(per))
if __name__=='__main__':
 for label in sys.argv[1:]:
  if label.startswith('local:'):
   import local;line(label,list(local.rows(label[6:]).values()))
  else:line(label,list(games(label)))
