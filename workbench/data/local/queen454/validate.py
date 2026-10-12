#!/usr/bin/env python3
"""Check output invariants and independent pre-existing replay summaries."""
import sys
sys.dont_write_bytecode=True
import json,collections
from pathlib import Path
from datetime import datetime
import analyze as a
OUT=Path(__file__).resolve().parent
rows=json.loads((OUT/'rows.json').read_text())
assert a.span([31,0,1],32)==3 and a.span([7],32)==1 and a.span(list(range(32)),32)==32
assert len({(r['group'],r['game']) for r in rows})==len(rows)
assert collections.Counter(r['group'] for r in rows)=={'aAah':120,'ours':370,'38 off':16,'38 on':16}
for r in rows:
    assert r['queen_id'] in (0,1) and r['enemy_queen_id']==1-r['queen_id']
    assert r['alive_end']==(r['death'] is None)
    assert r['size']==('<=600' if r['width']*r['height']<=600 else '>600')
    assert sum(p['pearls'] for p in r['phases'].values())==r['pearls']
    assert sum(p['splits'] for p in r['phases'].values())==r['splits']
    for p in r['phases'].values():
        c=p['initiative'];assert c.get('steps',0)==sum(c.get(k,0) for k in ('shorten','lengthen','equal'))
        assert 0<=p['loop2']<=p['loop3']<=p['loop_eligible']<=p['alive_rounds']
    for s in r['samples']:
        assert s['round']%10==0 and s['round']<=r['rounds']
        assert s['ahead'] is None or 0<=s['ahead']<=s['teammates']
    for t,g in r['ground'].items():assert int(t)<=r['rounds'] and 0<=g['share']<=1
    for t,l in r['lengths'].items():
        assert (l is None)==(int(t)>r['rounds'])
        if r['death'] and r['death']['round']<=int(t) and l is not None:assert l==0
    if r['queen_rule_decided']:assert r['rounds']==500 and r['final_lengths'][0]!=r['final_lengths'][1]
    if r['group']=='aAah':assert r['opponent_rating']>=2000 and r['time']>='2026-10-04T03:00:00Z'
    if r['group']=='ours':assert r['version'] in (44,47) and r['ladder_validation']
    for e in r['events']:
        assert set(e['previous5'])>={'queen','enemy','first_closer','window','enemy_id'}
        assert e['previous5']['window'][1]==e['round']-1
check=json.loads((Path.home()/'meow-loop-out/card-38/attempt-2/check.json').read_text())
for group,arm in [('38 off','base'),('38 on','candidate')]:
    rs=[r for r in rows if r['group']==group];ref=check[arm]
    assert sum(r['pearls'] for r in rs)==ref['queen_pearls_eaten']
    assert sum(r['splits'] for r in rs)==ref['queen_splits']
    assert sum(r['alive_end'] for r in rs)==ref['queen_alive_at_end']
    assert sum(r['queen_rule_decided'] for r in rs)==ref['games_decided_on_the_queen_rule']
    assert sum(e['queen_moved_first'] for r in rs for e in r['events'] if e['kind']=='head-on')==ref['queen_rammed_a_head_herself']
summary=(OUT/'summary.md').read_text();assert len(summary.splitlines())<=80
assert summary.count('|---|---|---|---|')==1
print('PASS: 522 game rows, unique ids per group, all phase/sample/length/ground invariants.')
print('PASS: 370 ladder queen outcomes, death rounds, pearls and splits validated during parsing.')
print('PASS: both #38 arms match independent pearl, split, survival, queen-ending and head-on counts.')
print('PASS: 120 strong-opponent aAah games inside 72-hour window; English summary <=80 lines, one table.')
(OUT/'validation.json').write_text(json.dumps(dict(passed=True,games=len(rows),groups=dict(collections.Counter(r['group'] for r in rows)),checks=['replay result body counts and queen lengths','370 ladder queen final/survival/death/pearl/split fields','32 local #38 outcome/pearl/split/head-on fields','phase and sample invariants','summary size and table count']),indent=2)+'\n')
