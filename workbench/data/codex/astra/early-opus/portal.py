"""Portal steps (a single step whose two cells are not neighbours on the torus), non-queen and queen, r0-100, both sides."""
import sys
sys.dont_write_bytecode=True
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from summ import games
def jumps(g,s):
 W,H=g['size'];out=[]
 for t in g['turns']:
  if t['side']!=s or not t['moves']:continue
  a=t['h']
  for b in t['moves']:
   dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1])
   if min(dx,W-dx)+min(dy,H-dy)!=1:out.append((t['r'],t['id'],t['queen']))
   a=b
 return out
for label in sys.argv[1:]:
 T=[Counter(),Counter()];n=0;per=[];lo=hi=0
 for g in games(label):
  J=[jumps(g,0),jumps(g,1)]
  if not J[0] and not J[1]:continue
  n+=1
  for s in (0,1):
   T[s]['r25']+=sum(1 for r,i,q in J[s] if r<=25);T[s]['r50']+=sum(1 for r,i,q in J[s] if r<=50);T[s]['r100']+=len(J[s]);T[s]['first']+=min((r for r,i,q in J[s]),default=101);T[s]['ids50']+=len({i for r,i,q in J[s] if r<=50})
  a=sum(1 for r,i,q in J[0] if r<=50);b=sum(1 for r,i,q in J[1] if r<=50);lo+=a<b;hi+=a>b
  per.append('%s %d/%d first %d/%d'%(g['map'][:8],a,b,min((r for r,i,q in J[0]),default=101),min((r for r,i,q in J[1]),default=101)))
 n=max(n,1)
 print('%-9s maps with portal steps %d | portal steps per game us/them: by r25 %.1f/%.1f, by r50 %.1f/%.1f, by r100 %.1f/%.1f | dragons that crossed by r50 %.1f/%.1f | first crossing round %.1f/%.1f | maps us fewer %d, more %d'%(label,n,T[0]['r25']/n,T[1]['r25']/n,T[0]['r50']/n,T[1]['r50']/n,T[0]['r100']/n,T[1]['r100']/n,T[0]['ids50']/n,T[1]['ids50']/n,T[0]['first']/n,T[1]['first']/n,lo,hi))
 print('     by r50 per map:',' | '.join(per))
