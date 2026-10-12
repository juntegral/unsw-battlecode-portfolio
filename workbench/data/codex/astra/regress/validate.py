#!/usr/bin/env python3
"""Cross-check stratified games using the pre-existing independent scanner."""
import sys
sys.dont_write_bytecode = True
import json
from collections import Counter
from count import HERE, ROOT
from ladder_replay import scan

rows = [json.loads(l) for l in (HERE/'games.jsonl').read_text().splitlines()]
good = [r for r in rows if 'excluded' not in r]
samples = []
for ver, m in [('one5','Australia'),('one7','Tower Defense'),('one8','Trauma'),
               ('one9','Portals'),('one10','Default'),('one11','Portals'),
               ('one12','Portals'),('one13','Trauma'),('one14','Portals')]:
    candidates = [r for r in good if r['version']==ver and r['map']==m]
    if candidates: samples.append(candidates[0])
results=[]
for r in samples:
    rp = ROOT/r['replay']
    j=json.loads((rp.parent/f'game-{r["gid"]}.json').read_text())
    other=scan(rp,j,r['folder'],set())
    v=r['values']
    for t in (50,100,200):
        assert v[f'pearls{t}']==sum(s=='us' and rnd<t for rnd,s in other['eaten_rounds'])
    for t in (100,200):
        snap=other['snapshots'].get(t-1,other['final'])['us']
        assert v[f'alive{t}']==snap['alive']
        assert v[f'total{t}']==snap['total']
        assert v[f'queen{t}']==snap['queen_length']
    qd=[d['round'] for d in other['deaths'] if d['side']=='us' and d['id']==other['queens']['us']]
    assert v['queen_death_median']==(qd[0] if qd else None)
    ours=[d for d in other['deaths'] if d['side']=='us' and d['round']<200]
    assert sum(v['deaths_'+c] for c in ('wall','own_body','mate','enemy_body',
                                     'rammed_head_on','initiated_head_on','mate_head_on','other'))==len(ours)
    assert v['deaths_wall']==sum(d['cause']=='wall' for d in ours)
    assert v['deaths_own_body']==sum(d['cause']=='own body' for d in ours)
    assert v['deaths_mate']+v['deaths_enemy_body']==sum(d['cause']=='other dragon body' for d in ours)
    assert v['deaths_rammed_head_on']+v['deaths_initiated_head_on']+v['deaths_mate_head_on']==sum(d['cause']=='head-on' for d in ours)
    results.append(dict(gid=r['gid'],version=r['version'],map=r['map'],result='match'))
out=dict(independent_checks=results,
         final_state_assertions=len(good),excluded=[r for r in rows if 'excluded' in r],
         label_mismatches=[dict(gid=r['gid'],folder=r['folder'],version=r['version'])
                           for r in good if r['folder'].split('-')[0]!=r['version']],
         early_ends={str(t):sum(r['last_round']<t for r in good) for t in (50,100,200)},
         multiple_initial_head_tiles=sum(len({tuple(h) for h in r['starter_heads']})>1 for r in good),
         opponent_bot_ids={v:dict(Counter(r['opponent_bot'] for r in good if r['version']==v))
                           for v in sorted({r['version'] for r in good})})
(HERE/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False))
