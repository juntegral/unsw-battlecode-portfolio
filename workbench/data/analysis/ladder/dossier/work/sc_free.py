# Scratch (diag-sacrifice): a closer look at the deaths by no valid action that had a free cell beside the head
# (deaths by choice), by team group and window: room behind the free cell, team size, the nearest mate, age.
# Usage: python3 data/analysis/ladder/dossier/work/sc_free.py [samples]
import sys, json
from collections import Counter, defaultdict
from statistics import median
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
games = []
for n in range(4):
    for line in Path(W + 'sc_ev-%d.jsonl' % n).read_text().splitlines():
        if line:
            games.append(json.loads(line))
BIG = ('chad gdp', 'Heartbreaker', ':3', 'f2p')


def win(r):
    return 0 if r <= 100 else 1 if r <= 200 else 2 if r <= 300 else 3


def bucket(v, cuts):
    for c in cuts:
        if v <= c:
            return '<=%d' % c
    return '>%d' % cuts[-1]


rows = defaultdict(list)
for g in games:
    grp = g['opponent'] if g['opponent'] in BIG else 'other 2100+' if g['rating'] >= 2100 else 'other below 2100'
    for d in g['events']:
        if d['reason'] != 4 or d['r'] > 300 or d['free'] == 0:
            continue
        d['game'] = g['game']
        d['battle'] = g['battle']
        d['layout'] = g['layout']
        rows[('US' if d['side'] == 'u' else grp), win(d['r'])].append(d)


def show(key, ds):
    n = len(ds)
    c = lambda f, cuts: ' '.join('%s:%d' % kv for kv in sorted(Counter(bucket(f(d), cuts) for d in ds).items()))
    near = [d['mates'][0] for d in ds if d['mates']]
    sib = sum(1 for d in ds if d['mates'] and (d['par'] == d['mates'][0][1]))
    eat_len = Counter()
    for d in ds:
        for s, wait, eid, elen, isq, istop in d['p']:
            eat_len['ours' if s != d['side'] else '2' if elen == 2 else '3' if elen == 3 else '4-5' if elen <= 5 else '6-9' if elen <= 9 else '10+'] += 1
    print('%-18s w%d n %5d | L %s | free cells %s | room %s' % (key[0], key[1], n, c(lambda d: d['L'], (2, 3, 5, 9)),
          c(lambda d: d['free'], (1, 2)), c(lambda d: d['room'], (1, 3, 8, 20, 59))))
    print('%-21s team alive %s | rounds since born %s | since last pearl %s | split as parent last round %d | pearl beside %d, pearls within 3 (med) %s' % (
        '', c(lambda d: d['n_side'] + 1, (10, 30, 50, 59)), c(lambda d: d['r'] - d['born'], (1, 5, 20, 60)),
        c(lambda d: d['r'] - d['last_eat'], (1, 5, 20, 60)), sum(1 for d in ds if d['split_r'] >= 0 and d['r'] - d['split_r'] <= 1),
        sum(d['pearl_adj'] for d in ds), median(d['pearl_near'] for d in ds)))
    print('%-21s nearest mate: dist %s | its length %s | it is the parent %d | queen within 4: %d | our head within 4: %d | moved in 6 turns (med) %s | eater length %s' % (
        '', ' '.join('%s:%d' % kv for kv in sorted(Counter(bucket(m[0], (1, 2, 3, 5)) for m in near).items())),
        ' '.join('%s:%d' % kv for kv in sorted(Counter(bucket(m[2], (2, 3, 5, 9)) for m in near).items())), sib,
        sum(1 for d in ds if d['q_alive'] and 0 <= d['q_dist'] <= 4), sum(1 for d in ds if d['foes'] and d['foes'][0][0] <= 4),
        median(d['moved6'] for d in ds), dict(eat_len)))


for key in sorted(rows):
    show(key, rows[key])

if len(sys.argv) > 1:
    print()
    for name in BIG:
        for wn in (0, 1, 2):
            ds = rows.get((name, wn), [])
            for d in ds[::max(1, len(ds) // 6)][:6]:
                print(name, 'battle', d['battle'], 'game', d['game'], d['layout'], 'r', d['r'], 'id', d['id'], 'L', d['L'], 'at', d['x'], d['y'],
                      'free', d['free'], 'room', d['room'], 'alive', d['n_side'] + 1, 'mates', d['mates'][:2], 'born', d['born'], 'last eat', d['last_eat'], 'eaten by', d['p'])
