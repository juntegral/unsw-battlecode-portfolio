import sys,json,statistics
from pathlib import Path
from collections import Counter
OUT=Path(__file__).resolve().parent
D={p.stem:[json.loads(l) for l in p.read_text().splitlines()] for p in OUT.glob('one*.jsonl')}
G={k:{x['map']:x for x in v} for k,v in D.items()}

def summ(rows):
 n=len(rows);q=sum(x['queen_pearls'] for x in rows);fe=sum(x['feeder_eat'] for x in rows)
 a=sum(x['queen_counts'].get('herd_alone',0) for x in rows);t=sum(x['queen_counts'].get('herd_turns',0) for x in rows)
 return dict(n=n,q=q,qmean=q/n,fe=fe,alone=a,turns=t,alone_pct=100*a/t if t else None,p300=sum(x['snaps']['300']['sides'][0]['pearls'] for x in rows)/n)

def rate(x):
 c=x['queen_counts'];return c.get('herd_alone',0)/c.get('herd_turns',1) if c.get('herd_turns',0) else None

def compare(k,v4,v5):
 base,a,b=G[k],G[v4],G[v5];maps=sorted(set(base)&set(a)&set(b))
 out={}
 for name,fn,sgn in [('q',lambda x:x['queen_pearls'],-1),('feed',lambda x:x['feeder_eat'],-1),('alone',rate,1),('p300',lambda x:x['snaps']['300']['sides'][0]['pearls'],-1)]:
  common=[m for m in maps if all(fn(g[m]) is not None for g in (base,a,b))]
  worse=[m for m in common if sgn*(fn(a[m])-fn(base[m]))>0 and sgn*(fn(b[m])-fn(base[m]))>0]
  better=[m for m in common if sgn*(fn(a[m])-fn(base[m]))<0 and sgn*(fn(b[m])-fn(base[m]))<0]
  out[name]=dict(eligible=len(common),worse=worse,better=better)
 return out

if __name__=='__main__':
 for k,v in D.items():print(k,summ(v))
 for s in ('w1','d1'):
  if not all('one'+v+'-'+s in D for v in '345'):continue
  print('same',s,compare('one3-'+s,'one4-'+s,'one5-'+s))
  print('deltas',s)
  for m,x in G['one3-'+s].items():
   print(m,[(v,G['one'+v+'-'+s][m]['queen_pearls']-x['queen_pearls'],G['one'+v+'-'+s][m]['feeder_eat']-x['feeder_eat']) for v in '45'])
