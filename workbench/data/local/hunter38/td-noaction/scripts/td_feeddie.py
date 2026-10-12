#!/usr/bin/env python3
"""Match every 'no valid action' death to a FEEDDIE log line of the same dragon in the same round.
Usage: td_feeddie.py [-v] REPLAY..."""
import sys, os
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'harness'))
import replay
from collections import Counter, defaultdict

NONE = replay.DEATH_REASONS[4]
verbose = '-v' in sys.argv
tot = Counter()
for path in [a for a in sys.argv[1:] if a != '-v']:
    info, events, team_of = replay.parse(path)
    name = os.path.basename(path).replace('.replay', '')
    logs = defaultdict(list)      # (round, id) -> texts
    acts = {}                     # (round, id) -> action
    alive = {t: set() for t in 'AB'}
    for did, t in team_of.items():
        pass
    kinds = Counter()
    rows = []
    for e in events:
        if e['kind'] == 'log':
            logs[(e['round'], e['id'])].append(e['text'])
            kinds[e['text'].split()[0] if e['text'].split() else ''] += 1
        elif e['kind'] == 'action':
            acts[(e['round'], e['id'])] = e['action']
        elif e['kind'] == 'death' and e['reason'] == NONE:
            key = (e['round'], e['id'])
            texts = logs.get(key, [])
            feed = [t for t in texts if 'FEEDDIE' in t]
            rows.append((e['round'], e['id'], e['team'], e['length'], acts.get(key), feed[0] if feed else None, texts))
    n = len(rows)
    with_feed = sum(1 for r in rows if r[5])
    tot['none'] += n; tot['feed'] += with_feed
    feedlogs = sum(1 for k, v in logs.items() for t in v if 'FEEDDIE' in t)
    tot['feedlogs'] += feedlogs
    print(f'{name}: no-action deaths {n}, with a FEEDDIE log that turn {with_feed}, FEEDDIE logs in game {feedlogs}, log kinds {dict(kinds)}')
    for r in rows:
        if verbose or not r[5]:
            print('   r%d id %d team %s len %d action %s log %r %s' % (r[0], r[1], r[2], r[3], r[4], r[5], '' if r[5] else r[6]))
print('total', dict(tot))
