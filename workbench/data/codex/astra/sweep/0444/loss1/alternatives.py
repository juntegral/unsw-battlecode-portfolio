import sys,json,importlib.util
from pathlib import Path
from collections import deque
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('a','data/codex/astra/sweep/0410/loss1/analyze.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
OUT=Path(__file__).resolve().parent
rows=[]
for gid,att in [(1488846,695),(1488847,312)]:
 x=json.loads((OUT/f'{gid}.json').read_text());t=x['queen_turns'][-1];w,h=x['dim'];root=a.lr.replay.load(Path(f'data/online/live-one1/b1488845/M{gid}.replay')).root();g=a.Geo(w,h,[tuple(map(int,l.split()[1:])) for l in root.text(0).splitlines() if l.startswith('EDGE ')]);bh=t['bodies'];src=bh[str(att)][0];start=t['start'][1]*w+t['start'][0];end=t['steps'][-1][1]*w+t['steps'][-1][0]
 def bfs(src):
  dist={src:0};q=deque([src])
  while q:
   c=q.popleft()
   for z in g.nxt[c]:
    if z>=0 and z not in dist:dist[z]=dist[c]+1;q.append(z)
  return dist
 def inview(c):return min(abs(c%w-start%w),w-abs(c%w-start%w))<=3 and min(abs(c//w-start//w),h-abs(c//w-start//w))<=3
 dist=bfs(src);occ={c for b in bh.values() for c in b};rows.append(dict(gid=gid,candidates=[]))
 for name,c in [('start',start),('played',end),('east',g.nxt[start][1])]:
  ds=bfs(c);unseen=min(d for z,d in ds.items() if not inview(z));rows[-1]['candidates'].append(dict(name=name,xy=[c%w,c//w],static_attacker_distance=dist.get(c),distance_to_unseen=unseen,occupied=c in occ))
(OUT/'alternatives.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
