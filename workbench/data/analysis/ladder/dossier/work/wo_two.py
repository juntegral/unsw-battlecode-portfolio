"""Scratch (diag-wipeout): what separates OUT from KILL and REST games in the first 60 rounds on layouts of 1200
cells or fewer: opponent rating, early deaths of starters, first split, eats, and the split/death account at r60.
Usage: python3 data/analysis/ladder/dossier/work/wo_two.py <O|L|R> [nostripes]"""
import sys, json
sys.dont_write_bytecode = True
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')


def load(src):
    rows = []
    for p in sorted(WORK.glob('wo_scan-' + src + '[0-9].jsonl')):
        for line in p.read_text().splitlines():
            g = json.loads(line)
            g.pop('contact', None)
            g.pop('samples', None)
            rows.append(g)
    return rows


def cls(g):
    return 'OUT' if g['final'][0] == 0 else 'KILL' if g['final'][4] == 0 else 'REST'


def kind(d):
    c = d['c']
    if c == 'head-on':
        return 'mate head-on' if not d['cross'] else 'rammed' if d['role'] == 'hit' else 'rams'
    if c == 'other body':
        return 'body-' + d.get('hit', '?')
    return c


def med(v):
    v = sorted(x for x in v if x is not None)
    return v[len(v) // 2] if v else None


def cum(g, lo, hi):
    out = [0] * 10
    for x in g['rc']:
        if lo <= x[0] <= hi:
            for k in range(10):
                out[k] += x[1 + k]
    return out


def describe(tag, a):
    n = len(a)
    if not n:
        return
    print('%s: games %d, opponent rating median %s' % (tag, n, med([g.get('opp_rating') for g in a])))
    at = lambda g, r: g['snap'][min(r, g['last'])]
    print('   count us/them r20 %.1f/%.1f r40 %.1f/%.1f r60 %.1f/%.1f' % tuple(sum(at(g, r)[k] for g in a) / n for r in (20, 40, 60) for k in (0, 4)))
    for lo, hi in ((0, 20), (21, 40), (41, 60)):
        T = [0] * 10
        ku, kt = Counter(), Counter()
        for g in a:
            c = cum(g, lo, hi)
            for k in range(10):
                T[k] += c[k]
            for d in g['deaths']:
                if lo <= d['r'] <= hi:
                    (ku if d['s'] == 0 else kt)[kind(d)] += 1
        print('   r%d-%d a game: us turns %.0f eats %.2f (%.1f/100 turns) splits %.2f deaths %.2f [%s] | them turns %.0f eats %.2f (%.1f/100) splits %.2f deaths %.2f [%s]' % (
            lo, hi, T[0] / n, (T[2] + T[3]) / n, 100 * (T[2] + T[3]) / max(T[0], 1), T[1] / n, sum(ku.values()) / n,
            ', '.join('%s %.2f' % (k, v / n) for k, v in ku.most_common(5)),
            T[5] / n, (T[7] + T[8]) / n, 100 * (T[7] + T[8]) / max(T[5], 1), T[6] / n, sum(kt.values()) / n,
            ', '.join('%s %.2f' % (k, v / n) for k, v in kt.most_common(5))))
    # starters
    lost = Counter()
    lost_kind = Counter()
    for g in a:
        n0 = g['snap'][0][0] if g['snap'][0] else 0
        ids = set()
        for d in g['deaths']:
            if d['s'] == 0 and d['r'] <= 40 and d['i'] < 2 * max(n0, 1) + 20:
                ids.add(d['i'])
        early = [d for d in g['deaths'] if d['s'] == 0 and d['r'] <= 40]
        lost[min(len(early), 3)] += 1
        for d in early:
            lost_kind[kind(d)] += 1
    print('   our deaths by r40 per game: none %d, one %d, two %d, three+ %d | kinds %s' % (lost[0], lost[1], lost[2], lost[3], dict(lost_kind.most_common(8))))


def main():
    src = sys.argv[1]
    rows = [g for g in load(src) if g['cells'] <= 1200]
    if len(sys.argv) > 2:
        rows = [g for g in rows if g['map'] != 'Stripes']
    small = [g for g in rows if g['snap'][0][0] == 2 and g['snap'][0][1] <= 6]
    other = [g for g in rows if not (g['snap'][0][0] == 2 and g['snap'][0][1] <= 6)]
    for name, part in (('START two dragons, length 6 or less', small), ('OTHER starts, 1200 cells or fewer', other)):
        print('==', name, 'games', len(part), dict(Counter(cls(g) for g in part)))
        for c in ('OUT', 'KILL', 'REST'):
            describe(c, [g for g in part if cls(g) == c])
        # early loss and outcome
        for horizon in (30, 40):
            tab = defaultdict(Counter)
            for g in part:
                e = sum(1 for d in g['deaths'] if d['s'] == 0 and d['r'] <= horizon)
                t = sum(1 for d in g['deaths'] if d['s'] == 1 and d['r'] <= horizon)
                key = 'we lose more' if e > t else 'they lose more' if t > e else 'level'
                tab[key][cls(g)] += 1
            print('   deaths by r%d: %s' % (horizon, '; '.join('%s: OUT %d KILL %d REST %d' % (k, v['OUT'], v['KILL'], v['REST']) for k, v in sorted(tab.items()))))
        for horizon in (20, 30):
            tab = defaultdict(Counter)
            for g in part:
                c = cum(g, 0, horizon)
                e, t = c[2] + c[3], c[7] + c[8]
                key = 'we eat more' if e > t else 'they eat more' if t > e else 'level'
                tab[key][cls(g)] += 1
            print('   eats by r%d: %s' % (horizon, '; '.join('%s: OUT %d KILL %d REST %d' % (k, v['OUT'], v['KILL'], v['REST']) for k, v in sorted(tab.items()))))


main()
