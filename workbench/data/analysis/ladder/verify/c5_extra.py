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


# ---------------------------------------------------------------- extras for the 06:27 run
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'


def walk_units(gs, flt):
    out = []
    for g in gs:
        u = [0, 0, 0, 0]
        for b in g['births']:
            if not b[4] or not b[14]:
                continue
            if flt and not flt(b):
                continue
            if b[1] == 0:
                u[1] += 1
                if b[9] == 1:
                    u[0] += 1
            else:
                u[3] += 1
                if b[9] == 1:
                    u[2] += 1
        out.append(tuple(u))
    return out


def boot_list(units, n=2000, seed=1):
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
    return vals


def main():
    G, bad = load()
    say('== F26 extras: walked gap ours minus theirs on large layouts, games resampled 2000 times')
    for code in ('main', 'v31'):
        L = [g for g in G if g['code'] == code and g['large']]
        for label, flt in (('all in view', None), ('nearer distance 1', lambda b: b[2] == 1), ('nearer distance 2 or more', lambda b: b[2] >= 2),
                           ('no kelp in the way', lambda b: b[18] == b[2]), ('one head a side', lambda b: b[5] == 1 and b[6] == 1),
                           ('nearer length 2 or 3', lambda b: b[7] <= 3), ('nearer length 4 to 6', lambda b: 4 <= b[7] <= 6)):
            us = walk_units(L, flt)
            v = boot_list(us)
            t4 = [sum(u[i] for u in us) for i in range(4)]
            say('  %-5s %-26s gap %+.4f (ours %d of %d, theirs %d of %d); 2.5 pct %+.4f, 97.5 pct %+.4f; resamples below 0.04: %.3f; at or below 0: %.3f' % (
                code, label, t4[0] / t4[1] - t4[2] / t4[3], t4[0], t4[1], t4[2], t4[3], v[int(0.025 * len(v))], v[int(0.975 * len(v)) - 1],
                sum(1 for x in v if x < 0.04) / len(v), sum(1 for x in v if x <= 0) / len(v)))
        n30 = []
        for g in L:
            u = walk_units([g], None)[0]
            if u[1] >= 30 and u[3] >= 30:
                n30.append((u[0] / u[1] - u[2] / u[3], u[1], u[3], g['game']))
        n30.sort(key=lambda t: abs(t[0]))
        say('  %-5s games with 30 or more a side: %d; with exactly 30 on a side: %s; the three narrowest gaps: %s' % (
            code, len(n30), [t[3] for t in n30 if t[1] == 30 or t[2] == 30], [(round(t[0], 4), t[1], t[2], t[3]) for t in n30[:3]]))
    say('')
    say('== F24 extras, free layouts')
    for code in ('v31', 'main'):
        gs = [g for g in G if g['code'] == code and g['free']]
        for b in BANDS:
            q = [g for g in gs if g['band'] == b]
            if not q:
                continue
            rr = [r for g in q for r in g['rams'] if r['s'] == 0 and r['cross'] and 'L' in r]
            inreach0 = sum(1 for r in rr if r['d0'] <= min(12, (r['L'] + 3) // 4 + r['L'] - 2))
            inreach1 = sum(1 for r in rr if r['d1'] <= min(12, (r['L'] + 3) // 4 + r['L'] - 2))
            by200 = sum(1 for g in q for r in g['rams'] if r['s'] == 0 and r['cross'] and r['r'] <= 200)
            ex = sum(g['reach'][0][1] for g in q)
            say('  %-5s %-10s rams %d: rammer within its full reach of her at her last turn start %s; of her head at the ram %s; rams by r200 %d against %d exposed turns (%.2f per exposed turn); length 2 rammers %s' % (
                code, b, len(rr), sh(inreach0, len(rr)), sh(inreach1, len(rr)), by200, ex, by200 / ex if ex else 0, sh(sum(1 for r in rr if r['L'] <= 2), len(rr))))
        hi = [r for g in gs if g['band'] == '2100+' for r in g['rams'] if r['s'] == 0 and r['cross'] and 'L' in r]
        lo = [r for g in gs if g['band'] != '2100+' for r in g['rams'] if r['s'] == 0 and r['cross'] and 'L' in r]
        k1 = sum(1 for r in hi if 3 <= r['L'] <= 4 and r['d1'] > 1)
        n1 = sum(1 for r in hi if 3 <= r['L'] <= 4)
        k2 = sum(1 for r in lo if 3 <= r['L'] <= 4 and r['d1'] > 1)
        n2 = sum(1 for r in lo if 3 <= r['L'] <= 4)
        say('  %-5s rammer length 3-4 only: 2100+ paid %s, under 2100 %s, Fisher p %.4g' % (code, sh(k1, n1), sh(k2, n2), fisher(k1, n1 - k1, k2, n2 - k2)))
        k1 = sum(1 for r in hi if r['L'] >= 3)
        k2 = sum(1 for r in lo if r['L'] >= 3)
        say('  %-5s rammers of length 3 or more: 2100+ %s, under 2100 %s, Fisher p %.4g' % (code, sh(k1, len(hi)), sh(k2, len(lo)), fisher(k1, len(hi) - k1, k2, len(lo) - k2)))
        k1 = sum(1 for r in hi if r['d0'] >= 3)
        k2 = sum(1 for r in lo if r['d0'] >= 3)
        say('  %-5s rammer 3 or more path steps away before her last step: 2100+ %s, under 2100 %s, Fisher p %.4g' % (code, sh(k1, len(hi)), sh(k2, len(lo)), fisher(k1, len(hi) - k1, k2, len(lo) - k2)))
    say('')
    say('== comparison with rows.jsonl (read only now, after the counts)')
    rows = {}
    for line in Path('data/analysis/ladder/rows.jsonl').read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            rows[r['game']] = r
    mine = {g['game']: g for g in G}
    say('  games: mine %d, rows %d, in both %d' % (len(mine), len(rows), len(set(mine).intersection(rows))))
    dc = dk = dw = dt = nt = dl = 0
    for gid, g in mine.items():
        r = rows.get(gid)
        if not r:
            continue
        rc = r['our_code'] if r['our_code'] in ('main', 'v31') else 'other'
        if rc != g['code']:
            dc += 1
        if r['map_key'] != g['map_key']:
            dk += 1
        if bool(r['win']) != bool(g['win']):
            dw += 1
        if g['code'] == 'other':
            continue
        if r['last_round'] != g['last_round']:
            dl += 1
        for m in ('100', '200', '300'):
            cv = r['curves'].get(m)
            sv = g['snap'].get(m)
            if (cv is None) != (sv is None):
                dt += 1
                continue
            if cv is None:
                continue
            nt += 1
            if cv['us']['total'] != sv[0][1] or cv['them']['total'] != sv[1][1] or cv['us']['alive'] != sv[0][0] or cv['them']['alive'] != sv[1][0]:
                dt += 1
    say('  differences: code label %d, map key %d, win %d, last round %d, totals or alive counts at r100/r200/r300 %d of %d compared' % (dc, dk, dw, dl, dt, nt))
    maps = json.loads(Path('data/analysis/ladder/maps.json').read_text())
    do = 0
    for g in G:
        mm = maps.get(g['map_key'])
        if not mm or mm['open_tiles'] != g['open_tiles'] or bool(mm['queen_spawn_dead_end']) == g['free']:
            do += 1
    say('  maps.json: games whose open tiles or dead-end flag differ from my layout reading: %d' % do)
    an = Counter()
    for g in G:
        if g['code'] == 'other':
            continue
        for k, v in (g.get('anomalies') or {}).items():
            an[k] += v
        if not g['final_ok']:
            an['final state differs from the result block'] += 1
        if g['drop_mismatch']:
            an['drop count mismatch'] += 1
        if g['bad_portals']:
            an['bad portal pairs'] += 1
    say('  rebuild anomalies over the 665 games:', dict(an))
    f = open(P + 'extras5.txt', 'w')
    f.write('\n'.join(LINES) + '\n')
    f.close()


main()
