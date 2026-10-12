"""Scratch (diag-queenkill): (1) taken/turns by mover length band and steps, every side; (2) refused sure hits by length band with the
result class of the game; (3) the pool: games lost on queen length and how many the switch reaches. Usage: python3 qk_band.py"""
import json
from collections import Counter
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
GROUPS = (('online', ('m1', 'sr51')), ('ladder', ('L0', 'L1', 'L2')), ('rank-1', ('T0', 'T1', 'T2')))


def load(tags):
    out = []
    for t in tags:
        for line in Path(W + 'qk_scanf-' + t + '.jsonl').read_text().splitlines():
            if line.strip():
                out.append(json.loads(line))
    return out


def sure(r, lo, hi):
    return not r[4] and lo <= r[3] <= hi and r[16] == 0 and r[9] > 0 and r[6] <= 3 and r[17] <= r[6] and not (r[5] and r[3] >= 5)


def flip_class(g):
    f = g['final']
    if g['win'] == 1:
        return 'won'
    if f[7] == 0:
        return 'lost, she died anyway'
    if g['decided'] != 'queen':
        return 'lost on another rule'
    if f[3] > 0 or f[1] > f[5]:
        return 'FLIP'
    return 'open' if f[5] == f[7] else 'lost, their longest ahead'


for name, tags in GROUPS:
    games = load(tags)
    print('=====', name, len(games), 'games')
    for s in (0, 1):
        c, t = Counter(), Counter()
        for g in games:
            for r in g['chs']:
                if r[1] != s or r[4] or r[16] != 0 or r[9] == 0:
                    continue
                key = ('2-4' if r[3] <= 4 else '5-8' if r[3] <= 8 else '9+', '1-3 steps' if r[6] <= 3 else '4-5 steps' if r[6] <= 5 else '6-8 steps')
                c[key] += 1
                t[key] += r[18]
        print('  side', s, 'non-queen movers, free way inside sprint reach, part of her in view: taken/turns',
              ' | '.join('%s, %s: %d/%d' % (k[0], k[1], t[k], c[k]) for k in sorted(c)))
    if name == 'rank-1':
        continue
    for lo, hi in ((2, 4), (5, 8), (9, 99), (2, 8), (2, 99)):
        per = {}
        n = took = 0
        firsts = []
        for g in games:
            rows = [r for r in g['chs'] if r[1] == 0 and sure(r, lo, hi)]
            took += sum(r[18] for r in rows)
            rows = [r for r in rows if not r[18]]
            if rows:
                per[g['game']] = g
                n += len(rows)
                firsts.append(rows[0])
        fc = Counter(flip_class(g) for g in per.values())
        print('  ours, length %d-%d: taken %d, refused %d turns in %d games %s | first refusal of a game: own queen alive %d, after round 300 %d' % (
            lo, hi, took, n, len(per), dict(fc.most_common()), sum(1 for r in firsts if r[14] > 0), sum(1 for r in firsts if r[0] > 300)))
        if (lo, hi) == (2, 99):
            print('     FLIP games:', sorted(g['game'] for g in per.values() if flip_class(g) == 'FLIP'), 'open:', sorted(g['game'] for g in per.values() if flip_class(g) == 'open'))
    ql = [g for g in games if g['win'] == 0 and g['decided'] == 'queen']
    dead = [g for g in ql if g['final'][3] == 0]
    ahead = [g for g in dead if g['final'][1] > g['final'][5]]
    reach = [g for g in dead if any(r[1] == 0 and sure(r, 2, 99) for r in g['chs'])]
    print('  pool: lost on queen length %d; our queen dead in %d; of those our longest above their longest at the end %d; a refused sure way at some time in %d (%d of the ahead ones)' % (
        len(ql), len(dead), len(ahead), len(reach), sum(1 for g in reach if g in ahead)))
