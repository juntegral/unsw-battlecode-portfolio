#!/usr/bin/env python3
"""For every FEEDDIE turn: own length, the leader length it logged, and the team's unit count when its turn started.
Usage: td_gate.py REPLAY_WITH_LOGS..."""
import sys, os
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'harness'))
import replay
tot = dict(n=0, ratio_ok=0, units_ok=0, min_units=999, queen=0)
for path in sys.argv[1:]:
    info, ev, team = replay.parse(path)
    alive = {}
    for line in info['map'].splitlines():
        p = line.split()
        if p and p[0] == 'DRAGON':
            alive[len(alive)] = 'AB'[int(p[1])]
    for e in ev:
        if e['kind'] == 'split':
            alive[e['child']] = e['team']
        elif e['kind'] == 'log' and e['text'].startswith('FEEDDIE'):
            _, ln, lid, llen = e['text'].split()
            ln, llen = int(ln), int(llen)
            t = alive.get(e['id'])
            units = sum(1 for v in alive.values() if v == t)
            tot['n'] += 1
            tot['ratio_ok'] += ln * 2 <= llen
            tot['units_ok'] += units > 3
            tot['min_units'] = min(tot['min_units'], units)
            tot['queen'] += e['id'] in (0, 1)
        elif e['kind'] == 'death':
            alive.pop(e['id'], None)
print('FEEDDIE turns', tot['n'], '| own length x 2 <= logged leader length in', tot['ratio_ok'], '| team had more than 3 units in', tot['units_ok'], '| smallest team size at a FEEDDIE', tot['min_units'], '| queens among them', tot['queen'])
