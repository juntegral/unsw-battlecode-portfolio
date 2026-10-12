import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
D=Path('data/analysis/ladder/dossier')
rows=[json.loads(s) for s in (D/'work/ll_games.jsonl').read_text().splitlines()]
assert len(rows)==1142
for name,p,n in [('Ladder',D/'per-game.jsonl',500),('Rank1',D/'target/per-game-top1.jsonl',597)]:
 ref={r['game']:r for r in map(json.loads,p.read_text().splitlines()) if r['relation']=='us'}
 rs=[r for r in rows if r['set']==name];assert len(rs)==n and {r['game'] for r in rs}==set(ref)
 for r in rs:
  q=ref[r['game']]
  assert r['last_round']==q['last_round']
  for c,w in [('100','0-100'),('300','101-300')]:
   v=q['ranges'][w]['end_state']['longest'] if int(c)<=q['last_round'] else q['final_reconstructed']['longest']
   assert r['checkpoints'][c]==v,(r['game'],c)
  assert len([x for x in r['rams'] if x['round']<=100])<=q['ranges']['0-100']['deaths'].get('head-on hit',0)
  assert len([x for x in r['rams'] if 100<x['round']<=300])<=q['ranges']['101-300']['deaths'].get('head-on hit',0)
for r in rows:
 for n in ('6','11','16','21','31'):assert r['near'].get(n,0)<=r['turns'].get(n,0)
 for x in r['rams']:
  assert x['leader']==(x['length']>=x['own_longest_before']-2)
  assert x['collision_step']==x['steps_walked']+1
  assert x['length_paid']==max(0,x['steps_walked']-(x['rammer_start_length']+3)//4)
  assert x['could_decide']==(x['own_longest_after']<x['opponent_final_longest'])
text=(D/'leader-len.md').read_text();assert len(text.splitlines())<=45
assert len([s for s in text.splitlines() if s and not s.startswith(('#','|'))])<=5
print('PASS: 1142 games; final states; 100/300 checkpoints; ram bounds; payment; turn bounds; report limits.')
