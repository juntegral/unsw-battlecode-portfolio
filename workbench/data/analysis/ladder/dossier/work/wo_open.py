"""Scratch (diag-wipeout): the opening of wipe-out games against other games.
Usage: python3 data/analysis/ladder/dossier/work/wo_open.py <O|L|R> games       -> per-game lines for wipe-outs (counts by round, first deaths)
       python3 data/analysis/ladder/dossier/work/wo_open.py <O|L|R> classes     -> means by outcome class and size band
Classes: OUT = we end with no dragon; KILL = they end with no dragon; REST = neither."""
import sys, json, math
sys.dont_write_bytecode = True
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')
MARKS = (10, 20, 30, 40, 50, 60, 80, 100, 150)


def load(src):
    rows = []
    for p in sorted(WORK.glob('wo_scan-' + src + '[0-9].jsonl')):
        for line in p.read_text().splitlines():
            rows.append(json.loads(line))
    return rows


def size(c):
    return '<=700' if c <= 700 else '701-1200' if c <= 1200 else '>1200'


def cls(g):
    return 'OUT' if g['final'][0] == 0 else 'KILL' if g['final'][4] == 0 else 'REST'


def kind(d):
    c = d['c']
    if c == 'head-on':
        if not d['cross']:
            return 'mate head-on'
        return 'rammed' if d['role'] == 'hit' else 'rams'
    if c == 'other body':
        return 'body-' + d.get('hit', '?')
    if c in ('wall', 'own body'):
        return c + ('' if d.get('free', 0) == 0 else '(free)')
    if c == 'no action':
        return 'noact' + ('' if d.get('free', 0) == 0 else '(choice)')
    return c


def at(g, r):
    return g['snap'][min(r, g['last'])]


def cum(g, r):
    out = [0] * 10
    for x in g['rc']:
        if x[0] <= r:
            for k in range(10):
                out[k] += x[1 + k]
    return out


def games(rows):
    for g in sorted([g for g in rows if cls(g) == 'OUT'], key=lambda g: g['gid']):
        print('%s %d %s %s %dx%d' % (g['src'], g['gid'], g['opp'][:10], g['map'], g['W'], g['H']))
        print('   round: ' + ' '.join('r%d %d/%d v %d/%d' % (r, at(g, r)[0], at(g, r)[1], at(g, r)[4], at(g, r)[5]) for r in MARKS if r <= g['last'] + 40))
        c50, c100 = cum(g, 50), cum(g, 100)
        print('   by r50: our splits %d eats %d+%d, their splits %d eats %d+%d | by r100: ours %d, %d+%d; theirs %d, %d+%d' % (
            c50[1], c50[2], c50[3], c50[6], c50[7], c50[8], c100[1], c100[2], c100[3], c100[6], c100[7], c100[8]))
        ds = [d for d in g['deaths'] if d['s'] == 0]
        print('   our deaths: ' + '; '.join('r%d #%d L%d %s%s z%.2f o5=%d e5=%d%s' % (
            d['r'], d['i'], d['L'], kind(d), ' Q' if d['q'] else '', d['z'], d['o5'], d['e5'],
            ' <-L%d k%d d%d' % (d['m']['L0'], d['m']['steps'], d['m']['d0']) if d.get('role') == 'hit' else '') for d in ds[:14]))
        dt = [d for d in g['deaths'] if d['s'] == 1 and d['r'] <= 80]
        print('   their deaths by r80: %d %s' % (len(dt), dict(Counter(kind(d) for d in dt))))


def classes(rows):
    for sz in ('<=700', '701-1200', '>1200'):
        for c in ('OUT', 'KILL', 'REST'):
            a = [g for g in rows if size(g['cells']) == sz and cls(g) == c]
            if not a:
                continue
            n = len(a)
            print('%s %s games %d wins %d' % (sz, c, n, sum(g['result'] == 'win' for g in a)))
            print('   count us/them: ' + ' '.join('r%d %.1f/%.1f' % (r, sum(at(g, r)[0] for g in a) / n, sum(at(g, r)[4] for g in a) / n) for r in MARKS))
            print('   total us/them: ' + ' '.join('r%d %.1f/%.1f' % (r, sum(at(g, r)[1] for g in a) / n, sum(at(g, r)[5] for g in a) / n) for r in MARKS))
            print('   queen alive us/them %%: ' + ' '.join('r%d %.0f/%.0f' % (r, 100 * sum(at(g, r)[3] > 0 for g in a) / n, 100 * sum(at(g, r)[7] > 0 for g in a) / n) for r in MARKS))
            for lo, hi in ((0, 30), (31, 60), (61, 100)):
                du = [d for g in a for d in g['deaths'] if d['s'] == 0 and lo <= d['r'] <= hi]
                dt = [d for g in a for d in g['deaths'] if d['s'] == 1 and lo <= d['r'] <= hi]
                tu = [0] * 10
                for g in a:
                    for x in g['rc']:
                        if lo <= x[0] <= hi:
                            for k in range(10):
                                tu[k] += x[1 + k]
                ku, kt = Counter(kind(d) for d in du), Counter(kind(d) for d in dt)
                print('   r%d-%d a game: our turns %.0f splits %.2f eats %.2f+%.2f deaths %.2f | their turns %.0f splits %.2f eats %.2f+%.2f deaths %.2f' % (
                    lo, hi, tu[0] / n, tu[1] / n, tu[2] / n, tu[3] / n, len(du) / n, tu[5] / n, tu[6] / n, tu[7] / n, tu[8] / n, len(dt) / n))
                print('      per 100 turns: our eats %.2f splits %.2f deaths %.2f | their eats %.2f splits %.2f deaths %.2f' % (
                    100 * (tu[2] + tu[3]) / max(tu[0], 1), 100 * tu[1] / max(tu[0], 1), 100 * len(du) / max(tu[0], 1),
                    100 * (tu[7] + tu[8]) / max(tu[5], 1), 100 * tu[6] / max(tu[5], 1), 100 * len(dt) / max(tu[5], 1)))
                print('      our deaths per 100 turns: ' + ', '.join('%s %.2f' % (k, 100 * v / max(tu[0], 1)) for k, v in ku.most_common(7)))
                print('      their deaths per 100 turns: ' + ', '.join('%s %.2f' % (k, 100 * v / max(tu[5], 1)) for k, v in kt.most_common(7)))


def main():
    rows = load(sys.argv[1])
    if len(sys.argv) > 3:
        rows = [g for g in rows if g['src'].startswith(sys.argv[3])]
    if sys.argv[2] == 'games':
        games(rows)
    else:
        classes(rows)


main()
