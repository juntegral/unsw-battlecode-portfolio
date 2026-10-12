import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque
sys.path[:0]=['tools','data/analysis/ladder/dossier']
import ladder_replay as lr
from count_dossier import Geo
P=Path(__file__).resolve().parent
for g,target,rnd in [(1493886,1002,481),(1493884,244,454),(1493884,315,485),(1493888,0,86),(1493888,0,87)]:
 d=json.loads((P/f'{g}-detail.json').read_text());t=next(t for t in d.get('long_turns',[])+d['queen_turns'] if t['id']==target and t['round']==rnd);w,h=d['w'],d['h'];root=lr.replay.load(f'data/online/smoke/one8-c2-old/M{g}.replay').root();geo=Geo(w,h,[tuple(map(int,l.split()[1:4])) for l in root.text(0).splitlines() if l.startswith('EDGE ')]);bs=t['before'];hd=bs[str(target)][0];win=geo.window(hd);occ={c for b in bs.values() for c in b}; heads={b[0] for b in bs.values()};th=set();full=set()
 for i,b in bs.items():
  if d['teams'][i]!=1 or b[0] not in win:continue
  for mode,limit,region in [('code',min(6,max(2,len(b))),th),('actual',(len(b)+3)//4+len(b)-2,full)]:
   seen={b[0]};queue=deque([(b[0],0)])
   while queue:
    c,n=queue.popleft()
    if n>=limit:continue
    for k,z in geo.moves[c]:
     if k==1 or z in seen or z in occ:continue
     seen.add(z);region.add(z);queue.append((z,n+1))
 q=deque([(hd,'')]);seen={hd};safe=[];allpaths=[]
 while q:
  c,path=q.popleft()
  if len(path)>=6:continue
  for dr,(k,z) in enumerate(geo.moves[c]):
   if k!=0 or z in occ or z in seen or z not in win:continue
   seen.add(z);pp=path+'NESW'[dr];q.append((z,pp));allpaths.append((pp,(z%w,z//w),z in th,z in full))
   if len(pp)>=2 and z not in th:safe.append((pp,(z%w,z//w)))
 print(g,target,rnd,'CODE_SAFE',safe,'PATHS',allpaths)
