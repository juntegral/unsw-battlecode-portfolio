# Scratch (diag-sacrifice): first tables from sc_ev-*.jsonl. Checks the counts against fingerprint.md, then splits
# every death up to round 300 by "boxed in" (no free cell beside the head at death) against "a free cell was there".
# Usage: python3 data/analysis/ladder/dossier/work/sc_tab.py
import sys, json
from collections import Counter, defaultdict
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
games = []
for n in range(4):
    for line in Path(W + 'sc_ev-%d.jsonl' % n).read_text().splitlines():
        if line:
            games.append(json.loads(line))
print('games', len(games), 'layouts', len({g['layout'] for g in games}))


def band(g):
    return 'lo' if g['rating'] < 1900 else 'mid' if g['rating'] < 2100 else 'hi'


def win(r):
    return 0 if r <= 100 else 1 if r <= 200 else 2 if r <= 300 else 3


# A. recount against fingerprint.md
turns = defaultdict(lambda: [0, 0, 0, 0])
for g in games:
    for s in 'ut':
        for k in range(4):
            turns[s, 'all'][k] += g['turns'][s][k]
            turns[s, band(g)][k] += g['turns'][s][k]
cnt = Counter()
for g in games:
    seen = set()
    for d in g['events']:
        if d['r'] > 300:
            continue
        wn = '0-100' if d['r'] <= 100 else '101-300'
        if d['reason'] == 4:
            cnt[d['side'], wn, d['cause'], 'all'] += 1
            cnt[d['side'], wn, d['cause'], band(g)] += 1
        elif d.get('st') and d['mover']:
            cnt[d['side'], wn, 'st-headon', 'all'] += 1
            cnt[d['side'], wn, 'st-headon', band(g)] += 1
print('A. per 1,000 turns (fingerprint: theirs noact 2.983 / 3.270, hi 5.475 / 7.978; ours 0 / 1.150; st head-on theirs 0.357 / 0.374, ours 0.098 / 0.107; split theirs 0.952 / 0.695)')
for s in 'ut':
    for b in ('all', 'lo', 'mid', 'hi'):
        t0 = turns[s, b][0]
        t1 = turns[s, b][1] + turns[s, b][2]
        row = []
        for c in ('noact', 'split', 'sprint', 'timeout', 'st-headon'):
            row.append('%s %d/%d = %.3f, %.3f' % (c, cnt[s, '0-100', c, b], cnt[s, '101-300', c, b],
                                                 1000 * cnt[s, '0-100', c, b] / t0, 1000 * cnt[s, '101-300', c, b] / t1))
        print(' ', s, b, 'turns', t0, t1, '|', ' | '.join(row))

# B. every death up to round 300: boxed in or not, by label
print()
print('B. deaths per 1,000 turns up to round 300, by window, side, band; boxed = no free cell beside the head')
tab = Counter()
for g in games:
    for r, s, L, cause, free, room, q, top, age, since, dead, nt, n_side in g['compact']:
        wn = min(win(r), 2)
        box = 'boxed' if free == 0 else 'free'
        for b in ('all', band(g)):
            tab[s, wn, b, box, cause] += 1
            tab[s, wn, b, box, 'ALL'] += 1
            if cause != 'headon':
                tab[s, wn, b, box, 'nonram'] += 1
                tab[s, wn, b, box, 'nonram-short' if L <= 3 else 'nonram-long'] += 1
                tab[s, wn, b, 'len', box] += L
causes = ('nonram', 'nonram-short', 'nonram-long', 'wall', 'own', 'body', 'noact', 'split', 'sprint', 'timeout', 'headon')
for wn in range(3):
    for b in ('all', 'lo', 'mid', 'hi'):
        for s in 'ut':
            t = turns[s, b][wn]
            for box in ('boxed', 'free'):
                print('  w%d %-3s %s %-5s' % (wn, b, s, box), ' '.join('%s %.2f' % (c, 1000 * tab[s, wn, b, box, c] / t) for c in causes),
                      '| n', tab[s, wn, b, box, 'nonram'], 'length lost/1k', '%.1f' % (1000 * tab[s, wn, b, 'len', box] / t))
