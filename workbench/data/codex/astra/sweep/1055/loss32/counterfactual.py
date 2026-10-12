import sys,json
from pathlib import Path
from collections import deque
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path('data/analysis/ladder/dossier/local').resolve()))
from count_local import Geo
O=Path(__file__).resolve().parent
result=[]
for gid,dirs in ((1512561,[3]),(1512562,[3,3]),(1512563,[0,3])):
 d=json.loads((O/f'{gid}-details.json').read_text());b=json.loads((O/f'{gid}-scan.json').read_text());qid=b['queens']['us'];t=[t for t in d['turns'] if t['id']==qid][-1];w,h=d['W'],d['H'];g=Geo(w,h,[tuple(map(int,l.split()[1:])) for l in b['text'].splitlines() if l.startswith('EDGE ')])
 board={int(i):tuple(y*w+x for x,y in bb) for i,bb in t['board'].items()};pearls={y*w+x for x,y in t['pearls']};free=(len(board[qid])+3)//4;qb=board[qid]
 for st,dr in enumerate(dirs):
  k,dst=g.moves[qb[0]][dr];assert k!=1
  assert all(dst not in bb for bb in board.values()),(gid,'occupied',dst)
  assert st<free or len(qb)>2
  eat=dst in pearls
  qb=(dst,)+qb
  if not eat:qb=qb[:-1]
  else:pearls.remove(dst)
  if st>=free:qb=qb[:-1]
  board[qid]=qb
 # Exact body-transition path enumeration for each enemy independently at frozen turn-start other occupancy.
 attacks=[]
 for eid,eb in board.items():
  if d['teams'][str(eid)]==0:continue
  occupied={x for i,bb in board.items() if i!=eid for x in bb};efree=(len(eb)+3)//4
  queue=deque([(eb,(),frozenset())]); visited=set();hit=None
  while queue:
   body,path,eaten=queue.popleft();st=len(path)
   if st>=8 or (st>=efree and len(body)<=2):continue
   for dr,(k,dst) in enumerate(g.moves[body[0]]):
    if k==1 or dst in body:continue
    if dst==qb[0]:hit=path+(dr,);break
    if dst in occupied:continue
    eat=dst in pearls and dst not in eaten
    nb=(dst,)+body
    if not eat:nb=nb[:-1]
    if st>=efree:nb=nb[:-1]
    ne=eaten|{dst} if eat else eaten
    state=(nb,len(path)+1,ne)
    if state not in visited:visited.add(state);queue.append((nb,path+(dr,),ne))
   if hit is not None:break
  if hit is not None:attacks.append(dict(id=eid,path=hit))
 result.append(dict(gid=gid,round=t['round'],dirs=dirs,end=[(c%w,c//w) for c in qb],attackers=attacks,scope='frozen other bodies, each enemy independent, max8 steps; not a full continuation'))
print(json.dumps(result,indent=2))
(O/'counterfactual.json').write_text(json.dumps(result,indent=2))
