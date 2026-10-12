import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque
sys.path.insert(0,'tools')
from ladder_replay import edge_id
O=Path('data/codex/astra/sweep/1055/loss6')
for gid in (1503502,1503503,1503504):
 j=json.loads((O/f'{gid}-fast.json').read_text());W,H=j['W'],j['H'];ed=dict(j['edges']);q=j['queens'][0]
 print('\nGAME',gid)
 for z in j['qboards']:
  b=z['bodies'];h=b[str(q)][0];occ={tuple(c):(i,k) for i,bb in b.items() for k,c in enumerate(bb)}
  print('Q',z['round'],h,[(di,ed.get(edge_id(W,H,*h,d),(0,-1)),occ.get(((h[0]+dx)%W,(h[1]+dy)%H))) for d,(di,dx,dy) in enumerate((('N',0,-1),('E',1,0),('S',0,1),('W',-1,0)))])
 # Round-end lexicographic final deciding key, last round not losing.
 scores=[]
 for r,b in j['snaps'].items():
  vals=[]
  for side in (0,1):
   ls=[len(bb) for i,bb in b.items() if j['teams'][i]==side];vals.append((len(b.get(str(j['queens'][side]),[])),max(ls,default=0),sum(ls)))
  scores.append((int(r),vals))
 last=max((r for r,v in scores if v[0]>=v[1]),default=-1)
 print('permanent deficit',last+1,[(r,v) for r,v in scores if last-1<=r<=last+2])
 print('queen splits',[s for s in j['splits'] if s['parent']==q])
 print('longest switches')
 prev=None
 for r,v in scores:
  if r>=390:
   b=j['snaps'][str(r)];tops=[]
   for side in (0,1):tops.append(sorted([(len(bb),int(i)) for i,bb in b.items() if j['teams'][i]==side],reverse=True)[:2])
   if r%10==0 or r in (402,403,404,496,497,498,499):print(r,tops)
