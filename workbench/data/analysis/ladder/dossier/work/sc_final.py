# Scratch (diag-sacrifice): the numbers of the kinds table. Boxed-in deaths of every label sorted the same way
# for both sides, queens at rounds 100/200/300, what their queen and longest eat from deaths by choice, and the
# same-team head-ons of the 2100+ band.
# Usage: python3 data/analysis/ladder/dossier/work/sc_final.py
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


turns = defaultdict(lambda: [0, 0, 0])
for g in games:
    for s in 'ut':
        for k in range(3):
            turns[s, 'all'][k] += g['turns'][s][k]
            turns[s, band(g)][k] += g['turns'][s][k]

print('1. Boxed-in deaths that are not head-ons, any label, per 1,000 turns (w0/w1/w2), and count')
tab = Counter()
lens = Counter()
for g in games:
    for r, s, L, cause, free, room, q, top, age, since, dead, nt, n_side in g['compact']:
        if cause == 'headon' or free != 0:
            continue
        if 0 <= since <= 1:
            kind = 'B1 front left by a split'
        elif age <= 1 and nt <= 2 and r > 1:
            kind = 'B2 new child'
        elif dead:
            kind = 'B3 dead-end cell'
        else:
            kind = 'B4 other (crowding)'
        for b in ('all', band(g)):
            tab[s, b, kind, win(r)] += 1
            tab[s, b, 'all boxed', win(r)] += 1
            if cause in ('noact', 'split', 'sprint', 'timeout'):
                tab[s, b, 'of these, labelled no valid action', win(r)] += 1
            if q:
                tab[s, b, 'the queen herself', win(r)] += 1
        lens[s, kind, '2' if L == 2 else '3' if L == 3 else '4+'] += 1
for kind in ('B1 front left by a split', 'B2 new child', 'B3 dead-end cell', 'B4 other (crowding)', 'all boxed', 'of these, labelled no valid action', 'the queen herself'):
    for s in 'tu':
        print('  %-36s %s' % (kind, s), ' | '.join('%s %s (n %d)' % (b, '/'.join('%.2f' % (1000 * tab[s, b, kind, k] / turns[s, b][k]) for k in range(3)),
              sum(tab[s, b, kind, k] for k in range(3))) for b in ('all', 'hi')), '| L', ' '.join('%s:%d' % (x, lens[s, kind, x]) for x in ('2', '3', '4+')))

print()
print('2. Queens: alive share, median length when alive, share 5 or longer; and the side longest (median)')
for label, sel, o in (('theirs 2100+', lambda g: g['rating'] >= 2100, 4), ('theirs below 2100', lambda g: g['rating'] < 2100, 4),
                      ('ours vs 2100+', lambda g: g['rating'] >= 2100, 0), ('ours vs below 2100', lambda g: g['rating'] < 2100, 0)):
    out = []
    for rr in ('100', '200', '300'):
        vs = [g['series'][rr] for g in games if sel(g) and rr in g['series']]
        ql = [v[o + 3] for v in vs]
        alive = [x for x in ql if x > 0]
        out.append('r%s n %d alive %.0f%% length %s, 5+ %.0f%%, longest %s, dragons %s, total %s' % (rr, len(vs), 100 * len(alive) / len(vs),
                   median(alive) if alive else '-', 100 * sum(1 for x in ql if x >= 5) / len(vs), median(v[o + 1] for v in vs),
                   median(v[o] for v in vs), median(v[o + 2] for v in vs)))
    print('  %-20s' % label, ' | '.join(out))

print()
print('3. Pearls from deaths by choice (free cell, no valid action) eaten by the queen / by the side longest, per game, by round eaten')
for label, sel, s in (('theirs 2100+', lambda g: g['rating'] >= 2100, 't'), ('theirs chad gdp', lambda g: g['opponent'] == 'chad gdp', 't'),
                      ('theirs 2100+ other', lambda g: g['rating'] >= 2100 and g['opponent'] != 'chad gdp', 't'),
                      ('theirs below 2100', lambda g: g['rating'] < 2100, 't'), ('ours', lambda g: True, 'u')):
    gs = [g for g in games if sel(g)]
    q = [0, 0, 0]
    t = [0, 0, 0]
    a = [0, 0, 0]
    for g in gs:
        for d in g['events']:
            if d['side'] != s or d['reason'] != 4 or d['free'] == 0:
                continue
            for es, wait, eid, elen, isq, istop in d['p']:
                r = d['r'] + wait
                if es == s and r <= 300:
                    a[win(r)] += 1
                    q[win(r)] += isq
                    t[win(r)] += istop
    print('  %-20s games %3d | queen %s | longest %s | any of the side %s' % (label, len(gs), '/'.join('%.2f' % (x / len(gs)) for x in q),
          '/'.join('%.2f' % (x / len(gs)) for x in t), '/'.join('%.1f' % (x / len(gs)) for x in a)))

print()
print('4. Same-team head-ons, their side, by band: mover had no other free cell / other free cell with our head within 4 / other free cell, no enemy near')
c = Counter()
for g in games:
    for d in g['events']:
        if d['reason'] == 3 and d.get('st') and d['mover'] and d['r'] <= 300:
            k = 'S1' if d['free'] <= 1 else 'S2' if d['foes'] and d['foes'][0][0] <= 4 else 'S3'
            c[d['side'], band(g), k] += 1
            c[d['side'], 'all', k] += 1
for s in 'tu':
    for b in ('all', 'lo', 'mid', 'hi'):
        t = sum(turns[s, b])
        print('  %s %-3s' % (s, b), ' '.join('%s %d (%.3f/1k)' % (k, c[s, b, k], 1000 * c[s, b, k] / t) for k in ('S1', 'S2', 'S3')))

print()
print('5. Their deaths by no valid action r0-300 with a free cell: by team, share of the total')
c = Counter()
for g in games:
    for d in g['events']:
        if d['side'] == 't' and d['reason'] == 4 and d['r'] <= 300 and d['free'] > 0:
            c[g['opponent']] += 1
            c['ALL'] += 1
            c['hi' if g['rating'] >= 2100 else 'below'] += 1
            if d['n_side'] + 1 >= 60:
                c['ALL at 60+'] += 1
print('  ', c.most_common(12))
print()
print('6. Their deaths by choice in r0-100, by rounds: count by 20-round bins, and by team alive (under 60 / 60+)')
c = Counter()
for g in games:
    for d in g['events']:
        if d['side'] == 't' and d['reason'] == 4 and d['r'] <= 100 and d['free'] > 0:
            c['r%d-%d' % (20 * (d['r'] // 20), 20 * (d['r'] // 20) + 19), '60+' if d['n_side'] + 1 >= 60 else 'under 60'] += 1
            c['room <=3' if d['room'] <= 3 else 'room 4+', '60+' if d['n_side'] + 1 >= 60 else 'under 60'] += 1
print('  ', sorted(c.items()))
