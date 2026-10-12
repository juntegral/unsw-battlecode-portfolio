# Scratch (diag-stripes): what the starting dragons (and all dragons) do in the opening: circling a 2x2 block beside a
# portal whose room holds a pearl, first entry into a pearl room, pearls and length by round.
# Usage: python3 data/analysis/ladder/dossier/work/st_open.py <rows file> [last round, default 60]
import sys, json
from collections import Counter, defaultdict
from statistics import median

LAST = int(sys.argv[2]) if len(sys.argv) > 2 else 60
games = [json.loads(line) for line in open(sys.argv[1])]
tot = Counter()
first = defaultdict(list)
firstq = defaultdict(list)
arrive = defaultdict(list)
for g in games:
    hist = defaultdict(list)
    got = {}
    door1 = {}
    for t in g['turns']:
        if t['r'] > LAST:
            break
        s, i = t['s'], t['id']
        took = t['dirs'][0][0] if t['dirs'] else None
        door = 0
        entered = None
        for d, o in enumerate(t['opts']):
            if o and o[0] == 2 and o[2] < 48 and o[6] == 0:
                if o[5] > 0:
                    door = max(door, 2 if o[3] else 1)
                if took == d:
                    entered = (o[3], o[5] > 0)
        h = hist[i]
        h.append((t['head'], door))
        for who in (['all', 'start'] if t['st'] else ['all']):
            tot[s, who, 'turns'] += 1
            if t['hs'] >= 48 and len(h) >= 5 and h[-5][0] == t['head']:
                tot[s, who, 'circle'] += 1
                dd = max(x[1] for x in h[-4:])
                if dd:
                    tot[s, who, 'circle at a pearl door'] += 1
                    tot[s, who, 'circle at a %s door' % ('loop-room' if dd == 2 else 'dead-room')] += 1
            if door and t['hs'] >= 48:
                tot[s, who, 'on a pearl-door tile'] += 1
                if entered is None:
                    tot[s, who, 'on a pearl-door tile, did not enter'] += 1
            if t['hs'] < 48:
                tot[s, who, 'inside a room'] += 1
            tot[s, who, 'ate'] += t['ate']
        if door and s not in door1:
            door1[s] = t['r']
        if entered is not None and entered[1] and s not in got:
            got[s] = t['r']
        if entered is not None and entered[1] and t['q'] and (s, 'q') not in got:
            got[s, 'q'] = t['r']
    for s in 'ut':
        first[s].append(got.get(s, 999))
        firstq[s].append(got.get((s, 'q'), 999))
        arrive[s].append(door1.get(s, 999))
print('rounds 0-%d, %d games' % (LAST, len(games)))
for who in ('start', 'all'):
    print('dragons:', 'the two starting dragons of each side' if who == 'start' else 'all dragons')
    for key in ('turns', 'ate', 'on a pearl-door tile', 'on a pearl-door tile, did not enter', 'circle', 'circle at a pearl door',
                'circle at a loop-room door', 'circle at a dead-room door'):
        u, t = tot['u', who, key], tot['t', who, key]
        print('  %-40s ours %5d (%.3f of turns)   theirs %5d (%.3f)' % (key, u, u / tot['u', who, 'turns'], t, t / tot['t', who, 'turns']))
for name, d in (('first round a dragon of the side stands on a tile with a portal step into a room holding a pearl', arrive),
                ('first round a dragon of the side takes such a step', first), ('same, the queen (lowest starting id)', firstq)):
    print(name)
    for s in 'ut':
        v = sorted(d[s])
        print('  %s median %s; by r10 %d, by r20 %d, by r40 %d, never by r%d %d of %d' % (
            'ours  ' if s == 'u' else 'theirs', median(v), sum(x <= 10 for x in v), sum(x <= 20 for x in v), sum(x <= 40 for x in v),
            LAST, sum(x == 999 for x in v), len(v)))
