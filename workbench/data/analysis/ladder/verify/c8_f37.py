#!/usr/bin/env python3
"""Verifier claims 8 (run of 2026-10-07 08:23 KST), F37: queen deaths by wall or own body in raw rounds 101-200.
Reads the x8 shards (own extraction from the raw replays) and writes f37-numbers.txt. maps.json is read for the
corridor share and to check the free-layout flag; rows.jsonl is read only in the last section, to compare."""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timedelta
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
LINES = []
REASON = ('wall', 'own body', 'other body', 'head-on', 'no valid action')
WIN = ((0, 100), (101, 200), (201, 300), (301, 499))
WN = ('r0-100', 'r101-200', 'r201-300', 'r301-499')
SIDE = ('ours', 'theirs')


def say(*a):
    s = ' '.join(str(x) for x in a)
    LINES.append(s)
    print(s)


def load():
    games = []
    for k in range(6):
        for line in (V / ('x8-%d.jsonl' % k)).read_text().splitlines():
            if line.strip():
                games.append(json.loads(line))
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
        g['full'] = g['last_round'] == 499
        g['d'] = [q['round'] if q else None for q in g['qdeath']]
    return order


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


def sh(k, n):
    return '%d of %d (%s)' % (k, n, ('%.3f' % (k / n)) if n else '-')


def boot_diff(units, n=2000, seed=1):
    """units (a, b, c, d) per cluster; statistic a/b - c/d; 2.5 and 97.5 percentiles and the share at or below 0."""
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
        if b and d:
            vals.append(a / b - c / d)
    vals.sort()
    L = len(vals)
    return (round(vals[int(0.025 * L)], 4), round(vals[int(0.975 * L) - 1], 4), round(sum(1 for v in vals if v <= 0) / L, 4))


def by_cluster(gs, key, f):
    acc = {}
    for g in gs:
        t = f(g)
        cur = acc.get(g[key])
        acc[g[key]] = t if cur is None else tuple(x + y for x, y in zip(cur, t))
    return acc


def alive100(g, s):
    return g['d'][s] is None or g['d'][s] > 100


def dies(g, s, lo, hi, reasons):
    q = g['qdeath'][s]
    return q is not None and lo <= q['round'] <= hi and q['reason'] in reasons


def rammed(g, s, lo, hi):
    q = g['qdeath'][s]
    return q is not None and lo <= q['round'] <= hi and q['reason'] == 3 and not q['actor'] and q.get('killer_side') == 1 - s


def trapped(g, s, lo, hi):
    """she was the mover and had no free tile at the start of that turn, whatever the engine reason"""
    q = g['qdeath'][s]
    return q is not None and lo <= q['round'] <= hi and q['actor'] and q.get('start_legal') == 0


def unit(g):
    a0, a1 = alive100(g, 0), alive100(g, 1)
    return (1 if a0 and dies(g, 0, 101, 200, (0, 1)) else 0, 1 if a0 else 0,
            1 if a1 and dies(g, 1, 101, 200, (0, 1)) else 0, 1 if a1 else 0)


def tunit(g):
    a0, a1 = alive100(g, 0), alive100(g, 1)
    return (1 if a0 and trapped(g, 0, 101, 200) else 0, 1 if a0 else 0,
            1 if a1 and trapped(g, 1, 101, 200) else 0, 1 if a1 else 0)


def q4(gs, f=unit):
    a = b = c = d = 0
    for g in gs:
        u = f(g)
        a += u[0]
        b += u[1]
        c += u[2]
        d += u[3]
    return a, b, c, d


def line(label, gs, f=unit):
    a, b, c, d = q4(gs, f)
    r = ((a / b) / (c / d)) if b and d and c else float('nan')
    say('  %-52s games %4d  ours %-18s theirs %-18s ratio %5.2f  Fisher p %.4f' % (label, len(gs), sh(a, b), sh(c, d), r, fisher(a, b - a, c, d - c)))
    return a, b, c, d


def split10(g, s):
    d = g['d'][s]
    return any(d - 10 <= r <= d for r in g['qsplits'][s])


def board(q):
    cls = [c[0] for c in q.get('start_cls') or []]
    return dict(free=sum(1 for c in cls if c == 'F'), kelp=sum(1 for c in cls if c == 'K'),
                own=sum(1 for c in cls if c in 'ST'), mate=sum(1 for c in cls if c in 'CM'),
                child=sum(1 for c in cls if c == 'C'), enemy=sum(1 for c in cls if c in 'EH'),
                portal=sum(1 for c in (q.get('start_cls') or []) if c.endswith('p')))


def tally(label, items):
    """items: (game, side) pairs of queen deaths as the mover"""
    n = len(items)
    t = Counter()
    pat = Counter()
    for g, s in items:
        q = g['qdeath'][s]
        b = board(q)
        t['no free tile'] += b['free'] == 0
        t['one free tile'] += b['free'] == 1
        t['two or more free tiles'] += b['free'] >= 2
        t['kelp on 2 or more sides'] += b['kelp'] >= 2
        t['kelp on 3 sides and her own body on the fourth (dead-end tile)'] += b['kelp'] == 3 and b['own'] == 1
        t['a dragon of her own team on a neighbour tile'] += b['mate'] >= 1
        t['her own child on a neighbour tile'] += b['child'] >= 1
        t['an enemy on a neighbour tile'] += b['enemy'] >= 1
        t['only kelp and her own body around her'] += b['free'] == 0 and b['mate'] == 0 and b['enemy'] == 0
        t['she split in the 10 rounds before'] += split10(g, s)
        t['died on a later step of a sprint'] += q.get('used', 0) > 0
        t['a portal edge next to her head'] += b['portal'] >= 1
        t['wall'] += q['reason'] == 0
        t['own body'] += q['reason'] == 1
        t['we won the game'] += bool(g['win'])
        pat[''.join(sorted(c[0] for c in q.get('start_cls') or []))] += 1
    say('  %s: %d deaths' % (label, n))
    for k in ('wall', 'own body', 'no free tile', 'one free tile', 'two or more free tiles', 'kelp on 2 or more sides',
              'kelp on 3 sides and her own body on the fourth (dead-end tile)', 'only kelp and her own body around her',
              'a dragon of her own team on a neighbour tile', 'her own child on a neighbour tile', 'an enemy on a neighbour tile',
              'she split in the 10 rounds before', 'died on a later step of a sprint', 'a portal edge next to her head', 'we won the game'):
        say('      %-64s %d' % (k, t[k]))
    say('      four neighbours, sorted letters (K kelp, S own body, T own tail, C own child, M own team, E enemy body, H enemy head, F free): %s' % dict(pat.most_common()))


def main():
    order = load()
    maps = json.loads(Path('data/analysis/ladder/maps.json').read_text())
    mv = [g for g in order if g['code'] in ('main', 'v31')]
    say('F37 numbers, verifier run 2026-10-07 08:23 KST. Source: x8 shards (own rebuild of all raw replays).')
    say('free flag agrees with maps.json queen_spawn_dead_end false: %d of %d main and v31 games' % (
        sum(1 for g in mv if g['map_key'] in maps and g['free'] == (not maps[g['map_key']]['queen_spawn_dead_end'])), len(mv)))
    free = [g for g in mv if g['free']]
    CODES = ('main', 'v31')
    A = {c: [g for g in free if g['code'] == c] for c in CODES}
    G = {c: [g for g in A[c] if g['last_round'] >= 200] for c in CODES}
    F = {c: [g for g in A[c] if g['full']] for c in CODES}
    pool = G['main'] + G['v31']
    say('free main and v31 games %d; reached raw round 200: main %d, v31 %d; full: main %d, v31 %d' % (
        len(free), len(G['main']), len(G['v31']), len(F['main']), len(F['v31'])))
    chk = Counter()
    for g in free:
        for s in (0, 1):
            q = g['qdeath'][s]
            if q and q['actor'] and q.get('kind') == 0 and 'fatal_cls' in q:
                c0 = q['fatal_cls'][0]
                ok = (q['reason'] == 0 and c0 == 'K') or (q['reason'] == 1 and c0 in 'ST') or (q['reason'] == 2 and c0 in 'CME') or q['reason'] == 3 or q['reason'] == 4
                chk['engine reason agrees with what her fatal step ran into' if ok else 'reason and board differ'] += 1
    say('check of the board rebuild on queen deaths as the mover:', dict(chk))

    say('')
    say('== 1. Wall or own body in raw rounds 101-200, queens alive after raw round 100, games that reached raw round 200 ==')
    for c in CODES:
        a, b, cc, d = line(c, G[c])
        for s in (0, 1):
            say('      %s %s: wall %d, own body %d' % (c, SIDE[s], sum(1 for g in G[c] if alive100(g, s) and dies(g, s, 101, 200, (0,))),
                                                    sum(1 for g in G[c] if alive100(g, s) and dies(g, s, 101, 200, (1,)))))
    line('both codes', pool)
    for c in CODES:
        for b in ('1700-1899', '1900-2099', '2100+'):
            line(c + ' ' + b, [g for g in G[c] if g['band'] == b])

    say('')
    say('== 2. Per layout ==')
    for label, gs in (('main', G['main']), ('v31', G['v31']), ('both codes', pool)):
        acc = by_cluster(gs, 'map_key', unit)
        say('  %s (ours deaths of alive at r100, theirs):' % label)
        for name, u in sorted(acc.items(), key=lambda kv: (-kv[1][0], kv[0])):
            say('      %-24s ours %-18s theirs %s' % (name, sh(u[0], u[1]), sh(u[2], u[3])))
        both = [u for u in acc.values() if u[1] and u[3]]
        say('      layouts where our share is higher %d, equal %d, lower %d (of %d)' % (
            sum(1 for u in both if u[0] / u[1] > u[2] / u[3]), sum(1 for u in both if u[0] / u[1] == u[2] / u[3]),
            sum(1 for u in both if u[0] / u[1] < u[2] / u[3]), len(both)))
    three = ('Maze #1', 'Portals #1', 'weakhold #1')
    for c in CODES:
        line(c + ' Maze only', [g for g in G[c] if g['map_key'] == 'Maze #1'])
        line(c + ' without Maze', [g for g in G[c] if g['map_key'] != 'Maze #1'])
        line(c + ' Maze, Portals, weakhold', [g for g in G[c] if g['map_key'] in three])
        line(c + ' without Maze, Portals, weakhold', [g for g in G[c] if g['map_key'] not in three])
    line('both codes without Maze', [g for g in pool if g['map_key'] != 'Maze #1'])
    line('both codes Maze, Portals, weakhold', [g for g in pool if g['map_key'] in three])
    line('both codes without Maze, Portals, weakhold', [g for g in pool if g['map_key'] not in three])
    a, b, cc, d = q4(pool)
    am = q4([g for g in pool if g['map_key'] == 'Maze #1'])[0]
    say('  share of our deaths that are on Maze: %s; main %s; v31 %s' % (
        sh(am, a), sh(q4([g for g in G['main'] if g['map_key'] == 'Maze #1'])[0], q4(G['main'])[0]),
        sh(q4([g for g in G['v31'] if g['map_key'] == 'Maze #1'])[0], q4(G['v31'])[0])))
    fl = sorted(set(g['map_key'] for g in free))
    cs = sorted(maps[k]['corridor_share'] for k in fl)
    med = (cs[len(cs) // 2 - 1] + cs[len(cs) // 2]) / 2 if len(cs) % 2 == 0 else cs[len(cs) // 2]
    say('  free layouts seen %d; median corridor share %.4f' % (len(fl), med))
    heavy = [g for g in pool if maps[g['map_key']]['corridor_share'] >= 0.165 and g['map_key'] not in ('Maze #1', 'Portals #1')]
    light = [g for g in pool if maps[g['map_key']]['corridor_share'] < 0.165 and g['map_key'] not in ('Maze #1', 'Portals #1')]
    line('corridor share at or above 0.165, no Maze, no Portals', heavy)
    line('corridor share below 0.165, no Maze, no Portals', light)

    say('')
    say('== 3. Full games only, by window (ours against theirs) ==')
    for c in CODES:
        gs = F[c]
        for name, fn in (('wall or own body', lambda g, s, lo, hi: dies(g, s, lo, hi, (0, 1))),
                         ('standing victim of an enemy head-on', rammed),
                         ('other body', lambda g, s, lo, hi: dies(g, s, lo, hi, (2,))),
                         ('no valid action', lambda g, s, lo, hi: dies(g, s, lo, hi, (4,))),
                         ('mover with no free tile, any reason', trapped),
                         ('all queen deaths', lambda g, s, lo, hi: dies(g, s, lo, hi, (0, 1, 2, 3, 4)))):
            say('  %s full (%d games) %-38s %s' % (c, len(gs), name, '; '.join('%s %d against %d' % (
                WN[w], sum(1 for g in gs if fn(g, 0, WIN[w][0], WIN[w][1])), sum(1 for g in gs if fn(g, 1, WIN[w][0], WIN[w][1]))) for w in range(4))))
        say('  %s full, queens alive at the start of each window: %s' % (c, '; '.join('%s %d against %d' % (
            WN[w], sum(1 for g in gs if g['d'][0] is None or g['d'][0] >= WIN[w][0]), sum(1 for g in gs if g['d'][1] is None or g['d'][1] >= WIN[w][0])) for w in range(4))))
    for c in CODES:
        won = [g for g in G[c] if alive100(g, 0) and dies(g, 0, 101, 200, (0, 1))]
        say('  %s: we won %d of the %d games with such a death of our queen; we won %d of the other %d games that reached r200' % (
            c, sum(1 for g in won if g['win']), len(won), sum(1 for g in G[c] if g not in won and g['win']), len(G[c]) - len(won)))

    say('')
    say('== 4. Chance and concentration ==')
    for c in CODES:
        gs = G[c]
        a, b, cc, d = q4(gs)
        say('  %s: difference of shares %.3f; bootstrap over games (2.5%%, 97.5%%, share at or below 0): %s' % (c, a / b - cc / d, boot_diff([unit(g) for g in gs])))
        for key in ('opp', 'map_key', 'evening'):
            acc = by_cluster(gs, key, unit)
            lo = []
            for name in acc:
                x = q4([g for g in gs if g[key] != name])
                lo.append((x[0] / x[1] - x[2] / x[3], name, x))
            mn = min(lo)
            say('     %s clusters (%d): bootstrap %s; leave one out: smallest difference %.3f without %s (ours %s, theirs %s)' % (
                key, len(acc), boot_diff(list(acc.values())), mn[0], mn[1], sh(mn[2][0], mn[2][1]), sh(mn[2][2], mn[2][3])))
            top = sorted(acc.items(), key=lambda kv: -kv[1][0])[:5]
            say('        most of our deaths: %s' % ', '.join('%s %d of %d' % (k, u[0], u[1]) for k, u in top))
        say('     three of our deaths removed: ours %s theirs %s, Fisher p %.4f' % (sh(a - 3, b - 3), sh(cc, d), fisher(a - 3, b - a, cc, d - cc)))

    say('')
    say('== 5. The board at the start of her fatal turn (deaths by wall or own body in r101-200) ==')
    for c in CODES:
        for s in (0, 1):
            items = [(g, s) for g in G[c] if alive100(g, s) and dies(g, s, 101, 200, (0, 1))]
            tally('%s %s, claim set' % (c, SIDE[s]), items)
    for s in (0, 1):
        items = [(g, s) for g in pool if alive100(g, s) and dies(g, s, 101, 200, (0, 1))]
        tally('both codes %s, claim set' % SIDE[s], items)
        tally('both codes %s, claim set without Portals' % SIDE[s], [(g, z) for g, z in items if g['map_key'] != 'Portals #1'])
        tally('both codes %s, claim set, Maze only' % SIDE[s], [(g, z) for g, z in items if g['map_key'] == 'Maze #1'])
    for s in (0, 1):
        wide = [(g, s) for g in free if dies(g, s, 101, 200, (0, 1))]
        say('  wider set, every free main or v31 game whatever its length: %s %d deaths (main %d, v31 %d); without Portals %d (main %d, v31 %d)' % (
            SIDE[s], len(wide), sum(1 for g, z in wide if g['code'] == 'main'), sum(1 for g, z in wide if g['code'] == 'v31'),
            sum(1 for g, z in wide if g['map_key'] != 'Portals #1'), sum(1 for g, z in wide if g['map_key'] != 'Portals #1' and g['code'] == 'main'),
            sum(1 for g, z in wide if g['map_key'] != 'Portals #1' and g['code'] == 'v31')))
        tally('wider set %s' % SIDE[s], wide)
        tally('wider set %s without Portals' % SIDE[s], [(g, z) for g, z in wide if g['map_key'] != 'Portals #1'])
    say('  every death of the claim set (game, layout, code, side, round, reason, N E S W at turn start, free tiles, length, split in 10 rounds, steps asked/taken, own and enemy dragons alive, won):')
    for s in (0, 1):
        for g in pool:
            if alive100(g, s) and dies(g, s, 101, 200, (0, 1)):
                q = g['qdeath'][s]
                say('      %d %-16s %-4s %-6s r%-3d %-8s %-14s free %d len %d split10 %s steps %d/%d dragons %d/%d %s' % (
                    g['game'], g['map_key'], g['code'], SIDE[s], q['round'], REASON[q['reason']], ' '.join(q.get('start_cls') or []), q.get('start_legal', -1),
                    q['length'], 'yes' if split10(g, s) else 'no', q.get('ndirs', 0), q.get('used', 0),
                    q['alive_us'] if s == 0 else q['alive_them'], q['alive_them'] if s == 0 else q['alive_us'], 'won' if g['win'] else 'lost'))

    say('')
    say('== 6. Plainer explanation: is it the trap or the way a trapped queen ends her turn? ==')
    say('  every death in r101-200 of a queen alive after r100, games that reached r200, by what the engine recorded and whether she had a free tile at turn start')
    for c in CODES:
        for s in (0, 1):
            n = sum(1 for g in G[c] if alive100(g, s))
            rc = Counter()
            for g in G[c]:
                q = g['qdeath'][s]
                if not alive100(g, s) or q is None or not 101 <= q['round'] <= 200:
                    continue
                if not q['actor']:
                    rc['rammed by an enemy head' if q.get('killer_side') == 1 - s else 'rammed by a head of her own team'] += 1
                elif q['reason'] == 3:
                    rc['head-on as the mover, ' + ('no free tile' if q.get('start_legal') == 0 else 'free tile available')] += 1
                else:
                    rc[REASON[q['reason']] + ', ' + ('no free tile' if q.get('start_legal') == 0 else 'free tile available')] += 1
            say('  %s %s (%d queens alive at r100, %d deaths): %s' % (c, SIDE[s], n, sum(rc.values()), dict(sorted(rc.items(), key=lambda kv: -kv[1]))))
    for c in CODES:
        line(c + ' mover with no free tile, any reason', G[c], tunit)
    line('both codes mover with no free tile, any reason', pool, tunit)
    for c in CODES:
        line(c + ' no free tile, without Maze', [g for g in G[c] if g['map_key'] != 'Maze #1'], tunit)
        line(c + ' no free tile, without Maze, Portals, weakhold', [g for g in G[c] if g['map_key'] not in three], tunit)
        line(c + ' no free tile, Maze only', [g for g in G[c] if g['map_key'] == 'Maze #1'], tunit)
        a, b, cc, d = q4(G[c], tunit)
        say('     bootstrap of the difference over games %s, over opponents %s, over layouts %s' % (
            boot_diff([tunit(g) for g in G[c]]), boot_diff(list(by_cluster(G[c], 'opp', tunit).values())), boot_diff(list(by_cluster(G[c], 'map_key', tunit).values()))))
    for label, gs in (('main', G['main']), ('v31', G['v31'])):
        acc = by_cluster(gs, 'map_key', tunit)
        say('  %s no-free-tile deaths per layout: %s' % (label, '; '.join('%s %d/%d v %d/%d' % (k, u[0], u[1], u[2], u[3]) for k, u in sorted(acc.items(), key=lambda kv: -kv[1][0] - kv[1][2]) if u[0] or u[2])))
    for c in CODES:
        for s in (0, 1):
            oc = Counter()
            nturn = 0
            for g in G[c]:
                nturn += g['qturns'][s][1]
                for r, out in g['zero_turns'][s]:
                    if 101 <= r <= 200:
                        oc[out] += 1
            say('  %s %s: queen turn starts in r101-200 %d; with no free tile %d; how those turns ended %s (d0 wall, d1 own body, d2 other body, d3 head-on, d4 no valid action)' % (
                c, SIDE[s], nturn, sum(oc.values()), dict(sorted(oc.items()))))
    for c in CODES:
        for s in (0, 1):
            hist = [0] * 5
            for g in G[c]:
                for z in range(5):
                    hist[z] += g['legal_hist'][s][1][z]
            tot = sum(hist)
            say('  %s %s: free tiles at queen turn start in r101-200: none %.4f, one %.3f, two %.3f, three %.3f (of %d turn starts)' % (
                c, SIDE[s], hist[0] / tot, hist[1] / tot, hist[2] / tot, hist[3] / tot, tot))
    say('  the same trap count in the other windows, full games (mover with no free tile, any reason): see section 3')

    say('')
    say('== 7. Compare with rows.jsonl (read only here) ==')
    rows = []
    for ln in Path('data/analysis/ladder/rows.jsonl').read_text().splitlines():
        if ln.strip():
            rows.append(json.loads(ln))
    for c in CODES:
        rs = [r for r in rows if r['our_code'] == c and not maps[r['map_key']]['queen_spawn_dead_end'] and r['last_round'] >= 200]
        out = []
        for name in ('us', 'them'):
            n = sum(1 for r in rs if r['queen'][name]['death_round'] is None or r['queen'][name]['death_round'] > 100)
            k = sum(1 for r in rs if r['queen'][name]['death_round'] is not None and 101 <= r['queen'][name]['death_round'] <= 200 and r['queen'][name]['death_cause'] in ('wall', 'own body'))
            out.append(sh(k, n))
        say('  rows.jsonl %s: games %d, ours %s, theirs %s' % (c, len(rs), out[0], out[1]))

    f = open(P + 'f37-numbers.txt', 'w')
    f.write('\n'.join(LINES) + '\n')
    f.close()


main()
