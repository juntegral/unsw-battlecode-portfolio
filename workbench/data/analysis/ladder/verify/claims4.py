#!/usr/bin/env python3
"""Verifier counts for the 05:20 queue (F23 queens in small rooms on Portals, F24 queen rammed by opponent rating,
F20 heads near busy tiles by band / early rounds / cost, F13 a safe step against the full reach) from x4-*.jsonl
written by extract4.py. Usage: python3 claims4.py <F23|F24|F20|F13|CHECK>"""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
from statistics import median, mean
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
LINES = []
DEAD = ('Schooltime', 'Slithery Fight')
BANDS = ('<1700', '1700-1899', '1900-2099', '2100+')


def out(*a):
    s = ' '.join(str(x) for x in a)
    print(s)
    LINES.append(s)


def load():
    games = []
    for k in range(6):
        for line in (V / ('x4-%d.jsonl' % k)).read_text().splitlines():
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


def fisher(a, b, c, d):
    n = a + b + c + d
    r1 = a + b
    c1 = a + c

    def pr(x):
        return math.comb(r1, x) * math.comb(n - r1, c1 - x) / math.comb(n, c1)
    p0 = pr(a)
    return sum(pr(x) for x in range(max(0, c1 - (n - r1)), min(r1, c1) + 1) if pr(x) <= p0 * (1 + 1e-9))


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


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def pearson(a, b):
    n = len(a)
    if n < 3:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    sa = sum((x - ma) ** 2 for x in a)
    sb = sum((y - mb) ** 2 for y in b)
    if sa == 0 or sb == 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(sa * sb)


def spearman(a, b):
    return pearson(ranks(a), ranks(b))


def sp(a, b, n=4000, seed=3):
    rho = spearman(a, b)
    if rho is None:
        return 'n/a (%d games)' % len(a)
    rng = random.Random(seed)
    ra, rb = ranks(a), ranks(b)
    hit = 0
    rb2 = list(rb)
    for _ in range(n):
        rng.shuffle(rb2)
        v = pearson(ra, rb2)
        if v is not None and abs(v) >= abs(rho) - 1e-12:
            hit += 1
    return '%+.2f on %d games (shuffles reaching it: %d of %d)' % (rho, len(a), hit, n)


# ---------------------------------------------------------------- F23
def cause(d):
    if d is None:
        return 'alive'
    r = d['reason']
    if r == 0:
        return 'wall'
    if r == 1:
        return 'own body'
    if r == 2:
        return 'body of own dragon' if d['hit'] == 'own' else 'body of enemy dragon' if d['hit'] == 'enemy' else 'other body (%s)' % d['hit']
    if r == 3:
        return 'head-on as mover' if d['is_actor'] else 'head-on as standing victim'
    return 'no valid action'


def qsum(gs, s):
    died = [g for g in gs if g['qs'][s]['death']]
    rooms = Counter(g['qs'][s]['death']['room'] for g in died)
    return dict(games=len(gs), died=len(died), rooms=sorted(rooms.items()),
                le6=sum(1 for g in died if g['qs'][s]['death']['room'] <= 6),
                portal=sum(1 for g in gs if g['qs'][s]['portal_steps']),
                first_small=sorted(Counter(str(g['qs'][s]['first_small']) for g in gs).items()),
                causes=sorted(Counter(cause(g['qs'][s]['death']) for g in died).items()),
                rounds=sorted(g['qs'][s]['death']['round'] for g in died),
                r9_10=sum(1 for g in died if g['qs'][s]['death']['round'] in (9, 10)),
                small_turns=sum(g['qs'][s]['turns_small'] for g in gs), turns=sum(g['qs'][s]['turns'] for g in gs),
                alive_end=sum(1 for g in gs if g['q_alive_end'][s]),
                ever_small=sum(1 for g in gs if g['qs'][s]['first_small'] is not None),
                ever_small_died_small=sum(1 for g in died if g['qs'][s]['death']['room'] <= 6))


def f23(games):
    for code in ('main', 'v31'):
        named = [g for g in games if g['code'] == code and g['map'] == 'Portals']
        gs = [g for g in named if g['map_key'] == 'Portals #1']
        out('')
        out('=== %s: %d games named Portals, %d on Portals #1' % (code, len(named), len(gs)))
        if not gs:
            continue
        g0 = gs[0]
        out('  board %dx%d, open tiles %d, portal pairs %d; rooms of 6 or fewer (size, how many): %s; largest rooms: %s' % (
            g0['W'], g0['H'], g0['open_tiles'], g0['portals'], g0['rooms_le_6'], g0['rooms_top']))
        out('  queen start length %s, room of her start tile %s' % (sorted(Counter(g['q_len0']['us'] for g in gs).items()),
                                                                 sorted(Counter(g['q_room0']['us'] for g in gs).items())))
        for s, label in (('us', 'OUR queen'), ('them', 'THEIR queen')):
            q = qsum(gs, s)
            out('  --- %s' % label)
            out('    died %d of %d; alive at the end %d' % (q['died'], q['games'], q['alive_end']))
            out('    room size at death (size, deaths): %s; in a room of 6 or fewer: %s' % (q['rooms'], ws(q['le6'], q['games'])))
            out('    games with a portal step before death: %d of %d' % (q['portal'], q['games']))
            out('    first raw round with a turn start in a room of 6 or fewer (round, games): %s' % q['first_small'])
            out('    causes: %s' % q['causes'])
            out('    death rounds: %s; at round 9 or 10: %d' % (q['rounds'], q['r9_10']))
            out('    turn starts in rooms of 6 or fewer: %d of %d = %.3f' % (q['small_turns'], q['turns'], q['small_turns'] / max(1, q['turns'])))
            out('    ever started a turn in a small room: %d games; of those died in a small room: %d' % (q['ever_small'], q['ever_small_died_small']))
            ps = [g for g in gs if g['qs'][s]['portal_steps']]
            out('    of the %d with a portal step: died in a small room %d, died elsewhere %d, alive at the end %d; first portal step rounds %s' % (
                len(ps), sum(1 for g in ps if g['qs'][s]['death'] and g['qs'][s]['death']['room'] <= 6),
                sum(1 for g in ps if g['qs'][s]['death'] and g['qs'][s]['death']['room'] > 6),
                sum(1 for g in ps if g['q_alive_end'][s]), sorted(Counter(g['qs'][s]['portal_steps'][0] for g in ps).items())))
            out('    queen length at death (length, deaths): %s' % sorted(Counter(g['qs'][s]['death']['length'] for g in gs if g['qs'][s]['death']).items()))
            out('    tile of death (x,y: deaths): %s' % sorted(Counter('%d,%d' % (g['qs'][s]['death']['x'], g['qs'][s]['death']['y']) for g in gs if g['qs'][s]['death']).items()))
        won = sum(1 for g in gs if g['win'])
        lost_q = sum(1 for g in gs if not g['win'] and not g['q_alive_end']['us'] and g['q_alive_end']['them'])
        out('  won %d of %d; lost with only their queen alive %d; lost otherwise %d; drawn %d' % (
            won, len(gs), lost_q, sum(1 for g in gs if not g['win'] and not g['drawn']) - lost_q, sum(1 for g in gs if g['drawn'])))
        out('  end reason (0 elimination, 1 rounds used up): %s' % sorted(Counter(g['end_reason'] for g in gs).items()))
        a = sum(1 for g in gs if g['qs']['us']['death'] and g['qs']['us']['death']['room'] <= 6)
        b = sum(1 for g in gs if g['qs']['them']['death'] and g['qs']['them']['death']['room'] <= 6)
        out('  [chance] died in a small room, ours %d against theirs %d of %d: Fisher p %.5f' % (a, b, len(gs), fisher(a, len(gs) - a, b, len(gs) - b)))
        a = sum(1 for g in gs if g['qs']['us']['portal_steps'])
        b = sum(1 for g in gs if g['qs']['them']['portal_steps'])
        out('  [chance] portal step, ours %d against theirs %d of %d: Fisher p %.5f' % (a, b, len(gs), fisher(a, len(gs) - a, b, len(gs) - b)))
        out('  [spread] opponents: %s' % sorted(Counter(g['opp'] for g in gs).items(), key=lambda kv: -kv[1]))
        out('  [spread] evenings: %s; bands: %s; our side: %s' % (sorted(Counter(g['evening'] for g in gs).items()),
                                                                  sorted(Counter(g['band'] for g in gs).items()), sorted(Counter(g['our_side'] for g in gs).items())))
        early = [g for g in gs if g['qs']['us']['death'] and g['qs']['us']['death']['round'] <= 10]
        late = [g for g in gs if g not in early]
        out('  [result] our queen dead by round 10: won %d of %d; later or never: won %d of %d' % (
            sum(1 for g in early if g['win']), len(early), sum(1 for g in late if g['win']), len(late)))
        tq = [g for g in gs if g['qs']['them']['death'] and g['qs']['them']['death']['room'] <= 6]
        out('  [result] their queen died in a small room: we won %d of %d; otherwise %d of %d' % (
            sum(1 for g in tq if g['win']), len(tq), sum(1 for g in gs if g not in tq and g['win']), len(gs) - len(tq)))
        out('  [per game] game, opponent rating, result, then per queen: room changes at her turn starts (round:room size:length), death')
        for g in gs:
            parts = []
            for s in ('us', 'them'):
                q = g['qs'][s]
                tr = ' '.join('%d:%d:%d' % (a2, b2, c2) for a2, b2, c2 in q['track'][:7])
                d = q['death']
                parts.append('%s [%s]%s %s' % (s, tr, ' ...' if len(q['track']) > 7 else '',
                                               'alive' if d is None else 'died r%d room %d len %d %s' % (d['round'], d['room'], d['length'], cause(d))))
            out('    %d %s %s %s | %s | %s' % (g['game'], g['opponentElo'], 'W' if g['win'] else 'L', g['evening'], parts[0], parts[1]))
    out('')
    out('=== contrast: Stripes')
    for code in ('main', 'v31'):
        gs = [g for g in games if g['code'] == code and g['map'] == 'Stripes']
        for s in ('us', 'them'):
            q = qsum(gs, s)
            out('  %s %s queen: %d games (%s), died %d, in a room of 6 or fewer %d; rooms at death %s; portal step in %d; small-room turn starts %d of %d' % (
                code, s, len(gs), sorted(Counter(g['map_key'] for g in gs).items()), q['died'], q['le6'], q['rooms'], q['portal'], q['small_turns'], q['turns']))
    out('')
    out('=== queen portal steps in raw rounds 0-100, portal layouts other than Portals and Stripes')
    for code in ('main', 'v31'):
        gs = [g for g in games if g['code'] == code and g['portals'] > 0 and g['map'] not in ('Portals', 'Stripes')]
        for s in ('us', 'them'):
            st = sum(sum(1 for r in g['qs'][s]['portal_steps'] if r <= 100) for g in gs)
            tn = sum(g['qs'][s]['turns_r100'] for g in gs)
            out('  %s %s: %d steps in %d queen turns (%d games)' % (code, s, st, tn, len(gs)))
            per = defaultdict(lambda: [0, 0, 0])
            for g in gs:
                c = per[g['map_key']]
                c[0] += 1
                c[1] += sum(1 for r in g['qs'][s]['portal_steps'] if r <= 100)
                c[2] += g['qs'][s]['turns_r100']
            out('     by layout (games, steps, turns): %s' % sorted((k, v) for k, v in per.items()))
    out('')
    out('=== all layouts: games in which a queen starts a turn in a room of 6 or fewer, and dies in one')
    for code in ('main', 'v31'):
        per = defaultdict(lambda: [0, 0, 0, 0, 0])
        for g in games:
            if g['code'] != code:
                continue
            c = per[g['map_key']]
            c[0] += 1
            for z, s in enumerate(('us', 'them')):
                q = g['qs'][s]
                if q['first_small'] is not None:
                    c[1 + 2 * z] += 1
                if q['death'] and q['death']['room'] <= 6:
                    c[2 + 2 * z] += 1
        out('  %s (layout: games, ours ever in, ours died in, theirs ever in, theirs died in): %s' % (
            code, sorted((k, v) for k, v in per.items() if v[1] or v[3])))


# ---------------------------------------------------------------- F24
def rammed(g, s, cross_only=False):
    d = g['qs'][s]['death']
    if not d or d['reason'] != 3 or d['is_actor']:
        return False
    if cross_only:
        return any(r['side'] == s and r['cross'] for r in g['rams'])
    return True


def first_dead(g):
    a, b = g['qs']['us']['death'], g['qs']['them']['death']
    if a is None and b is None:
        return None
    if b is None:
        return 'us'
    if a is None:
        return 'them'
    return 'us' if a['ei'] < b['ei'] else 'them'


def perm_trend(gs, fn, n=4000, seed=11):
    """Opponent ratings shuffled between battles (a battle keeps its games). Statistics: rate at 2100+ minus rate
    at 1700-1899, and the covariance of rating with the outcome over games."""
    bt = defaultdict(list)
    elo = {}
    for g in gs:
        bt[g['battle']].append(1 if fn(g) else 0)
        elo[g['battle']] = g['opponentElo']
    keys = sorted(bt)

    def stats(es):
        lo = [0, 0]
        hi = [0, 0]
        sx = sy = sxy = nn = 0
        for kk, e in zip(keys, es):
            ys = bt[kk]
            if 1700 <= e < 1900:
                lo[0] += sum(ys)
                lo[1] += len(ys)
            elif e >= 2100:
                hi[0] += sum(ys)
                hi[1] += len(ys)
            sx += e * len(ys)
            sy += sum(ys)
            sxy += e * sum(ys)
            nn += len(ys)
        d = (hi[0] / hi[1] - lo[0] / lo[1]) if hi[1] and lo[1] else 0.0
        return d, sxy / nn - (sx / nn) * (sy / nn)
    es = [elo[kk] for kk in keys]
    d0, c0 = stats(es)
    rng = random.Random(seed)
    hd = hc = 0
    for _ in range(n):
        rng.shuffle(es)
        d, c = stats(es)
        if d >= d0 - 1e-12:
            hd += 1
        if c >= c0 - 1e-12:
            hc += 1
    return 'top band minus 1700-1899: %+.3f, shuffles reaching it %d of %d; rating covariance: shuffles reaching it %d of %d; %d battles' % (d0, hd, n, hc, n, len(keys))


def f24(games):
    for code in ('main', 'v31'):
        allg = [g for g in games if g['code'] == code]
        gs = [g for g in allg if g['map'] not in DEAD]
        out('')
        out('=== %s: %d games, %d on layouts where the queen can leave spawn' % (code, len(allg), len(gs)))
        out('  band: games | our queen rammed (any mover) | by an enemy | their queen rammed (any) | by ours | our queen alive at end | theirs alive | ours died first / theirs first / neither died')
        for band in BANDS + ('all',):
            bg = [g for g in gs if band == 'all' or g['band'] == band]
            if not bg:
                continue
            n = len(bg)
            fd = Counter(first_dead(g) for g in bg)
            out('  %-10s %4d | %s | %d | %d of %d = %.3f | %d | %s | %d of %d = %.3f | %d / %d / %d' % (
                band, n, ws(sum(1 for g in bg if rammed(g, 'us')), n), sum(1 for g in bg if rammed(g, 'us', True)),
                sum(1 for g in bg if rammed(g, 'them')), n, sum(1 for g in bg if rammed(g, 'them')) / n, sum(1 for g in bg if rammed(g, 'them', True)),
                ws(sum(1 for g in bg if g['q_alive_end']['us']), n),
                sum(1 for g in bg if g['q_alive_end']['them']), n, sum(1 for g in bg if g['q_alive_end']['them']) / n,
                fd['us'], fd['them'], fd[None]))
        out('  [share of her deaths] our queen: rammed / died, by band: %s' % ', '.join(
            '%s %d of %d' % (band, sum(1 for g in gs if g['band'] == band and rammed(g, 'us')), sum(1 for g in gs if g['band'] == band and g['qs']['us']['death'])) for band in BANDS))
        out('  [share of her deaths] their queen: rammed / died, by band: %s' % ', '.join(
            '%s %d of %d' % (band, sum(1 for g in gs if g['band'] == band and rammed(g, 'them')), sum(1 for g in gs if g['band'] == band and g['qs']['them']['death'])) for band in BANDS))
        out('  [causes of our queen death by band] %s' % '; '.join(
            '%s: %s' % (band, sorted(Counter(cause(g['qs']['us']['death']) for g in gs if g['band'] == band).items())) for band in BANDS))
        hs = sorted(gs, key=lambda g: (g['completedAt'], g['game']))
        half = len(hs) // 2
        for label, part in (('first half by time', hs[:half]), ('second half by time', hs[half:])):
            fd = Counter(first_dead(g) for g in part)
            out('  [first to die] %s (%d games): ours %d, theirs %d' % (label, len(part), fd['us'], fd['them']))
        out('  [at the ram, her last own turn start; rams by an enemy with the rammer on that board]')
        for band in BANDS + ('all',):
            rr = [r for g in gs if band == 'all' or g['band'] == band for r in g['rams'] if r['side'] == 'us' and r['cross']]
            wb = [r for r in rr if not r.get('no_snapshot') and r.get('born_later') is False]
            if not rr:
                continue
            out('    %-10s rams %d, with a board %d; fewer than 2 friends within 5: %d (at the ram itself: %d of %d); enemy heads within 6: mean %.2f (counting the rammer when farther: %.2f)' % (
                band, len(rr), len(wb), sum(1 for r in wb if r['friends0'] < 2), sum(1 for r in rr if r['friends'] < 2), len(rr),
                mean(r['enemies6'] for r in wb) if wb else 0,
                mean(r['enemies6'] + (0 if any(f[0] and f[2] <= 6 for f in r['foes']) else 1) for r in wb) if wb else 0))
        out('  [chance, our queen rammed] %s' % perm_trend(gs, lambda g: rammed(g, 'us')))
        out('  [chance, our queen NOT alive at end] %s' % perm_trend(gs, lambda g: not g['q_alive_end']['us']))
        out('  [chance, their queen rammed] %s' % perm_trend(gs, lambda g: rammed(g, 'them')))
        out('  [chance, ours died first, among games where a queen died] %s' % perm_trend([g for g in gs if first_dead(g)], lambda g: first_dead(g) == 'us'))
        b = [g for g in gs if g['band'] == '1700-1899']
        c = [g for g in gs if g['band'] == '1900-2099']
        d = [g for g in gs if g['band'] == '2100+']
        for label, fn in (('our queen rammed', lambda g: rammed(g, 'us')), ('our queen alive at end', lambda g: g['q_alive_end']['us'])):
            kb, kc, kd = sum(1 for g in b if fn(g)), sum(1 for g in c if fn(g)), sum(1 for g in d if fn(g))
            out('  [Fisher, games as units] %s: 1700-1899 against 1900-2099 p %.4f; 1900-2099 against 2100+ p %.4f; 1700-1899 against 2100+ p %.4f; under 1900 against 1900 and over p %.4f' % (
                label, fisher(kb, len(b) - kb, kc, len(c) - kc), fisher(kc, len(c) - kc, kd, len(d) - kd) if d else 1, fisher(kb, len(b) - kb, kd, len(d) - kd) if d else 1,
                fisher(sum(1 for g in gs if g['opponentElo'] < 1900 and fn(g)), sum(1 for g in gs if g['opponentElo'] < 1900 and not fn(g)),
                       sum(1 for g in gs if g['opponentElo'] >= 1900 and fn(g)), sum(1 for g in gs if g['opponentElo'] >= 1900 and not fn(g)))))
        out('  [2100+ cell by opponent: games, our queen rammed, our queen alive at end, their queen rammed, won]')
        for opp, n in sorted(Counter(g['opp'] for g in d).items(), key=lambda kv: -kv[1]):
            og = [g for g in d if g['opp'] == opp]
            out('    %-34s %3d %3d %3d %3d %3d  ratings %s' % (opp, n, sum(1 for g in og if rammed(g, 'us')), sum(1 for g in og if g['q_alive_end']['us']),
                                                               sum(1 for g in og if rammed(g, 'them')), sum(1 for g in og if g['win']), sorted(set(g['opponentElo'] for g in og))))
        out('  [2100+ cell by layout: games, rammed, alive] %s' % sorted((mk, n, sum(1 for g in d if g['map_key'] == mk and rammed(g, 'us')),
                                                                         sum(1 for g in d if g['map_key'] == mk and g['q_alive_end']['us'])) for mk, n in Counter(g['map_key'] for g in d).items()))
        out('  [2100+ cell] evenings %s; battles %d' % (sorted(Counter(g['evening'] for g in d).items()), len(set(g['battle'] for g in d))))
        if d:
            vals = []
            for opp in sorted(set(g['opp'] for g in d)):
                rest = [g for g in d if g['opp'] != opp]
                if rest:
                    vals.append((sum(1 for g in rest if rammed(g, 'us')) / len(rest), opp, len(rest)))
            if vals:
                out('  [2100+ rammed share without one opponent] %.3f (without %s, %d games left) to %.3f (without %s, %d left)' % (
                    min(vals)[0], min(vals)[1], min(vals)[2], max(vals)[0], max(vals)[1], max(vals)[2]))
        out('  [layout held fixed] rammed share 1900 and over minus under 1900, per layout with 4 or more games on each side:')
        up = down = 0
        wsum = wn = 0.0
        parts = []
        for mk in sorted(set(g['map_key'] for g in gs)):
            lo = [g for g in gs if g['map_key'] == mk and g['opponentElo'] < 1900]
            hi = [g for g in gs if g['map_key'] == mk and g['opponentElo'] >= 1900]
            if len(lo) < 4 or len(hi) < 4:
                continue
            dd = sum(1 for g in hi if rammed(g, 'us')) / len(hi) - sum(1 for g in lo if rammed(g, 'us')) / len(lo)
            w = len(lo) * len(hi) / (len(lo) + len(hi))
            wsum += w * dd
            wn += w
            if dd > 0:
                up += 1
            elif dd < 0:
                down += 1
            parts.append('%s %+.2f (%d, %d)' % (mk, dd, len(lo), len(hi)))
        out('    higher on %d layouts, lower on %d; weighted mean difference %+.3f; %s' % (up, down, wsum / wn if wn else 0, '; '.join(parts)))
        out('  [finer bands, our queen rammed] %s' % ', '.join('%d-%d: %d of %d' % (lo, lo + 99, sum(1 for g in gs if lo <= g['opponentElo'] < lo + 100 and rammed(g, 'us')),
                                                                                     sum(1 for g in gs if lo <= g['opponentElo'] < lo + 100)) for lo in range(1500, 2400, 100)
                                                         if any(lo <= g['opponentElo'] < lo + 100 for g in gs)))
        out('  [finer bands, our queen alive at end] %s' % ', '.join('%d-%d: %d of %d' % (lo, lo + 99, sum(1 for g in gs if lo <= g['opponentElo'] < lo + 100 and g['q_alive_end']['us']),
                                                                                         sum(1 for g in gs if lo <= g['opponentElo'] < lo + 100)) for lo in range(1500, 2400, 100)
                                                              if any(lo <= g['opponentElo'] < lo + 100 for g in gs)))
        dz = [g for g in allg if g['map'] in DEAD]
        out('  [for contrast, Schooltime and Slithery Fight] %s' % ', '.join('%s: rammed %d, alive %d of %d' % (
            band, sum(1 for g in dz if g['band'] == band and rammed(g, 'us')), sum(1 for g in dz if g['band'] == band and g['q_alive_end']['us']),
            sum(1 for g in dz if g['band'] == band)) for band in BANDS))


# ---------------------------------------------------------------- F20
def near_set(W, H, tiles, radius):
    s = set()
    for ci in tiles:
        x, y = ci % W, ci // W
        for dx in range(-radius, radius + 1):
            for dy in range(-(radius - abs(dx)), radius - abs(dx) + 1):
                s.add(((y + dy) % H) * W + (x + dx) % W)
    return s


def f20_rows(g, busy, rounds, radius=2, tol=1.1):
    W, H = g['W'], g['H']
    ns = near_set(W, H, busy, radius)
    rows = []
    for r, sn in sorted(g['snaps'].items(), key=lambda kv: int(kv[0])):
        if int(r) not in rounds:
            continue
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
        out('  %-46s no snapshots' % label)
        return
    out('  %-46s snapshots %4d  our heads %6d  their heads %6d  our share %.3f  their share %.3f  gap %+.3f' % (label, n, nu, nt, au / nu, at / nt, at / nt - au / nu))


def gap20(rowsets):
    n, nu, nt, au, at = pool20(rowsets)
    if not n or not nu or not nt:
        return None
    return at / nt - au / nu


R_LATE = (100, 125, 150, 175, 200, 225, 250, 275, 300)
R_EARLY = (50, 75)


def f20(games):
    bigs = [g for g in games if g['code'] in ('main', 'v31') and g['open_tiles'] >= 1500]
    lay_busy = defaultdict(Counter)
    lay_n = Counter(g['map_key'] for g in bigs)
    for g in bigs:
        for ci, v in g['tiles'].items():
            if v[0] >= 8:
                lay_busy[g['map_key']][int(ci)] += 1
    own = {}
    cross = {}
    for g in bigs:
        own[g['game']] = [int(ci) for ci, v in g['tiles'].items() if v[0] >= 8]
        others = lay_n[g['map_key']] - 1
        cross[g['game']] = [ci for ci, n in lay_busy[g['map_key']].items()
                            if others > 0 and (n - (1 if g['tiles'].get(str(ci), [0])[0] >= 8 else 0)) * 2 >= others]
    late = {g['game']: f20_rows(g, own[g['game']], R_LATE) for g in bigs}
    early = {g['game']: f20_rows(g, own[g['game']], R_EARLY) for g in bigs}
    late_x = {g['game']: f20_rows(g, cross[g['game']], R_LATE) for g in bigs}
    early_x = {g['game']: f20_rows(g, cross[g['game']], R_EARLY) for g in bigs}
    for code in ('main', 'v31'):
        gs = [g for g in bigs if g['code'] == code]
        out('')
        out('=== %s: %d games on layouts with 1500 or more open tiles (%s)' % (code, len(gs), sorted(Counter(g['map_key'] for g in gs).items())))
        out(' raw rounds 100-300, busy tiles from the game itself')
        line20(code + ' all', [late[g['game']] for g in gs])
        for band in BANDS:
            bg = [g for g in gs if g['band'] == band]
            if bg:
                line20('  ' + band + ' (%d games)' % len(bg), [late[g['game']] for g in bg])
                out('      gap %s; kept snapshots by layout %s' % (bs(bg, lambda gg: gap20([late[g['game']] for g in gg])),
                                                                  sorted(Counter(g['map_key'] for g in bg for _ in late[g['game']]).items())))
        out(' the same with layout mix held fixed: gap per band within a layout (kept snapshots)')
        for mk in sorted(set(g['map_key'] for g in gs)):
            parts = []
            for band in BANDS:
                bg = [g for g in gs if g['band'] == band and g['map_key'] == mk]
                n = pool20([late[g['game']] for g in bg])[0]
                v = gap20([late[g['game']] for g in bg])
                if n:
                    parts.append('%s %+.3f (%d)' % (band, v, n))
            out('    %-20s %s' % (mk, ', '.join(parts)))
        out(' raw rounds 100-300, busy tiles from the other games on the layout (8 or more births in at least half of them)')
        line20(code + ' all', [late_x[g['game']] for g in gs])
        for band in BANDS:
            bg = [g for g in gs if g['band'] == band]
            if bg:
                line20('  ' + band, [late_x[g['game']] for g in bg])
        out(' raw rounds 50 and 75 pooled, busy tiles from the game itself')
        line20(code + ' r50+r75', [early[g['game']] for g in gs])
        line20('  r50 only', [[r for r in early[g['game']] if r[0] == 50] for g in gs])
        line20('  r75 only', [[r for r in early[g['game']] if r[0] == 75] for g in gs])
        for mk in sorted(set(g['map_key'] for g in gs)):
            line20('  ' + mk, [early[g['game']] for g in gs if g['map_key'] == mk])
        out('   gap r50+r75: %s' % bs(gs, lambda gg: gap20([early[g['game']] for g in gg])))
        pg = [gap20([early[g['game']]]) for g in gs]
        pg = [v for v in pg if v is not None]
        out('   by game (games with a kept early snapshot %d): theirs higher in %d, ours higher in %d, equal %d' % (
            len(pg), sum(1 for v in pg if v > 0), sum(1 for v in pg if v < 0), sum(1 for v in pg if v == 0)))
        out(' raw rounds 50 and 75, busy tiles from the other games on the layout')
        line20(code + ' r50+r75', [early_x[g['game']] for g in gs])
        for mk in sorted(set(g['map_key'] for g in gs)):
            line20('  ' + mk, [early_x[g['game']] for g in gs if g['map_key'] == mk])
        out('   gap r50+r75, other-game busy tiles: %s' % bs(gs, lambda gg: gap20([early_x[g['game']] for g in gg])))
        out(' all snapshots at r50 and r75 whatever the head counts:')
        allr = {g['game']: f20_rows(g, own[g['game']], R_EARLY, tol=1e9) for g in gs}
        line20(code + ' r50+r75 unfiltered', allr.values())
        out('   early snapshots: %d taken, %d kept' % (sum(len(v) for v in allr.values()), sum(len(early[g['game']]) for g in gs)))
    out('')
    out('=== cost: per game gap (their share minus ours, kept snapshots r100-300, at least 3) against our share of pearls eaten in r101-300')
    for mk in ('Around UNSW #1', 'Slithery Fight #1'):
        for src, label in ((late, 'busy tiles of the game itself'), (late_x, 'busy tiles of the other games')):
            pts = []
            for g in bigs:
                if g['map_key'] != mk or len(late[g['game']]) < 3:
                    continue
                v = gap20([src[g['game']]])
                eu, et = g['eat']['us'][1], g['eat']['them'][1]
                if v is None or eu + et == 0:
                    continue
                pts.append((v, eu / (eu + et), g))
            out('  %s, %s: %d games (main %d, v31 %d)' % (mk, label, len(pts), sum(1 for p in pts if p[2]['code'] == 'main'), sum(1 for p in pts if p[2]['code'] == 'v31')))
            out('    Spearman together %s' % sp([p[0] for p in pts], [p[1] for p in pts]))
            for code in ('main', 'v31'):
                sub = [p for p in pts if p[2]['code'] == code]
                out('    Spearman %s %s' % (code, sp([p[0] for p in sub], [p[1] for p in sub])))
            srt = sorted(pts, key=lambda p: p[0])
            h = len(srt) // 2
            out('    smaller-gap half: won %d of %d, mean pearl share %.3f; bigger-gap half: won %d of %d, mean pearl share %.3f' % (
                sum(1 for p in srt[:h] if p[2]['win']), h, mean(p[1] for p in srt[:h]),
                sum(1 for p in srt[h:] if p[2]['win']), len(srt) - h, mean(p[1] for p in srt[h:])))
            if src is late:
                # the share of our heads near busy tiles alone, and theirs alone, against the pearl share
                ou = []
                th = []
                ps = []
                for v, sh, g in pts:
                    n, nu, nt, au, at = pool20([late[g['game']]])
                    ou.append(au / nu)
                    th.append(at / nt)
                    ps.append(sh)
                out('    our share of heads near alone: Spearman %s; their share alone: %s' % (sp(ou, ps), sp(th, ps)))
                bz = [len(own[p[2]['game']]) for p in pts]
                out('    number of busy tiles in the game against our pearl share: Spearman %s' % sp(bz, ps))
                # busy tiles where each side ate more
                gu = []
                for v, sh, g in pts:
                    mine = sum(1 for ci, t in g['tiles'].items() if t[0] >= 8 and t[1] > t[2])
                    tot = sum(1 for ci, t in g['tiles'].items() if t[0] >= 8)
                    gu.append(mine / tot if tot else 0)
                out('    share of busy tiles on which we ate more against the gap: Spearman %s' % sp(gu, [p[0] for p in pts]))
                wins = [p for p in pts if p[2]['win']]
                loss = [p for p in pts if not p[2]['win']]
                out('    mean gap in games won %.3f (%d), lost %.3f (%d)' % (mean(p[0] for p in wins) if wins else 0, len(wins), mean(p[0] for p in loss) if loss else 0, len(loss)))
                top = sorted(pts, key=lambda p: (ranks([q[0] for q in pts])[pts.index(p)] - len(pts) / 2) * (ranks([q[1] for q in pts])[pts.index(p)] - len(pts) / 2))[:3]
                rest = [p for p in pts if p not in top]
                out('    without the three games that support it most: Spearman %s' % sp([p[0] for p in rest], [p[1] for p in rest]))
                for key in ('opp', 'evening'):
                    vals = []
                    for kk in sorted(set(p[2][key] for p in pts)):
                        sub = [p for p in pts if p[2][key] != kk]
                        v = spearman([p[0] for p in sub], [p[1] for p in sub])
                        if v is not None:
                            vals.append((v, kk))
                    out('    leave one %s out: %.2f (without %s) to %.2f (without %s)' % (key, min(vals)[0], min(vals)[1], max(vals)[0], max(vals)[1]))
    out('')
    out('  wins by gap half, both layouts pooled (median split inside each layout, busy tiles of the game itself):')
    lo_w = lo_n = hi_w = hi_n = 0
    for mk in ('Around UNSW #1', 'Slithery Fight #1'):
        pts = [(gap20([late[g['game']]]), g) for g in bigs if g['map_key'] == mk and len(late[g['game']]) >= 3]
        pts = sorted([p for p in pts if p[0] is not None], key=lambda p: p[0])
        h = len(pts) // 2
        lo_n += h
        hi_n += len(pts) - h
        lo_w += sum(1 for p in pts[:h] if p[1]['win'])
        hi_w += sum(1 for p in pts[h:] if p[1]['win'])
    out('    smaller-gap half won %d of %d; bigger-gap half won %d of %d' % (lo_w, lo_n, hi_w, hi_n))


# ---------------------------------------------------------------- F13
def reach_full(L):
    return (L + 3) // 4 + L - 2


def reach_full1(L):
    return (L + 3) // 4 + L - 1


def reach_free(L):
    return (L + 3) // 4


def safe(r, reach, rammer_only=False, radius=6):
    foes = [f for f in r['foes'] if f[0] or (not rammer_only and f[2] <= radius)]
    for j in range(r['n_legal']):
        if all(f[3][j] > reach(f[1]) for f in foes):
            return True
    return False


def f13(games):
    out('=== the reach formula against what rammers did (every ram on a queen, all layouts, main and v31)')
    allr = [r for g in games if g['code'] in ('main', 'v31') for r in g['rams']]
    over = [r for r in allr if r['mover_steps'] > reach_full(r['mover_len_turn_start'])]
    paid = Counter()
    for r in allr:
        L = r['mover_len_turn_start']
        paid[(L, r['mover_steps'])] += 1
    out('  rams %d; rammer made more steps than ceil(L/4)+L-2: %d; more than ceil(L/4)+L-1: %d' % (
        len(allr), len(over), sum(1 for r in allr if r['mover_steps'] > reach_full1(r['mover_len_turn_start']))))
    out('  rammer length 2: steps made %s; length 3: %s; length 4: %s' % (
        sorted((k[1], v) for k, v in paid.items() if k[0] == 2), sorted((k[1], v) for k, v in paid.items() if k[0] == 3), sorted((k[1], v) for k, v in paid.items() if k[0] == 4)))
    out('  rammer made more steps than its free steps: %d of %d' % (sum(1 for r in allr if r['mover_steps'] > reach_free(r['mover_len_turn_start'])), len(allr)))
    for code in ('main', 'v31'):
        allg = [g for g in games if g['code'] == code]
        gs = [g for g in allg if g['map'] not in DEAD]
        out('')
        out('=== %s: %d games, %d on free layouts' % (code, len(allg), len(gs)))
        for vs, lone, label in (('us', True, 'OUR lone queen (their queen dead)'), ('them', True, 'THEIR lone queen (our queen dead)'),
                                ('us', False, 'OUR queen, their queen alive'), ('them', False, 'THEIR queen, our queen alive')):
            rams = [(g, r) for g in gs for r in g['rams'] if r['cross'] and r['side'] == vs and r['other_queen_dead'] == lone]
            wb = [(g, r) for g, r in rams if not r.get('no_snapshot') and r.get('born_later') is False]
            n = len(wb)
            out('')
            out('--- %s, %s: rams %d, no snapshot %d, rammer born later %d, with a board %d' % (
                code, label, len(rams), sum(1 for g, r in rams if r.get('no_snapshot')), sum(1 for g, r in rams if r.get('born_later')), n))
            if not n:
                continue
            kf = sum(1 for g, r in wb if safe(r, reach_full))
            out('  safe from the full reach of every enemy head within 6 and the rammer: %s' % ws(kf, n))
            out('  safe from the free reach of the same heads: %s' % ws(sum(1 for g, r in wb if safe(r, reach_free)), n))
            out('  rammer only: full %s; free %s' % (ws(sum(1 for g, r in wb if safe(r, reach_full, True)), n), ws(sum(1 for g, r in wb if safe(r, reach_free, True)), n)))
            out('  [sensitivity] full reach with one more paid step (L-1): %d; heads within 4: %d; within 3: %d; within 2: %d' % (
                sum(1 for g, r in wb if safe(r, reach_full1)), sum(1 for g, r in wb if safe(r, reach_full, False, 4)),
                sum(1 for g, r in wb if safe(r, reach_full, False, 3)), sum(1 for g, r in wb if safe(r, reach_full, False, 2))))
            out('  [what blocks] no safe step even from the rammer alone: %d; safe from the rammer but not from another head: %d; safe from all: %d' % (
                sum(1 for g, r in wb if not safe(r, reach_full, True)), sum(1 for g, r in wb if safe(r, reach_full, True) and not safe(r, reach_full)), kf))
            out('  [legal steps] (number of legal steps, rams): %s' % sorted(Counter(r['n_legal'] for g, r in wb).items()))
            out('  [heads considered] (heads, rams): %s; rammer within 6 at her last turn: %d of %d' % (
                sorted(Counter(len(r['foes']) for g, r in wb).items()), sum(1 for g, r in wb if any(f[0] and f[2] <= 6 for f in r['foes'])), n))
            out('  [rammer length at her last turn] (length, rams): %s' % sorted(Counter(f[1] for g, r in wb for f in r['foes'] if f[0]).items()))
            out('  [rammer path distance to her at her last turn] (distance, rams): %s' % sorted(Counter(f[4] for g, r in wb for f in r['foes'] if f[0]).items()))
            out('  [what the rammer did] steps made above its free steps (extra, rams): %s' % sorted(Counter(max(0, r['mover_steps'] - reach_free(r['mover_len_turn_start'])) for g, r in wb).items()))
            # a step that ends farther from the rammer than the rammer actually travelled, and beyond its free steps
            ka = 0
            for g, r in wb:
                f = [x for x in r['foes'] if x[0]][0]
                if any(d > max(reach_free(f[1]), f[5]) for d in f[3]):
                    ka += 1
            out('  [middle measure] a legal step farther from the rammer than max(free steps, the distance it really covered): %s' % ws(ka, n))
            out('  [she moved on her last turn] %d of %d; her length at that turn (length, rams): %s' % (
                sum(1 for g, r in wb if r['moved']), n, sorted(Counter(r['qlen0'] for g, r in wb).items())))
            if lone and vs == 'us':
                out('  [spread] opponents %d (largest %d rams), layouts %d, evenings %s, bands %s' % (
                    len(set(g['opp'] for g, r in wb)), max(Counter(g['opp'] for g, r in wb).values()), len(set(g['map_key'] for g, r in wb)),
                    sorted(Counter(g['evening'] for g, r in wb).items()), sorted(Counter(g['band'] for g, r in wb).items())))
                out('  [the rams with a safe step] %s' % [(g['game'], g['map_key'], g['band'], g['evening']) for g, r in wb if safe(r, reach_full)])
                out('  [by band] safe from full reach: %s' % ', '.join('%s %d of %d' % (band, sum(1 for g, r in wb if g['band'] == band and safe(r, reach_full)),
                                                                                         sum(1 for g, r in wb if g['band'] == band)) for band in BANDS))
                out('  [by evening] safe from full reach: %s' % ', '.join('%s %d of %d' % (e, sum(1 for g, r in wb if g['evening'] == e and safe(r, reach_full)),
                                                                                            sum(1 for g, r in wb if g['evening'] == e)) for e in sorted(set(g['evening'] for g, r in wb))))
                out('  [by layout] safe from full reach: %s' % ', '.join('%s %d of %d' % (mk, sum(1 for g, r in wb if g['map_key'] == mk and safe(r, reach_full)),
                                                                                           sum(1 for g, r in wb if g['map_key'] == mk)) for mk in sorted(set(g['map_key'] for g, r in wb))))
        res = {}
        for vs in ('us', 'them'):
            wb = [r for g in gs for r in g['rams'] if r['cross'] and r['side'] == vs and r['other_queen_dead'] and not r.get('no_snapshot') and r.get('born_later') is False]
            res[vs] = (sum(1 for r in wb if safe(r, reach_full)), len(wb))
        out('')
        out('  [chance] %s lone queen, ours %d of %d against theirs %d of %d: Fisher p %.3f' % (
            code, res['us'][0], res['us'][1], res['them'][0], res['them'][1],
            fisher(res['us'][0], res['us'][1] - res['us'][0], res['them'][0], res['them'][1] - res['them'][0])))
    tot = {}
    for code in ('main', 'v31'):
        wb = [r for g in games if g['code'] == code and g['map'] not in DEAD for r in g['rams']
              if r['cross'] and r['side'] == 'us' and r['other_queen_dead'] and not r.get('no_snapshot') and r.get('born_later') is False]
        tot[code] = (sum(1 for r in wb if safe(r, reach_full)), len(wb))
    out('')
    out('  [chance] our lone queen, main %d of %d against v31 %d of %d: Fisher p %.3f' % (
        tot['main'][0], tot['main'][1], tot['v31'][0], tot['v31'][1],
        fisher(tot['main'][0], tot['main'][1] - tot['main'][0], tot['v31'][0], tot['v31'][1] - tot['v31'][0])))


# ---------------------------------------------------------------- CHECK
def check(games, bad):
    out('games read %d, with an error %d %s' % (len(games) + len(bad), len(bad), [(b['game'], b['error']) for b in bad][:5]))
    mv = [g for g in games if g['code'] in ('main', 'v31')]
    out('codes %s' % sorted(Counter(g['code'] for g in games).items()))
    out('final state equals the result block: %d of %d; games with anomalies %d %s; drop mismatches %d; bad head-on groups %d of %d; bad portals %d' % (
        sum(1 for g in mv if g['final_ok']), len(mv), sum(1 for g in mv if g['anomalies']),
        sorted(Counter(k for g in mv for k in g['anomalies']).items()), sum(g['drop_mismatch'] for g in mv),
        sum(g['bad_head_on_groups'] for g in mv), sum(g['head_on_groups'] for g in mv), sum(g['bad_portals'] for g in mv)))
    rows = {}
    for line in Path('data/analysis/ladder/rows.jsonl').read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            rows[r['game']] = r
    maps = json.loads(Path('data/analysis/ladder/maps.json').read_text())
    out('rows.jsonl games %d; mine %d; in both %d' % (len(rows), len(games), sum(1 for g in games if g['game'] in rows)))
    diff = Counter()
    n = 0
    for g in games:
        r = rows.get(g['game'])
        if r is None:
            continue
        n += 1
        rc = r['our_code'] if r['our_code'] in ('main', 'v31') else 'other'
        if rc != g['code']:
            diff['code'] += 1
        if r['map_key'] != g['map_key']:
            diff['map_key'] += 1
        if r['win'] != g['win']:
            diff['win'] += 1
        if r['opponent_rating'] != g['opponentElo']:
            diff['rating'] += 1
        if maps[r['map_key']]['queen_spawn_dead_end'] != (g['map'] in DEAD):
            diff['dead end'] += 1
        if g['code'] == 'other':
            continue
        if r['last_round'] != g['last_round']:
            diff['last_round'] += 1
        for s in ('us', 'them'):
            q = r['queen'][s]
            d = g['qs'][s]['death']
            if q['alive_end'] != g['q_alive_end'][s]:
                diff['alive_end'] += 1
            if (q['death_round'] if q['death_round'] is not None else None) != (d['round'] if d else None):
                diff['death round'] += 1
            theirs = q['death_cause'] == 'head-on' and q['head_on'] is not None and q['head_on']['victim'] == q['id']
            if theirs != rammed(g, s):
                diff['rammed'] += 1
            if d and q['death_cause'] != ('wall', 'own body', 'other dragon body', 'head-on', 'other')[d['reason']]:
                diff['death cause'] += 1
        pr = r['pearls']['r101-300']
        if pr['eaten']['us'] != g['eat']['us'][1] or pr['eaten']['them'] != g['eat']['them'][1]:
            diff['pearls r101-300'] += 1
    out('compared %d games; differences: %s' % (n, dict(diff) if diff else 'none'))


def main():
    which = sys.argv[1]
    games, bad = load()
    if which == 'F23':
        f23(games)
        Path(P + 'f23-numbers.txt').write_text('\n'.join(LINES) + '\n')
    elif which == 'F24':
        f24(games)
        Path(P + 'f24-numbers.txt').write_text('\n'.join(LINES) + '\n')
    elif which == 'F20':
        f20(games)
        Path(P + 'f20-0520-numbers.txt').write_text('\n'.join(LINES) + '\n')
    elif which == 'F13':
        f13(games)
        Path(P + 'f13-0520-numbers.txt').write_text('\n'.join(LINES) + '\n')
    else:
        check(games, bad)
        Path(P + 'check4.txt').write_text('\n'.join(LINES) + '\n')


main()
