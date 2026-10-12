#!/usr/bin/env python3
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
"""Verifier counts 13 (run of 2026-10-07 15:12 KST): F44, F42, F7 from x13-0..5.jsonl (extract13.py)."""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict

OUT = []


def say(*a):
    OUT.append(' '.join(str(x) for x in a))


def wilson(a, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = a / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def fr(a, n):
    lo, hi = wilson(a, n)
    return '%d of %d (%.3f; %.2f to %.2f)' % (a, n, a / n if n else 0, lo, hi)


def fisher(a, n1, c, n2):
    K = a + c
    N = n1 + n2
    tot = math.comb(N, K)

    def pm(x):
        return math.comb(n1, x) * math.comb(n2, K - x) / tot
    p0 = pm(a)
    return sum(pm(x) for x in range(max(0, K - n2), min(n1, K) + 1) if pm(x) <= p0 * (1 + 1e-9))


def band(e):
    if e is None:
        return 'none'
    return 'under' if e < 1700 else '1700-1899' if e < 1900 else '1900-2099' if e < 2100 else '2100+'


BANDS = ['1700-1899', '1900-2099', '2100+']
games = []
for i in range(6):
    for line in Path(P + 'x13-%d.jsonl' % i).read_text().splitlines():
        if line.strip():
            games.append(json.loads(line))
games.sort(key=lambda g: g['game'])
say('games read', len(games), 'errors', sum(1 for g in games if 'error' in g))
for g in games:
    if 'error' in g:
        say('  ERROR', g['game'], g['error'])
games = [g for g in games if 'error' not in g]
say('ranked', sum(1 for g in games if g.get('ranked')), 'not in ledger', sum(1 for g in games if 'ranked' not in g),
    'ledger complete', sum(1 for g in games if g.get('ledger_complete')))
say('final state equals result block', sum(1 for g in games if g['final_ok']), 'owner map ok', sum(1 for g in games if g['own_ok']),
    'rounds consecutive', sum(1 for g in games if g['rounds_ok']), 'games with anomalies', sum(1 for g in games if g['anomalies']),
    'bad portals', sum(1 for g in games if g['bad_portals']))
maps = json.loads(Path('data/analysis/ladder/maps.json').read_text())
seen = defaultdict(list)
for g in games:
    ls = seen[g['map']]
    if g['layout'] not in ls:
        ls.append(g['layout'])
    g['map_key'] = '%s #%d' % (g['map'], ls.index(g['layout']) + 1)
    m = maps.get(g['map_key'])
    g['dead_end'] = bool(m and m['queen_spawn_dead_end'])
    if m is None or (m['width'], m['height']) != (g['W'], g['H']):
        say('  map key mismatch', g['game'], g['map_key'])
    g['band'] = band(g.get('opponentElo'))
    g['cells'] = g['W'] * g['H']
    g['small'] = g['cells'] <= 1200
    g['date'] = (g.get('at_kst') or '')[:13]
    g['day'] = (g.get('at_kst') or '')[:10]
say('layouts', len(set(g['map_key'] for g in games)), 'dead-end keys in maps.json', sorted(k for k, v in maps.items() if v['queen_spawn_dead_end']))
say('codes', dict(Counter(g['code'] for g in games)))
for code in ('main', 'v31'):
    z = 0
    for g in games:
        if g['code'] == code:
            g['idx'] = z
            g['half'] = 1 if z < 97 else 2
            z += 1
say('layout sizes:', sorted(set((g['map_key'], g['W'], g['H'], g['cells'], tuple(g['spawn_n']), g['qdist']) for g in games), key=lambda t: t[3]))


def perm_battles(gs, flag, lab_a, lab_b, B=20000, seed=5):
    """battles keep their games; band labels are shuffled over the battles of the two bands"""
    bt = defaultdict(lambda: [0, 0, None])
    for g in gs:
        if g['band'] in (lab_a, lab_b):
            r = bt[g['battle']]
            r[0] += 1 if flag(g) else 0
            r[1] += 1
            r[2] = g['band']
    rows = list(bt.values())

    def stat(labels):
        a = sum(r[0] for r, l in zip(rows, labels) if l == lab_a)
        na = sum(r[1] for r, l in zip(rows, labels) if l == lab_a)
        b = sum(r[0] for r, l in zip(rows, labels) if l == lab_b)
        nb = sum(r[1] for r, l in zip(rows, labels) if l == lab_b)
        return (a / na if na else 0) - (b / nb if nb else 0)
    labels = [r[2] for r in rows]
    obs = stat(labels)
    rng = random.Random(seed)
    hit = 0
    for _ in range(B):
        rng.shuffle(labels)
        if stat(labels) >= obs - 1e-12:
            hit += 1
    return obs, hit, B, len(rows)


# ---------------------------------------------------------------- F44
say('')
say('=================== F44 ===================')


def wipe(g):
    return g['end_reason'] == 0 and g['final'][0]['alive'] == 0 and g['last_round'] <= 125


def mirror(g):
    return g['end_reason'] == 0 and g['final'][1]['alive'] == 0 and g['last_round'] <= 125


def at(lst, r):
    return lst[r] if r < len(lst) else lst[-1]


def rammed(g):
    q = g['qdeath'][0]
    return bool(q) and q['reason'] == 3 and q['mover_side'] == 1


RNAME = ['wall', 'own body', 'other body', 'head-on', 'other']
for code in ('main', 'v31'):
    gs = [g for g in games if g['code'] == code]
    sm = [g for g in gs if g['small']]
    ws = [g for g in gs if wipe(g)]
    say('')
    say('--', code, 'games', len(gs), 'on layouts of 1200 cells or fewer', len(sm))
    say('early wipe-outs (all layouts):', fr(len(ws), len(gs)), ' on small layouts:', sum(1 for g in ws if g['small']),
        ' mirror all layouts:', sum(1 for g in gs if mirror(g)), ' both sides empty:', sum(1 for g in gs if wipe(g) and mirror(g)))
    say('eliminations by r125 with a side empty that is neither:', sum(1 for g in gs if g['end_reason'] == 0 and g['last_round'] <= 125 and not wipe(g) and not mirror(g)))
    for b in ['under'] + BANDS:
        x = [g for g in sm if g['band'] == b]
        if not x:
            continue
        losses = sum(1 for g in x if not g['win'])
        say('  band %-9s small layouts: wiped %s | mirror %s | games lost %d, wiped of lost %s | battles %d opponents %d' % (
            b, fr(sum(1 for g in x if wipe(g)), len(x)), fr(sum(1 for g in x if mirror(g)), len(x)), losses,
            '%d of %d' % (sum(1 for g in x if wipe(g)), losses), len(set(g['battle'] for g in x)), len(set(g['opponentId'] for g in x))))
    lo = [g for g in sm if g['band'] == '1700-1899']
    hi = [g for g in sm if g['band'] == '2100+']
    mid = [g for g in sm if g['band'] == '1900-2099']
    a, c = sum(1 for g in hi if wipe(g)), sum(1 for g in lo if wipe(g))
    say('  2100+ against 1700-1899: Fisher exact p = %.5f' % fisher(a, len(hi), c, len(lo)))
    obs, hit, B, nb = perm_battles(sm, wipe, '2100+', '1700-1899')
    say('  whole battles shuffled between the two bands: gap %.3f, %d of %d shuffles as large (%d battles)' % (obs, hit, B, nb))
    a2 = sum(1 for g in mid if wipe(g))
    say('  1900-2099 against 1700-1899: Fisher exact p = %.5f' % fisher(a2, len(mid), c, len(lo)))
    obs, hit, B, nb = perm_battles(sm, wipe, '1900-2099', '1700-1899')
    say('  whole battles shuffled (1900-2099 v 1700-1899): gap %.3f, %d of %d as large (%d battles)' % (obs, hit, B, nb))
    obs, hit, B, nb = perm_battles(sm, wipe, '2100+', '1900-2099')
    say('  whole battles shuffled (2100+ v 1900-2099): gap %.3f, %d of %d as large (%d battles)' % (obs, hit, B, nb))
    say('  mirror 1700-1899 against 2100+: Fisher p = %.5f' % fisher(sum(1 for g in lo if mirror(g)), len(lo), sum(1 for g in hi if mirror(g)), len(hi)))
    say('  halves (by order of this code): half 1 %d of %d, half 2 %d of %d' % (
        sum(1 for g in ws if g['half'] == 1), sum(1 for g in gs if g['half'] == 1),
        sum(1 for g in ws if g['half'] == 2), sum(1 for g in gs if g['half'] == 2)))
    say('  halves on small layouts: half 1 %d of %d, half 2 %d of %d' % (
        sum(1 for g in ws if g['half'] == 1 and g['small']), sum(1 for g in sm if g['half'] == 1),
        sum(1 for g in ws if g['half'] == 2 and g['small']), sum(1 for g in sm if g['half'] == 2)))
    for h in (1, 2):
        say('   half %d bands on small layouts:' % h, {b: '%d of %d' % (sum(1 for g in sm if g['band'] == b and g['half'] == h and wipe(g)), sum(1 for g in sm if g['band'] == b and g['half'] == h)) for b in BANDS})
    say('  by day (small layouts):', {d: '%d of %d' % (sum(1 for g in sm if g['day'] == d and wipe(g)), sum(1 for g in sm if g['day'] == d)) for d in sorted(set(g['day'] for g in sm))})
    say('  by bot id:', {b: '%d of %d' % (sum(1 for g in sm if g['bot'] == b and wipe(g)), sum(1 for g in sm if g['bot'] == b)) for b in sorted(set(g['bot'] for g in sm))})
    say('  per small layout: wiped / mirror / games, and by band wiped of games')
    exp_hi = 0.0
    exp_hi_v = 0.0
    for mk in sorted(set(g['map_key'] for g in sm)):
        x = [g for g in sm if g['map_key'] == mk]
        inb = [g for g in x if g['band'] in BANDS]
        rate = sum(1 for g in inb if wipe(g)) / len(inb) if inb else 0
        nh = sum(1 for g in x if g['band'] == '2100+')
        exp_hi += nh * rate
        say('    %-22s cells %4d start %s qdist %2d: %2d / %2d / %3d   %s' % (mk, x[0]['cells'], x[0]['spawn_n'], x[0]['qdist'],
            sum(1 for g in x if wipe(g)), sum(1 for g in x if mirror(g)), len(x),
            {b: '%d of %d' % (sum(1 for g in x if g['band'] == b and wipe(g)), sum(1 for g in x if g['band'] == b)) for b in BANDS}))
    say('  expected wipe-outs in 2100+ if each layout had its pooled rate: %.2f (observed %d)' % (exp_hi, a))
    say('  wipe-outs by opponent:', dict(Counter('%s (%s)' % (g['opponent'], g['band']) for g in ws)))
    say('  wipe-outs by battle:', dict(Counter(g['battle'] for g in ws)))
    for b in BANDS:
        x = [g for g in sm if g['band'] == b]
        opp = Counter(g['opponent'] for g in x)
        say('   band', b, 'opponents (games, wiped):', {o: '%d, %d' % (n, sum(1 for g in x if g['opponent'] == o and wipe(g))) for o, n in opp.most_common()})
    # leave one opponent out, 2100+ v 1700-1899
    res = []
    for o in sorted(set(g['opponent'] for g in hi + lo)):
        h2 = [g for g in hi if g['opponent'] != o]
        l2 = [g for g in lo if g['opponent'] != o]
        res.append((o, sum(1 for g in h2 if wipe(g)), len(h2), sum(1 for g in l2 if wipe(g)), len(l2)))
    worst = sorted(res, key=lambda r: (r[1] / r[2] if r[2] else 0) - (r[3] / r[4] if r[4] else 0))[:3]
    say('  one opponent left out, the three smallest gaps (opponent, 2100+ wiped of n, 1700-1899 wiped of n):', worst)
    say('  2100+ with its three wipe-out-richest battles removed: see the by-battle list')
    # properties of the wipe-outs
    und = [g for g in ws if at(g['eaten'][0], 50) * 2 < at(g['eaten'][1], 50)]
    say('  pearls by r50 under half of theirs:', '%d of %d' % (len(und), len(ws)))
    say('  two-dragon start:', '%d of %d' % (sum(1 for g in ws if g['spawn_n'] == [2, 2]), len(ws)),
        '; of all small-layout games:', '%d of %d' % (sum(1 for g in sm if g['spawn_n'] == [2, 2]), len(sm)))
    say('  our queen rammed by a dragon of theirs (head-on, mover theirs):', '%d of %d' % (sum(1 for g in ws if rammed(g)), len(ws)))
    say('  our queen death reasons:', dict(Counter(RNAME[g['qdeath'][0]['reason']] + (' mover ours' if g['qdeath'][0]['mover_side'] == 0 else ' mover theirs' if g['qdeath'][0]['mover_side'] == 1 else '') for g in ws if g['qdeath'][0])))
    say('  queen spawn distance 10 or less:', '%d of %d' % (sum(1 for g in ws if g['qdist'] <= 10), len(ws)),
        '; of all small-layout games:', '%d of %d' % (sum(1 for g in sm if g['qdist'] <= 10), len(sm)))

    def dmean(x):
        n = len(x)
        if not n:
            return 'none'
        return '%.1f of which head-on %.1f, wall %.1f, own %.1f, other body %.1f, other %.1f (n %d)' % (
            sum(sum(g['dw'][0][0]) for g in x) / n, sum(g['dw'][0][0][3] for g in x) / n, sum(g['dw'][0][0][0] for g in x) / n,
            sum(g['dw'][0][0][1] for g in x) / n, sum(g['dw'][0][0][2] for g in x) / n, sum(g['dw'][0][0][4] for g in x) / n, n)
    say('  our deaths r0-100 per game, wipe-outs:', dmean(ws))
    say('  other games on all small layouts:', dmean([g for g in sm if not wipe(g)]))
    keys = set(g['map_key'] for g in ws)
    say('  other games on the layouts that have a wipe-out:', dmean([g for g in sm if not wipe(g) and g['map_key'] in keys]))
    say('  other games lost on small layouts:', dmean([g for g in sm if not wipe(g) and not g['win']]))
    # baselines
    oth = [g for g in sm if not wipe(g)]
    othl = [g for g in oth if not g['win']]
    say('  baseline, pearls by r50 under half: other small-layout games %d of %d, other lost %d of %d' % (
        sum(1 for g in oth if at(g['eaten'][0], 50) * 2 < at(g['eaten'][1], 50)), len(oth),
        sum(1 for g in othl if at(g['eaten'][0], 50) * 2 < at(g['eaten'][1], 50)), len(othl)))
    say('  baseline, wiped among games with pearls by r50 under half, by band:', {b: '%d of %d' % (
        sum(1 for g in sm if g['band'] == b and wipe(g) and at(g['eaten'][0], 50) * 2 < at(g['eaten'][1], 50)),
        sum(1 for g in sm if g['band'] == b and at(g['eaten'][0], 50) * 2 < at(g['eaten'][1], 50))) for b in BANDS})
    qd = [g for g in oth if g['qdeath'][0]]
    qd125 = [g for g in qd if g['qdeath'][0]['round'] <= 125]
    say('  baseline, our queen rammed by theirs among other small-layout games where she died: %d of %d; died by r125: %d of %d' % (
        sum(1 for g in qd if rammed(g)), len(qd), sum(1 for g in qd125 if rammed(g)), len(qd125)))
    say('  mirror games: their queen rammed by ours: %d of %d; their pearls by r50 under half of ours: %d of %d' % (
        sum(1 for g in sm if mirror(g) and g['qdeath'][1] and g['qdeath'][1]['reason'] == 3 and g['qdeath'][1]['mover_side'] == 0),
        sum(1 for g in sm if mirror(g)),
        sum(1 for g in sm if mirror(g) and at(g['eaten'][1], 50) * 2 < at(g['eaten'][0], 50)), sum(1 for g in sm if mirror(g))))
    say('  wipe-out threshold round, wiped per band on small layouts:')
    for R in (100, 125, 150, 200):
        say('    by r%d:' % R, {b: '%d of %d' % (sum(1 for g in sm if g['band'] == b and g['end_reason'] == 0 and g['final'][0]['alive'] == 0 and g['last_round'] <= R),
                                               sum(1 for g in sm if g['band'] == b)) for b in BANDS},
            'mirror', {b: sum(1 for g in sm if g['band'] == b and g['end_reason'] == 0 and g['final'][1]['alive'] == 0 and g['last_round'] <= R) for b in BANDS})
    say('  the wipe-outs:')
    for g in ws:
        q = g['qdeath'][0]
        say('    %d battle %s %-20s %-28s %4d %-9s half %d last r%3d pearls r50 %2d v %2d start %s qdist %2d queen died r%s %s mover %s other len %s (their queen %s) alive then %s; our deaths r0-100 %d head-on %d; alive r50 %d v %d' % (
            g['game'], g['battle'], g['map_key'], g['opponent'], g['opponentElo'], g['band'], g['half'], g['last_round'],
            at(g['eaten'][0], 50), at(g['eaten'][1], 50), g['spawn_n'], g['qdist'], q['round'] if q else '-', RNAME[q['reason']] if q else '-',
            q['mover_side'] if q else '-', q['other_len'] if q else '-', q['other_queen'] if q else '-', q['alive'] if q else '-',
            sum(g['dw'][0][0]), g['dw'][0][0][3], at(g['alive'][0], 50), at(g['alive'][1], 50)))

# ---------------------------------------------------------------- F42
say('')
say('=================== F42 ===================')


def kept42(g):
    f = g['final']
    return (g['last_round'] == 499 and g['end_reason'] == 1 and f[0]['queen'] != f[1]['queen']
            and (f[0]['queen'] > 0) != (f[1]['queen'] > 0) and not g['dead_end'])


def group42(g):
    f = g['final']
    if f[0]['queen'] > 0:
        return 'mirror'
    return 'flagged' if f[0]['longest'] > f[1]['longest'] else 'not flagged'


def pooled(x, key):
    t = sum(aft(g)['turns'] for g in x)
    return sum(aft(g)[key] for g in x) / t if t else 0.0


def aft(g):
    return g['after'][0 if g['final'][0]['queen'] > 0 else 1]


def bootp(x, key, B=4000, seed=11):
    rng = random.Random(seed)
    vals = []
    n = len(x)
    for _ in range(B):
        s = [x[rng.randrange(n)] for _ in range(n)]
        vals.append(pooled(s, key))
    vals.sort()
    return vals[int(0.025 * B)], vals[int(0.975 * B)]


def permg(x1, x0, key, B=20000, seed=13):
    obs = pooled(x1, key) - pooled(x0, key)
    allg = x1 + x0
    n1 = len(x1)
    rng = random.Random(seed)
    hit = 0
    for _ in range(B):
        rng.shuffle(allg)
        if abs(pooled(allg[:n1], key) - pooled(allg[n1:], key)) >= abs(obs) - 1e-12:
            hit += 1
    return obs, hit, B


G42 = {}
for code in ('main', 'v31'):
    ks = [g for g in games if g['code'] == code and kept42(g)]
    say('')
    say('--', code, 'kept (full game, queen rule, one queen alive, no dead-end spawn):', len(ks),
        ' only theirs alive:', sum(1 for g in ks if group42(g) != 'mirror'), ' flagged:', sum(1 for g in ks if group42(g) == 'flagged'))
    say('   kept games that are not a loss among only-theirs-alive:', sum(1 for g in ks if group42(g) != 'mirror' and g['win']),
        ' not a win among mirror:', sum(1 for g in ks if group42(g) == 'mirror' and not g['win']))
    say('   surviving queen whose turns after the death number zero:', sum(1 for g in ks if aft(g)['turns'] == 0))
    for grp in ('flagged', 'not flagged', 'mirror'):
        x = [g for g in ks if group42(g) == grp]
        G42[code, grp] = x
        t = sum(aft(g)['turns'] for g in x)
        if not x:
            continue
        loA, hiA = bootp(x, 'A6')
        loB, hiB = bootp(x, 'B6')
        say('  %-11s %2d games, %5d turns, A %.3f (games resampled %.3f to %.3f), B %.3f (%.3f to %.3f), within 2 steps: short %.4f any %.4f' % (
            grp, len(x), t, pooled(x, 'A6'), loA, hiA, pooled(x, 'B6'), loB, hiB, pooled(x, 'A2'), pooled(x, 'B2')))
        say('     per game B, sorted:', ' '.join('%.2f' % (aft(g)['B6'] / aft(g)['turns']) for g in sorted(x, key=lambda g: aft(g)['B6'] / max(1, aft(g)['turns']))))
        pg = sorted(aft(g)['B6'] / aft(g)['turns'] for g in x if aft(g)['turns'])
        pa = sorted(aft(g)['A6'] / aft(g)['turns'] for g in x if aft(g)['turns'])
        say('     per game: median B %.3f, mean B %.3f, median A %.3f, mean A %.3f; games with B zero %d (Portals %d); games with A zero %d' % (
            pg[len(pg) // 2], sum(pg) / len(pg), pa[len(pa) // 2], sum(pa) / len(pa),
            sum(1 for g in x if aft(g)['B6'] == 0), sum(1 for g in x if aft(g)['B6'] == 0 and g['map'] == 'Portals'),
            sum(1 for g in x if aft(g)['A6'] == 0)))
        say('     heads of the other side alive per turn %.1f, short (4 or less) %.1f, in her connected area %.1f; turns with some head of theirs in her area %.3f' % (
            sum(aft(g)['n_other'] for g in x) / t, sum(aft(g)['n_short'] for g in x) / t, sum(aft(g)['n_same'] for g in x) / t, pooled(x, 'same')))
        say('     tiles within 6 steps of her, mean %.1f; if the heads in her area stood on random tiles of it: A %.3f, B %.3f' % (
            sum(aft(g)['ball'] for g in x) / t, pooled(x, 'expA'), pooled(x, 'expB')))
        hA = [sum(aft(g)['histA'][d] for g in x) for d in range(8)]
        hB = [sum(aft(g)['histB'][d] for g in x) for d in range(8)]
        say('     nearest head, steps 0..6 and beyond: any', hB, 'short', hA)
        wt = [sum(aft(g)['wt'][w] for g in x) for w in range(4)]
        wB = [sum(aft(g)['wB'][w] for g in x) for w in range(4)]
        say('     B by raw round window (0-100, 101-200, 201-300, 301-499):', ['%d of %d' % (b, n) for b, n in zip(wB, wt)])
        say('     by layout (games, turns, B):', {mk: '%d, %d, %.3f' % (len([g for g in x if g['map_key'] == mk]), sum(aft(g)['turns'] for g in x if g['map_key'] == mk), pooled([g for g in x if g['map_key'] == mk], 'B6')) for mk in sorted(set(g['map_key'] for g in x))})
        np_ = [g for g in x if g['map'] != 'Portals']
        say('     without Portals: %d games, %d turns, A %.3f, B %.3f' % (len(np_), sum(aft(g)['turns'] for g in np_), pooled(np_, 'A6'), pooled(np_, 'B6')))
        # leave one out
        for what in ('opponent', 'map_key', 'day'):
            vals = []
            for o in sorted(set(g[what] for g in x)):
                y = [g for g in x if g[what] != o]
                if y:
                    vals.append((pooled(y, 'B6'), pooled(y, 'A6'), o))
            if vals:
                say('     one %s left out: B %.3f to %.3f, A %.3f to %.3f (%d values)' % (what, min(v[0] for v in vals), max(v[0] for v in vals), min(v[1] for v in vals), max(v[1] for v in vals), len(vals)))
        top = sorted(x, key=lambda g: -aft(g)['B6'])[:3]
        y = [g for g in x if g not in top]
        say('     three games with most near turns removed: B %.3f, A %.3f (%d games)' % (pooled(y, 'B6'), pooled(y, 'A6'), len(y)))
        top = sorted(x, key=lambda g: -(aft(g)['turns'] - aft(g)['B6']))[:3]
        y = [g for g in x if g not in top]
        say('     three games with most far turns removed: B %.3f, A %.3f (%d games)' % (pooled(y, 'B6'), pooled(y, 'A6'), len(y)))
        say('     by band:', {b: '%d games B %.3f' % (len([g for g in x if g['band'] == b]), pooled([g for g in x if g['band'] == b], 'B6')) for b in BANDS})
        for g in x:
            a = aft(g)
            say('       %d %s %-20s %-26s %4d turns %3d A %.3f B %.3f B2 %.3f others %.1f short %.1f in area %.2f qdeath r%d final longest %d v %d total %d v %d alive %d v %d' % (
                g['game'], g['battle'], g['map_key'], g['opponent'], g['opponentElo'], a['turns'], a['A6'] / max(1, a['turns']), a['B6'] / max(1, a['turns']),
                a['B2'] / max(1, a['turns']), a['n_other'] / max(1, a['turns']), a['n_short'] / max(1, a['turns']), a['same'] / max(1, a['turns']),
                g['qdeath'][1 if g['final'][0]['queen'] > 0 else 0]['round'], g['final'][0]['longest'], g['final'][1]['longest'],
                g['final'][0]['total'], g['final'][1]['total'], g['final'][0]['alive'], g['final'][1]['alive']))
    fl, nf, mi = G42[code, 'flagged'], G42[code, 'not flagged'], G42[code, 'mirror']
    for nm, x1, x0 in (('flagged v not flagged', fl, nf), ('mirror v flagged', mi, fl), ('mirror v all only-theirs', mi, fl + nf)):
        for key in ('A6', 'B6'):
            if x1 and x0:
                obs, hit, B = permg(list(x1), list(x0), key)
                say('  %s, %s: gap %.3f, %d of %d game-label shuffles as large' % (nm, key, obs, hit, B))
    new = [g for g in fl + nf if int(g['battle']) > 1302921]
    say('  only-theirs-alive losses after battle 1302921: %d, flagged %d' % (len(new), sum(1 for g in new if group42(g) == 'flagged')))
    old = [g for g in fl if int(g['battle']) <= 1302921]
    say('  flagged up to battle 1302921: %d games, B %.3f; after: %d games, B %.3f' % (len(old), pooled(old, 'B6'), len(fl) - len(old), pooled([g for g in fl if int(g['battle']) > 1302921], 'B6')))
both_fl = G42['main', 'flagged'] + G42['v31', 'flagged']
both_nf = G42['main', 'not flagged'] + G42['v31', 'not flagged']
both_mi = G42['main', 'mirror'] + G42['v31', 'mirror']
say('')
say('both codes: flagged %d games A %.3f B %.3f; not flagged %d games A %.3f B %.3f; mirror %d games A %.3f B %.3f' % (
    len(both_fl), pooled(both_fl, 'A6'), pooled(both_fl, 'B6'), len(both_nf), pooled(both_nf, 'A6'), pooled(both_nf, 'B6'),
    len(both_mi), pooled(both_mi, 'A6'), pooled(both_mi, 'B6')))
for nm, x1, x0 in (('mirror v all only-theirs, both codes', both_mi, both_fl + both_nf), ('flagged v not flagged, both codes', both_fl, both_nf)):
    for key in ('A6', 'B6'):
        obs, hit, B = permg(list(x1), list(x0), key)
        say('  %s, %s: gap %.3f, %d of %d shuffles as large' % (nm, key, obs, hit, B))
# same measure in dead-end layouts, for the record
for code in ('main', 'v31'):
    x = [g for g in games if g['code'] == code and g['last_round'] == 499 and g['end_reason'] == 1 and g['dead_end']
         and (g['final'][0]['queen'] > 0) != (g['final'][1]['queen'] > 0)]
    say('  dead-end layouts,', code, ': one queen alive in', len(x), 'full games')

# ---------------------------------------------------------------- F7
say('')
say('=================== F7 ===================')


def ng(g, s, thr=6, R=100):
    if g['last_round'] >= R:
        return g['alive'][s][R] <= thr
    return g['final'][s]['alive'] == 0


for code in ('main', 'v31', 'other'):
    gs = [g for g in games if g['code'] == code and g['spawn_n'] == [2, 2]]
    say('')
    say('--', code, 'games on 2-start layouts:', len(gs), ' layouts:', dict(Counter(g['map_key'] for g in gs)))
    if not gs:
        continue
    say('   ended before r100:', [(g['game'], g['map_key'], g['last_round'], 'win' if g['win'] else 'loss') for g in gs if g['last_round'] < 100])
    o = [g for g in gs if ng(g, 0)]
    t = [g for g in gs if ng(g, 1)]
    say('  ours never grew:', fr(len(o), len(gs)), 'won', sum(1 for g in o if g['win']), '| theirs:', fr(len(t), len(gs)), '| both:', sum(1 for g in o if ng(g, 1)))
    onlyo = [g for g in o if not ng(g, 1)]
    botho = [g for g in o if ng(g, 1)]
    onlyt = [g for g in t if not ng(g, 0)]
    say('  won when only we never grew: %d of %d; when both: %d of %d; when only they never grew: %d of %d; when neither: %d of %d' % (
        sum(1 for g in onlyo if g['win']), len(onlyo), sum(1 for g in botho if g['win']), len(botho),
        sum(1 for g in onlyt if g['win']), len(onlyt), sum(1 for g in gs if g['win'] and not ng(g, 0) and not ng(g, 1)), sum(1 for g in gs if not ng(g, 0) and not ng(g, 1))))
    say('  per layout: ours / theirs / games | only ours, only theirs (sign test p) | won')
    for mk in sorted(set(g['map_key'] for g in gs), key=lambda k: -sum(1 for g in gs if g['map_key'] == k and ng(g, 0))):
        x = [g for g in gs if g['map_key'] == mk]
        a = sum(1 for g in x if ng(g, 0) and not ng(g, 1))
        b = sum(1 for g in x if ng(g, 1) and not ng(g, 0))
        n = a + b
        p = min(1.0, 2 * sum(math.comb(n, k) for k in range(0, min(a, b) + 1)) / 2 ** n) if n else 1.0
        al0 = sorted(at(g['alive'][0], 100) for g in x)
        al1 = sorted(at(g['alive'][1], 100) for g in x)
        say('    %-20s %2d / %2d / %2d | %2d, %2d (p %.3f) | won %d | median alive r100 %d v %d' % (mk, sum(1 for g in x if ng(g, 0)), sum(1 for g in x if ng(g, 1)), len(x), a, b, p,
            sum(1 for g in x if g['win']), al0[len(al0) // 2], al1[len(al1) // 2]))
    for b in ['under'] + BANDS:
        x = [g for g in gs if g['band'] == b]
        if x:
            say('  band %-9s ours %s | theirs %s | battles %d' % (b, fr(sum(1 for g in x if ng(g, 0)), len(x)), fr(sum(1 for g in x if ng(g, 1)), len(x)), len(set(g['battle'] for g in x))))
    for s, nm in ((1, 'theirs'), (0, 'ours')):
        obs, hit, B, nb = perm_battles(gs, lambda g: ng(g, s), '1700-1899', '2100+')
        say('  %s, 1700-1899 minus 2100+: gap %.3f, %d of %d battle shuffles as large (%d battles)' % (nm, obs, hit, B, nb))
        obs, hit, B, nb = perm_battles(gs, lambda g: ng(g, s), '1700-1899', '1900-2099')
        say('  %s, 1700-1899 minus 1900-2099: gap %.3f, %d of %d battle shuffles as large (%d battles)' % (nm, obs, hit, B, nb))
        obs, hit, B, nb = perm_battles(gs, lambda g: ng(g, s), '2100+', '1700-1899')
        say('  %s, 2100+ minus 1700-1899: gap %.3f, %d of %d battle shuffles as large' % (nm, obs, hit, B))
    nt = [g for g in gs if g['map'] not in ('Tower Defense', 'Stripes')]
    say('  without Tower Defense and Stripes: ours %s | theirs %s' % (fr(sum(1 for g in nt if ng(g, 0)), len(nt)), fr(sum(1 for g in nt if ng(g, 1)), len(nt))))
    for b in BANDS:
        x = [g for g in nt if g['band'] == b]
        if x:
            say('     band %-9s ours %d of %d | theirs %d of %d' % (b, sum(1 for g in x if ng(g, 0)), len(x), sum(1 for g in x if ng(g, 1)), len(x)))
    say('  layout mix per band (games):', {b: dict(Counter(g['map'] for g in gs if g['band'] == b)) for b in BANDS})
    say('  per layout and band, ours/theirs/games:')
    for mk in sorted(set(g['map_key'] for g in gs)):
        say('    %-20s' % mk, {b: '%d/%d/%d' % (sum(1 for g in gs if g['map_key'] == mk and g['band'] == b and ng(g, 0)), sum(1 for g in gs if g['map_key'] == mk and g['band'] == b and ng(g, 1)), sum(1 for g in gs if g['map_key'] == mk and g['band'] == b)) for b in BANDS})
    say('  halves, ours:', {h: '%d of %d (%d won)' % (sum(1 for g in gs if g.get('half') == h and ng(g, 0)), sum(1 for g in gs if g.get('half') == h), sum(1 for g in gs if g.get('half') == h and ng(g, 0) and g['win'])) for h in (1, 2)},
        'theirs:', {h: '%d of %d' % (sum(1 for g in gs if g.get('half') == h and ng(g, 1)), sum(1 for g in gs if g.get('half') == h)) for h in (1, 2)})
    say('  by day, ours/theirs/games:', {d: '%d/%d/%d' % (sum(1 for g in gs if g['day'] == d and ng(g, 0)), sum(1 for g in gs if g['day'] == d and ng(g, 1)), sum(1 for g in gs if g['day'] == d)) for d in sorted(set(g['day'] for g in gs))})
    say('  thresholds (ours / theirs of %d):' % len(gs))
    for R in (60, 80, 100, 120, 150):
        say('    r%d:' % R, {thr: '%d / %d' % (sum(1 for g in gs if ng(g, 0, thr, R)), sum(1 for g in gs if ng(g, 1, thr, R))) for thr in (3, 4, 6, 8, 10)})
    say('  thresholds without Tower Defense and Stripes (ours / theirs of %d):' % len(nt))
    for R in (80, 100, 120):
        say('    r%d:' % R, {thr: '%d / %d' % (sum(1 for g in nt if ng(g, 0, thr, R)), sum(1 for g in nt if ng(g, 1, thr, R))) for thr in (3, 4, 6, 8, 10)})
    opp = Counter(g['opponent'] for g in gs)
    res = []
    for o2 in opp:
        y = [g for g in gs if g['opponent'] != o2]
        res.append((sum(1 for g in y if ng(g, 0)) / len(y), sum(1 for g in y if ng(g, 1)) / len(y)))
    say('  one opponent left out (%d opponents, largest %s): ours %.3f to %.3f, theirs %.3f to %.3f' % (len(opp), opp.most_common(1), min(r[0] for r in res), max(r[0] for r in res), min(r[1] for r in res), max(r[1] for r in res)))
    say('  2100+ opponents (games, ours, theirs):', {o2: '%d, %d, %d' % (sum(1 for g in gs if g['opponent'] == o2 and g['band'] == '2100+'), sum(1 for g in gs if g['opponent'] == o2 and g['band'] == '2100+' and ng(g, 0)), sum(1 for g in gs if g['opponent'] == o2 and g['band'] == '2100+' and ng(g, 1))) for o2 in sorted(set(g['opponent'] for g in gs if g['band'] == '2100+'))})
    say('  our pearls r0-100 in our never-grew games, median: %s ; theirs in theirs: %s' % (
        sorted(at(g['eaten'][0], 100) for g in o)[len(o) // 2] if o else '-', sorted(at(g['eaten'][1], 100) for g in t)[len(t) // 2] if t else '-'))
# other layouts: how often is a side at 6 or fewer at r100
for code in ('main', 'v31'):
    gs = [g for g in games if g['code'] == code and g['spawn_n'] != [2, 2]]
    say('  %s other layouts: ours %d, theirs %d of %d' % (code, sum(1 for g in gs if ng(g, 0)), sum(1 for g in gs if ng(g, 1)), len(gs)))

# ---------------------------------------------------------------- compare with rows.jsonl
say('')
say('=================== compare with rows.jsonl ===================')
rows = {}
for line in Path('data/analysis/ladder/rows.jsonl').read_text().splitlines():
    if line.strip():
        r = json.loads(line)
        rows[r['game']] = r
say('rows', len(rows), 'mine', len(games), 'in both', sum(1 for g in games if g['game'] in rows))
bad = Counter()
CAUSE = {'wall': 0, 'own body': 1, 'other dragon body': 2, 'head-on': 3, 'other': 4}
for g in games:
    r = rows.get(g['game'])
    if r is None:
        bad['missing row'] += 1
        continue
    code = r['our_code'] if r['our_code'] in ('main', 'v31') else 'other'
    if code != g['code']:
        bad['code'] += 1
    if r['map_key'] != g['map_key']:
        bad['map_key'] += 1
    if r['last_round'] != g['last_round']:
        bad['last_round'] += 1
    if (r['ended_by'] == 'elimination') != (g['end_reason'] == 0):
        bad['ended_by'] += 1
    if r['win'] != g['win']:
        bad['win'] += 1
    if r['opponent_rating'] != g.get('opponentElo'):
        bad['rating'] += 1
    for s, nm in ((0, 'us'), (1, 'them')):
        f = r['final'][nm]
        if (f['alive'], f['longest'], f['total'], f['queen_length']) != (g['final'][s]['alive'], g['final'][s]['longest'], g['final'][s]['total'], g['final'][s]['queen']):
            bad['final'] += 1
        for key in ('50', '100'):
            c = r['curves'][key]
            if c is None:
                if g['last_round'] >= int(key):
                    bad['curve missing'] += 1
                continue
            if c[nm]['alive'] != g['alive'][s][int(key)]:
                bad['alive r' + key] += 1
            if c[nm]['pearls'] != g['eaten'][s][int(key)]:
                bad['pearls r' + key] += 1
            if c[nm]['total'] != g['total'][s][int(key)]:
                bad['total r' + key] += 1
        q = r['queen'][nm]
        mine = g['qdeath'][s]
        if (q['death_round'] is None) != (mine is None):
            bad['queen death'] += 1
        elif mine is not None:
            if q['death_round'] != mine['round'] or CAUSE[q['death_cause']] != mine['reason'] or q['death_length'] != mine['length']:
                bad['queen death detail'] += 1
            if mine['reason'] == 3 and q['head_on'] is not None:
                side = q['head_on']['attacker_side']
                want = 'us' if mine['mover_side'] == 0 else 'them'
                if side != want:
                    bad['queen head-on mover (%s v %s)' % (side, want)] += 1
        d = r['deaths']['r0-100'][nm]
        if [d['wall'], d['own body'], d['other dragon body'], d['head-on'], d['other']] != g['dw'][s][0]:
            bad['deaths r0-100'] += 1
    m = maps.get(g['map_key'])
    if m and (m['dragons_at_spawn'] != g['spawn_n'][0] or m['queen_spawn_distance'] != g['qdist']):
        bad['map spawn count or distance'] += 1
say('disagreements:', dict(bad) if bad else 'none')
open(P + 'c13-numbers.txt', 'w').write('\n'.join(OUT) + '\n')
print('lines', len(OUT))
