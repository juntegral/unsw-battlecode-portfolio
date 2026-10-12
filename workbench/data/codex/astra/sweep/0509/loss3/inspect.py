import sys,json
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/losses/counts']
from count_replays import Geometry
from pathlib import Path
O=Path(__file__).resolve().parent
for gid in (1490798,1490799,1490800):
 g=json.loads((O/f'{gid}.json').read_text());w=g['width'];h=g['height'];xy=lambda c:(c%w,c//w)
 raw=[tuple(map(int,a[1:4])) for l in g['text'].splitlines() if (a:=l.split())[0]=='EDGE'];geo=Geometry(w,h,raw)
 print('\nGAME',gid,w,h)
 for t in g['qturns'][-6:]:
  bs=t['frame']['bodies'];occ={c:(i,n) for i,b in bs.items() for n,c in enumerate(b)}
  print('r',t['round'],'head',xy(t['body'][0]),'L',len(t['body']))
  for d,(k,c) in enumerate(geo.moves[t['body'][0]]): print(' NESW'[d+1],k,xy(c),occ.get(c))
 if gid==1490798:
  for r in range(110,116):
   print('attacker',[(t['round'],t['id'],list(map(xy,t['body'])),t.get('dirs'),list(map(xy,t['end']))) for t in g['turns'] if t['round']==r and t['id'] in (21,95)])
  print('early',[(t['round'],t['id'],len(t['body']),len(t['eats']),t.get('dirs'),t['splits']) for t in g['turns'] if t['side']=='B' and 20<=t['round']<=30])
 if gid==1490799:
  for t in g['turns']:
   if (108<=t['round']<=112 and t['id']==78) or (458<=t['round']<=461 and t['id']==137):print('specific',t)
 if gid==1490800:
  print('late top',[(t['round'],t['id'],len(t['body']),len(t['end']),t['eats'],t['splits'],t.get('dirs')) for t in g['turns'] if t['side']=='B' and len(t['body'])>=20 and t['round']>=482])
