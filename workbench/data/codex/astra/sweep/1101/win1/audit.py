import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import Counter

out=Path(__file__).resolve().parent
rows=[json.loads((out/f'{gid}.json').read_text()) for gid in (1518019,1518020,1518022,1518023)]
counts=Counter()
for x in rows:
    assert not x['anomalies']
    for r,ss in x['econ']['snaps'].items():
        for team,s in enumerate(('A','B')):
            assert x['states'][r][s]==[ss[team][0],ss[team][2],ss[team][1],ss[team][3]]
    for team,s in enumerate(('A','B')):
        eats=sum(e[1]==team for e in x['econ']['eats'])
        dead=sum(d[2] for d in x['econ']['deaths'] if d[1]==team)
        paid=sum(p[3] for p in x['econ']['paids'] if p[1]==team)
        final=x['states'][str(x['last'])][s][2]
        assert x['initial'][s][2]+eats-dead-paid-final==0
    for f in x['far']:
        assert f['when']==f['r']
        counts['far_sends']+=1
        counts['far_queen_hits']+=x['queens']['us'] in f['recipients']
        counts['far_queen_hits_before_her_turn']+=x['queens']['us'] in f['recipients'] and f['queen_last_turn']<f['r']
    for t in x['queen_turns']:
        counts['queen_splits']+=bool(t['split'])
        counts['queen_keep2_splits']+=bool(t['split'] and t['split'][0]==2)
        counts['queen_L4_nonsplits']+=t['L']==4 and not t['split']
    for t in x['turns']:
        counts['adjacent_pearl_eat_turns']+=bool(any(c in t['eaten'] for c in t['pearls']) and not t['split'])
        counts['adjacent_pearl_pass_no_eat_survive_move']+=bool(t['pearls'] and not t['ate'] and not t['dead'] and not t['split'])
        counts['adjacent_pearl_pass_no_enemy_head_manhattan8']+=bool(t['pearls'] and not t['ate'] and not t['dead'] and not t['split'] and not t['foes'])
        if t['L']<4 and not t['queen']:
            counts['short_successful_portal_crossings']+=sum(z['step']<t['used'] for z in t['portals'])
        counts['long_multi_step_near_head_candidate_turns']+=bool(t['L']>=8 and not t['queen'] and len(t['steps'])>=2 and t['foes'])
    counts['long_rammed_count']+=sum(d[1]==0 and d[2]>=8 and d[4]=='rammed' for d in x['econ']['deaths'])
    counts['long_rammed_length']+=sum(d[2] for d in x['econ']['deaths'] if d[1]==0 and d[2]>=8 and d[4]=='rammed')
    counts['no_action_deaths']+=len(x['own_no_action'])
    counts['early_natural_us']+=sum(e[1]==0 and e[3]=='n' and e[0]<=100 for e in x['econ']['eats'])
    counts['early_natural_them']+=sum(e[1]==1 and e[3]=='n' and e[0]<=100 for e in x['econ']['eats'])
(out/'audit.json').write_text(json.dumps({
    'counts':counts,
    'checks':'Both sides: final state and queen match replay result via ladder_replay; all shared o1 checkpoints agree; length ledger residual zero; sonar SipHash test vector passed in analyze.py; parsed far report rounds match replay round.',
    'limits':'Action signatures are not branch instrumentation. Portal unknown uses individual cumulative 7x7 view, not sonar or inferred map knowledge. Passed pearl is reachable over one open/portal edge into a currently empty cell; enemy-head exclusion is toroidal Manhattan <=8, not a verified safety test.'
},ensure_ascii=False,indent=2)+'\n')
print(dict(counts))
