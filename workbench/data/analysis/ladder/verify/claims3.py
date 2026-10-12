#!/usr/bin/env python3
"""Verifier counts for the 04:25 queue (F13 rams on a lone queen, F11 births near both sides, F20 heads near
busy tiles, F18 adjacent pearls passed up) from x3-*.jsonl written by extract3.py.
Usage: python3 claims3.py <F13|F11|F20|F18>"""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
from statistics import median
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
LINES = []
DEAD = ('Schooltime', 'Slithery Fight')


def out(*a):
    s = ' '.join(str(x) for x in a)
    print(s)
    LINES.append(s)


def load():
    games = []
    for k in range(6):
        for line in (V / ('x3-%d.jsonl' % k)).read_text().splitlines():
            games.append(json.loads(line))
    bad = [g for g in games if 'error' in g]
    games = [g for g in games if 'error' not in g]
    order = sorted(games, key=lambda g: (g['completedAt'], g['game']))
    seen = {}
    for g in order:
        lst = seen.setdefault(g['map'], [])
        if g['layout'] not in lst:
            lst.append(g['layout'])
        g['map_key'] = '%s #%d' % (g['map'], lst.index(g['layout']) + 1)
        e = g.get('opponentElo')
        g['band'] = 'unknown' if e is None else '<1700' if e < 1700 else '1700-1899' if e < 1900 else '1900-2099' if e < 2100 else '2100+'
        g['opp'] = '%s (%s)' % (g.get('opponent'), g.get('opponentId'))
        k = g.get('at_kst') or ''
        hour = int(k[11:13]) if k else 0
        g['evening'] = k[5:10] + ('a' if hour < 12 else 'b')
    return order, bad


def wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return mid - hw, mid + hw


def ws(k, n):
    if not n:
        return '0 of 0'
    lo, hi = wilson(k, n)
    return '%d of %d = %.3f (95%% %.2f to %.2f)' % (k, n, k / n, lo, hi)


def rt(k, n):
    return 'n/a (0)' if not n else '%.3f of %d' % (k / n, n)


def fisher(a, b, c, d):
    n = a + b + c + d
    r1 = a + b
    c1 = a + c

    def pr(x):
        return math.comb(r1, x) * math.comb(n - r1, c1 - x) / math.comb(n, c1)
    p0 = pr(a)
    return sum(pr(x) for x in range(max(0, c1 - (n - r1)), min(r1, c1) + 1) if pr(x) <= p0 * (1 + 1e-9))


def sign_p(a, b):
    n = a + b
    if not n:
        return 1.0
    k = min(a, b)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def boot(gs, fn, n=1000, seed=7):
    rng = random.Random(seed)
    m = len(gs)
    vals = []
    for _ in range(n):
        v = fn([gs[rng.randrange(m)] for _ in range(m)])
        if v is not None:
            vals.append(v)
    vals.sort()
    if not vals:
        return None, None
    return vals[int(0.025 * len(vals))], vals[min(len(vals) - 1, int(0.975 * len(vals)))]


def bs(gs, fn, n=1000, fmt='%.3f'):
    if not gs:
        return 'no games'
    v = fn(gs)
    lo, hi = boot(gs, fn, n)
    if v is None or lo is None:
        return 'n/a'
    return (fmt + ' (game bootstrap 95%% ' + fmt + ' to ' + fmt + ')') % (v, lo, hi)


def loo(gs, key, fn):
    vals = []
    for k in sorted(set(g[key] for g in gs)):
        v = fn([g for g in gs if g[key] != k])
        if v is not None:
            vals.append((v, k))
    if not vals:
        return 'n/a'
    return '%.3f (without %s) to %.3f (without %s), %d groups' % (min(vals)[0], min(vals)[1], max(vals)[0], max(vals)[1], len(vals))


# ---------------------------------------------------------------- F13
def f13(games):
    for code in ('main', 'v31'):
        allg = [g for g in games if g['code'] == code]
        gs = [g for g in allg if g['map'] not in DEAD]
        out('')
        out('=== %s: %d games, %d off Schooltime and Slithery Fight' % (code, len(allg), len(gs)))
        for vs, label in (('us', 'OUR queen rammed after theirs had died'), ('them', 'THEIR queen rammed by ours after ours had died')):
            rams = [(g, r) for g in gs for r in g['rams'] if r['cross'] and r['other_queen_dead'] and r['side'] == vs]
            board = [(g, r) for g, r in rams if r.get('born_later') is False]
            n = len(rams)
            nb = len(board)
            out('')
            out('--- %s, %s' % (code, label))
            out('  rams %d in %d games; no last-turn snapshot %d; rammer born later %d; with board %d' % (
                n, len(set(g['game'] for g, r in rams)), sum(1 for g, r in rams if r.get('no_snapshot')),
                sum(1 for g, r in rams if r.get('born_later')), nb))
            if not n:
                continue
            out('  friends within 5 under 2:', ws(sum(1 for g, r in rams if r['friends'] < 2), n))
            out('  friends within 5 equal 0:', ws(sum(1 for g, r in rams if r['friends'] == 0), n))
            out('  friends histogram', sorted(Counter(r['friends'] for g, r in rams).items()))
            out('  own other dragons alive at the ram: median', median(r['others_alive'] for g, r in rams),
                'min', min(r['others_alive'] for g, r in rams), '; with none alive', sum(1 for g, r in rams if r['others_alive'] == 0),
                '; with under 5 alive', sum(1 for g, r in rams if r['others_alive'] < 5))
            out('  enemy dragons alive at the ram: median', median(r['enemies_alive'] for g, r in rams))
            if nb:
                out('  escape beyond free steps (of with board):', ws(sum(1 for g, r in board if r['esc_free']), nb))
                out('  escape beyond actual ram distance:', ws(sum(1 for g, r in board if r['esc_actual']), nb))
                out('  rammer in the 7x7 square:', ws(sum(1 for g, r in board if r['in_square']), nb))
                out('  [extra] a legal step beyond the free reach of EVERY enemy head:', ws(sum(1 for g, r in board if r['esc_all']), nb))
                out('  [extra] no legal step at all:', sum(1 for g, r in board if r['n_legal'] == 0), '; legal steps histogram',
                    sorted(Counter(r['n_legal'] for g, r in board).items()))
                out('  [extra] she ended where the rammer needed more than its free steps (d_ram > free):',
                    ws(sum(1 for g, r in board if r['d_ram'] > r['free']), nb))
                out('  [extra] rammer made more steps in the ram turn than its free steps (paid length):',
                    ws(sum(1 for g, r in rams if r['mover_steps'] > (r['mover_len_turn_start'] + 3) // 4), n))
                out('  [extra] rammer steps in the ram turn histogram', sorted(Counter(r['mover_steps'] for g, r in rams).items()),
                    '; rammer length at its turn start histogram', sorted(Counter(r['mover_len_turn_start'] for g, r in rams).items()))
                a = [(g, r) for g, r in board if r['d_ram'] <= r['free']]
                b = [(g, r) for g, r in board if r['d_ram'] > r['free']]
                out('  [extra] ended inside free reach: %d, of which another step led beyond free: %d; ended beyond free reach and was rammed anyway: %d' % (
                    len(a), sum(1 for g, r in a if r['esc_free']), len(b)))
                out('  [extra] enemy heads with her start tile inside their free reach, histogram',
                    sorted(Counter(r['threats_at_q0'] for g, r in board).items()))
                out('  [extra] queen length histogram', sorted(Counter(r['qlen'] for g, r in rams).items()))
                out('  [extra] start-of-last-turn path distance rammer to queen histogram', sorted(Counter(min(r['d_q0'], 20) for g, r in board).items()))
            for bd in ('<1700', '1700-1899', '1900-2099', '2100+'):
                sub = [(g, r) for g, r in rams if g['band'] == bd]
                sb = [(g, r) for g, r in sub if r.get('born_later') is False]
                if sub:
                    out('  band %s: rams %d, alone (friends under 2) %d, friends 0 %d, with board %d, escape free %d, escape actual %d, in square %d, escape every enemy %d' % (
                        bd, len(sub), sum(1 for g, r in sub if r['friends'] < 2), sum(1 for g, r in sub if r['friends'] == 0), len(sb),
                        sum(1 for g, r in sb if r['esc_free']), sum(1 for g, r in sb if r['esc_actual']), sum(1 for g, r in sb if r['in_square']),
                        sum(1 for g, r in sb if r['esc_all'])))
            for key in ('map_key', 'opp', 'evening'):
                c = Counter(g[key] for g, r in rams)
                parts = []
                for k, m in c.most_common():
                    sub = [(g, r) for g, r in rams if g[key] == k]
                    sb = [(g, r) for g, r in sub if r.get('born_later') is False]
                    parts.append('%s: %d rams, alone %d, board %d, esc free %d, esc actual %d' % (
                        k, m, sum(1 for g, r in sub if r['friends'] < 2), len(sb), sum(1 for g, r in sb if r['esc_free']),
                        sum(1 for g, r in sb if r['esc_actual'])))
                out('  by %s (%d groups):' % (key, len(c)))
                for q in parts[:12]:
                    out('     ', q)
                vals = []
                vals2 = []
                for k in c:
                    sub = [(g, r) for g, r in rams if g[key] != k]
                    sb = [(g, r) for g, r in sub if r.get('born_later') is False]
                    if sub:
                        vals.append(sum(1 for g, r in sub if r['friends'] < 2) / len(sub))
                    if sb:
                        vals2.append(sum(1 for g, r in sb if r['esc_free']) / len(sb))
                if vals and vals2:
                    out('     leave one %s out: alone share %.3f to %.3f; escape-free share %.3f to %.3f' % (key, min(vals), max(vals), min(vals2), max(vals2)))
            lt = [sum(g['lone'][vs][j] for g in gs) for j in range(3)]
            out('  [baseline] all turns of this queen while the other queen is dead: %d turns, friends under 2 in %s, friends 0 in %s' % (
                lt[0], rt(lt[1], lt[0]), rt(lt[2], lt[0])))
            rg = set(g['game'] for g, r in rams)
            lt2 = [sum(g['lone'][vs][j] for g in gs if g['game'] in rg) for j in range(3)]
            out('  [baseline] same, only the games with such a ram: %d turns, friends under 2 in %s, friends 0 in %s' % (
                lt2[0], rt(lt2[1], lt2[0]), rt(lt2[2], lt2[0])))
            out('  [rate] rams per 1000 such queen turns: %.2f' % (1000 * n / lt[0] if lt[0] else 0))
            oth = [(g, r) for g in gs for r in g['rams'] if r['cross'] and not r['other_queen_dead'] and r['side'] == vs and not r['mover_is_queen']]
            ob = [(g, r) for g, r in oth if r.get('born_later') is False]
            if oth and ob:
                out('  [contrast] same queen rammed while the other queen was still alive: %d rams, alone %s, friends 0 %s, escape free %s, escape actual %s, in square %s' % (
                    len(oth), rt(sum(1 for g, r in oth if r['friends'] < 2), len(oth)), rt(sum(1 for g, r in oth if r['friends'] == 0), len(oth)),
                    rt(sum(1 for g, r in ob if r['esc_free']), len(ob)), rt(sum(1 for g, r in ob if r['esc_actual']), len(ob)),
                    rt(sum(1 for g, r in ob if r['in_square']), len(ob))))
    out('')
    out('checks: games with final state not equal to the result block', sum(1 for g in games if g['code'] != 'other' and not g['final_ok']),
        '; anomalies', dict(sum((Counter(g['anomalies']) for g in games if g['code'] != 'other'), Counter())),
        '; head-on groups not victim-then-mover', sum(g['bad_head_on_groups'] for g in games if g['code'] != 'other'),
        'of', sum(g['head_on_groups'] for g in games if g['code'] != 'other'),
        '; drop mismatches', sum(g['drop_mismatch'] for g in games if g['code'] != 'other'),
        '; bad portal pairs', sum(g['bad_portals'] for g in games if g['code'] != 'other'))


# ---------------------------------------------------------------- F11
def near_counts(g, flt=None):
    c = dict(o=[0, 0, 0], t=[0, 0, 0], e=[0, 0, 0])
    for key, n in g['near'].items():
        du, dt, bal, rw, eater = [int(x) for x in key.split(',')]
        if flt is not None and not flt(du, dt, bal, rw):
            continue
        k = 'o' if du < dt else 't' if dt < du else 'e'
        c[k][0 if eater == 1 else 1 if eater == 2 else 2] += n
    return c


def near_sum(gs, flt=None, cache=None):
    tot = dict(o=[0, 0, 0], t=[0, 0, 0], e=[0, 0, 0])
    for g in gs:
        c = near_counts(g, flt) if cache is None else cache[g['game']]
        for k in tot:
            for j in range(3):
                tot[k][j] += c[k][j]
    return tot


def div(a, b):
    return None if not b else a / b


def near_stats(c):
    on, tn, en = sum(c['o']), sum(c['t']), sum(c['e'])
    return dict(on=on, tn=tn, en=en, share=div(on, on + tn), we=div(c['o'][0], c['o'][0] + c['o'][1]),
                they=div(c['t'][1], c['t'][0] + c['t'][1]), ties=div(c['e'][0], c['e'][0] + c['e'][1]),
                un_o=div(c['o'][2], on), un_t=div(c['t'][2], tn))


def f3(x):
    return 'n/a' if x is None else '%.3f' % x


def near_line(label, gs, flt=None):
    s = near_stats(near_sum(gs, flt))
    out('  %-34s games %3d  ours nearer %6d  tie %5d  theirs nearer %6d  our share %s  we eat ours %s  they eat theirs %s  we eat ties %s  uneaten ours/theirs %s/%s' % (
        label, len(gs), s['on'], s['en'], s['tn'], f3(s['share']), f3(s['we']), f3(s['they']), f3(s['ties']), f3(s['un_o']), f3(s['un_t'])))
    return s


def f11(games):
    for code in ('main', 'v31'):
        allg = [g for g in games if g['code'] == code]
        large = [g for g in allg if g['open_tiles'] >= 2000]
        rest = [g for g in allg if g['open_tiles'] < 2000]
        cache = {g['game']: near_counts(g) for g in allg}
        out('')
        out('=== %s' % code)
        near_line(code + ' large', large)
        near_line(code + ' other', rest)
        for mk in sorted(set(g['map_key'] for g in large)):
            near_line('  ' + mk, [g for g in large if g['map_key'] == mk])
        for bd in ('<1700', '1700-1899', '1900-2099', '2100+'):
            near_line(code + ' large band ' + bd, [g for g in large if g['band'] == bd])
            near_line(code + ' other band ' + bd, [g for g in rest if g['band'] == bd])
        out('  [extra] other layouts one by one:')
        for mk in sorted(set(g['map_key'] for g in rest)):
            near_line('  ' + mk, [g for g in rest if g['map_key'] == mk])
        out('  [extra] by head-count balance at the birth (large):')
        near_line('similar (within 10 percent)', large, lambda du, dt, bal, rw: bal == 0)
        near_line('we have more heads', large, lambda du, dt, bal, rw: bal == 1)
        near_line('they have more heads', large, lambda du, dt, bal, rw: bal == 2)
        out('  [extra] by head-count balance at the birth (other):')
        near_line('similar (within 10 percent)', rest, lambda du, dt, bal, rw: bal == 0)
        near_line('we have more heads', rest, lambda du, dt, bal, rw: bal == 1)
        near_line('they have more heads', rest, lambda du, dt, bal, rw: bal == 2)
        out('  [extra] by round of birth (large):')
        near_line('r0-100', large, lambda du, dt, bal, rw: rw == 0)
        near_line('r101-300', large, lambda du, dt, bal, rw: rw == 1)
        near_line('r301+', large, lambda du, dt, bal, rw: rw == 2)
        near_line('r0-100 and similar heads', large, lambda du, dt, bal, rw: rw == 0 and bal == 0)
        near_line('r101-300 and similar heads', large, lambda du, dt, bal, rw: rw == 1 and bal == 0)
        near_line('r301+ and similar heads', large, lambda du, dt, bal, rw: rw == 2 and bal == 0)
        out('  [extra] eaten share by the nearer side, by how near and by how much nearer (large; cell = nearer distance, gap):')
        for grp, label in ((large, 'large'), (rest, 'other')):
            cells = defaultdict(lambda: [0, 0, 0, 0])
            for g in grp:
                for key, n in g['near'].items():
                    du, dt, bal, rw, eater = [int(x) for x in key.split(',')]
                    if eater == 0 or du == dt:
                        continue
                    if du < dt:
                        c = cells[(du, min(dt - du, 3))]
                        c[0] += n
                        if eater == 1:
                            c[1] += n
                    else:
                        c = cells[(dt, min(du - dt, 3))]
                        c[2] += n
                        if eater == 2:
                            c[3] += n
            so = st = sw = 0.0
            parts = []
            for key in sorted(cells):
                a, b, c2, d = cells[key]
                if a and c2:
                    w = a + c2
                    so += w * b / a
                    st += w * d / c2
                    sw += w
                if key[0] <= 3:
                    parts.append('d%d gap%d%s: we %s, they %s' % (key[0], key[1], '+' if key[1] == 3 else '', rt(b, a), rt(d, c2)))
            out('    %s: standardised to the same mix of (nearer distance, gap): we eat ours %.3f, they eat theirs %.3f' % (label, so / sw, st / sw))
            for q in parts:
                out('       ', q)

        def share_fn(gg):
            s = near_stats(near_sum(gg, cache=cache))
            return s['share']

        def gap_fn(gg):
            s = near_stats(near_sum(gg, cache=cache))
            if s['we'] is None or s['they'] is None:
                return None
            return s['they'] - s['we']
        out('  [chance] our nearer share, large:', bs(large, share_fn), '; other:', bs(rest, share_fn))
        out('  [chance] they-eat-theirs minus we-eat-ours, large:', bs(large, gap_fn), '; other:', bs(rest, gap_fn))
        pg = [near_stats(cache[g['game']]) for g in large]
        out('  [by game] large games with our nearer share under one half: %d of %d; with they-eat-theirs above we-eat-ours: %d of %d' % (
            sum(1 for s in pg if s['share'] is not None and s['share'] < 0.5), sum(1 for s in pg if s['share'] is not None),
            sum(1 for s in pg if s['we'] is not None and s['they'] is not None and s['they'] > s['we']),
            sum(1 for s in pg if s['we'] is not None and s['they'] is not None)))
        out('  [leave one out] our nearer share, large: opponent', loo(large, 'opp', share_fn), '; evening', loo(large, 'evening', share_fn))
        out('  [leave one out] eating gap, large: opponent', loo(large, 'opp', gap_fn), '; evening', loo(large, 'evening', gap_fn))
        ranked = sorted(large, key=lambda g: (near_stats(cache[g['game']])['share'] or 0))
        out('  [without the three large games with the lowest share] share %s, eating gap %s' % (f3(share_fn(ranked[3:])), f3(gap_fn(ranked[3:]))))
        rng = random.Random(5)
        obs = share_fn(rest) - share_fn(large)
        pool = large + rest
        hit = 0
        for _ in range(1000):
            rng.shuffle(pool)
            if share_fn(pool[len(large):]) - share_fn(pool[:len(large)]) >= obs:
                hit += 1
        out('  [chance] large-other difference in our nearer share %.3f; game-label shuffles reaching it: %d of 1000' % (obs, hit))
        lays = sorted(set(g['map_key'] for g in allg))
        vals = sorted((share_fn([g for g in allg if g['map_key'] == mk]), mk) for mk in lays)
        out('  [by layout] our nearer share, all layouts low to high:', ', '.join('%s %.3f' % (mk, v) for v, mk in vals if v is not None))
        vals = sorted((gap_fn([g for g in allg if g['map_key'] == mk]) or 0, mk) for mk in lays)
        out('  [by layout] they-eat-theirs minus we-eat-ours, low to high:', ', '.join('%s %+.3f' % (mk, v) for v, mk in vals))
        hs = [sum(n for key, n in g['near'].items()) for g in large]
        out('  births within 6 of both sides per large game: median %d; all natural births per large game: median %d' % (median(hs), median(g['n_nat'] for g in large)))


# ---------------------------------------------------------------- F20
def wrap_d(W, H, a, b):
    dx = abs(a[0] - b[0])
    dx = min(dx, W - dx)
    dy = abs(a[1] - b[1])
    dy = min(dy, H - dy)
    return dx + dy


def near_set(W, H, tiles, radius):
    s = set()
    for ci in tiles:
        x, y = ci % W, ci // W
        for dx in range(-radius, radius + 1):
            for dy in range(-(radius - abs(dx)), radius - abs(dx) + 1):
                s.add(((y + dy) % H) * W + (x + dx) % W)
    return s


def f20_rows(g, busy, radius=2, tol=1.1):
    W, H = g['W'], g['H']
    ns = near_set(W, H, busy, radius)
    rows = []
    for r, sn in sorted(g['snaps'].items(), key=lambda kv: int(kv[0])):
        nu, nt = len(sn['us']), len(sn['them'])
        if nu < 1 or nt < 1 or nu > tol * nt or nt > tol * nu:
            continue
        rows.append((int(r), nu, nt, sum(1 for h in sn['us'] if h[1] * W + h[0] in ns), sum(1 for h in sn['them'] if h[1] * W + h[0] in ns)))
    return rows


def pool20(rowsets):
    nu = nt = au = at = n = 0
    for rows in rowsets:
        for r, a, b, c, d in rows:
            n += 1
            nu += a
            nt += b
            au += c
            at += d
    return n, nu, nt, au, at


def line20(label, rowsets):
    n, nu, nt, au, at = pool20(rowsets)
    if not n:
        out('  %-44s no snapshots' % label)
        return
    out('  %-44s snapshots %4d  our heads %6d  their heads %6d  our share %.3f  their share %.3f' % (label, n, nu, nt, au / nu, at / nt))


def f20(games):
    bigs = [g for g in games if g['code'] in ('main', 'v31') and g['open_tiles'] >= 1500]
    lay_n = Counter(g['map_key'] for g in bigs)
    lay_busy = defaultdict(Counter)
    for g in bigs:
        for ci, v in g['tiles'].items():
            if v[0] >= 8:
                lay_busy[g['map_key']][int(ci)] += 1
    for code in ('main', 'v31'):
        gs = [g for g in bigs if g['code'] == code]
        out('')
        out('=== %s: %d games on layouts with 1500 or more open tiles' % (code, len(gs)))
        base = {}
        for g in gs:
            busy = [int(ci) for ci, v in g['tiles'].items() if v[0] >= 8]
            base[g['game']] = f20_rows(g, busy)
        line20(code + ' (busy 8+, radius 2)', base.values())
        for mk in sorted(set(g['map_key'] for g in gs)):
            line20('  ' + mk + ' (%d games)' % sum(1 for g in gs if g['map_key'] == mk), [base[g['game']] for g in gs if g['map_key'] == mk])
        nm = Counter()
        for g in gs:
            nm[g['map']] += len(base[g['game']])
        out('  kept snapshots by map name', dict(nm))
        for thr, rad in ((8, 1), (8, 3), (8, 4), (5, 2), (12, 2), (20, 2)):
            line20('[variant] busy %d+, radius %d' % (thr, rad),
                   [f20_rows(g, [int(ci) for ci, v in g['tiles'].items() if v[0] >= thr], rad) for g in gs])
        line20('[variant] all snapshots, any head counts', [f20_rows(g, [int(ci) for ci, v in g['tiles'].items() if v[0] >= 8], 2, 1e9) for g in gs])
        line20('[variant] head counts within 25 percent', [f20_rows(g, [int(ci) for ci, v in g['tiles'].items() if v[0] >= 8], 2, 1.25) for g in gs])
        for lo, hi in ((100, 150), (175, 225), (250, 300)):
            line20('[by round] r%d-%d' % (lo, hi), [[r for r in base[g['game']] if lo <= r[0] <= hi] for g in gs])
        # busy from the other games on the same layout
        els = {}
        for g in gs:
            own = set(int(ci) for ci, v in g['tiles'].items() if v[0] >= 8)
            m = lay_n[g['map_key']] - 1
            busy = [ci for ci, k in lay_busy[g['map_key']].items() if m > 0 and (k - (1 if ci in own else 0)) >= 0.5 * m]
            els[g['game']] = f20_rows(g, busy)
        line20('[check] busy = 8+ births in at least half of the OTHER games on the layout', els.values())
        for mk in sorted(set(g['map_key'] for g in gs)):
            line20('    ' + mk, [els[g['game']] for g in gs if g['map_key'] == mk])
        # who feeds the busy tiles
        tb = tt = 0
        eu = et = 0
        fed_o = {}
        fed_t = {}
        for g in gs:
            bo = []
            bt = []
            for ci, v in g['tiles'].items():
                if v[0] >= 8:
                    tb += 1
                    eu += v[1]
                    et += v[2]
                    if v[2] > v[1]:
                        tt += 1
                        bt.append(int(ci))
                    else:
                        bo.append(int(ci))
            fed_o[g['game']] = f20_rows(g, bo)
            fed_t[g['game']] = f20_rows(g, bt)
        out('  [check] busy tiles %d (%.1f per game); those where they ate more than we did: %d (%.3f); pearls eaten on busy tiles: ours %d, theirs %d (their share %.3f)' % (
            tb, tb / len(gs), tt, tt / tb, eu, et, et / (eu + et)))
        line20('[check] near busy tiles mostly eaten by US', fed_o.values())
        line20('[check] near busy tiles mostly eaten by THEM', fed_t.values())
        # chance
        keep = [g for g in gs if base[g['game']]]

        def diff_fn(gg):
            n, nu, nt, au, at = pool20([base[g['game']] for g in gg])
            if not nu or not nt:
                return None
            return at / nt - au / nu
        out('  [chance] their share minus ours:', bs(keep, diff_fn), 'over', len(keep), 'games with a kept snapshot')
        for name in ('Around UNSW', 'Slithery Fight'):
            sub = [g for g in keep if g['map'] == name]
            out('  [chance] %s: their share minus ours %s over %d games' % (name, bs(sub, diff_fn), len(sub)))
        snap_pos = snap_neg = snap_eq = 0
        game_pos = game_neg = 0
        for g in keep:
            for r, a, b, c, d in base[g['game']]:
                if d / b > c / a:
                    snap_pos += 1
                elif d / b < c / a:
                    snap_neg += 1
                else:
                    snap_eq += 1
            v = diff_fn([g])
            if v > 0:
                game_pos += 1
            elif v < 0:
                game_neg += 1
        out('  [by snapshot] their share higher in %d, ours higher in %d, equal %d' % (snap_pos, snap_neg, snap_eq))
        out('  [by game] their pooled share higher in %d games, ours higher in %d (sign test p %.4f)' % (game_pos, game_neg, sign_p(game_pos, game_neg)))
        out('  [leave one out] their share minus ours: opponent', loo(keep, 'opp', diff_fn), '; layout', loo(keep, 'map_key', diff_fn), '; evening', loo(keep, 'evening', diff_fn))
        ranked = sorted(keep, key=lambda g: -diff_fn([g]) * sum(r[1] + r[2] for r in base[g['game']]))
        out('  [without the three games that add most to the gap] their share minus ours %.3f' % diff_fn(ranked[3:]))
        for bd in ('1700-1899', '1900-2099', '2100+'):
            line20('[band] ' + bd, [base[g['game']] for g in gs if g['band'] == bd])
        line20('[result] games we won', [base[g['game']] for g in gs if g['win']])
        line20('[result] games we lost', [base[g['game']] for g in gs if not g['win']])
        # nearest friend
        sm = lg = eq = 0
        for g in gs:
            if g['open_tiles'] < 2000:
                continue
            W, H = g['W'], g['H']
            for r, sn in g['snaps'].items():
                nu, nt = len(sn['us']), len(sn['them'])
                if nu < 2 or nt < 2 or nu > 1.1 * nt or nt > 1.1 * nu:
                    continue
                med = []
                for hs in (sn['us'], sn['them']):
                    ds = []
                    for i, a in enumerate(hs):
                        ds.append(min(wrap_d(W, H, a, b) for j, b in enumerate(hs) if j != i))
                    med.append(median(ds))
                if med[0] < med[1]:
                    sm += 1
                elif med[0] > med[1]:
                    lg += 1
                else:
                    eq += 1
        out('  [nearest friend, my guess at the definition: median over heads of the distance to the nearest own head, kept snapshots on layouts with 2000+ open tiles] ours smaller %d, ours larger %d, tied %d' % (sm, lg, eq))


# ---------------------------------------------------------------- F18
def f18_sum(gs, flt):
    c = dict(us=[0, 0], them=[0, 0])
    for g in gs:
        for key, n in g['f18'].items():
            s, rb, pocket, via, passed = key.split('|')
            if not flt(int(rb), int(pocket), via):
                continue
            c[s][1] += n
            if passed == '1':
                c[s][0] += n
    return c


def line18(label, gs, flt):
    c = f18_sum(gs, flt)
    out('  %-58s ours %s, theirs %s (%d games)' % (label, rt(c['us'][0], c['us'][1]), rt(c['them'][0], c['them'][1]), len(gs)))
    return c


def f18(games):
    for code in ('main', 'v31'):
        gs = [g for g in games if g['code'] == code]
        st = [g for g in gs if g['map'] == 'Stripes']
        rest = [g for g in gs if g['map'] != 'Stripes']
        out('')
        out('=== %s: %d games, %d on Stripes' % (code, len(gs), len(st)))
        line18('(1) all layouts r0-100', gs, lambda rb, pk, via: rb == 0)
        line18('(2) Stripes r0-100', st, lambda rb, pk, via: rb == 0)
        line18('    Stripes r0-100, opponents under 1900', [g for g in st if g['opponentElo'] < 1900], lambda rb, pk, via: rb == 0)
        line18('    Stripes r0-100, opponents 1900 or more', [g for g in st if g['opponentElo'] >= 1900], lambda rb, pk, via: rb == 0)
        line18('(3) Stripes r0-199 pocket chances via portal', st, lambda rb, pk, via: pk == 1 and via == 'P')
        line18('(3) Stripes r0-199 pocket chances not via portal', st, lambda rb, pk, via: pk == 1 and via != 'P')
        line18('    of those: reached both ways (mixed)', st, lambda rb, pk, via: pk == 1 and via == 'M')
        line18('(4) pocket chances r0-100, all layouts but Stripes', rest, lambda rb, pk, via: rb == 0 and pk == 1)
        out('  Stripes results: %d games, %d won, we were eliminated in %d, they were eliminated in %d, went to r499 in %d' % (
            len(st), sum(1 for g in st if g['win']), sum(1 for g in st if g['final_alive']['us'] == 0),
            sum(1 for g in st if g['final_alive']['them'] == 0), sum(1 for g in st if g['last_round'] == 499)))
        out('  [extra] other cuts:')
        line18('all layouts but Stripes r0-100', rest, lambda rb, pk, via: rb == 0)
        line18('Stripes r0-199 all chances', st, lambda rb, pk, via: True)
        line18('Stripes r0-199 via portal, not a pocket', st, lambda rb, pk, via: pk == 0 and via == 'P')
        line18('Stripes r0-199 open edge, not a pocket', st, lambda rb, pk, via: pk == 0 and via != 'P')
        line18('Stripes r0-100 pocket via portal', st, lambda rb, pk, via: rb == 0 and pk == 1 and via == 'P')
        line18('Stripes r101-199 pocket via portal', st, lambda rb, pk, via: rb == 1 and pk == 1 and via == 'P')
        line18('other layouts r0-199 via portal (any)', rest, lambda rb, pk, via: via == 'P')
        line18('other layouts r0-199 via portal, pocket', rest, lambda rb, pk, via: via == 'P' and pk == 1)
        line18('other layouts r0-199 via portal, not a pocket', rest, lambda rb, pk, via: via == 'P' and pk == 0)
        line18('other layouts r0-199 pocket, open edge', rest, lambda rb, pk, via: via != 'P' and pk == 1)
        line18('other layouts r0-199 not a pocket, open edge', rest, lambda rb, pk, via: via != 'P' and pk == 0)
        out('  [by layout] r0-100 all chances; then r0-199 via portal; then r0-199 pocket via portal:')
        for mk in sorted(set(g['map_key'] for g in gs)):
            sub = [g for g in gs if g['map_key'] == mk]
            a = f18_sum(sub, lambda rb, pk, via: rb == 0)
            b = f18_sum(sub, lambda rb, pk, via: via == 'P')
            c = f18_sum(sub, lambda rb, pk, via: via == 'P' and pk == 1)
            out('     %-22s %2d games | all: ours %s, theirs %s | portal: ours %s, theirs %s | pocket portal: ours %s, theirs %s' % (
                mk, len(sub), rt(a['us'][0], a['us'][1]), rt(a['them'][0], a['them'][1]), rt(b['us'][0], b['us'][1]), rt(b['them'][0], b['them'][1]),
                rt(c['us'][0], c['us'][1]), rt(c['them'][0], c['them'][1])))
        if not st:
            continue
        pp = lambda rb, pk, via: pk == 1 and via == 'P'

        def rate_fn(side):
            def fn(gg):
                c = f18_sum(gg, pp)
                return div(c[side][0], c[side][1])
            return fn

        def gapfn(gg):
            c = f18_sum(gg, pp)
            if not c['us'][1] or not c['them'][1]:
                return None
            return c['us'][0] / c['us'][1] - c['them'][0] / c['them'][1]
        out('  [chance] Stripes pocket via portal: ours', bs(st, rate_fn('us')), '; theirs', bs(st, rate_fn('them')), '; gap', bs(st, gapfn))
        hi = lo = eq = na = 0
        per = []
        for g in st:
            c = f18_sum([g], pp)
            per.append('%s %s vs %s%s' % (g['opp'], rt(c['us'][0], c['us'][1]), rt(c['them'][0], c['them'][1]), ' W' if g['win'] else ' L'))
            if not c['us'][1] or not c['them'][1]:
                na += 1
                continue
            a, b = c['us'][0] / c['us'][1], c['them'][0] / c['them'][1]
            if a > b:
                hi += 1
            elif a < b:
                lo += 1
            else:
                eq += 1
        out('  [by game] Stripes pocket via portal: our pass-up rate higher in %d games, lower in %d, equal %d, one side without a chance %d (sign test p %.4f)' % (
            hi, lo, eq, na, sign_p(hi, lo)))
        for q in per:
            out('       ', q)
        out('  [leave one out] gap: opponent', loo(st, 'opp', gapfn), '; evening', loo(st, 'evening', gapfn))
        ranked = sorted(st, key=lambda g: -(f18_sum([g], pp)['us'][0]))
        c = f18_sum(ranked[3:], pp)
        out('  [without the three games with most of our passed-up chances] ours %s, theirs %s' % (rt(c['us'][0], c['us'][1]), rt(c['them'][0], c['them'][1])))
        # detail rows: who, how long, what happens next
        dr = dict(us=defaultdict(list), them=defaultdict(list))
        took_die = dict(us=[0, 0], them=[0, 0])
        pass_die = dict(us=[0, 0], them=[0, 0])
        regs = dict(us=Counter(), them=Counter())
        lens = dict(us=Counter(), them=Counter())
        queens = dict(us=[0, 0], them=[0, 0])
        for g in st:
            for r, a, s, L, tiles, passed, died, isq, pocket, via in g['f18rows']:
                if not pocket or via != 'P':
                    continue
                dr[s][(g['game'], a)].append((r, passed))
                for t in tiles:
                    regs[s][t[3]] += 1
                lens[s][min(L, 12)] += 1
                queens[s][1] += 1
                queens[s][0] += isq
                dd = g['death_by_id'].get(str(a))
                dies = 1 if (dd is not None and dd[0] - r <= 10) else 0
                tgt = pass_die if passed else took_die
                tgt[s][1] += 1
                tgt[s][0] += dies
        for s in ('us', 'them'):
            d = dr[s]
            runs = [len(v) for v in d.values()]
            ever = sum(1 for v in d.values() if any(p == 0 for r, p in v))
            out('  [detail] %s: %d dragons had a pocket-via-portal chance; %d of them took one at least once; chances per dragon median %s, max %d; chances from the 5 dragons with most: %d of %d' % (
                s, len(d), ever, median(runs) if runs else 0, max(runs) if runs else 0, sum(sorted(runs)[-5:]), sum(runs)))
            out('           region sizes of the pearl tiles %s; dragon lengths (12 = 12 or more) %s; chances that were the queen: %d of %d' % (
                sorted(regs[s].items()), sorted(lens[s].items()), queens[s][0], queens[s][1]))
            out('           dragon dead within 10 rounds after TAKING: %s; after PASSING UP: %s' % (rt(took_die[s][0], took_die[s][1]), rt(pass_die[s][0], pass_die[s][1])))


def main():
    what = sys.argv[1]
    games, bad = load()
    out('games loaded', len(games), 'errors', len(bad), '; main', sum(1 for g in games if g['code'] == 'main'),
        'v31', sum(1 for g in games if g['code'] == 'v31'), 'other', sum(1 for g in games if g['code'] == 'other'))
    out('latest game completed at', max(g['completedAt'] for g in games))
    if what == 'F13':
        f13(games)
        open(P + 'f13-0425-numbers.txt', 'w').write('\n'.join(LINES) + '\n')
    elif what == 'F11':
        f11(games)
        open(P + 'f11-0425-numbers.txt', 'w').write('\n'.join(LINES) + '\n')
    elif what == 'F20':
        f20(games)
        open(P + 'f20-numbers.txt', 'w').write('\n'.join(LINES) + '\n')
    elif what == 'F18':
        f18(games)
        open(P + 'f18-numbers.txt', 'w').write('\n'.join(LINES) + '\n')


main()
