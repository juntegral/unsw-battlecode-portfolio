import sys,json
sys.dont_write_bytecode=True
sys.path.insert(0,'data/codex/astra/approach')
from scan import Board,replay,edge_id
from pathlib import Path
from collections import deque
O=Path(__file__).resolve().parent
B=Board('data/online/live-one1/b1478190/M1478190.replay');records=[]
for ev in B.root.pointer(3):
 k=ev.u16(0);p=ev.pointer(0)
 if k==0 and p.i32(0)>173:break
 B.update(k,p)
 if k==1 and B.actor==1 and B.rnd in [171,172,173]:records.append({'r':B.rnd,**B.snap()})
 if k==1 and B.actor==196 and B.rnd==172:
  body=tuple(B.bodies[196]);food=set(B.pearls);occ={c for i,b in B.bodies.items() if i!=196 for c in b};target=B.bodies[1][0]
  free=(len(body)+3)//4;path=[]
  for depth,d in enumerate([0,1,1],1):
   n=B.adj[body[0]][d];pay=depth>free
   assert n is not None and n not in body and (n not in occ or n==target)
   assert not pay or len(body)>2
   eat=n in food;L=len(body)+eat-pay
   body=((n,)+body)[:L];food.discard(n)
   path.append(dict(step=depth,head=n,length=L,eat=eat,pay=pay,ram=n==target))
  assert path[-1]['ram'] and path[-1]['length']==2
# Independent all-round snapshots match the existing extra() counter.
a=json.loads((O/'target.json').read_text());b=json.loads((O/'game-1478190.json').read_text())
assert a['all_snapshots']==b['snapshots']
# North branch under the bot's portal exclusion and frozen own body.
s=next(x for x in records if x['r']==172);body=[tuple(c) for c in s['bodies']['1']];food={tuple(c) for c in s['pearls']}
start=(24,10);occ={tuple(c) for bb in s['bodies'].values() for c in bb};room={start};q=deque([start])
while q:
 c=q.popleft()
 for d,n in enumerate(B.adj[c]):
  if B.edges.get(edge_id(B.W,B.H,*c,d),(0,-1))[0]==2:continue
  if n is None or n in room or n in occ:continue
  room.add(n);q.append(n)
assert room=={(24,10),(24,9)}
result={'last3':records,'r172_attacker_counterfactual':path,'north_nonportal_room':sorted(room),'code_ring_r172':{'seen_parts':3,'view_edge':True,'minimum_size_estimate':4,'free':1,'QS_PAY_REACH':3,'west_distance':3,'west_risk':1,'north_risk':0,'north_closed':True,'note':'Code reconstruction with observed body; no bot execution.'},'target_500_round_snapshots_match':True,'limitations':'Counterfactual NEE holds all other dragons fixed at attacker turn. No bot execution or winning-line test.'}
(O/'mechanism.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='last3'},indent=2))
