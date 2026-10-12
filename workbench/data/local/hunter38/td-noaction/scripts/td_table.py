#!/usr/bin/env python3
"""Per-game table of 'no valid action' deaths. Usage: td_table.py REPLAY..."""
import sys, os
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'harness'))
import replay
from collections import Counter

NONE = replay.DEATH_REASONS[4]
for path in sys.argv[1:]:
    info, events, team_of = replay.parse(path)
    name = os.path.basename(path).replace('.replay', '')
    deaths = [e for e in events if e['kind'] == 'death']
    none = [e for e in deaths if e['reason'] == NONE]
    per = Counter(e['team'] for e in none)
    rounds = {t: sorted(e['round'] for e in none if e['team'] == t) for t in 'AB'}
    q = [(e['round'], e['id'], e['length'], e['reason']) for e in deaths if e['id'] in (0, 1)]
    tle = sum(1 for e in events if e['kind'] == 'action' and e['tle'])
    maxpts = max((e['points'] for e in events if e['kind'] == 'action'), default=0)
    first_other = {t: min((e['round'] for e in deaths if e['team'] == t and e['reason'] != NONE), default=None) for t in 'AB'}
    print(name)
    print('  A =', os.path.basename(info['botA']), ' B =', os.path.basename(info['botB']), ' end', info['endReason'], 'winner', info['winner'], info['standings'])
    print('  no-action deaths A', per['A'], 'B', per['B'], '| all deaths A', sum(1 for e in deaths if e['team']=='A'), 'B', sum(1 for e in deaths if e['team']=='B'))
    print('  A rounds', rounds['A'])
    print('  B rounds', rounds['B'])
    print('  A lens', [e['length'] for e in none if e['team']=='A'], 'B lens', [e['length'] for e in none if e['team']=='B'])
    print('  queen deaths (round,id,len,reason)', q, '| tle', tle, 'max points', maxpts)
