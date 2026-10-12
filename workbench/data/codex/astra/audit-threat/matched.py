import sys
sys.dont_write_bytecode=True
import json,random,math
from collections import Counter
import summarize as s
O=s.OUT;gs=s.load_games();result={};rng=random.Random(20261009)
for before,after,opps in [(5,8,('WeHaveQuizzes','Cache me outside')),(7,8,('WeHaveQuizzes','Cache me outside')),(8,9,('kraken',)),(9,10,('kraken',))]:
 aa={};bb={}
 for g in gs:
  if g['opp'] not in opps or not g['path'].startswith('data/online/smoke/'):continue
  if g['v']==before:aa[g['opp'],g['map']]=g
  if g['v']==after:bb[g['opp'],g['map']]=g
 keys=sorted(aa.keys()&bb.keys());a=[aa[k] for k in keys];b=[bb[k] for k in keys]
 row=dict(pairs=len(keys),before=s.combined(a),after=s.combined(b),same_opponent_bot=sum(aa[k]['opp_bot']==bb[k]['opp_bot'] for k in keys),same_side=sum(aa[k]['side']==bb[k]['side'] for k in keys))
 if keys:
  diffs={x:[] for x in ('other','q')}
  def rate(seq,kind):
   q=kind=='q';n=sum(sum(bool(r['q'])==q for r in g['rams']) for g in seq);d=sum(g['counts'].get('queen_turns' if q else 'other_turns',0) for g in seq);return 1000*n/d
  for _ in range(4000):
   inds=[rng.randrange(len(keys)) for _ in keys];ba=[a[i] for i in inds];bb_=[b[i] for i in inds]
   for kind in diffs:diffs[kind].append(rate(bb_,kind)-rate(ba,kind))
  row['paired_bootstrap_95_diff_after_minus_before']={kind:[sorted(v)[100],sorted(v)[3899]] for kind,v in diffs.items()}
 result[f'{before}->{after}']=row
 print(before,after,'pairs',len(keys),'sameOppBot',row['same_opponent_bot'],'sameSide',row['same_side'])
 for side in ('before','after'):
  r=row[side];print(side,'rams',r['ram_rates'],'eat',r['short_pearls_per_turn'],r['queen_pearls_per_turn'],'food',r['queen_not_toward_food_fraction'])
 print(row.get('paired_bootstrap_95_diff_after_minus_before'))
(O/'matched.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
