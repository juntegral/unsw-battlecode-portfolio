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
