import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque
sys.path.insert(0,str(Path.cwd()/'data/analysis/ladder/dossier/local'))
from count_local import Geo
O=Path(__file__).resolve().parent
out=[]
for gid,r,att,alternative,follow in [(1510787,263,263,(5,7),(5,6)),(1510788,93,29,(12,5),(12,6))]:
 g=json.loads((O/f'{gid}.json').read_text());geo=Geo(g['w'],g['h'],g['edges']);w=g['w'];q=g['queens'][0]
 t=next(t for t in g['turns'] if t['id']==q and t['round']==r);prev=next(t for t in g['turns'] if t['id']==q and t['round']==r-1)
 cell=lambda xy:xy[1]*w+xy[0]
 def xy(c):return [c%w,c//w]
 occ={c for bb in t['bodies'].values() for c in bb};legal=[c for k,c in geo.moves[cell(t['head'])] if k!=1 and c not in occ]
 ah=t['bodies'][str(att)][0];print(gid,'legal',[xy(c) for c in legal],'attacker',xy(ah),'adjacent',[c in geo.adj[ah] for c in legal]);assert all(c in geo.adj[ah] for c in legal)
 # Fixed observed enemy reply, not a minimax proof.
 pocc={c for bb in prev['bodies'].values() for c in bb};a,f=cell(alternative),cell(follow)
 assert a in geo.adj[cell(prev['head'])] and a not in pocc
 assert f in geo.adj[a] and f not in pocc
 ds={ah:0};qq=deque([ah])
 while qq:
  c=qq.popleft()
  for d in geo.adj[c]:
   if d not in ds:ds[d]=ds[c]+1;qq.append(d)
 out.append(dict(gid=gid,round=r,legal=[xy(c) for c in legal],attacker=att,head=xy(ah),alternative=list(alternative),next=list(follow),next_distance=ds[f]))
 print('alternative',alternative,follow,'distance from observed enemy reply',ds[f])
(O/'geometry-checks.json').write_text(json.dumps(out,indent=2))
