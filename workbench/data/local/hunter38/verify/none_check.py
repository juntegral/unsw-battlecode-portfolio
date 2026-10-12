#!/usr/bin/env python3
"""The 'no valid action' queen deaths on tower_defense: what else happens in that round?
Run from the repo root:  python3 data/local/hunter38/verify/none_check.py"""
import sys
sys.dont_write_bytecode = True
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'harness'))
import replay

for name in ('base_tower_defense_3000_0', 'base_tower_defense_3001_0', 'candidate_tower_defense_3000_0'):
    info, events, team_of = replay.parse(os.path.join(os.path.dirname(HERE), 'replays', name + '.replay'))
    none = [e for e in events if e['kind'] == 'death' and e['reason'] == replay.DEATH_REASONS[4]]
    by_round = Counter((e['round'], e['team']) for e in none)
    q = [e for e in none if e['id'] in (0, 1)]
    alive_actions = Counter()
    for e in events:
        if e['kind'] == 'action' and e['round'] in {x['round'] for x in q}:
            alive_actions[(e['round'], team_of.get(e['id']), e['action'])] += 1
    tle = sum(1 for e in events if e['kind'] == 'action' and e['tle'])
    print(name, 'end:', info['endReason'], 'winner', info['winner'], 'standings', info['standings'])
    print('   no-valid-action deaths in the game:', len(none), 'by (round, team):', sorted(by_round.items())[:12])
    print('   queen rows:', [(e['round'], e['id'], e['team'], e['length']) for e in q], 'timeouts flagged:', tle)
    print('   actions in those rounds by (round, team, action):', sorted(alive_actions.items()))
