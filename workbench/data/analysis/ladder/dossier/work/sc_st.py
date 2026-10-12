# Scratch (diag-sacrifice): same-team head-ons up to round 300, both sides. The mover's free-cell count is taken
# after the dragon it hit was removed, so 1 means "no free cell but the mate's head" when the hit dragon is 2 long.
# Usage: python3 data/analysis/ladder/dossier/work/sc_st.py
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


def win(r):
    return 0 if r <= 100 else 1 if r <= 200 else 2 if r <= 300 else 3


def band(g):
    return 'lo' if g['rating'] < 1900 else 'mid' if g['rating'] < 2100 else 'hi'


pairs = defaultdict(list)
team = defaultdict(lambda: [0, 0, 0, 0])
turns = defaultdict(int)
for g in games:
    for s in 'ut':
        turns[s] += sum(g['turns'][s][:3])
        turns[s, band(g)] += sum(g['turns'][s][:3])
        team[g['opponent'] if s == 't' else 'US'][3] += sum(g['turns'][s][:3])
    by = {}
    for d in g['events']:
        if d['reason'] == 3:
            by[d['r'], d['id']] = d
    for d in g['events']:
        if d['reason'] == 3 and d.get('st') and d['mover'] and d['r'] <= 300:
            hit = by[d['r'], d['o_id']]
            other = d['free'] - 1
            if other <= 0:
                kind = 'S1 mover had no other free cell'
            elif d['foes'] and d['foes'][0][0] <= 4:
                kind = 'S2 other cell free, our head within 4' if d['side'] == 't' else 'S2 other cell free, their head within 4'
            else:
                kind = 'S3 other cell free, no enemy near'
            d['kind'] = kind
            d['hit'] = hit
            d['band'] = band(g)
            pairs[d['side']].append(d)
            name = g['opponent'] if d['side'] == 't' else 'US'
            team[name][0 if other <= 0 else 1 if kind[1] == '2' else 2] += 1

for s, label in (('t', 'THEIRS'), ('u', 'OURS')):
    ds = pairs[s]
    print(label, 'same-team head-ons r0-300:', len(ds), 'per 1,000 turns %.3f' % (1000 * len(ds) / turns[s]),
          '| by band', ' '.join('%s %.3f' % (b, 1000 * sum(1 for d in ds if d['band'] == b) / turns[s, b]) for b in ('lo', 'mid', 'hi')))
    for kind in sorted({d['kind'] for d in ds}):
        sel = [d for d in ds if d['kind'] == kind]
        n = len(sel)
        eat = Counter()
        drop = 0
        for d in sel:
            for x in (d, d['hit']):
                drop += x['np']
                for es, wait, eid, elen, isq, istop in x['p']:
                    eat['ours' if es != x['side'] else 'queen' if isq else 'longest' if istop else '5+' if elen >= 5 else '2-4'] += 1
        print('  %-40s n %4d (w0 %d, w1 %d, w2 %d) | hit 3+ long %d | mover L 2:%d 3:%d 4+:%d | hit L 2:%d 3:%d 4+:%d | hit one had no free cell %d | parent and child %d | mover split last round %d | hit is queen %d, mover is queen %d | team 60+ alive %d | third mate twice the mover within 4: %d' % (
            kind, n, sum(1 for d in sel if win(d['r']) == 0), sum(1 for d in sel if win(d['r']) == 1), sum(1 for d in sel if win(d['r']) == 2),
            sum(1 for d in sel if d['hit']['L'] >= 3),
            sum(1 for d in sel if d['L'] == 2), sum(1 for d in sel if d['L'] == 3), sum(1 for d in sel if d['L'] >= 4),
            sum(1 for d in sel if d['hit']['L'] == 2), sum(1 for d in sel if d['hit']['L'] == 3), sum(1 for d in sel if d['hit']['L'] >= 4),
            sum(1 for d in sel if d['hit']['free'] == 0), sum(1 for d in sel if d['par'] == d['o_id'] or d['hit']['par'] == d['id']),
            sum(1 for d in sel if d['split_r'] >= 0 and d['r'] - d['split_r'] <= 1), sum(1 for d in sel if d['hit']['q']), sum(1 for d in sel if d['q']),
            sum(1 for d in sel if d['n_side'] + 1 >= 60),
            sum(1 for d in sel if len([m for m in d['mates'] if m[1] != d['o_id'] and m[0] <= 4 and m[2] >= 2 * d['L']]) > 0)))
        print('  %-40s length lost %d, dropped %d: eaten by own 2-4 %.0f%%, own 5+ %.0f%%, their longest %.0f%%, their queen %.0f%%, the other side %.0f%%, nobody %.0f%%' % (
            '', sum(d['L'] + d['hit']['L'] for d in sel), drop, 100 * eat['2-4'] / drop, 100 * eat['5+'] / drop, 100 * eat['longest'] / drop,
            100 * eat['queen'] / drop, 100 * eat['ours'] / drop, 100 * (drop - sum(eat.values())) / drop))
print()
print('teams by rate (S1/S2/S3 per 1,000 turns), 10 highest with 10+ events:')
rows = sorted(((1000 * sum(v[:3]) / v[3], k, v) for k, v in team.items() if sum(v[:3]) >= 10), reverse=True)
for rate, k, v in rows[:10]:
    print('  %-24s %.2f  (%d/%d/%d)' % (k[:24], rate, v[0], v[1], v[2]))
v = team['US']
print('  %-24s %.2f  (%d/%d/%d)' % ('US', 1000 * sum(v[:3]) / v[3], v[0], v[1], v[2]))
