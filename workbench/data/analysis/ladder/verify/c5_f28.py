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


# ---------------------------------------------------------------- F28
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'


def cnt(q, flt=None):
    out = [[0, 0, 0], [0, 0, 0]]
    for g in q:
        for c in g['cases']:
            if flt and not flt(c):
                continue
            x = out[c['s']]
            if c['died']:
                x[2] += 1
                continue
            x[1] += 1
            if c['nd'] < c['d']:
                x[0] += 1
    return out


def line(o):
    s = 'ours %s, theirs %s' % (sh(o[0][0], o[0][1]), sh(o[1][0], o[1][1]))
    if o[0][1] and o[1][1]:
        s += ', gap %+.3f, Fisher p %.3g' % (o[0][0] / o[0][1] - o[1][0] / o[1][1], fisher(o[0][0], o[0][1] - o[0][0], o[1][0], o[1][1] - o[1][0]))
    s += ' (died in her turn: ours %d, theirs %d)' % (o[0][2], o[1][2])
    return s


def unit(g, flt):
    o = cnt([g], flt)
    return (o[0][0], o[0][1], o[1][0], o[1][1])


def runs(q, d):
    """one case per run of consecutive rounds at distance d for the same queen: [first turn closer, any turn closer, runs]"""
    out = [[0, 0, 0], [0, 0, 0]]
    for g in q:
        for s in (0, 1):
            cs = sorted((c for c in g['cases'] if c['s'] == s and c['d'] == d), key=lambda c: c['r'])
            prev = None
            cur = None
            for c in cs:
                if prev is None or c['r'] != prev + 1:
                    if cur is not None:
                        out[s][2] += 1
                        out[s][0] += cur[0]
                        out[s][1] += cur[1]
                    cur = [1 if (not c['died'] and c['nd'] < c['d']) else 0, 0]
                if not c['died'] and c['nd'] < c['d']:
                    cur[1] = 1
                prev = c['r']
            if cur is not None:
                out[s][2] += 1
                out[s][0] += cur[0]
                out[s][1] += cur[1]
    return out


def main():
    G, bad = load()
    say('games loaded', len(G), 'errors', len(bad))
    d4 = lambda c: c['d'] == 4
    d3 = lambda c: c['d'] == 3
    for code in ('main', 'v31'):
        gs = [g for g in G if g['code'] == code and g['free']]
        say('')
        say('=====', code, 'free layouts, games', len(gs), 'battles', len(set(g['battle'] for g in gs)))
        asym = sum(1 for g in gs for c in g['cases'] if c['sym'] != c['d'])
        say(' cases where the path from the reference to her differs from the path from her to it:', asym)
        say(' pooled    :', line(cnt(gs)))
        say(' distance 4:', line(cnt(gs, d4)))
        say(' distance 3:', line(cnt(gs, d3)))
        say(' with a legal first step that does not come closer, pooled:', line(cnt(gs, lambda c: c['alt'] >= 1)))
        say('   the same, distance 4:', line(cnt(gs, lambda c: c['alt'] >= 1 and c['d'] == 4)))
        say('   the same, distance 3:', line(cnt(gs, lambda c: c['alt'] >= 1 and c['d'] == 3)))
        say(' a real choice (a legal first step that comes closer and one that does not), distance 4:', line(cnt(gs, lambda c: c['alt'] >= 1 and c['nl'] - c['alt'] >= 1 and c['d'] == 4)))
        say('   the same, distance 3:', line(cnt(gs, lambda c: c['alt'] >= 1 and c['nl'] - c['alt'] >= 1 and c['d'] == 3)))
        say(' no legal first step at all (nl = 0), distance 4: ours %d theirs %d' % (
            sum(1 for g in gs for c in g['cases'] if c['d'] == 4 and c['s'] == 0 and c['nl'] == 0), sum(1 for g in gs for c in g['cases'] if c['d'] == 4 and c['s'] == 1 and c['nl'] == 0)))
        say(' by rating band, pooled then distance 4')
        for b in BANDS:
            q = [g for g in gs if g['band'] == b]
            if q:
                say('   %-10s games %3d: %s' % (b, len(q), line(cnt(q))))
                say('   %-10s      d 4: %s' % (b, line(cnt(q, d4))))
        for label, flt, mn in (('pooled', None, 8), ('distance 4', d4, 8), ('distance 4', d4, 4)):
            hi = lo = eq = 0
            for g in gs:
                o = cnt([g], flt)
                if o[0][1] >= mn and o[1][1] >= mn:
                    a = o[0][0] / o[0][1]
                    b_ = o[1][0] / o[1][1]
                    if a > b_:
                        hi += 1
                    elif a < b_:
                        lo += 1
                    else:
                        eq += 1
            say(' games with %d or more cases a side, %s: ours higher %d, lower %d, equal %d, sign p %.3g' % (mn, label, hi, lo, eq, sign(min(hi, lo), hi + lo)))
        say(' resampling (2000), gap ours - theirs: 2.5 pct, 97.5 pct, share at or below zero')
        for label, flt in (('distance 4', d4), ('distance 3', d3), ('pooled', None), ('distance 4 with a non-closing legal step', lambda c: c['d'] == 4 and c['alt'] >= 1)):
            say('   %-40s games %s | battles %s | opponents %s | layouts %s' % (
                label, boot_gap([unit(g, flt) for g in gs]), boot_gap(by_cluster(gs, 'battle', lambda g: unit(g, flt))),
                boot_gap(by_cluster(gs, 'opp', lambda g: unit(g, flt))), boot_gap(by_cluster(gs, 'map_key', lambda g: unit(g, flt)))))
        for d in (4, 3):
            r = runs(gs, d)
            say(' runs of consecutive turns at distance %d: ours %d runs, closer on the first turn %s, closer on any turn %s | theirs %d runs, first %s, any %s' % (
                d, r[0][2], sh(r[0][0], r[0][2]), sh(r[0][1], r[0][2]), r[1][2], sh(r[1][0], r[1][2]), sh(r[1][1], r[1][2])))
            if r[0][2] and r[1][2]:
                say('     first turn of the run: Fisher p %.3g; any turn: p %.3g' % (
                    fisher(r[0][0], r[0][2] - r[0][0], r[1][0], r[1][2] - r[1][0]), fisher(r[0][1], r[0][2] - r[0][1], r[1][1], r[1][2] - r[1][1])))
        say(' per layout, distance 4')
        up = dn = 0
        for mk in sorted(set(g['map_key'] for g in gs)):
            q = [g for g in gs if g['map_key'] == mk]
            o = cnt(q, d4)
            say('   %-22s games %3d: %s' % (mk, len(q), line(o)))
            if o[0][1] >= 10 and o[1][1] >= 10:
                if o[0][0] / o[0][1] > o[1][0] / o[1][1]:
                    up += 1
                else:
                    dn += 1
        say('   layouts with 10 or more cases a side: ours higher on %d, not higher on %d' % (up, dn))
        say(' distance 4 without weakhold, Devil and Prisoners Dilemma #1:', line(cnt([g for g in gs if g['map_key'] not in ('weakhold #1', 'Devil #1', 'Prisoners Dilemma #1')], d4)))
        gl = []
        for mk in sorted(set(g['map_key'] for g in gs)):
            o = cnt([g for g in gs if g['map_key'] != mk], d4)
            if o[0][1] and o[1][1]:
                gl.append((o[0][0] / o[0][1] - o[1][0] / o[1][1], mk))
        gl.sort()
        say(' distance 4, one layout left out: gap from %+.3f (without %s) to %+.3f (without %s)' % (gl[0][0], gl[0][1], gl[-1][0], gl[-1][1]))
        go = []
        for op in sorted(set(g['opp'] for g in gs)):
            o = cnt([g for g in gs if g['opp'] != op], d4)
            if o[0][1] and o[1][1]:
                go.append((o[0][0] / o[0][1] - o[1][0] / o[1][1], op))
        go.sort()
        say(' distance 4, one opponent left out (%d): gap from %+.3f (without %s) to %+.3f (without %s)' % (len(go), go[0][0], go[0][1], go[-1][0], go[-1][1]))
        sup = sorted(gs, key=lambda g: -(cnt([g], d4)[0][0]))[:3]
        ids = set(g['game'] for g in sup)
        say(' distance 4 without the three games with most of our closer turns (%s):' % [cnt([g], d4)[0][:2] for g in sup], line(cnt([g for g in gs if g['game'] not in ids], d4)))
        say(' by evening, distance 4')
        for ev in sorted(set(g['evening'] for g in gs)):
            say('   %s: %s' % (ev, line(cnt([g for g in gs if g['evening'] == ev], d4))))
        say(' distance 4, turns in which she ate no pearl:', line(cnt(gs, lambda c: c['d'] == 4 and c['te'] == 0)))
        say(' distance 4, turns in which she ate a pearl :', line(cnt(gs, lambda c: c['d'] == 4 and c['te'] >= 1)))
        say(' distance 4, the reference is not a queen:', line(cnt(gs, lambda c: c['d'] == 4 and not c['rq'])))
        say(' distance 4, the reference is a queen    :', line(cnt(gs, lambda c: c['d'] == 4 and c['rq'])))
        for lo_, hi_ in ((1, 2), (3, 4), (5, 6)):
            say(' distance 4, reference length %d-%d: %s' % (lo_, hi_, line(cnt(gs, lambda c, lo_=lo_, hi_=hi_: c['d'] == 4 and lo_ <= c['rl'] <= hi_))))
        for lo_, hi_ in ((1, 3), (4, 6), (7, 999)):
            say(' distance 4, queen length %d-%d: %s' % (lo_, hi_, line(cnt(gs, lambda c, lo_=lo_, hi_=hi_: c['d'] == 4 and lo_ <= c['ql'] <= hi_))))
        for lo_, hi_ in ((0, 50), (51, 100), (101, 200)):
            say(' distance 4, rounds %d-%d: %s' % (lo_, hi_, line(cnt(gs, lambda c, lo_=lo_, hi_=hi_: c['d'] == 4 and lo_ <= c['r'] <= hi_))))
        for s, sn in ((0, 'ours'), (1, 'theirs')):
            cs = [c for g in gs for c in g['cases'] if c['s'] == s and c['d'] == 4 and not c['died']]
            if cs:
                say(' distance 4 %s: path after her turn %s; steps in the turn %s' % (
                    sn, sorted(Counter(min(c['nd'], 9) for c in cs).items()), sorted(Counter(c['st'] for c in cs).items())))
        say(' queen turns in rounds 0-200 (all, for scale): ours %d, theirs %d; distance-4 cases per 100 queen turns: ours %.2f, theirs %.2f' % (
            sum(g['reach'][0][0] for g in gs), sum(g['reach'][1][0] for g in gs),
            100 * sum(1 for g in gs for c in g['cases'] if c['s'] == 0 and c['d'] == 4) / max(1, sum(g['reach'][0][0] for g in gs)),
            100 * sum(1 for g in gs for c in g['cases'] if c['s'] == 1 and c['d'] == 4) / max(1, sum(g['reach'][1][0] for g in gs))))
    f = open(P + 'f28-numbers.txt', 'w')
    f.write('\n'.join(LINES) + '\n')
    f.close()


main()
