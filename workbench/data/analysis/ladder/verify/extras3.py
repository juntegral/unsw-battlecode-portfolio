#!/usr/bin/env python3
"""Verifier extra checks for the 04:25 queue, from x3-*.jsonl (extract3.py) and, for F20 only, the real pearl
gaps of Around UNSW and Australia read from the local replays that maps.json names as their source.
Usage: python3 extras3.py"""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path('../battlecode').resolve()))
import replay
V = Path('data/analysis/ladder/verify')
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
LINES = []
DEAD = ('Schooltime', 'Slithery Fight')


def out(*a):
    s = ' '.join(str(x) for x in a)
    print(s)
    LINES.append(s)


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


def binom_tail(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


games = []
for k in range(6):
    for line in (V / ('x3-%d.jsonl' % k)).read_text().splitlines():
        games.append(json.loads(line))
games = [g for g in games if 'error' not in g and g['code'] in ('main', 'v31')]
games.sort(key=lambda g: (g['completedAt'], g['game']))
seen = {}
for g in games:
    lst = seen.setdefault(g['map'], [])
    if g['layout'] not in lst:
        lst.append(g['layout'])
    g['map_key'] = '%s #%d' % (g['map'], lst.index(g['layout']) + 1)
    e = g['opponentElo']
    g['band'] = '<1700' if e < 1700 else '1700-1899' if e < 1900 else '1900-2099' if e < 2100 else '2100+'

out('##### F13 extras')
for code in ('main', 'v31'):
    gs = [g for g in games if g['code'] == code and g['map'] not in DEAD]
    res = {}
    for vs in ('us', 'them'):
        rams = [r for g in gs for r in g['rams'] if r['cross'] and r['other_queen_dead'] and r['side'] == vs]
        board = [r for r in rams if r.get('born_later') is False]
        nb = len(board)
        m1 = sum(1 for r in board if any(d > r['free'] + r['L0'] - 1 for d in r['legal_d']))
        m2 = sum(1 for r in board if any(d > r['free'] + r['L0'] for d in r['legal_d']))
        took = sum(1 for r in board if r['esc_free'] and r['d_ram'] > r['free'])
        missed = sum(1 for r in board if r['esc_free'] and r['d_ram'] <= r['free'])
        nomove = sum(1 for r in board if not r['moved'])
        res[vs] = (len(rams), sum(1 for r in rams if r['friends'] < 2), nb, sum(1 for r in board if r['esc_free']), sum(1 for r in board if r['esc_actual']))
        out('%s %s queen: with board %d; step beyond free steps %d = she took such a step and was rammed anyway %d + she ended inside the free reach though another step led out %d' % (
            code, 'OUR' if vs == 'us' else 'THEIR', nb, took + missed, took, missed))
        out('    a legal step beyond free + length - 1 (all the rammer could pay for and live): %s; beyond free + length: %s; queen did not move on her last turn: %d' % (rt(m1, nb), rt(m2, nb), nomove))
        lt = [sum(g['lone'][vs][j] for g in gs) for j in range(3)]
        base = lt[1] / lt[0]
        k = sum(1 for r in rams if r['friends'] < 2)
        out('    alone at the ram %d of %d against %.3f of her turns in that state: binomial upper tail p %.5f' % (k, len(rams), base, binom_tail(k, len(rams), base)))
        byq = Counter()
        for r in board:
            byq[(r['qlen'] <= 3, r['esc_actual'])] += 1
        out('    escape beyond actual ram, queen length 3 or less: %s; queen longer: %s' % (
            rt(byq[(True, True)], byq[(True, True)] + byq[(True, False)]), rt(byq[(False, True)], byq[(False, True)] + byq[(False, False)])))
    a, b = res['us'], res['them']
    out('%s ours against theirs: alone %d of %d vs %d of %d, Fisher p %.3f; step beyond free %d of %d vs %d of %d, p %.3f; beyond actual %d of %d vs %d of %d, p %.3f' % (
        code, a[1], a[0], b[1], b[0], fisher(a[1], a[0] - a[1], b[1], b[0] - b[1]),
        a[3], a[2], b[3], b[2], fisher(a[3], a[2] - a[3], b[3], b[2] - b[3]),
        a[4], a[2], b[4], b[2], fisher(a[4], a[2] - a[4], b[4], b[2] - b[4])))
ma = [r for g in games if g['code'] == 'main' and g['map'] not in DEAD for r in g['rams'] if r['cross'] and r['other_queen_dead'] and r['side'] == 'us' and r.get('born_later') is False]
va = [r for g in games if g['code'] == 'v31' and g['map'] not in DEAD for r in g['rams'] if r['cross'] and r['other_queen_dead'] and r['side'] == 'us' and r.get('born_later') is False]
out('main against v31, our queen: step beyond free %d of %d vs %d of %d, Fisher p %.3f; beyond actual %d of %d vs %d of %d, p %.3f' % (
    sum(1 for r in ma if r['esc_free']), len(ma), sum(1 for r in va if r['esc_free']), len(va),
    fisher(sum(1 for r in ma if r['esc_free']), sum(1 for r in ma if not r['esc_free']), sum(1 for r in va if r['esc_free']), sum(1 for r in va if not r['esc_free'])),
    sum(1 for r in ma if r['esc_actual']), len(ma), sum(1 for r in va if r['esc_actual']), len(va),
    fisher(sum(1 for r in ma if r['esc_actual']), sum(1 for r in ma if not r['esc_actual']), sum(1 for r in va if r['esc_actual']), sum(1 for r in va if not r['esc_actual']))))
open(P + 'f13-0425-extras.txt', 'w').write('\n'.join(LINES) + '\n')
LINES.clear()

out('##### F18 extras')
REASON = ('wall', 'own body', 'other body', 'head-on', 'no action')
for code in ('main', 'v31'):
    st = [g for g in games if g['code'] == code and g['map'] == 'Stripes']
    for s in ('us', 'them'):
        why = Counter()
        gap = Counter()
        took = 0
        same_turn = 0
        for g in st:
            for r, a, sd, L, tiles, passed, died, isq, pocket, via in g['f18rows']:
                if sd != s or not pocket or via != 'P' or passed:
                    continue
                took += 1
                same_turn += died
                dd = g['death_by_id'].get(str(a))
                if dd is not None and dd[0] - r <= 10:
                    why[REASON[dd[1]]] += 1
                    gap[dd[0] - r] += 1
        out('%s Stripes %s: took a pocket pearl through a portal %d times; dead within 10 rounds %d, by cause %s; rounds until death %s; died in that same turn %d' % (
            code, s, took, sum(why.values()), dict(why), sorted(gap.items()), same_turn))
    for lab, sub in (('games won', [g for g in st if g['win']]), ('games lost', [g for g in st if not g['win']]),
                     ('opponents under 1900', [g for g in st if g['opponentElo'] < 1900]), ('opponents 1900 or more', [g for g in st if g['opponentElo'] >= 1900])):
        c = dict(us=[0, 0], them=[0, 0])
        for g in sub:
            for key, n in g['f18'].items():
                sd, rb, pocket, via, passed = key.split('|')
                if pocket == '1' and via == 'P':
                    c[sd][1] += n
                    if passed == '1':
                        c[sd][0] += n
        out('%s Stripes pocket via portal r0-199, %s (%d games): ours %s, theirs %s' % (code, lab, len(sub), rt(c['us'][0], c['us'][1]), rt(c['them'][0], c['them'][1])))
    # pearls eaten in r0-199 is not in the extraction; chances per game instead
    tot = dict(us=0, them=0)
    for g in st:
        for key, n in g['f18'].items():
            sd, rb, pocket, via, passed = key.split('|')
            tot[sd] += n
    out('%s Stripes: all chances r0-199 ours %d, theirs %d in %d games' % (code, tot['us'], tot['them'], len(st)))
open(P + 'f18-extras.txt', 'w').write('\n'.join(LINES) + '\n')
LINES.clear()

out('##### F11 extras')


def stats(gs):
    c = dict(o=[0, 0, 0], t=[0, 0, 0])
    for g in gs:
        for key, n in g['near'].items():
            du, dt, bal, rw, eater = [int(x) for x in key.split(',')]
            if du == dt:
                continue
            k = 'o' if du < dt else 't'
            c[k][0 if eater == 1 else 1 if eater == 2 else 2] += n
    on, tn = sum(c['o']), sum(c['t'])
    if not on or not tn or not (c['o'][0] + c['o'][1]) or not (c['t'][0] + c['t'][1]):
        return None
    return on / (on + tn), c['t'][1] / (c['t'][0] + c['t'][1]) - c['o'][0] / (c['o'][0] + c['o'][1])


def boot2(gs, idx, n=1000, seed=3):
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        v = stats([gs[rng.randrange(len(gs))] for _ in range(len(gs))])
        if v is not None:
            vals.append(v[idx])
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]


for code in ('main', 'v31'):
    allg = [g for g in games if g['code'] == code]
    large = [g for g in allg if g['open_tiles'] >= 2000]
    for bd in ('1700-1899', '1900-2099'):
        sub = [g for g in large if g['band'] == bd]
        v = stats(sub)
        lo1, hi1 = boot2(sub, 0)
        lo2, hi2 = boot2(sub, 1)
        out('%s large %s (%d games): our nearer share %.3f (game bootstrap 95%% %.3f to %.3f); eating gap %.3f (%.3f to %.3f)' % (code, bd, len(sub), v[0], lo1, hi1, v[1], lo2, hi2))
    for mk in sorted(set(g['map_key'] for g in large)):
        sub = [g for g in large if g['map_key'] == mk]
        v = stats(sub)
        lo1, hi1 = boot2(sub, 0)
        lo2, hi2 = boot2(sub, 1)
        out('%s %s (%d games): our nearer share %.3f (%.3f to %.3f); eating gap %.3f (%.3f to %.3f)' % (code, mk, len(sub), v[0], lo1, hi1, v[1], lo2, hi2))
    lays = sorted(set(g['map_key'] for g in allg))
    big5 = set(g['map_key'] for g in large)
    for idx, name in ((0, 'our nearer share (low is the claim)'), (1, 'eating gap (high is the claim)')):
        vals = []
        for mk in lays:
            v = stats([g for g in allg if g['map_key'] == mk])
            if v is not None:
                vals.append((v[idx] if idx == 0 else -v[idx], mk))
        vals.sort()
        ranks = [i + 1 for i, (v, mk) in enumerate(vals) if mk in big5]
        tot = sum(ranks)
        n = len(vals)
        hit = sum(1 for cmb in combinations(range(1, n + 1), len(ranks)) if sum(cmb) <= tot)
        out('%s layout level, %s: the large five rank %s of %d; five layouts at random have a rank sum this extreme in %d of %d draws (%.4f)' % (
            code, name, ranks, n, hit, math.comb(n, len(ranks)), hit / math.comb(n, len(ranks))))
open(P + 'f11-0425-extras.txt', 'w').write('\n'.join(LINES) + '\n')
LINES.clear()

out('##### F20 extras')
maps = json.loads(Path('data/analysis/ladder/maps.json').read_text())


def near_set(W, H, tiles, radius):
    s = set()
    for ci in tiles:
        x, y = ci % W, ci // W
        for dx in range(-radius, radius + 1):
            for dy in range(-(radius - abs(dx)), radius - abs(dx) + 1):
                s.add(((y + dy) % H) * W + (x + dx) % W)
    return s


def pooled(gs, busy_of, radius=2):
    n = nu = nt = au = at = 0
    for g in gs:
        W, H = g['W'], g['H']
        ns = near_set(W, H, busy_of(g), radius)
        for r, sn in g['snaps'].items():
            a, b = len(sn['us']), len(sn['them'])
            if a < 1 or b < 1 or a > 1.1 * b or b > 1.1 * a:
                continue
            n += 1
            nu += a
            nt += b
            au += sum(1 for h in sn['us'] if h[1] * W + h[0] in ns)
            at += sum(1 for h in sn['them'] if h[1] * W + h[0] in ns)
    return n, nu, nt, au, at


def show(label, gs, busy_of, radius=2):
    n, nu, nt, au, at = pooled(gs, busy_of, radius)
    if not n:
        out('  %-70s no snapshots' % label)
        return
    out('  %-70s snapshots %3d  our share %.3f  their share %.3f' % (label, n, au / nu, at / nt))


bigs = [g for g in games if g['open_tiles'] >= 1500]
lay_n = Counter(g['map_key'] for g in bigs)
lay_busy = defaultdict(Counter)
for g in bigs:
    for ci, v in g['tiles'].items():
        if v[0] >= 8:
            lay_busy[g['map_key']][int(ci)] += 1


def elsewhere(frac):
    def fn(g):
        own = set(int(ci) for ci, v in g['tiles'].items() if v[0] >= 8)
        m = lay_n[g['map_key']] - 1
        return [ci for ci, k in lay_busy[g['map_key']].items() if m > 0 and (k - (1 if ci in own else 0)) >= frac * m]
    return fn


real = {}
for mk in ('Around UNSW #1', 'Australia #1'):
    src = maps[mk].get('source')
    root = replay.load(Path(src)).root()
    W = H = None
    fast = []
    slow = []
    for ln in root.text(0).splitlines():
        q = ln.split()
        if not q:
            continue
        if q[0] == 'MAP':
            W, H = int(q[1]), int(q[2])
        elif q[0] == 'TILE':
            x, y, lo, hi = int(q[1]), int(q[2]), int(q[3]), int(q[4])
            if 1 <= hi <= 12:
                fast.append(y * W + x)
            elif hi > 12:
                slow.append(y * W + x)
    real[mk] = (W, H, fast, slow)
    sub = [g for g in bigs if g['map_key'] == mk]
    off = sum(v[0] for g in sub for ci, v in g['tiles'].items() if int(ci) not in set(fast) and int(ci) not in set(slow))
    allb = sum(v[0] for g in sub for ci, v in g['tiles'].items())
    onfast = sum(v[0] for g in sub for ci, v in g['tiles'].items() if int(ci) in set(fast))
    out('%s: local file %dx%d, real fast tiles (gap up to 12) %d, slower pearl tiles %d; natural births in our %d games: %d, on tiles the file says never spawn: %d, on real fast tiles: %d (%.3f)' % (
        mk, W, H, len(fast), len(slow), len(sub), allb, off, onfast, onfast / allb))
for code in ('main', 'v31'):
    gs = [g for g in bigs if g['code'] == code]
    out('=== %s' % code)
    show('busy in this game (the claim)', gs, lambda g: [int(ci) for ci, v in g['tiles'].items() if v[0] >= 8])
    for frac in (0.25, 0.5, 0.75):
        show('busy (8+) in at least %d percent of the other games on the layout' % int(100 * frac), gs, elsewhere(frac))
    for name in ('Around UNSW', 'Slithery Fight'):
        sub = [g for g in gs if g['map'] == name]
        show(name + ': busy in this game', sub, lambda g: [int(ci) for ci, v in g['tiles'].items() if v[0] >= 8])
        for frac in (0.25, 0.5, 0.75):
            show(name + ': busy in at least %d percent of the other games' % int(100 * frac), sub, elsewhere(frac))
    for mk in ('Around UNSW #1', 'Australia #1'):
        sub = [g for g in gs if g['map_key'] == mk]
        for rad in (1, 2, 3):
            show('%s: within %d of a REAL fast tile (map property)' % (mk, rad), sub, lambda g: real[g['map_key']][2], rad)
        show('%s: within 2 of a slower pearl tile' % mk, sub, lambda g: real[g['map_key']][3], 2)
        fs = set(real[mk][2])
        eu = sum(v[1] for g in sub for ci, v in g['tiles'].items() if int(ci) in fs)
        et = sum(v[2] for g in sub for ci, v in g['tiles'].items() if int(ci) in fs)
        eu2 = sum(v[1] for g in sub for ci, v in g['tiles'].items() if int(ci) not in fs)
        et2 = sum(v[2] for g in sub for ci, v in g['tiles'].items() if int(ci) not in fs)
        out('  %s: natural pearls eaten on real fast tiles: ours %d, theirs %d (our share %.3f); on the other tiles: ours %d, theirs %d (our share %.3f)' % (
            mk, eu, et, eu / (eu + et), eu2, et2, eu2 / (eu2 + et2)))
open(P + 'f20-extras.txt', 'w').write('\n'.join(LINES) + '\n')
