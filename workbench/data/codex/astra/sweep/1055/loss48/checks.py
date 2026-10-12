import sys,json
from pathlib import Path
from collections import Counter
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/local']
from count_local import Geo
O=Path(__file__).parent
for gid in [1513842,1513844,1513845]:
 d=json.loads((O/f'{gid}-detail.json').read_text());s=json.loads((O/f'{gid}-scan.json').read_text());W,H=d['W'],d['H']
 raw=[tuple(map(int,q[1:4])) for q in map(str.split,s['text'].splitlines()) if q[0]=='EDGE'];g=Geo(W,H,raw)
 portal=[[],[]]; mouths=[[],[]]
 for t in d['turns']:
  pos=t['body'][0][1]*W+t['body'][0][0]
  if any(k==2 for k,b in g.moves[pos]):mouths[t['side']].append([t['r'],t['id'],t['L'],t['body'][0],t['dirs']])
  for z,(i,xy) in enumerate(t['moves']):
   assert i==t['id'];direction=t['dirs'][z];k,dest=g.moves[pos][direction];assert dest==xy[1]*W+xy[0],(gid,t['r'],t['id'])
   if k==2:portal[t['side']].append([t['r'],i,t['L']])
   pos=dest
 print(gid,'portal steps',list(map(len,portal)),[x[:5] for x in portal]);print('mouth turns',list(map(len,mouths)),'examples',mouths[0][:10]);print('last round',s['last_round'])
 if gid==1513842:
  ss=s['snapshots'];print('191',ss['190'],ss['191']);print('maxlong',max(v['us']['longest'] for v in ss.values()));print('queen cell edges',[(x,y,g.moves[y*W+x]) for x,y in [(2,1),(3,1),(2,2),(3,2)]])
 if gid!=1513842:
  out=[]
  for t in d['qturns'][0][-3:]:
   out.append(f"r{t['r']} L{t['L']} center {t['body'][0]} dirs {t['dirs']}")
   for y in range(7):
    out.append(''.join('+'+('-' if t['edges'][y*7+x][2][0]==1 else 'P' if t['edges'][y*7+x][2][0]==2 else ' ') for x in range(7))+'+')
    out.append(''.join(('|' if t['edges'][y*7+x][2][3]==1 else 'P' if t['edges'][y*7+x][2][3]==2 else ' ')+t['board'][y][x] for x in range(7))+('|' if t['edges'][y*7+6][2][1]==1 else ' '))
   out.append(''.join('+'+('-' if t['edges'][42+x][2][2]==1 else 'P' if t['edges'][42+x][2][2]==2 else ' ') for x in range(7))+'+')
  (O/f'{gid}-boards.txt').write_text('\n'.join(out))
