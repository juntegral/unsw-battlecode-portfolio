import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter,deque,defaultdict
sys.path[:0]=['data/analysis/ladder/dossier/work','data/analysis/ladder/dossier/local','tools']
from ladder_replay import edge_id,canonical_edges,replay
import o1_qdef
OUT=Path('data/codex/astra/sweep/0436/win2');F=Path('data/online/live-one1/b1488287')
results=[]
for gid in (1488288,1488289,1488291):
 a=json.loads((OUT/f'{gid}.json').read_text());root=replay.load(F/f'M{gid}.replay').root();W,H=map(int,root.text(0).splitlines()[0].split()[1:3]);raw=[tuple(map(int,q[1:4])) for q in map(str.split,root.text(0).splitlines()) if q and q[0]=='EDGE'];edges=canonical_edges(W,H,raw);ports=defaultdict(list)
 for e,(k,p) in edges.items():
  if k==2:ports[p].append(e)
 def dest(h,d):
  e=edge_id(W,H,*h,d);k,p=edges.get(e,(0,-1))
  if k==1:return None
  if k==2:
   z=next(z for z in ports[p] if z!=e);row,x=divmod(z,W+1);return ((x-(d==3))%W,(row//2-(d==0))%H)
  dx,dy=((0,-1),(1,0),(0,1),(-1,0))[d];return ((h[0]+dx)%W,(h[1]+dy)%H)
 def gap(a,b):
  x,y=abs(a[0]-b[0]),abs(a[1]-b[1]);return min(x,W-x)+min(y,H-y)
 def bfs(h,target,occ,cap=6):
  q=deque([(tuple(h),0)]);seen={tuple(h)}
  while q:
   c,d=q.popleft()
   if d>=cap:continue
   for dr in range(4):
    n=dest(c,dr)
    if n==tuple(target):return d+1
    if n is None or n in seen or n in occ:continue
    seen.add(n);q.append((n,d+1))
  return 99
 queens=a['queen_ids'];qt=[t for t in a['turns'] if t['id']==queens[0]];ours=[t for t in a['turns'] if t['s']==0]
 adjp=[t for t in ours if any(n[2] for n in t['adj'])];moving=[t for t in adjp if t['steps']];taken=[t for t in moving if any(n[2] and n[1]==t['steps'][0] for n in t['adj'])];skips=[t for t in moving if t not in taken]
 no_enemy_skips=[t for t in skips if not t['enemies']]
 preserve=[t for t in qt if t['L']==4 and t['before'][0][3]>=6 and t['r']<=200 and t['actions'][0][0]!=1]
 herd=[t for t in qt if t['before'][0][3]>=12 and len(t['mates'])<2 and t['mates'] and t['steps'] and min(gap(t['steps'][-1],m[1]) for m in t['mates'])<min(gap(t['h'],m[1]) for m in t['mates'])]
 guards=o1_qdef.scan('win2',F/f'M{gid}.replay',json.loads((F/f'game-{gid}.json').read_text()))
 guard_rams=[g for g in guards['guard'] if g[1]<=4 and g[5]<=3 and g[8]]
 # Geometric queen risk: actual board, fixed bodies, allow entering her head as the target.
 hazards=[]
 for t in qt:
  if not t['end']:continue
  occ={tuple(c) for bb in t['bodies'].values() for c in bb};occ-=set(map(tuple,t['body']));occ|=set(map(tuple,t['end']))
  for i,h,L in t['enemies']:
   dist=bfs(h,t['end'][0],occ)
   if dist<=3:hazards.append(dict(r=t['r'],queen_L=t['L'],queen_end=t['end'][0],enemy=i,enemy_L=L,enemy_h=h,steps=dist,can_without_eating=dist<=((L+3)//4+max(0,L-2)),enemy_moves_after_queen=i>queens[0]))
 hazard_sorted=sorted(hazards,key=lambda h:(not h['can_without_eating'],h['steps'],h['r']))
 own_hunts=[d for d in a['deaths'] if d['s']==1 and d['cause']==3 and d['actor'] not in queens]
 queen_hunts=[d for d in own_hunts if d['id']==queens[1]]
 no_victim_deaths=[d for d in a['deaths'] if d['s']==0 and d['cause']!=3]
 unit_halves=[]
 rounds=sorted((int(r),st) for r,st in a['rounds'].items())
 for (r0,x),(r1,y) in zip(rounds,rounds[1:]):
  if x[0][3]>=2 and 2*y[0][3]<=x[0][3]:unit_halves.append((r0,r1,x[0][3],y[0][3]))
 row=dict(game=gid,adjacent_pearl_turns=len(adjp),moving_with_adjacent_pearl=len(moving),firststep_pearl=len(taken),passed_adjacent_pearl=len(skips),no_visible_enemy_skips=len(no_enemy_skips),skip_examples=[{k:t[k] for k in ('r','id','L','adj','steps','enemies')} for t in no_enemy_skips[:3]],preserve_gate_turns=len(preserve),preserve_examples=[{k:t[k] for k in ('r','L','before','actions')} for t in preserve[:3]],herd_nearer_turns=len(herd),herd_examples=[{k:t[k] for k in ('r','L','h','steps','mates')} for t in herd[:3]],guard_ram_pairs=guard_rams,queen_hunts=queen_hunts,ordinary_deaths=len(no_victim_deaths),hazards=hazard_sorted,unit_halves=unit_halves,zero_move_nonsplit=sum(not t['steps'] and t['actions'][0][0]!=1 and t['end']!=[] for t in ours),portal_tail_splits_early=sum(s['s']==0 and s['portal_tail'] and s['r']<=100 for s in a['splits']),portal_ids_over_guard=sum(p>=2*W*H for p in ports),cap_rounds_before350=sum(st[0][3]>=56 and r>200 for r,st in rounds))
 results.append(row)
 print(gid,{k:v for k,v in row.items() if k not in ('hazards','skip_examples','herd_examples','preserve_examples')})
 print('hazards',hazard_sorted[:6]);print('herd',row['herd_examples']);print('preserve',row['preserve_examples'])
(OUT/'metrics.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
