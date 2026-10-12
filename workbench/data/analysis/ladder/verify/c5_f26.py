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


# ---------------------------------------------------------------- F26
# birth record: 0 round, 1 nearer side (0 ours), 2 nearer distance, 3 other side distance, 4 in view, 5 heads of the
# nearer side within 6, 6 heads of the other side within 6, 7 nearer dragon length, 8 nearer is a queen, 9 status
# (0 turn never came, 1 walked away, 2 not farther, 3 ate it in that turn, 4 another ate it first, 5 died first),
# 10 pearls eaten in that turn, 11 steps in that turn, 12 distance after, 13 split in that turn, 14 eaten later,
# 15 eater side, 16 eaten by the nearer dragon itself, 17 meal round - birth round, 18 path steps tile to nearer
# head (cap 8, 99 beyond), 19 path steps tile to the other side nearest head
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'


def agg(gs, flt=None, eaten_only=True, view=1):
    c = [[0] * 11, [0] * 11]
    for g in gs:
        for b in g['births']:
            if view is not None and b[4] != view:
                continue
            if eaten_only and not b[14]:
                continue
            if flt and not flt(b):
                continue
            x = c[b[1]]
            x[0] += 1
            if b[14] and b[15] == b[1]:
                x[1] += 1
            st = b[9]
            if st == 1:
                x[2] += 1
                if b[10] > 0:
                    x[4] += 1
                if b[14] and b[15] == b[1]:
                    x[10] += 1
            elif st == 5:
                x[5] += 1
            elif st == 3:
                x[6] += 1
            elif st == 4:
                x[7] += 1
            elif st == 2:
                x[8] += 1
            if b[14] and b[15] != b[1] and b[17] >= 3:
                x[3] += 1
            if b[16]:
                x[9] += 1
    return c


def line(c):
    out = []
    for s, sn in ((0, 'ours'), (1, 'theirs')):
        x = c[s]
        n = x[0]
        if not n:
            out.append('%s n 0' % sn)
            continue
        out.append('%s n %d finished %.3f walked %.3f lying %.3f' % (sn, n, x[1] / n, x[2] / n, x[3] / n))
    if c[0][0] and c[1][0]:
        out.append('gaps: finished theirs-ours %+.3f, walked ours-theirs %+.3f' % (c[1][1] / c[1][0] - c[0][1] / c[0][0], c[0][2] / c[0][0] - c[1][2] / c[1][0]))
    return ' | '.join(out)


def detail(c):
    out = []
    for s, sn in ((0, 'ours'), (1, 'theirs')):
        x = c[s]
        n = x[0]
        if not n:
            continue
        out.append('%s: walked %.3f (of which ate another pearl in that turn %.3f; still finished by the side %.3f), not farther %.3f, ate it in that turn %.3f, another ate it first %.3f, died first %.3f, eaten by the nearer dragon itself %.3f' % (
            sn, x[2] / n, (x[4] / x[2]) if x[2] else 0, (x[10] / x[2]) if x[2] else 0, x[8] / n, x[6] / n, x[7] / n, x[5] / n, x[9] / n))
    return ' | '.join(out)


def main():
    G, bad = load()
    say('games loaded', len(G), 'errors', len(bad))
    for g in G:
        if g['code'] != 'other':
            g['a'] = agg([g])
    for code in ('main', 'v31'):
        gs = [g for g in G if g['code'] == code]
        L = [g for g in gs if g['large']]
        O = [g for g in gs if not g['large']]
        say('')
        say('=====', code, 'games', len(gs), 'large', len(L), 'other', len(O))
        say(' in view, later eaten')
        say('   large:', line(agg(L)))
        say('   other:', line(agg(O)))
        say('   large detail:', detail(agg(L)))
        say('   other detail:', detail(agg(O)))
        cl = agg(L)
        for s, sn in ((0, 'ours'), (1, 'theirs')):
            x = cl[s]
            say('   large %s walked %s; walked without eating another pearl in that turn %s; walked and the side did not finish %s' % (
                sn, sh(x[2], x[0]), sh(x[2] - x[4], x[0]), sh(x[2] - x[10], x[0])))
        say(' -- all births in view (eaten or not): large', line(agg(L, eaten_only=False)))
        say(' -- nearer distance 0 or 1, all births: large', line(agg(L, flt=lambda b: b[2] <= 1, eaten_only=False, view=None)))
        say(' -- nearer distance 0 or 1, eaten only: large', line(agg(L, flt=lambda b: b[2] <= 1)))
        co = agg(L, view=0)
        coa = agg(L, view=0, eaten_only=False)
        say(' -- out of view births, large: eaten ours %d theirs %d; all ours %d theirs %d' % (co[0][0], co[1][0], coa[0][0], coa[1][0]))
        say(' -- game resampling, large (2000 resamples): 2.5 pct, 97.5 pct, share of resamples at or below zero')
        say('    walked ours-theirs, games as units  ', boot_gap([(g['a'][0][2], g['a'][0][0], g['a'][1][2], g['a'][1][0]) for g in L]))
        say('    walked ours-theirs, battles as units', boot_gap(by_cluster(L, 'battle', lambda g: (g['a'][0][2], g['a'][0][0], g['a'][1][2], g['a'][1][0]))))
        say('    walked ours-theirs, opponents as units', boot_gap(by_cluster(L, 'opp', lambda g: (g['a'][0][2], g['a'][0][0], g['a'][1][2], g['a'][1][0]))))
        say('    finished theirs-ours, games as units  ', boot_gap([(g['a'][1][1], g['a'][1][0], g['a'][0][1], g['a'][0][0]) for g in L]))
        say('    finished theirs-ours, battles as units', boot_gap(by_cluster(L, 'battle', lambda g: (g['a'][1][1], g['a'][1][0], g['a'][0][1], g['a'][0][0]))))
        say('    finished theirs-ours, opponents as units', boot_gap(by_cluster(L, 'opp', lambda g: (g['a'][1][1], g['a'][1][0], g['a'][0][1], g['a'][0][0]))))
        say('    other layouts: walked ours-theirs, games', boot_gap([(g['a'][0][2], g['a'][0][0], g['a'][1][2], g['a'][1][0]) for g in O]),
            'finished theirs-ours, games', boot_gap([(g['a'][1][1], g['a'][1][0], g['a'][0][1], g['a'][0][0]) for g in O]))
        hi = lo = eq = small = 0
        fhi = flo = 0
        contrib = []
        for g in L:
            a = g['a']
            if a[0][0] < 30 or a[1][0] < 30:
                small += 1
                continue
            wu = a[0][2] / a[0][0]
            wt = a[1][2] / a[1][0]
            if wu > wt:
                hi += 1
            elif wu < wt:
                lo += 1
            else:
                eq += 1
            fu = a[0][1] / a[0][0]
            ft = a[1][1] / a[1][0]
            if ft > fu:
                fhi += 1
            elif ft < fu:
                flo += 1
            contrib.append((wu - wt, g))
        say(' -- large games with 30 or more births a side: our walked share higher in %d, lower in %d, equal %d (too few births %d), sign p %.4g; their finished share higher in %d, lower in %d' % (
            hi, lo, eq, small, sign(min(hi, lo), hi + lo), fhi, flo))
        contrib.sort(key=lambda t: -t[0])
        drop = set(g['game'] for _d, g in contrib[:3])
        say(' -- large without the three games with the widest walked gap:', line(agg([g for g in L if g['game'] not in drop])))
        say(' -- by rating band, large')
        for b in BANDS:
            q = [g for g in L if g['band'] == b]
            if q:
                say('    %-10s games %d: %s' % (b, len(q), line(agg(q))))
        say(' -- per large layout')
        for mk in sorted(set(g['map_key'] for g in L)):
            q = [g for g in L if g['map_key'] == mk]
            say('    %-16s games %d: %s' % (mk, len(q), line(agg(q))))
        say(' -- large, one layout name left out')
        for nm in sorted(set(g['map'] for g in L)):
            say('    without %-12s %s' % (nm, line(agg([g for g in L if g['map'] != nm]))))
        gaps = []
        for op in sorted(set(g['opp'] for g in L)):
            c = agg([g for g in L if g['opp'] != op])
            if c[0][0] and c[1][0]:
                gaps.append((c[0][2] / c[0][0] - c[1][2] / c[1][0], c[1][1] / c[1][0] - c[0][1] / c[0][0], op))
        gaps.sort()
        say(' -- large, one opponent left out (%d opponents): walked gap from %+.3f (without %s) to %+.3f (without %s); finished gap from %+.3f to %+.3f' % (
            len(gaps), gaps[0][0], gaps[0][2], gaps[-1][0], gaps[-1][2], min(x[1] for x in gaps), max(x[1] for x in gaps)))
        opp_hi = opp_lo = 0
        for op in sorted(set(g['opp'] for g in L)):
            c = agg([g for g in L if g['opp'] == op])
            if c[0][0] >= 30 and c[1][0] >= 30:
                if c[0][2] / c[0][0] > c[1][2] / c[1][0]:
                    opp_hi += 1
                else:
                    opp_lo += 1
        say('    opponents (30 or more births a side) with our walked share higher %d, not higher %d' % (opp_hi, opp_lo))
        say(' -- by our seat, large')
        for seat in 'AB':
            say('    we are %s: %s' % (seat, line(agg([g for g in L if g['our_side'] == seat]))))
        say(' -- head counts within 6 of the tile at the birth, large (nearer side heads, other side heads)')
        for a_, b_ in ((1, 1), (1, 2), (2, 1), (2, 2)):
            say('    %d and %d: %s' % (a_, b_, line(agg(L, flt=lambda b, a_=a_, b_=b_: b[5] == a_ and b[6] == b_))))
        say('    3 or more on the nearer side:', line(agg(L, flt=lambda b: b[5] >= 3)))
        say('    3 or more on the other side :', line(agg(L, flt=lambda b: b[6] >= 3)))
        for s, sn in ((0, 'ours nearer'), (1, 'theirs nearer')):
            ns = no = n = 0
            for g in L:
                for b in g['births']:
                    if b[4] and b[14] and b[1] == s:
                        n += 1
                        ns += b[5]
                        no += b[6]
            if n:
                say('    %s: mean heads of the nearer side within 6 %.2f, of the other side %.2f' % (sn, ns / n, no / n))
        say(' -- same cells for both sides (nearer distance, other distance, head counts capped at 3), weighted by their births, large')
        cells = {}
        for g in L:
            for b in g['births']:
                if not b[4] or not b[14]:
                    continue
                key = (b[2], b[3], min(b[5], 3), min(b[6], 3))
                x = cells.setdefault(key, [[0, 0, 0], [0, 0, 0]])[b[1]]
                x[0] += 1
                if b[15] == b[1]:
                    x[1] += 1
                if b[9] == 1:
                    x[2] += 1
        w = fo = ft = wo = wt = 0.0
        for key, (u, t) in cells.items():
            if u[0] >= 5 and t[0] >= 5:
                w += t[0]
                fo += t[0] * u[1] / u[0]
                ft += t[1]
                wo += t[0] * u[2] / u[0]
                wt += t[2]
        if w:
            say('    common cells cover %d of their births: finished ours %.3f theirs %.3f; walked ours %.3f theirs %.3f' % (w, fo / w, ft / w, wo / w, wt / w))
        say(' -- by nearer distance, large')
        for dn in range(0, 6):
            say('    distance %d: %s' % (dn, line(agg(L, flt=lambda b, dn=dn: b[2] == dn))))
        say(' -- path steps to the nearer head equal the plain distance (no kelp in the way), large:', line(agg(L, flt=lambda b: b[18] == b[2])))
        say(' -- path steps longer than the plain distance or beyond 8, large:', line(agg(L, flt=lambda b: b[18] != b[2])))
        say(' -- nearer dragon is not a queen, large:', line(agg(L, flt=lambda b: not b[8])))
        say(' -- nearer dragon is a queen, large:', line(agg(L, flt=lambda b: b[8])))
        say(' -- nearer dragon length, large')
        for lo_, hi_ in ((1, 1), (2, 2), (3, 3), (4, 6), (7, 99)):
            say('    length %d-%d: %s' % (lo_, hi_, line(agg(L, flt=lambda b, lo_=lo_, hi_=hi_: lo_ <= b[7] <= hi_))))
        say(' -- by birth round, large')
        for lo_, hi_ in ((0, 100), (101, 200), (201, 300), (301, 499)):
            say('    r%d-%d: %s' % (lo_, hi_, line(agg(L, flt=lambda b, lo_=lo_, hi_=hi_: lo_ <= b[0] <= hi_))))
        say(' -- by birth round, other')
        for lo_, hi_ in ((0, 100), (101, 200), (201, 300), (301, 499)):
            say('    r%d-%d: %s' % (lo_, hi_, line(agg(O, flt=lambda b, lo_=lo_, hi_=hi_: lo_ <= b[0] <= hi_))))
        say(' -- other layouts by name')
        for mk in sorted(set(g['map_key'] for g in O)):
            q = [g for g in O if g['map_key'] == mk]
            say('    %-22s games %d: %s' % (mk, len(q), line(agg(q))))
    f = open(P + 'f26-numbers.txt', 'w')
    f.write('\n'.join(LINES) + '\n')
    f.close()


main()
