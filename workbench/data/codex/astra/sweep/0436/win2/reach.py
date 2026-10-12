import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import defaultdict,deque
sys.path[:0]=['tools']
from ladder_replay import edge_id,canonical_edges,replay
O=Path('data/codex/astra/sweep/0436/win2');out=[]
for gid in (1488288,1488289,1488291):
 a=json.loads((O/f'{gid}.json').read_text());r=replay.load(Path(f'data/online/live-one1/b1488287/M{gid}.replay')).root();W,H=map(int,r.text(0).splitlines()[0].split()[1:3]);raw=[tuple(map(int,q[1:4])) for q in map(str.split,r.text(0).splitlines()) if q and q[0]=='EDGE'];ed=canonical_edges(W,H,raw);po=defaultdict(list)
 for e,(k,p) in ed.items():
  if k==2:po[p].append(e)
 def dest(h,d):
  k,p=ed.get(edge_id(W,H,*h,d),(0,-1))
  if k==1:return None
  if k==2:
   partner=next(z for z in po[p] if z!=edge_id(W,H,*h,d));row,x=divmod(partner,W+1);return ((x-(d==3))%W,(row//2-(d==0))%H)
  dx,dy=((0,-1),(1,0),(0,1),(-1,0))[d];return ((h[0]+dx)%W,(h[1]+dy)%H)
 def reach(h,L,occ,pearls):
  free=(L+3)//4;q=deque([(tuple(h),0,0,())]);seen={tuple(h)};res={}
  while q:
   c,s,e,path=q.popleft()
   if s>=3 or (s>=free and L+e-max(0,s-free)<=2):continue
   for d in range(4):
    n=dest(c,d)
    if n is None or n in seen or n in occ:continue
    seen.add(n);ne=e+(n in pearls);res[n]=(s+1,ne,path+(n,));q.append((n,s+1,ne,path+(n,)))
  return res
 cases=[]
 for t in a['turns']:
  if t['id']!=a['queen_ids'][0]:continue
  occ={tuple(c) for bb in t['bodies'].values() for c in bb};pearls=set(map(tuple,t['pearls']))
  for i,h,L in t['enemies']:
   if i==a['queen_ids'][1]:continue
   rp=reach(h,L,occ,pearls);rn=reach(h,L,occ,set());added=set(rp)-set(rn);adj={tuple(n[1]) for n in t['adj']}
   critical=adj&added
   if critical:cases.append(dict(r=t['r'],queen=t['id'],enemy=i,L=L,added_adj=[dict(cell=c,path=rp[c][2]) for c in sorted(critical)],choice=t['steps'],avoided=not t['steps'] or tuple(t['steps'][0]) not in critical))
 out.append(dict(game=gid,queen_turns_with_new_danger=len({c['r'] for c in cases}),cases=cases));print(gid,len(cases),cases[:6])
(O/'reach.json').write_text(json.dumps(out,indent=2))
