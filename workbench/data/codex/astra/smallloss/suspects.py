import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parent))
from tabulate import loadall,writecsv
from analyze import HERE,ARMS,firstdiv

gs=loadall();rows=[];pairs=[]
for g in gs:
 for scope in ('all','short_nonqueen'):
  ts=[t for t in g['turns'] if t['s']==0 and t['r']<=100 and (scope=='all' or not t['q'] and t['L']<=4)]
  opp=[t for t in ts if t['action'][0]==0 and any(o['pearl'] and o['occupant'] is None and o['edge']!=1 for o in t['opts'])]
  rows.append(dict(version=g['version'],folder=g['folder'],scope=scope,turns=len(ts),pearls=sum(t['eaten'] for t in ts),natural=sum(t['natural'] for t in ts),adjacent_pearl_move_turns=len(opp),no_eat_despite_adjacent=sum(t['eaten']==0 for t in opp)))
for v,prev in (('one8','one5'),('one9','one8'),('one10','one9'),('war8','one10')):
 for g in [g for g in gs if g['version']==v]:
  b=next(x for x in gs if x['version']==prev and x['folder']==g['folder']);d=firstdiv(g,b)
  t=next(t for t in g['turns'] if t['r']==d['a'][0] and t['id']==d['a'][1]) if d else None
  pairs.append(dict(version=v,previous=prev,folder=g['folder'],firstdiv=d,turn=t))
writecsv('short-economy.csv',rows)
(HERE/'consecutive-divergences.json').write_text(json.dumps(pairs,indent=2))
for v in ARMS.values():
 ts=[x for x in rows if x['version']==v and x['scope']=='short_nonqueen'];N=sum(x['turns'] for x in ts);E=sum(x['pearls'] for x in ts);nat=sum(x['natural'] for x in ts);opp=sum(x['adjacent_pearl_move_turns'] for x in ts);miss=sum(x['no_eat_despite_adjacent'] for x in ts)
 print(v,N,E,nat,round(100*E/N,3),round(100*nat/N,3),'adjacentmiss',miss,opp)
