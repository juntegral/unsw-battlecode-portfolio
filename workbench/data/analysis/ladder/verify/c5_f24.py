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


# ---------------------------------------------------------------- F24 (wording of the 06:00 queue)
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'


def rams(q, s):
    return [(g, r) for g in q for r in g['rams'] if r['s'] == s and r['cross']]


def paid(r):
    return r['d1'] > (r['L'] + 3) // 4


def paid_direct(r):
    return r['st'] > (r['ml0'] + 3) // 4


def main():
    G, bad = load()
    say('games loaded', len(G), 'errors', len(bad))
    for code in ('v31', 'main'):
        gs = [g for g in G if g['code'] == code and g['free']]
        say('')
        say('=====', code, 'free layouts, games', len(gs))
        say(' (a) reach, raw rounds 0-200, queen turn starts')
        for b in BANDS:
            q = [g for g in gs if g['band'] == b]
            if not q:
                continue
            t = sum(g['reach'][0][0] for g in q)
            fu = sum(g['reach'][0][1] for g in q)
            fr = sum(g['reach'][0][2] for g in q)
            t2 = sum(g['reach'][1][0] for g in q)
            fu2 = sum(g['reach'][1][1] for g in q)
            fr2 = sum(g['reach'][1][2] for g in q)
            anyx = sum(1 for g in q if g['reach'][0][1] > 0)
            say('   %-10s games %3d battles %2d opponents %2d | our queen exposed (full reach) %s, within free steps %s, games with any exposed turn %s | their queen to our heads: %s, free %s' % (
                b, len(q), len(set(g['battle'] for g in q)), len(set(g['opp'] for g in q)), sh(fu, t), sh(fr, t), sh(anyx, len(q)), sh(fu2, t2), sh(fr2, t2)))
        hi = [g for g in gs if g['band'] == '2100+']
        lo = [g for g in gs if g['band'] == '1700-1899']
        mid = [g for g in gs if g['band'] == '1900-2099']
        f = lambda g: (g['reach'][0][1], g['reach'][0][0])
        if hi and lo:
            say('   exposed share 2100+ minus 1700-1899, battles resampled inside each band:', boot_two(by_cluster(hi, 'battle', f), by_cluster(lo, 'battle', f)))
            say('   exposed share 2100+ minus 1900-2099, battles resampled inside each band:', boot_two(by_cluster(hi, 'battle', f), by_cluster(mid, 'battle', f)))
            say('   games as units:', boot_two([f(g) for g in hi], [f(g) for g in lo]))
        say('   2100+ by opponent: games, exposed turns of queen turns')
        for op in sorted(set(g['opp'] for g in hi)):
            q = [g for g in hi if g['opp'] == op]
            say('     %-34s %d  %s' % (op, len(q), sh(sum(g['reach'][0][1] for g in q), sum(g['reach'][0][0] for g in q))))
        say('   exposed share by layout, 2100+ against 1700-1899 (layouts with 2 or more games in each)')
        up = dn = 0
        for mk in sorted(set(g['map_key'] for g in hi)):
            a = [g for g in hi if g['map_key'] == mk]
            c = [g for g in lo if g['map_key'] == mk]
            if len(a) >= 2 and len(c) >= 2:
                ra = sum(g['reach'][0][1] for g in a) / max(1, sum(g['reach'][0][0] for g in a))
                rc = sum(g['reach'][0][1] for g in c) / max(1, sum(g['reach'][0][0] for g in c))
                if ra > rc:
                    up += 1
                else:
                    dn += 1
        say('     higher at 2100+ on %d layouts, not higher on %d' % (up, dn))
        say(' (b) rams on our queen (she is the stationary victim, rammer of the other team)')
        for b in BANDS:
            q = [g for g in gs if g['band'] == b]
            if not q:
                continue
            rr = rams(q, 0)
            ok = [(g, r) for g, r in rr if 'L' in r]
            by200 = sum(1 for g, r in rr if r['r'] <= 200)
            pd = sum(1 for g, r in ok if paid(r))
            pdd = sum(1 for g, r in rr if paid_direct(r))
            shrt = sum(1 for g, r in ok if r['d1'] < r['d0'])
            say('   %-10s games %3d rams %3d (by r200 %d, per game %.2f); rammer alive at her last turn start %d; paid %s Wilson %s; paid by the steps of the ramming turn itself %s; her last step shortened the path %s' % (
                b, len(q), len(rr), by200, by200 / len(q), len(ok), sh(pd, len(ok)), wilson(pd, len(ok)), sh(pdd, len(rr)), sh(shrt, len(ok))))
            if ok:
                say('              mean d0 %.2f, mean d1 %.2f, mean rammer length %.2f; d1 values %s; rammer lengths %s' % (
                    sum(r['d0'] for g, r in ok) / len(ok), sum(r['d1'] for g, r in ok) / len(ok), sum(r['L'] for g, r in ok) / len(ok),
                    sorted(Counter(r['d1'] for g, r in ok).items()), sorted(Counter(r['L'] for g, r in ok).items())))
        allr = [(g, r) for g, r in rams(gs, 0) if 'L' in r]
        say('   all bands: her last step shortened the path', sh(sum(1 for g, r in allr if r['d1'] < r['d0']), len(allr)),
            '| she had moved at all', sh(sum(1 for g, r in allr if r['moved']), len(allr)),
            '| excluded: rams by our own dragons', sum(1 for g in gs for r in g['rams'] if r['s'] == 0 and not r['cross']),
            ', rammer not alive at her last turn start', sum(1 for g, r in rams(gs, 0) if 'L' not in r))
        okh = [(g, r) for g, r in rams(hi, 0) if 'L' in r]
        okl = [(g, r) for g, r in rams(lo, 0) if 'L' in r]
        okm = [(g, r) for g, r in rams(mid, 0) if 'L' in r]
        if okh and okl:
            a = sum(1 for g, r in okh if paid(r))
            c = sum(1 for g, r in okl if paid(r))
            e = sum(1 for g, r in okm if paid(r))
            say('   chance (Fisher, rams as units): 2100+ against 1700-1899 p %.4g; against 1900-2099 p %.4g; against everything under 2100 p %.4g' % (
                fisher(a, len(okh) - a, c, len(okl) - c), fisher(a, len(okh) - a, e, len(okm) - e), fisher(a, len(okh) - a, c + e, len(okl) + len(okm) - c - e)))
            fp = lambda g: (sum(1 for r in g['rams'] if r['s'] == 0 and r['cross'] and 'L' in r and paid(r)), sum(1 for r in g['rams'] if r['s'] == 0 and r['cross'] and 'L' in r))
            say('   paid share 2100+ minus 1700-1899, battles resampled inside each band:', boot_two(by_cluster(hi, 'battle', fp), by_cluster(lo, 'battle', fp)))
            say('   paid share 2100+ minus 1900-2099, battles resampled inside each band:', boot_two(by_cluster(hi, 'battle', fp), by_cluster(mid, 'battle', fp)))
            say('   2100+ without three paid rams: %s' % sh(max(a - 3, 0), len(okh) - 3))
        say('   2100+ by opponent: games, rams, paid')
        loo = []
        for op in sorted(set(g['opp'] for g in hi)):
            q = [g for g in hi if g['opp'] == op]
            ok = [(g, r) for g, r in rams(q, 0) if 'L' in r]
            rest = [(g, r) for g, r in okh if g['opp'] != op]
            say('     %-34s %d  %s' % (op, len(q), sh(sum(1 for g, r in ok if paid(r)), len(ok))))
            if rest:
                loo.append(sum(1 for g, r in rest if paid(r)) / len(rest))
        if loo:
            say('     one opponent left out: paid share from %.3f to %.3f' % (min(loo), max(loo)))
        say('   paid share by rammer length at her last turn start (free steps 1 for lengths 1-4, 2 for 5-8, 3 for 9-12)')
        for lo_, hi_ in ((1, 2), (3, 4), (5, 8), (9, 99)):
            parts = []
            for b in BANDS:
                ok = [(g, r) for g, r in rams([g for g in gs if g['band'] == b], 0) if 'L' in r and lo_ <= r['L'] <= hi_]
                if ok:
                    parts.append('%s %s' % (b, sh(sum(1 for g, r in ok if paid(r)), len(ok))))
            say('     length %d-%d: %s' % (lo_, hi_, '; '.join(parts)))
        say('   paid against not paid: mean rammer length')
        okall = allr
        pl = [r['L'] for g, r in okall if paid(r)]
        nl = [r['L'] for g, r in okall if not paid(r)]
        if pl and nl:
            say('     paid %.2f (n %d), not paid %.2f (n %d)' % (sum(pl) / len(pl), len(pl), sum(nl) / len(nl), len(nl)))
        say('   split at battle 1270027 (the analyst shards stop there): paid share by band, up to it | after it')
        for b in BANDS:
            q = [g for g in gs if g['band'] == b]
            a = [(g, r) for g, r in rams(q, 0) if 'L' in r and int(g['battle']) <= 1270027]
            c = [(g, r) for g, r in rams(q, 0) if 'L' in r and int(g['battle']) > 1270027]
            if a or c:
                say('     %-10s %s | %s (games after: %d)' % (b, sh(sum(1 for g, r in a if paid(r)), len(a)), sh(sum(1 for g, r in c if paid(r)), len(c)),
                                                             sum(1 for g in q if int(g['battle']) > 1270027)))
        say(' mirror: our rams on their queen (their queen is the stationary victim)')
        for b in BANDS:
            q = [g for g in gs if g['band'] == b]
            if not q:
                continue
            rr = rams(q, 1)
            ok = [(g, r) for g, r in rr if 'L' in r]
            say('   %-10s rams %3d; paid %s; her last step shortened the path %s' % (b, len(rr), sh(sum(1 for g, r in ok if paid(r)), len(ok)), sh(sum(1 for g, r in ok if r['d1'] < r['d0']), len(ok))))
    f = open(P + 'f24-0627-numbers.txt', 'w')
    f.write('\n'.join(LINES) + '\n')
    f.close()


main()
