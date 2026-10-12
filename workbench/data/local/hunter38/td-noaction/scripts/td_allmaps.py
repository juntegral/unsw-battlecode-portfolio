#!/usr/bin/env python3
"""No-action deaths per map over all 136 hunter38 replays. Usage: td_allmaps.py REPLAY_DIR"""
import sys, os, glob
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'harness'))
import replay
from collections import defaultdict
NONE = replay.DEATH_REASONS[4]
agg = defaultdict(lambda: dict(games=0, with_na=0, na=0, first=999, queen=0, before401=0, lens=[]))
for p in sorted(glob.glob(os.path.join(sys.argv[1], '*.replay'))):
    name = os.path.basename(p)[:-7]
    m = name.split('_', 1)[1].rsplit('_', 2)[0]
    info, ev, team = replay.parse(p)
    cells = [int(x) for x in info['map'].splitlines()[0].split()[1:3]]
    a = agg[m]; a['games'] += 1; a['cells'] = cells[0] * cells[1]
    na = [e for e in ev if e['kind'] == 'death' and e['reason'] == NONE]
    a['with_na'] += bool(na); a['na'] += len(na)
    a['queen'] += sum(1 for e in na if e['id'] in (0, 1))
    a['before401'] += sum(1 for e in na if e['round'] < 401)
    if na: a['first'] = min(a['first'], min(e['round'] for e in na))
print('%-22s %5s %5s %9s %9s %7s %10s %12s' % ('map', 'cells', 'games', 'games w/', 'no-action', 'first', 'before', 'queens that'))
print('%-22s %5s %5s %9s %9s %7s %10s %12s' % ('', '', '', 'any', 'deaths', 'round', 'r401', 'died so'))
for m, a in sorted(agg.items(), key=lambda kv: kv[1]['cells']):
    print('%-22s %5d %5d %9d %9d %7s %10d %12d' % (m, a['cells'], a['games'], a['with_na'], a['na'], a['first'] if a['na'] else '-', a['before401'], a['queen']))
print('total no-action deaths', sum(a['na'] for a in agg.values()), 'before r401', sum(a['before401'] for a in agg.values()), 'queens', sum(a['queen'] for a in agg.values()))
