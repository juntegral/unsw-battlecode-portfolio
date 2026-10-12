"""Pacing: non-queen dragon turns that lie inside a 12-turn window in which the head used at most 4 different cells and ate nothing.
python3 -B stuck.py <online label | local:arm> ..."""
import sys
sys.dont_write_bytecode=True
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from summ import games
def stuck(g,s,queen=False):
 by=defaultdict(list)
 for t in g['turns']:
  if t['side']==s and bool(t['queen'])==queen:by[t['id']].append(t)
 n=0;tot=0;far=0;ex=[]
 for i,ts in by.items():
  tot+=len(ts);mark=[False]*len(ts)
  for a in range(0,len(ts)-11):
   w=ts[a:a+12]
   if w[11]['r']-w[0]['r']!=11:continue
   if any(sum(x['eats'].values()) for x in w) or any(x['split'] for x in w):continue
   if len({tuple(x['h']) for x in w})<=4:
    for k in range(a,a+12):mark[k]=True
  c=sum(mark);n+=c;far+=sum(1 for k,x in enumerate(ts) if mark[k] and x['d0']>=7)
  if c:ex.append((c,i,ts[mark.index(True)]['r'],ts[mark.index(True)]['h'],ts[mark.index(True)]['d0'],ts[mark.index(True)]['L']))
 return n,tot,far,sorted(ex,reverse=True)[:2]
def line(name,rows):
 A=[0,0,0];B=[0,0,0];hi=lo=0;per=[];exs=[]
 for g in rows:
  a=stuck(g,0);b=stuck(g,1)
  for k in range(3):A[k]+=a[k];B[k]+=b[k]
  pa=100*a[0]/max(a[1],1);pb=100*b[0]/max(b[1],1);hi+=pa>pb+1;lo+=pa<pb-1;per.append('%s %.0f/%.0f'%(g['map'][:8],pa,pb))
  exs+=[(g.get('gid'),g['map'][:10])+e for e in a[3][:1]]
 n=max(len(rows),1)
 print('%-12s pacing turns per game us %.0f (%.1f%% of non-queen turns; %.0f of them 7+ steps from a pearl) / them %.0f (%.1f%%; %.0f) | maps us higher %d, lower %d'%(name,A[0]/n,100*A[0]/max(A[1],1),A[2]/n,B[0]/n,100*B[0]/max(B[1],1),B[2]/n,hi,lo))
 print('     per map %:',' '.join(per))
 print('     our longest (game, map, turns, id, first round, cell, pearl distance, length):',sorted(exs,key=lambda e:-e[2])[:5])
if __name__=='__main__':
 for label in sys.argv[1:]:
  if label.startswith('local:'):
   import local;line(label,list(local.rows(label[6:]).values()))
  else:line(label,list(games(label)))
