#!/usr/bin/env python3
"""Verifier claims 8 (run of 2026-10-07 08:23 KST), F35: lone queens. Reads the x8 shards (own extraction from the raw
replays) and writes f35-numbers.txt. rows.jsonl is read only in the last section, to compare."""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timedelta
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
LINES = []
CUT = datetime.fromisoformat('2026-10-06T14:48:15+00:00')
REASON = ('wall', 'own body', 'other body', 'head-on', 'no valid action')


def say(*a):
    s = ' '.join(str(x) for x in a)
    LINES.append(s)
    print(s)


def window(r):
    return 0 if r <= 100 else 1 if r <= 200 else 2 if r <= 300 else 3


WN = ('r0-100', 'r101-200', 'r201-300', 'r301-499')


def load():
    games = []
    for k in range(6):
        for line in (V / ('x8-%d.jsonl' % k)).read_text().splitlines():
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
        g['free'] = g['map'] not in ('Schooltime', 'Slithery Fight')
        g['evening'] = (datetime.fromisoformat(g['at_kst']) - timedelta(hours=6)).strftime('%m-%d') if g.get('at_kst') else '?'
        g['opp'] = '%s (%s)' % (g.get('opponent'), g.get('opponentId'))
        g['big'] = g['W'] * g['H'] > 1200
        g['full'] = g['last_round'] == 499
        g['d'] = [q['round'] if q else None for q in g['qdeath']]
        t = g['completedAt']
        g['t'] = datetime.fromisoformat(t[:-1] + '+00:00') if t.endswith('Z') else datetime.fromisoformat(t)
    return order, bad


def fisher(a, b, c, d):
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


def sh(k, n):
    return '%d of %d (%s)' % (k, n, ('%.3f' % (k / n)) if n else '-')


def ratio(ku, nu, kt, nt):
    if not nu or not nt or not kt:
        return float('nan')
    return (ku / nu) / (kt / nt)


def boot_ratio(units, n=2000, seed=1):
    """units: one (a, b, c, d) per cluster; statistic (sum a / sum b) / (sum c / sum d) over resampled clusters.
    Returns 2.5 and 97.5 percentiles, the share of resamples at or above 0.7, at or above 1, and at or below 1."""
    rng = random.Random(seed)
    m = len(units)
    vals = []
    for _ in range(n):
        a = b = c = d = 0
        for _k in range(m):
            u = units[rng.randrange(m)]
            a += u[0]
            b += u[1]
            c += u[2]
            d += u[3]
        if b and d and c:
            vals.append((a / b) / (c / d))
    vals.sort()
    if not vals:
        return None
    L = len(vals)
    return (round(vals[int(0.025 * L)], 3), round(vals[int(0.975 * L) - 1], 3),
            round(sum(1 for v in vals if v >= 0.7) / L, 4), round(sum(1 for v in vals if v >= 1) / L, 4),
            round(sum(1 for v in vals if v <= 1) / L, 4))


def by_cluster(gs, key, f):
    acc = {}
    for g in gs:
        t = f(g)
        cur = acc.get(g[key])
        acc[g[key]] = t if cur is None else tuple(x + y for x, y in zip(cur, t))
    return acc


def lone(g, s):
    d = g['d']
    return d[1 - s] is not None and (d[s] is None or d[1 - s] < d[s])


def unit(g):
    lu = lone(g, 0)
    lt = lone(g, 1)
    return (1 if lu and g['d'][0] is None else 0, 1 if lu else 0, 1 if lt and g['d'][1] is None else 0, 1 if lt else 0)


def q4(gs):
    a = b = c = d = 0
    for g in gs:
        u = unit(g)
        a += u[0]
        b += u[1]
        c += u[2]
        d += u[3]
    return a, b, c, d


def line(label, gs):
    ku, nu, kt, nt = q4(gs)
    say('  %-46s games %4d  ours %-18s theirs %-18s ratio %.2f  Fisher p %.4f' % (
        label, len(gs), sh(ku, nu), sh(kt, nt), ratio(ku, nu, kt, nt), fisher(ku, nu - ku, kt, nt - kt)))
    return ku, nu, kt, nt


def hz(gs, s):
    turns = sum(g['lone_turns'][s] for g in gs)
    deaths = sum(1 for g in gs if lone(g, s) and g['d'][s] is not None)
    deaths_ev = sum(1 for g in gs if g['qdeath'][s] and g['qdeath'][s]['other_queen_dead'])
    return deaths, deaths_ev, turns


def hunit(g):
    return (1 if lone(g, 0) and g['d'][0] is not None else 0, g['lone_turns'][0],
            1 if lone(g, 1) and g['d'][1] is not None else 0, g['lone_turns'][1])


def hline(label, gs):
    du, eu, tu = hz(gs, 0)
    dt, et, tt = hz(gs, 1)
    ru = 1000 * du / tu if tu else float('nan')
    rt = 1000 * dt / tt if tt else float('nan')
    rr = ru / rt if rt else float('nan')
    se = math.sqrt(1 / du + 1 / dt) if du and dt else float('nan')
    say('  %-40s games %4d  ours %.2f (%d deaths, %d turns)  theirs %.2f (%d, %d)  rate ratio %.2f (log-normal 95%% %.2f to %.2f)  [event-order deaths %d / %d]' % (
        label, len(gs), ru, du, tu, rt, dt, tt, rr, rr * math.exp(-1.96 * se), rr * math.exp(1.96 * se), eu, et))
    return du, tu, dt, tt


def main():
    order, bad = load()
    say('F35 numbers, verifier run 2026-10-07 08:23 KST. Source: x8 shards (own rebuild of all raw replays).')
    say('games read %d, unreadable %d, final state differs from the result block %d, tile ownership off %d, anomalies %s' % (
        len(order), len(bad), sum(1 for g in order if not g['final_ok']), sum(1 for g in order if not g['own_ok']),
        dict(sum((Counter(g['anomalies']) for g in order), Counter()))))
    say('queen alive flag agrees with no death record: %d of %d sides' % (
        sum(1 for g in order for s in (0, 1) if g['q_alive_end'][s] == (g['d'][s] is None)), 2 * len(order)))
    say('by code:', dict(Counter(g['code'] for g in order)))
    mv = [g for g in order if g['code'] in ('main', 'v31')]
    free = [g for g in mv if g['free']]
    full = [g for g in free if g['full']]
    say('main and v31 games %d; on free layouts %d; of those full (last raw round 499) %d; up to battle 1276407: %d of the main and v31 games, %d on free layouts' % (
        len(mv), len(free), len(full), sum(1 for g in mv if int(g['battle']) <= 1276407),
        sum(1 for g in free if int(g['battle']) <= 1276407)))
    say('full games whose end reason is not round limit: %d; games ended by elimination with last round 499: %d' % (
        sum(1 for g in full if g['end_reason'] != 1), sum(1 for g in free if g['end_reason'] == 0 and g['last_round'] == 499)))
    say('both queens died in the same raw round (neither is lone): %d of the %d full free games' % (
        sum(1 for g in full if g['d'][0] is not None and g['d'][0] == g['d'][1]), len(full)))
    C = {c: [g for g in full if g['code'] == c] for c in ('main', 'v31')}
    A = {c: [g for g in free if g['code'] == c] for c in ('main', 'v31')}

    say('')
    say('== 1. First part: lone queen alive at the end, full games on free layouts ==')
    for c in ('main', 'v31'):
        line(c, C[c])
    line('main and v31 pooled', full)
    for b in ('<1700', '1700-1899', '1900-2099', '2100+'):
        line('main ' + b, [g for g in C['main'] if g['band'] == b])
    for b in ('<1700', '1700-1899', '1900-2099', '2100+'):
        line('v31 ' + b, [g for g in C['v31'] if g['band'] == b])
    line('layouts above 1200 cells, both codes', [g for g in full if g['big']])
    line('other layouts, both codes', [g for g in full if not g['big']])
    for c in ('main', 'v31'):
        line(c + ' layouts above 1200 cells', [g for g in C[c] if g['big']])
        line(c + ' other layouts', [g for g in C[c] if not g['big']])
    line('main before 2026-10-06T14:48:15Z', [g for g in C['main'] if g['t'] < CUT])
    line('main from 2026-10-06T14:48:15Z', [g for g in C['main'] if g['t'] >= CUT])
    for c in ('main', 'v31'):
        gs = C[c]
        e = Counter()
        w = Counter()
        for g in gs:
            a, b = g['d'][0] is None, g['d'][1] is None
            k = 'both alive' if a and b else 'only ours' if a else 'only theirs' if b else 'both dead'
            e[k] += 1
            w[k] += 1 if g['win'] else 0
        say('  endings %s full: %s' % (c, ', '.join('%s %d (%d won)' % (k, e[k], w[k]) for k in ('both dead', 'only theirs', 'only ours', 'both alive'))))
    for c in ('main', 'v31'):
        out = []
        for s in (0, 1):
            n = k = 0
            for g in C[c]:
                if lone(g, s) and g['d'][1 - s] + 100 <= 499:
                    n += 1
                    if g['d'][s] is None or g['d'][s] > g['d'][1 - s] + 100:
                        k += 1
            out.append(sh(k, n))
        say('  alive 100 rounds after the other queen died, %s: ours %s, theirs %s' % (c, out[0], out[1]))
    for c in ('main', 'v31'):
        say('  queen dead by raw round 200, %s full games: ours %d, theirs %d of %d' % (
            c, sum(1 for g in C[c] if g['d'][0] is not None and g['d'][0] <= 200),
            sum(1 for g in C[c] if g['d'][1] is not None and g['d'][1] <= 200), len(C[c])))

    say('')
    say('== 2. Chance (first part) ==')
    for c in ('main', 'v31', 'both'):
        gs = full if c == 'both' else C[c]
        ku, nu, kt, nt = q4(gs)
        say('  %s: ours %s Wilson %s; theirs %s Wilson %s; ratio %.2f' % (c, sh(ku, nu), wilson(ku, nu), sh(kt, nt), wilson(kt, nt), ratio(ku, nu, kt, nt)))
        say('     bootstrap over games (2.5%%, 97.5%%, share of resamples with ratio at or above 0.7, at or above 1): %s' % (boot_ratio([unit(g) for g in gs])[:4],))
        for key in ('battle', 'opp', 'map_key', 'evening'):
            say('     bootstrap over %s clusters (%d): %s' % (key, len(set(g[key] for g in gs)), boot_ratio(list(by_cluster(gs, key, unit).values()))[:4]))

    say('')
    say('== 3. Who carries their surviving lone queens (full free games) ==')
    for c in ('main', 'v31'):
        for key in ('opp', 'map_key', 'evening'):
            acc = by_cluster(C[c], key, unit)
            top = sorted(acc.items(), key=lambda kv: (-kv[1][2], kv[0]))
            say('  %s by %s (ours survived of lone, theirs survived of lone):' % (c, key))
            for name, u in top[:12]:
                say('      %-28s ours %d of %d   theirs %d of %d' % (name, u[0], u[1], u[2], u[3]))
            ku, nu, kt, nt = q4(C[c])
            two = [name for name, u in top[:2]]
            rest = [g for g in C[c] if g[key] not in two]
            a, b, cc, d = q4(rest)
            say('      without the two with most surviving lone queens of theirs (%s): ours %s theirs %s ratio %.2f' % (', '.join(two), sh(a, b), sh(cc, d), ratio(a, b, cc, d)))
            rs = []
            for name in acc:
                a, b, cc, d = q4([g for g in C[c] if g[key] != name])
                rs.append((ratio(a, b, cc, d), name))
            rs = [r for r in rs if r[0] == r[0]]
            say('      leave one %s out: ratio from %.2f to %.2f (highest when %s is left out)' % (key, min(rs)[0], max(rs)[0], max(rs)[1]))
            shares = [(u[0] / u[1] if u[1] else None, u[2] / u[3] if u[3] else None) for u in acc.values()]
            both = [x for x in shares if x[0] is not None and x[1] is not None]
            say('      %s clusters with lone queens on both sides: %d; ours share lower in %d, equal in %d, higher in %d' % (
                key, len(both), sum(1 for x in both if x[0] < x[1]), sum(1 for x in both if x[0] == x[1]), sum(1 for x in both if x[0] > x[1])))

    say('')
    say('== 4. Three most supporting games removed (full free games) ==')
    for c in ('main', 'v31'):
        ku, nu, kt, nt = q4(C[c])
        best = None
        for a in range(4):
            b = 3 - a
            r = ratio(ku, nu - a, kt - b, nt - b)
            if best is None or r > best[0]:
                best = (r, a, b)
        say('  %s: ratio %.2f; worst case after removing 3 games (%d where our lone queen died, %d where their lone queen lived): %.2f' % (
            c, ratio(ku, nu, kt, nt), best[1], best[2], best[0]))

    say('')
    say('== 5. Does restricting to full games bias the first part? ==')
    for c in ('main', 'v31'):
        gs = A[c]
        el = [g for g in gs if not g['full']]
        say('  %s free games %d: full %d, ended early %d (we won %d, they won %d, drawn %d)' % (
            c, len(gs), len(C[c]), len(el), sum(1 for g in el if g['win']), sum(1 for g in el if not g['win'] and not g['drawn']), sum(1 for g in el if g['drawn'])))
        line(c + ' full games', C[c])
        line(c + ' games ended early', el)
        line(c + ' early, we won', [g for g in el if g['win']])
        line(c + ' early, they won', [g for g in el if not g['win']])
        line(c + ' all games', gs)
    line('both codes all games', free)
    for c in ('main', 'v31'):
        el = [g for g in A[c] if not g['full']]
        e = Counter()
        for g in el:
            a, b = g['d'][0] is None, g['d'][1] is None
            e[('we won' if g['win'] else 'they won') + ', ' + ('both alive' if a and b else 'only ours alive' if a else 'only theirs alive' if b else 'both dead')] += 1
        say('  %s early endings by queens at the end: %s' % (c, dict(sorted(e.items()))))

    say('')
    say('== 6. Games level in total length at raw round 100 (smaller total at least 0.8 of the larger) ==')
    def level(g, lo=0.8):
        if g['last_round'] < 100:
            return False
        a, b = g['total'][0][100], g['total'][1][100]
        return min(a, b) >= lo * max(a, b) and max(a, b) > 0
    for c in ('main', 'v31'):
        lv = [g for g in C[c] if level(g)]
        line(c + ' full, level at r100', lv)
        line(c + ' full, we are ahead by more', [g for g in C[c] if not level(g) and g['total'][0][100] > g['total'][1][100]])
        line(c + ' full, they are ahead by more', [g for g in C[c] if not level(g) and g['total'][0][100] < g['total'][1][100]])
        line(c + ' all games, level at r100', [g for g in A[c] if level(g)])
    line('both codes full, level at r100', [g for g in full if level(g)])
    line('both codes full, level within 10 percent', [g for g in full if level(g, 0.9)])
    say('  bootstrap over games, both codes full level: %s' % (boot_ratio([unit(g) for g in full if level(g)])[:4],))
    say('  bootstrap over opponents, both codes full level: %s' % (boot_ratio(list(by_cluster([g for g in full if level(g)], 'opp', unit).values()))[:4],))

    say('')
    say('== 7. Plainer explanations: when the lone spell starts and who is ahead then (full free games, both codes and apart) ==')
    for label, gs in (('main', C['main']), ('v31', C['v31']), ('both', full)):
        for w in range(4):
            a = b = cc = d = 0
            for g in gs:
                for s in (0, 1):
                    if lone(g, s) and window(g['d'][1 - s]) == w:
                        if s == 0:
                            b += 1
                            a += 1 if g['d'][0] is None else 0
                        else:
                            d += 1
                            cc += 1 if g['d'][1] is None else 0
            say('  %-5s other queen died in %-9s ours %-18s theirs %-18s ratio %.2f' % (label, WN[w], sh(a, b), sh(cc, d), ratio(a, b, cc, d)))
    for label, gs in (('main', C['main']), ('v31', C['v31']), ('both', full)):
        for ahead in (True, False):
            a = b = cc = d = 0
            for g in gs:
                for s in (0, 1):
                    if lone(g, s):
                        L = g['d'][1 - s]
                        if (g['total'][s][L] >= g['total'][1 - s][L]) != ahead:
                            continue
                        if s == 0:
                            b += 1
                            a += 1 if g['d'][0] is None else 0
                        else:
                            d += 1
                            cc += 1 if g['d'][1] is None else 0
            say('  %-5s lone side %-34s ours %-18s theirs %-18s ratio %.2f' % (label, 'ahead or level in total length then' if ahead else 'behind in total length then', sh(a, b), sh(cc, d), ratio(a, b, cc, d)))
    for label, gs in (('main', C['main']), ('v31', C['v31'])):
        med = []
        for s in (0, 1):
            xs = sorted(g['d'][1 - s] for g in gs if lone(g, s))
            ys = sorted(g['alive'][s][g['d'][1 - s]] for g in gs if lone(g, s))
            zs = sorted(g['alive'][1 - s][g['d'][1 - s]] for g in gs if lone(g, s))
            ls = sorted(g['qlen'][s][g['d'][1 - s]] for g in gs if lone(g, s))
            med.append('median start round %s, own dragons then %s, enemy dragons then %s, her length then %s' % (
                xs[len(xs) // 2] if xs else '-', ys[len(ys) // 2] if ys else '-', zs[len(zs) // 2] if zs else '-', ls[len(ls) // 2] if ls else '-'))
        say('  %s lone queens of ours: %s' % (label, med[0]))
        say('  %s lone queens of theirs: %s' % (label, med[1]))

    say('')
    say('== 8. Second part: deaths per 1,000 lone turns ==')
    say('  lone turn = a turn start of a queen with the other queen already gone from the board; deaths = lone queens (other died in a strictly earlier round) that died.')
    for c in ('main', 'v31'):
        hline(c + ' all free games', A[c])
        hline(c + ' up to battle 1276407', [g for g in A[c] if int(g['battle']) <= 1276407])
        hline(c + ' full games', C[c])
        hline(c + ' games ended early', [g for g in A[c] if not g['full']])
        for b in ('1700-1899', '1900-2099'):
            hline(c + ' ' + b, [g for g in A[c] if g['band'] == b])
        hline(c + ' big layouts', [g for g in A[c] if g['big']])
        hline(c + ' other layouts', [g for g in A[c] if not g['big']])
        hline(c + ' level at r100', [g for g in A[c] if level(g)])
        gs = A[c]
        say('     bootstrap of the rate ratio over games (2.5%%, 97.5%%, share at or below 1): %s' % ([boot_ratio([hunit(g) for g in gs])[i] for i in (0, 1, 4)],))
        for key in ('opp', 'map_key', 'evening'):
            acc = by_cluster(gs, key, hunit)
            bt = boot_ratio(list(acc.values()))
            rs = []
            for name in acc:
                a = b = cc = d = 0
                for n2, u in acc.items():
                    if n2 != name:
                        a += u[0]
                        b += u[1]
                        cc += u[2]
                        d += u[3]
                if b and d and cc:
                    rs.append(((a / b) / (cc / d), name))
            say('     %s clusters (%d): bootstrap %s; leave one out: rate ratio from %.2f (without %s) to %.2f (without %s)' % (
                key, len(acc), [bt[i] for i in (0, 1, 4)], min(rs)[0], min(rs)[1], max(rs)[0], max(rs)[1]))
        for w in range(4):
            tu = sum(g['lone_by'][0][w] for g in gs)
            tt = sum(g['lone_by'][1][w] for g in gs)
            du = sum(1 for g in gs if lone(g, 0) and g['d'][0] is not None and window(g['d'][0]) == w)
            dt = sum(1 for g in gs if lone(g, 1) and g['d'][1] is not None and window(g['d'][1]) == w)
            say('     %s %-9s ours %.2f (%d deaths, %d turns)  theirs %.2f (%d, %d)' % (
                c, WN[w], 1000 * du / tu if tu else float('nan'), du, tu, 1000 * dt / tt if tt else float('nan'), dt, tt))
        for s in (0, 1):
            rc = Counter()
            for g in gs:
                if lone(g, s) and g['d'][s] is not None:
                    q = g['qdeath'][s]
                    if q['reason'] == 3:
                        rc['head-on, she moved' if q['actor'] else 'head-on, rammed by ' + ('an enemy' if q.get('killer_side') != s else 'a dragon of her team')] += 1
                    elif q['reason'] in (0, 1, 2, 4):
                        rc[REASON[q['reason']] + (' with no free tile' if q.get('start_legal') == 0 else ' with a free tile')] += 1
            say('     %s how lone queens of %s died: %s' % (c, 'ours' if s == 0 else 'theirs', dict(sorted(rc.items(), key=lambda kv: -kv[1]))))
    hline('both codes all free games', free)

    say('')
    say('== 9. Compare with rows.jsonl (read only here) ==')
    rows = {}
    for ln in Path('data/analysis/ladder/rows.jsonl').read_text().splitlines():
        if ln.strip():
            r = json.loads(ln)
            rows[r['game']] = r
    mine = {g['game']: g for g in order}
    CAUSE = {'wall': 0, 'own body': 1, 'other dragon body': 2, 'head-on': 3, 'other': 4}
    diff = Counter()
    for gid, r in rows.items():
        g = mine.get(gid)
        if g is None:
            diff['row without a game of mine'] += 1
            continue
        if r['last_round'] != g['last_round']:
            diff['last_round'] += 1
        if r['map_key'] != g['map_key']:
            diff['map_key'] += 1
        rc = r['our_code'] if r['our_code'] in ('main', 'v31') else 'other'
        if rc != g['code']:
            diff['code'] += 1
        for s, name in ((0, 'us'), (1, 'them')):
            q = r['queen'][name]
            if q['death_round'] != g['d'][s]:
                diff['queen death round'] += 1
            if q['alive_end'] != g['q_alive_end'][s]:
                diff['queen alive at end'] += 1
            if g['qdeath'][s] and CAUSE.get(q['death_cause']) != g['qdeath'][s]['reason']:
                diff['queen death cause'] += 1
    say('  rows %d, my games %d, games of mine without a row %d; fields that differ: %s' % (len(rows), len(mine), sum(1 for k in mine if k not in rows), dict(diff) or 'none'))

    f = open(P + 'f35-numbers.txt', 'w')
    f.write('\n'.join(LINES) + '\n')
    f.close()


main()
