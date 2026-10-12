"""Scratch (diag-attack): the proposed rule H as it would be coded, per layout, and what it costs.
H = a non-queen dragon of length 2-4 with an enemy head showing at least twice its length in parts in its 7x7 view,
    within ceil(L/4)+L-2 steps. No count rule, no round rule, no unit rule. "new" = today's rule says no (TRADE_EVEN on or off: argv[1]).
Usage: python3 data/analysis/ladder/dossier/work/at_more.py [even|plain]"""
import sys, json
from collections import Counter, defaultdict
from pathlib import Path

EVEN = len(sys.argv) < 2 or sys.argv[1] == 'even'
D = Path('data/analysis/ladder/dossier/work')
G = []
for n in range(5):
    with open(D / ('at_scan-%d.jsonl' % n)) as f:
        for line in f:
            G.append(json.loads(line))
NG = len(G)
for g in G:
    g['grow'] = 150 if g['cells'] > 1200 else 300
    s300 = g['series'].get('300')
    g['feed'] = 300 if (g['cells'] > 600 and s300 and s300[3] > 0) else 400
    g['aggr'] = g['cells'] <= 1200
    g['hox'] = dict(((x['r'], x['mid'], x['vid']), x) for x in g['hos'] if x['cross'])


def fails(g, r, even):
    rnd, L, q, Lt, dist, free, ov, ev, vis, n_own, lng, big, pe = r[0], r[3], r[4], r[7], r[10], r[11], r[12], r[13], r[16], r[17], r[19], r[20], r[24]
    feeding = rnd > g['feed'] or (rnd > 200 and n_own >= 56)
    plain_reach = free + L - 2
    if not q and L <= 10 and dist <= plain_reach and dist <= 8:
        if (vis >= 10 and vis >= L + 4) or big:
            return ()
        if feeding and vis >= 6 and vis * 2 >= L and lng > 0:
            return ()
    f = []
    if q:
        f.append('queen')
    if L > 4:
        f.append('len>4')
    if rnd > g['feed']:
        f.append('feedround')
    if n_own < (1 if g['aggr'] else 8):
        f.append('units')
    if ov + 1 - ev < 1:
        f.append('count')
    cap = n_own >= 59
    need = L if (cap or g['aggr'] or even) else max(5, L + 2)
    if vis < need:
        f.append('size')
    if dist > min(plain_reach, 3 if g['aggr'] else 4):
        f.append('steps')
    return tuple(f)


def H(g, r):
    L = r[3]
    return (not r[4]) and L <= 4 and r[16] >= 2 * L and r[10] <= r[11] + L - 2


def new(g, r):
    return H(g, r) and bool(fails(g, r, EVEN))


def swing(x):
    return (x['mm'] + x['vm'] - x['L0']) - (x['mv'] + x['vv'] - x['Lv'])


print('TRADE_EVEN counted as', 'on' if EVEN else 'off')
# 1 per layout
lay = defaultdict(Counter)
for g in G:
    a = lay[g['layout']]
    a['games'] += 1
    a['cells'] = g['cells']
    a['won'] += int(g['result'] == 'win')
    for r in g['chs']:
        if not H(g, r):
            continue
        s = r[1]
        isnew = bool(fails(g, r, EVEN))
        tag = 'new' if isnew else 'old'
        a[(s, tag, 'n')] += 1
        a[(s, tag, 'took')] += int(r[22] == 1)
        if r[22] == 1:
            x = g['hox'].get((r[0], r[2], r[6]))
            if x:
                a[(s, tag, 'sw')] += swing(x)
                a[(s, tag, 'hn')] += 1
                a[(s, tag, 'Lv')] += x['Lv']
print('layout | cells | games (won) | H new: ours chances a game, take; theirs chances a game, take | their swing per meeting (n) | H already allowed: ours a game, take')
hi = 0
tot = Counter()
for k, a in sorted(lay.items(), key=lambda z: -z[1]['cells']):
    n = a['games']
    ro = a[(0, 'new', 'took')] / max(1, a[(0, 'new', 'n')])
    rt = a[(1, 'new', 'took')] / max(1, a[(1, 'new', 'n')])
    if a[(0, 'new', 'n')] >= 10 and a[(1, 'new', 'n')] >= 10:
        tot['both'] += 1
        hi += int(rt > ro)
    print('  %-22s %5d | %3d (%2d) | %6.2f %.3f; %6.2f %.3f | %+6.2f (%d) | %6.2f %.3f' % (
        k, a['cells'], n, a['won'], a[(0, 'new', 'n')] / n, ro, a[(1, 'new', 'n')] / n, rt,
        a[(1, 'new', 'sw')] / max(1, a[(1, 'new', 'hn')]), a[(1, 'new', 'hn')],
        a[(0, 'old', 'n')] / n, a[(0, 'old', 'took')] / max(1, a[(0, 'old', 'n')])))
print('layouts with 10 or more new chances on both sides: %d; theirs take more on %d' % (tot['both'], hi))

# 2 totals and what the rule would add
c = Counter()
for g in G:
    big = not g['aggr']
    for r in g['chs']:
        if not new(g, r):
            continue
        s = r[1]
        for tag in ('all', 'big' if big else 'small'):
            c[(s, tag, 'n')] += 1
            c[(s, tag, 'took')] += int(r[22] == 1)
            c[(s, tag, 'units')] += int(r[17] < 8 and big)
            if r[22] == 1:
                x = g['hox'].get((r[0], r[2], r[6]))
                if x:
                    c[(s, tag, 'hn')] += 1
                    c[(s, tag, 'sw')] += swing(x)
                    for z in ('L0', 'Lv', 'paid', 'vtop', 'vq', 'vbig'):
                        c[(s, tag, z)] += x[z]
                    c[(s, tag, 'gm')] += x['mm'] + x['vm']
                    c[(s, tag, 'gv')] += x['mv'] + x['vv']
                    c[(s, tag, 'drop')] += x['dm'] + x['dv']
                    c[(s, tag, 'v10')] += int(x['Lv'] >= 10)
nb = sum(1 for g in G if not g['aggr'])
print()
print('H new, totals. games: all %d, above 1200 cells %d, at or below %d' % (NG, nb, NG - nb))
for tag, ng in (('all', NG), ('big', nb), ('small', NG - nb)):
    for s, name in ((0, 'ours'), (1, 'theirs')):
        n = c[(s, tag, 'n')]
        h = max(1, c[(s, tag, 'hn')])
        print('  %-5s %-6s: %6.2f chances a game of that kind, take %.3f (with fewer than 8 of its side alive: %.3f of chances) | taken: mover start %.2f (paid %.2f), victim %.2f, victim 10+ %.3f, victim its side longest %.3f, a queen %.3f, longer than all of the mover side %.3f | dropped %.2f, eaten by mover side %.2f, by victim side %.2f | swing %+.2f (n=%d)' % (
            tag, name, n / ng, c[(s, tag, 'took')] / max(1, n), c[(s, tag, 'units')] / max(1, n), c[(s, tag, 'L0')] / h, c[(s, tag, 'paid')] / h, c[(s, tag, 'Lv')] / h, c[(s, tag, 'v10')] / h,
            c[(s, tag, 'vtop')] / h, c[(s, tag, 'vq')] / h, c[(s, tag, 'vbig')] / h, c[(s, tag, 'drop')] / h, c[(s, tag, 'gm')] / h, c[(s, tag, 'gv')] / h, c[(s, tag, 'sw')] / h, c[(s, tag, 'hn')]))
    no = c[(0, tag, 'n')]
    ro = c[(0, tag, 'took')] / max(1, no)
    rt = c[(1, tag, 'took')] / max(1, c[(1, tag, 'n')])
    st = c[(1, tag, 'sw')] / max(1, c[(1, tag, 'hn')])
    print('    -> at their rate %+.2f rams a game, %+.1f length swing a game; if every such chance is taken (0.85) %+.2f rams, %+.1f' % (
        (rt - ro) * no / ng, (rt - ro) * no / ng * st, (0.85 - ro) * no / ng, (0.85 - ro) * no / ng * st))

# 3 the class of the recount, from my scan
rc = Counter()
for g in G:
    for x in g['hos']:
        if not x['cross']:
            continue
        k = 'they' if x['ms'] == 1 else 'we'
        for tag in ('all', 'big') if (x['Ld'] <= 4 and x['Lv'] >= 2 * x['Ld']) else ('all',):
            rc[(k, tag, 'n')] += 1
            rc[(k, tag, 'Lm')] += x['Ld']
            rc[(k, tag, 'Lv')] += x['Lv']
            rc[(k, tag, 'eat_m')] += x['mm'] + x['vm']
            rc[(k, tag, 'eat_v')] += x['mv'] + x['vv']
            rc[(k, tag, 'drops')] += x['dm'] + x['dv']
print()
print('for the recount (lengths at death): who, class, meetings, mover length, victim length, drops, eaten by mover side, by victim side')
for k in ('they', 'we'):
    for tag in ('all', 'big'):
        print('  %-4s %-3s %6d %7d %7d %7d %7d %7d' % (k, tag, rc[(k, tag, 'n')], rc[(k, tag, 'Lm')], rc[(k, tag, 'Lv')], rc[(k, tag, 'drops')], rc[(k, tag, 'eat_m')], rc[(k, tag, 'eat_v')]))

# 4 rounds
print()
print('H new by 100 rounds: ours chances a game, take | theirs chances a game, take')
rb = Counter()
for g in G:
    for r in g['chs']:
        if new(g, r):
            b = min(4, (r[0] - 1) // 100)
            rb[(r[1], b, 'n')] += 1
            rb[(r[1], b, 'took')] += int(r[22] == 1)
for b in range(5):
    print('  r%d-%d: %5.2f %.3f | %5.2f %.3f' % (b * 100 + 1, b * 100 + 100, rb[(0, b, 'n')] / NG, rb[(0, b, 'took')] / max(1, rb[(0, b, 'n')]), rb[(1, b, 'n')] / NG, rb[(1, b, 'took')] / max(1, rb[(1, b, 'n')])))

# 5 examples: lost on longest dragon, a refused new chance against their longest after round 300
print()
print('examples (lost on longest dragon; refused new chance of ours against their longest dragon, 8+, after round 300): game layout rating | final longest ours/theirs | round actor L -> target Lt vis own/enemy in view dist')
shown = 0
for g in sorted(G, key=lambda g: g['game']):
    if g['result'] != 'loss' or g['ended_by'] != 'longest dragon':
        continue
    ex = [r for r in g['chs'] if r[1] == 0 and new(g, r) and r[22] != 1 and r[9] and r[7] >= 8 and r[0] > 300]
    if not ex:
        continue
    f = g['final']
    print('  %d %s %d | %d/%d | %s' % (g['game'], g['layout'], g['rating'], f[1], f[5], '; '.join('r%d #%d L%d -> #%d L%d vis%d %d/%d d%d' % (r[0], r[2], r[3], r[6], r[7], r[16], r[12] + 1, r[13], r[10]) for r in ex[:6])))
    shown += 1
print('games listed', shown)

# 6 where to put the ratio: chances our rule refuses only for the count or the round, by visible parts over own length
print()
print('refused only for count or round (TRADE_EVEN on), by visible parts / own length: ours chances a game, take | theirs a game, take | their swing (n) | ours taken swing (n)')
rt = defaultdict(Counter)
for g in G:
    for r in g['chs']:
        if r[4] or r[3] > 4 or r[10] > r[11] + r[3] - 2:
            continue
        f = fails(g, r, True)
        if not f or any(x not in ('count', 'feedround') for x in f):
            continue
        q = r[16] / r[3]
        b = '1.0-1.49' if q < 1.5 else '1.5-1.99' if q < 2 else '2.0-2.99' if q < 3 else '3.0+'
        for key in (b, b + (' count' if 'count' in f else ' round only')):
            a = rt[key]
            a[(r[1], 'n')] += 1
            a[(r[1], 'took')] += int(r[22] == 1)
            if r[22] == 1:
                x = g['hox'].get((r[0], r[2], r[6]))
                if x:
                    a[(r[1], 'hn')] += 1
                    a[(r[1], 'sw')] += swing(x)
for b in sorted(rt):
    a = rt[b]
    print('  %-20s %6.2f %.3f | %6.2f %.3f | %+.2f (%d) | %+.2f (%d)' % (b, a[(0, 'n')] / NG, a[(0, 'took')] / max(1, a[(0, 'n')]), a[(1, 'n')] / NG, a[(1, 'took')] / max(1, a[(1, 'n')]),
                                                         a[(1, 'sw')] / max(1, a[(1, 'hn')]), a[(1, 'hn')], a[(0, 'sw')] / max(1, a[(0, 'hn')]), a[(0, 'hn')]))

# 7 inside the layouts above 1200 cells: wins against losses
print()
print('layouts above 1200 cells, per game, wins | losses: H chances of ours (new), taken; H rams by ours (all); H rams by theirs on us (all); their H-new take')
wl = defaultdict(Counter)
for g in G:
    if g['aggr'] or g['result'] not in ('win', 'loss'):
        continue
    a = wl[g['result']]
    a['games'] += 1
    for r in g['chs']:
        if not H(g, r):
            continue
        isnew = bool(fails(g, r, EVEN))
        s = r[1]
        a[(s, 'h')] += 1
        a[(s, 'htook')] += int(r[22] == 1)
        if isnew:
            a[(s, 'n')] += 1
            a[(s, 'took')] += int(r[22] == 1)
for k in ('win', 'loss'):
    a = wl[k]
    n = a['games']
    print('  %-4s %3d games: new chances %.2f, take %.3f | our H rams %.2f | their H rams %.2f | their new chances %.2f, take %.3f' % (
        k, n, a[(0, 'n')] / n, a[(0, 'took')] / max(1, a[(0, 'n')]), a[(0, 'htook')] / n, a[(1, 'htook')] / n, a[(1, 'n')] / n, a[(1, 'took')] / max(1, a[(1, 'n')])))

# 8 the mover in the meetings ours already take in H: is it our longest or the queen
mt = Counter()
for g in G:
    for r in g['chs']:
        if r[1] == 0 and H(g, r) and r[22] == 1:
            x = g['hox'].get((r[0], r[2], r[6]))
            if x:
                mt['n'] += 1
                mt['mtop'] += x['mtop']
                mt['mtop_after'] += int(x['mtop'] and x['r'] > g['grow'])
                mt['mq'] += x['mq']
print()
print('H meetings ours start today: %d; the mover is one of our longest in %d (after the switch round %d); the mover is our queen in %d' % (mt['n'], mt['mtop'], mt['mtop_after'], mt['mq']))
