#!/usr/bin/env python3
"""Verifier claims 5, shared part (run of 2026-10-07 06:27 KST): loader and small statistics for the x5 shards."""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timedelta
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')
BANDS = ('<1700', '1700-1899', '1900-2099', '2100+')
LINES = []


def say(*a):
    s = ' '.join(str(x) for x in a)
    LINES.append(s)
    print(s)


def load():
    games = []
    for k in range(6):
        for line in (V / ('x5-%d.jsonl' % k)).read_text().splitlines():
            if line.strip():
                games.append(json.loads(line))
    bad = [g for g in games if 'error' in g]
    games = [g for g in games if 'error' not in g]
    order = sorted(games, key=lambda g: (g.get('completedAt') or '', g['game']))
    seen = {}
    for g in order:
        lst = seen.setdefault(g['map'], [])
        if g['layout'] not in lst:
            lst.append(g['layout'])
        g['map_key'] = '%s #%d' % (g['map'], lst.index(g['layout']) + 1)
        e = g.get('opponentElo') or 0
        g['band'] = '<1700' if e < 1700 else '1700-1899' if e < 1900 else '1900-2099' if e < 2100 else '2100+'
        g['large'] = g['open_tiles'] >= 2000
        g['free'] = g['map'] not in ('Schooltime', 'Slithery Fight')
        g['evening'] = (datetime.fromisoformat(g['at_kst']) - timedelta(hours=6)).strftime('%m-%d') if g.get('at_kst') else '?'
        g['opp'] = '%s (%s)' % (g.get('opponent'), g.get('opponentId'))
    return order, bad


def fisher(a, b, c, d):
    """two-sided p for the table [[a, b], [c, d]]"""
    n = a + b + c + d
    r1 = a + b
    c1 = a + c
    if n == 0:
        return 1.0

    def pr(x):
        return math.comb(r1, x) * math.comb(n - r1, c1 - x) / math.comb(n, c1)
    p0 = pr(a)
    return sum(pr(x) for x in range(max(0, c1 - (n - r1)), min(r1, c1) + 1) if pr(x) <= p0 * (1 + 1e-9))


def wilson(k, n):
    if n == 0:
        return (0.0, 1.0)
    z = 1.96
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (round(mid - half, 3), round(mid + half, 3))


def sign(k, n):
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1)) / 2 ** n)


def sh(k, n):
    return '%d of %d (%s)' % (k, n, ('%.3f' % (k / n)) if n else '-')


def boot_gap(units, n=2000, seed=1):
    """units: one (a_num, a_den, b_num, b_den) per cluster; statistic a_num/a_den - b_num/b_den over resampled
    clusters. Returns 2.5 and 97.5 percentiles and the share of resamples at or below zero."""
    rng = random.Random(seed)
    m = len(units)
    vals = []
    for _ in range(n):
        an = ad = bn = bd = 0
        for _k in range(m):
            u = units[rng.randrange(m)]
            an += u[0]
            ad += u[1]
            bn += u[2]
            bd += u[3]
        if ad and bd:
            vals.append(an / ad - bn / bd)
    vals.sort()
    if not vals:
        return None
    return (round(vals[int(0.025 * len(vals))], 4), round(vals[int(0.975 * len(vals)) - 1], 4),
            round(sum(1 for v in vals if v <= 0) / len(vals), 4))


def boot_two(units_a, units_b, n=2000, seed=1):
    """two independent sets of clusters, each unit (num, den); statistic share_a - share_b."""
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        an = ad = bn = bd = 0
        for _k in range(len(units_a)):
            u = units_a[rng.randrange(len(units_a))]
            an += u[0]
            ad += u[1]
        for _k in range(len(units_b)):
            u = units_b[rng.randrange(len(units_b))]
            bn += u[0]
            bd += u[1]
        if ad and bd:
            vals.append(an / ad - bn / bd)
    vals.sort()
    if not vals:
        return None
    return (round(vals[int(0.025 * len(vals))], 4), round(vals[int(0.975 * len(vals)) - 1], 4),
            round(sum(1 for v in vals if v <= 0) / len(vals), 4))


def by_cluster(gs, key, f):
    """sum the tuples f(g) over the games of each cluster"""
    acc = {}
    for g in gs:
        t = f(g)
        if t is None:
            continue
        cur = acc.get(g[key])
        acc[g[key]] = t if cur is None else tuple(x + y for x, y in zip(cur, t))
    return list(acc.values())


# ---------------------------------------------------------------- F25
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
REASONS = ('wall', 'own body', 'other body', 'head-on', 'other')


def tot(g, m):
    s = g['snap'].get(str(m))
    if not s:
        return None
    return s[0][1], s[1][1]


def qualifies(g):
    t = tot(g, 100)
    if t is None:
        return False
    a, b = t
    if a + b == 0:
        return False
    return a * 100 >= 95 * b


def change(g, m, add=0):
    t1 = tot(g, 100)
    t2 = tot(g, m)
    if t1 is None or t2 is None:
        return None
    a1, b1 = t1
    a2, b2 = t2
    a2 += add
    if a2 + b2 == 0 or a1 + b1 == 0:
        return None
    # exact comparison in whole numbers: -1 fall of 10 points or more, +1 rise of 10 points or more, else 0
    lhs = 10 * a2 * (a1 + b1)
    rhs = 10 * a1 * (a2 + b2)
    w = (a1 + b1) * (a2 + b2)
    flag = -1 if lhs <= rhs - w else 1 if lhs >= rhs + w else 0
    return flag, a2 / (a2 + b2) - a1 / (a1 + b1)


def rate(gs, m, want, add=None):
    k = n = 0
    for g in gs:
        c = change(g, m, add(g) if add else 0)
        if c is None:
            continue
        n += 1
        if c[0] == want:
            k += 1
    return k, n


def main():
    G, bad = load()
    say('games loaded', len(G), 'errors', len(bad), [b.get('error') for b in bad][:5])
    say('codes', dict(Counter(g['code'] for g in G)))
    for g in G:
        if g['code'] == 'other':
            continue
        if g.get('anomalies') or not g.get('final_ok') or g.get('drop_mismatch'):
            say('  check game', g['game'], g.get('anomalies'), g.get('final_ok'), g.get('drop_mismatch'))
    say('large layouts', sorted(set(g['map_key'] for g in G if g['large'])))
    floatdiff = 0
    for code in ('main', 'v31'):
        gs = [g for g in G if g['code'] == code]
        Q = [g for g in gs if qualifies(g)]
        say('')
        say('=====', code, 'games', len(gs), 'reached r100', sum(1 for g in gs if tot(g, 100)), 'qualify (ours >= 0.95 theirs at r100)', len(Q))
        for g in Q:
            for m in (200, 300):
                c = change(g, m)
                if c is None:
                    continue
                fl = -1 if c[1] <= -0.10 else 1 if c[1] >= 0.10 else 0
                if fl != c[0]:
                    floatdiff += 1
        for name, sel in (('large', True), ('other', False)):
            q = [g for g in Q if g['large'] == sel]
            r2 = [g for g in q if tot(g, 200)]
            r3 = [g for g in q if tot(g, 300)]
            say(' ', name, 'qualifying', len(q), 'reach r200', len(r2), 'reach r300', len(r3))
            say('    fall by r300', sh(*rate(q, 300, -1)), '| fall by r200', sh(*rate(q, 200, -1)),
                '| rise by r200', sh(*rate(q, 200, 1)), '| rise by r300', sh(*rate(q, 300, 1)))
            say('    wins: all qualifying', sh(sum(g['win'] for g in q), len(q)), '| reaching r200', sh(sum(g['win'] for g in r2), len(r2)),
                '| reaching r300', sh(sum(g['win'] for g in r3), len(r3)))
            ds = [change(g, 300)[1] for g in r3 if change(g, 300)]
            d2 = [change(g, 200)[1] for g in r2 if change(g, 200)]
            if ds:
                ds.sort()
                d2.sort()
                say('    share change to r300: mean %.3f median %.3f, below zero %s | to r200: mean %.3f median %.3f, below zero %s' % (
                    sum(ds) / len(ds), ds[len(ds) // 2], sh(sum(1 for x in ds if x < 0), len(ds)),
                    sum(d2) / len(d2), d2[len(d2) // 2], sh(sum(1 for x in d2 if x < 0), len(d2))))
            tt = sorted(sum(tot(g, 100)) for g in q)
            s1 = sorted(tot(g, 100)[0] / sum(tot(g, 100)) for g in q)
            if tt:
                say('    total length of both sides at r100: median %d, lowest quarter %d, min %d | our share at r100: median %.3f mean %.3f' % (
                    tt[len(tt) // 2], tt[len(tt) // 4], tt[0], s1[len(s1) // 2], sum(s1) / len(s1)))
        L = [g for g in Q if g['large']]
        O = [g for g in Q if not g['large']]
        say('  -- chance (Fisher, games as units), large against other')
        for label, m, want in (('fall by r300', 300, -1), ('fall by r200', 200, -1), ('rise by r200', 200, 1)):
            a, n1 = rate(L, m, want)
            c, n2 = rate(O, m, want)
            say('    %s: large %s, other %s, p %.4g' % (label, sh(a, n1), sh(c, n2), fisher(a, n1 - a, c, n2 - c)))
            say('       Wilson large', wilson(a, n1), 'other', wilson(c, n2), '| large without its three strongest games', sh(max(a - 3, 0), n1 - 3) if want == -1 else sh(a, n1 - 3))
        say('  -- per layout: fall by r300 | fall by r200 | rise by r200 | r100 total median')
        for mk in sorted(set(g['map_key'] for g in Q)):
            q = [g for g in Q if g['map_key'] == mk]
            tt = sorted(sum(tot(g, 100)) for g in q)
            say('    %-22s %s | %s | %s | %d %s' % (mk, sh(*rate(q, 300, -1)), sh(*rate(q, 200, -1)), sh(*rate(q, 200, 1)), tt[len(tt) // 2], 'LARGE' if q[0]['large'] else ''))
        say('  -- large, one layout name left out: fall by r300 | fall by r200 | rise by r200')
        for nm in sorted(set(g['map'] for g in L)):
            q = [g for g in L if g['map'] != nm]
            say('    without %-12s %s | %s | %s' % (nm, sh(*rate(q, 300, -1)), sh(*rate(q, 200, -1)), sh(*rate(q, 200, 1))))
        q = [g for g in L if g['map'] != 'Schooltime']
        say('  -- large, one opponent left out (opponents in the large slice: %d, battles %d)' % (len(set(g['opp'] for g in L)), len(set(g['battle'] for g in L))))
        lo = []
        for op in sorted(set(g['opp'] for g in L)):
            q = [g for g in L if g['opp'] != op]
            mine = [g for g in L if g['opp'] == op]
            lo.append((rate(q, 200, -1), rate(q, 300, -1), op, rate(mine, 200, -1), rate(mine, 300, -1)))
        r200 = sorted(k / n for (k, n), _b, _c, _d, _e in lo if n)
        r300 = sorted(k / n for _a, (k, n), _c, _d, _e in lo if n)
        say('    fall by r200 runs from %.3f to %.3f; fall by r300 from %.3f to %.3f' % (r200[0], r200[-1], r300[0], r300[-1]))
        top = sorted(lo, key=lambda t: -t[3][0])[:6]
        for t in top:
            say('    opponent %-34s own games: fall by r200 %s, by r300 %s' % (t[2], sh(*t[3]), sh(*t[4])))
        say('  -- by evening (KST day starting 06:00), large: fall by r300 | fall by r200')
        for ev in sorted(set(g['evening'] for g in L)):
            q = [g for g in L if g['evening'] == ev]
            say('    %s %s | %s' % (ev, sh(*rate(q, 300, -1)), sh(*rate(q, 200, -1))))
        say('  -- by rating band, large then other: fall by r300 | fall by r200 | rise by r200')
        for b in BANDS:
            for nm, grp in (('large', L), ('other', O)):
                q = [g for g in grp if g['band'] == b]
                if q:
                    say('    %-10s %-5s %s | %s | %s' % (b, nm, sh(*rate(q, 300, -1)), sh(*rate(q, 200, -1)), sh(*rate(q, 200, 1))))
        say('  -- by our share at r100, large then other: fall by r300 | fall by r200 | rise by r200')
        for lo_, hi_ in ((0, 0.55), (0.55, 0.7), (0.7, 1.01)):
            for nm, grp in (('large', L), ('other', O)):
                q = [g for g in grp if lo_ <= tot(g, 100)[0] / sum(tot(g, 100)) < hi_]
                if q:
                    say('    share %.2f-%.2f %-5s %s | %s | %s' % (lo_, hi_, nm, sh(*rate(q, 300, -1)), sh(*rate(q, 200, -1)), sh(*rate(q, 200, 1))))
        say('  -- only games with 40 or more total length (both sides) at r100, large then other')
        for nm, grp in (('large', L), ('other', O)):
            q = [g for g in grp if sum(tot(g, 100)) >= 40]
            say('    %-5s %s | %s | %s' % (nm, sh(*rate(q, 300, -1)), sh(*rate(q, 200, -1)), sh(*rate(q, 200, 1))))
        say('  -- only games under 40 total at r100, large then other')
        for nm, grp in (('large', L), ('other', O)):
            q = [g for g in grp if sum(tot(g, 100)) < 40]
            say('    %-5s %s | %s | %s' % (nm, sh(*rate(q, 300, -1)), sh(*rate(q, 200, -1)), sh(*rate(q, 200, 1))))
        say('  -- no selection at r100 (all games of the code that reached the round), large then other')
        for nm, sel in (('large', True), ('other', False)):
            q = [g for g in gs if g['large'] == sel and tot(g, 100) and sum(tot(g, 100)) > 0]
            say('    %-5s %s | %s | %s' % (nm, sh(*rate(q, 300, -1)), sh(*rate(q, 200, -1)), sh(*rate(q, 200, 1))))
        say('  -- our own deaths in the qualifying games, per game (count, length), by window and engine reason')
        for nm, grp in (('large', L), ('other', O)):
            for wi, wn in ((0, 'r0-100'), (1, 'r101-200'), (2, 'r201-300')):
                need = (100, 200, 300)[wi]
                q = [g for g in grp if tot(g, need)]
                if not q:
                    continue
                parts = []
                for ri, rn in enumerate(REASONS):
                    cnt = sum(g['dth'][0][wi][ri][0] for g in q)
                    ln = sum(g['dth'][0][wi][ri][1] for g in q)
                    parts.append('%s %.1f, %.1f' % (rn, cnt / len(q), ln / len(q)))
                tparts = []
                for ri, rn in enumerate(REASONS):
                    cnt = sum(g['dth'][1][wi][ri][0] for g in q)
                    ln = sum(g['dth'][1][wi][ri][1] for g in q)
                    tparts.append('%s %.1f, %.1f' % (rn, cnt / len(q), ln / len(q)))
                say('    %-5s %-9s games %d | ours: %s' % (nm, wn, len(q), '; '.join(parts)))
                say('    %-5s %-9s            | theirs: %s' % (nm, wn, '; '.join(tparts)))
            early = [g for g in grp if g['first_r4'][0] is not None and g['first_r4'][0] <= 200]
            fr = sorted(g['first_r4'][0] for g in grp if g['first_r4'][0] is not None)
            say('    %-5s games with a reason-4 (no action) death of ours at r200 or before: %d of %d; first such round over games: min %s, median %s; games with none at all %d' % (
                nm, len(early), len(grp), fr[0] if fr else '-', fr[len(fr) // 2] if fr else '-', sum(1 for g in grp if g['first_r4'][0] is None)))
        say('  -- flows between r100 and r200, and r200 and r300, per game, large qualifying games (fell by r300 against not)')
        for nm, grp in (('large fell by r300', [g for g in L if change(g, 300) and change(g, 300)[0] == -1]),
                        ('large did not fall', [g for g in L if change(g, 300) and change(g, 300)[0] != -1]),
                        ('other fell by r300', [g for g in O if change(g, 300) and change(g, 300)[0] == -1]),
                        ('other did not fall', [g for g in O if change(g, 300) and change(g, 300)[0] != -1])):
            if not grp:
                continue
            n = len(grp)
            for wi, wn, m0, m1 in ((1, 'r101-200', 100, 200), (2, 'r201-300', 200, 300)):
                row = []
                for s, sn in ((0, 'ours'), (1, 'theirs')):
                    eaten = sum(sum(g['eat'][s][wi]) for g in grp) / n
                    self_d = sum(g['dth'][s][wi][0][1] + g['dth'][s][wi][1][1] + g['dth'][s][wi][4][1] for g in grp) / n
                    fight = sum(g['dth'][s][wi][2][1] + g['dth'][s][wi][3][1] for g in grp) / n
                    net = sum(tot(g, m1)[s] - tot(g, m0)[s] for g in grp) / n
                    start = sum(tot(g, m0)[s] for g in grp) / n
                    row.append('%s start %.1f, eaten %.1f, lost to wall/own body/no action %.1f, lost to enemy or ally bodies and head-on %.1f, net %+.1f, rest (paid steps) %+.1f' % (
                        sn, start, eaten, self_d, fight, net, net - eaten + self_d + fight))
                say('    %-19s n %d %s | %s' % (nm, n, wn, ' | '.join(row)))
        say('  -- had our wall / own body / no action deaths after r100 not happened (their full length added back at the later round)')
        def addself(m):
            def f(g):
                x = 0
                for wi in ((1,) if m == 200 else (1, 2)):
                    x += g['dth'][0][wi][0][1] + g['dth'][0][wi][1][1] + g['dth'][0][wi][4][1]
                return x
            return f
        def addhalf(m):
            def f(g):
                x = 0
                for wi in ((1,) if m == 200 else (1, 2)):
                    x += (g['dth'][0][wi][0][1] + g['dth'][0][wi][1][1] + g['dth'][0][wi][4][1]) // 2
                return x
            return f
        for nm, grp in (('large', L), ('other', O)):
            say('    %-5s fall by r300 %s -> full add-back %s, half add-back %s | fall by r200 %s -> %s, %s | rise by r200 %s -> %s' % (
                nm, sh(*rate(grp, 300, -1)), sh(*rate(grp, 300, -1, addself(300))), sh(*rate(grp, 300, -1, addhalf(300))),
                sh(*rate(grp, 200, -1)), sh(*rate(grp, 200, -1, addself(200))), sh(*rate(grp, 200, -1, addhalf(200))),
                sh(*rate(grp, 200, 1)), sh(*rate(grp, 200, 1, addself(200)))))
        say('  -- growth multiple r100 to r300 (total at r300 / total at r100), medians, qualifying games reaching r300')
        for nm, grp in (('large', L), ('other', O)):
            q = [g for g in grp if tot(g, 300) and tot(g, 100)[0] > 0 and tot(g, 100)[1] > 0]
            if q:
                mu = sorted(tot(g, 300)[0] / tot(g, 100)[0] for g in q)
                mt = sorted(tot(g, 300)[1] / tot(g, 100)[1] for g in q)
                say('    %-5s n %d ours x%.2f theirs x%.2f ; games where their multiple is the larger %s' % (
                    nm, len(q), mu[len(mu) // 2], mt[len(mt) // 2], sh(sum(1 for g in q if tot(g, 300)[1] / tot(g, 100)[1] > tot(g, 300)[0] / tot(g, 100)[0]), len(q))))
        say('  -- list of large qualifying games: game, layout, opponent, rating, r100 ours-theirs, r200, r300, change200, change300, win')
        for g in sorted(L, key=lambda g: (g['map_key'], g['game'])):
            c2 = change(g, 200)
            c3 = change(g, 300)
            say('    %d %-16s %-28s %s  %s  %s  %s  %s %s %s' % (g['game'], g['map_key'], g['opp'][:28], g.get('opponentElo'), tot(g, 100), tot(g, 200), tot(g, 300),
                                                       ('%+.3f' % c2[1]) if c2 else '-', ('%+.3f' % c3[1]) if c3 else '-', 'W' if g['win'] else 'L'))
    say('')
    say('float against exact threshold disagreements', floatdiff)
    f = open(P + 'f25-numbers.txt', 'w')
    f.write('\n'.join(LINES) + '\n')
    f.close()


main()
