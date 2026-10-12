# Scratch (diag-walk): from wk_keep-*.jsonl, what follows a blind step that keeps the direction, one that turns onto a
# new tile, and one onto the dragon's own last 12 tiles: pearl in view at the next turn start, pearls eaten by that
# dragon in the next 10 rounds. Rates inside a layout first, then the equal-weight mean over layouts.
# Usage: python3 data/analysis/ladder/dossier/work/wk_kept.py
import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
from statistics import mean

WORK = Path('data/analysis/ladder/dossier/work')
WIN = ('r0-100', 'r101-300')
NOTH = ('N4', 'N6', 'Nf')
RECS = dict(O=[], R=[])
for path in sorted(WORK.glob('wk_keep-[OR][0-9].jsonl')):
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            RECS[r['who']].append(r)
LAYOUTS = sorted({r['layout'] for r in RECS['O']})
print('games', {w: len(v) for w, v in RECS.items()})


def lay(who, test):
    # per layout: kept-new, turned-new, re-tread: [next, found, elig10, eat10, n]
    out = {l: [[0] * 5 for _ in range(3)] for l in LAYOUTS}
    for r in RECS[who]:
        acc = out[r['layout']]
        for k, v in r['steps'].items():
            q = k.split('|')
            if q[6] == '9' or not test(q):
                continue
            a = acc[0 if q[6] == '1' else 1]
            a[0] += v[4]
            a[1] += v[5]
            a[2] += v[8]
            a[3] += v[9]
            a[4] += v[0] - v[1]
            a = acc[2]
            a[0] += v[6]
            a[1] += v[7]
            a[2] += v[10]
            a[3] += v[11]
            a[4] += v[1]
    return out


def eq(tab, kind, a, c, least=20):
    vals = [tab[l][kind][a] / tab[l][kind][c] for l in LAYOUTS if tab[l][kind][c] >= least]
    return mean(vals) if vals else 0.0


def more(tab, x, y, a, c, least=20):
    n = m = 0
    for l in LAYOUTS:
        if tab[l][x][c] >= least and tab[l][y][c] >= least:
            m += 1
            n += int(tab[l][x][a] / tab[l][x][c] > tab[l][y][a] / tab[l][y][c])
    return '%d/%d' % (n, m)


cuts = (('all blind moved', lambda q: True), ('nothing scores', lambda q: q[3] in NOTH),
        ('nothing, open or walls near', lambda q: q[3] in NOTH and q[4] in ('O', 'W')),
        ('nothing, mate within 3', lambda q: q[3] in NOTH and q[4] == 'M'),
        ('nothing, never-seen tile within 4 (N4)', lambda q: q[3] == 'N4'), ('nothing, never-seen tile 5+ away', lambda q: q[3] in ('N6', 'Nf')),
        ('nothing, first 15 rounds of life', lambda q: q[3] in NOTH and q[2] in ('a', 'b')),
        ('nothing, blind 5+ rounds', lambda q: q[3] in NOTH and q[5] == '1'),
        ('target S R H', lambda q: q[3] in ('S', 'R', 'H')), ('threat', lambda q: q[3] == 'T'))
print('window | who | cut | share kept/turned/re-tread | found next: kept, turned, re-tread (kept > turned on) | eaten in 10: kept, turned, re-tread (kept > turned on)')
for wi in (0, 1):
    for name, test in cuts:
        for who in 'OR':
            t = lay(who, lambda q: int(q[0]) == wi and test(q))
            sh = [mean(t[l][k][4] / max(1, sum(t[l][z][4] for z in range(3))) for l in LAYOUTS if sum(t[l][z][4] for z in range(3))) for k in range(3)]
            print(WIN[wi], '|', who, '|', name, '| %.1f/%.1f/%.1f' % tuple(100 * x for x in sh),
                  '| %.1f, %.1f, %.1f (%s)' % (100 * eq(t, 0, 1, 0), 100 * eq(t, 1, 1, 0), 100 * eq(t, 2, 1, 0), more(t, 0, 1, 1, 0)),
                  '| %.3f, %.3f, %.3f (%s)' % (eq(t, 0, 3, 2), eq(t, 1, 3, 2), eq(t, 2, 3, 2), more(t, 0, 1, 3, 2)))

print('\n== pooled over our 500 games: pearls per game if our turned steps above rank-1 share kept direction instead ==')
for wi in (0, 1):
    for name, test in cuts[:6]:
        tot = {}
        for who in 'OR':
            t = lay(who, lambda q: int(q[0]) == wi and test(q))
            tot[who] = [[sum(t[l][k][j] for l in LAYOUTS) for j in range(5)] for k in range(3)]
        o, r = tot['O'], tot['R']
        n_o = sum(o[k][4] for k in range(3))
        n_r = sum(r[k][4] for k in range(3))
        kept_o, kept_r = o[0][4] / n_o, r[0][4] / n_r
        e_kept, e_turn = o[0][3] / max(1, o[0][2]), o[1][3] / max(1, o[1][2])
        extra = (kept_r - kept_o) * n_o / len(RECS['O'])
        print(WIN[wi], name, '| kept share O %.1f%% R %.1f%% | our eaten in 10 after kept %.3f, after turned-new %.3f | steps to move per game %.0f | pearls per game %+.2f' % (
            100 * kept_o, 100 * kept_r, e_kept, e_turn, extra, extra * (e_kept - e_turn)))
