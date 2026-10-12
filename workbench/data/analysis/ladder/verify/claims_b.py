#!/usr/bin/env python3
"""Verifier counts for the 03:25 queue, part 2 (F10, F8, F15), from x2-*.jsonl written by extract2.py.
Usage: python3 claims_b.py <F10|F8|F15>"""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
from statistics import median
from itertools import combinations
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
CUT = '2026-10-06T14:48:15'
BANDS = ('<1700', '1700-1899', '1900-2099', '2100+')
LINES = []


def out(*a):
    s = ' '.join(str(x) for x in a)
    print(s)
    LINES.append(s)


def load():
    games = []
    for k in range(6):
        for line in (V / ('x2-%d.jsonl' % k)).read_text().splitlines():
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
        g['half'] = 'first' if g['completedAt'][:19] < CUT else 'second'
        g['opp'] = '%s (%s)' % (g.get('opponent'), g.get('opponentId'))
        k = g.get('at_kst') or ''
        hour = int(k[11:13]) if k else 0
        g['evening'] = k[5:10] + ('a' if hour < 12 else 'b')
    return order, bad


def pct(k, n):
    return 'n/a' if not n else '%.3f' % (k / n)


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


def bs(gs, fn, n=1000):
    if not gs:
        return 'no games'
    v = fn(gs)
    lo, hi = boot(gs, fn, n)
    if v is None or lo is None:
        return 'n/a'
    return '%.3f (game bootstrap 95%% %.3f to %.3f)' % (v, lo, hi)


def perm(g1, g2, fn, n=2000, seed=11):
    rng = random.Random(seed)
    obs = fn(g1) - fn(g2)
    pool = g1 + g2
    hit = 0
    for _ in range(n):
        rng.shuffle(pool)
        a, b = fn(pool[:len(g1)]), fn(pool[len(g1):])
        if a is None or b is None:
            continue
        if abs(a - b) >= abs(obs) - 1e-12:
            hit += 1
    return obs, hit, n


def eaten(g, lo, hi):
    return sum(g['eat']['us'][lo:hi + 1]), sum(g['eat']['them'][lo:hi + 1])


def pooled(key):
    def fn(gs):
        u = t = 0
        for g in gs:
            u += g[key][0]
            t += g[key][1]
        return u / (u + t) if u + t else None
    return fn


def flush(name):
    if name == 'F10':
        f = open(P + 'f10-numbers.txt', 'w')
    elif name == 'F8':
        f = open(P + 'f8-numbers.txt', 'w')
    else:
        f = open(P + 'f15-numbers.txt', 'w')
    f.write('\n'.join(LINES) + '\n')
    f.close()


# ---------------------------------------------------------------- F10
FOUR = ('Tower Defense', 'Stripes', 'Trauma', 'Queen Of Spades')


def nth(g, s, k):
    v = g['splits'][s]
    return v[k] if len(v) > k else 500


def f10(games):
    allg = [g for g in games if g['code'] in ('main', 'v31')]
    pool = [g for g in allg if g['last_round'] >= 50]
    for g in pool:
        g['p'] = eaten(g, 0, 50)
    fp = pooled('p')
    out('F10 recount from raw replays. Pearls by r50 = meals with raw round <= 50. Games that reached raw round 50 only.')
    keep = {}
    for code in ('main', 'v31'):
        cg = [g for g in pool if g['code'] == code]
        out('[%s] games %d of %d reached raw round 50' % (code, len(cg), sum(1 for g in allg if g['code'] == code)))
        tab = defaultdict(list)
        for g in cg:
            tab[g['map_key']].append(g)
        info = {}
        for k, gs in tab.items():
            info[k] = (len(gs), median(sum(g['p']) for g in gs), fp(gs), gs[0]['start']['us'])
        out('[%s] per layout (dragons per side at start, games, median pearls both sides by r50, our share, class):' % code)
        for k, v in sorted(info.items(), key=lambda kv: kv[1][1]):
            cls = 'unclassed (under 5 games)' if v[0] < 5 else 'SCARCE' if v[1] < 30 else 'other'
            out('   %-22s start %2d games %3d median %6.1f share %.3f %s' % (k, v[3], v[0], v[1], v[2] or 0, cls))
        for cutoff in (20, 25, 30, 40, 50):
            sk = [k for k, v in info.items() if v[0] >= 5 and v[1] < cutoff]
            ok = [k for k, v in info.items() if v[0] >= 5 and v[1] >= cutoff]
            S = [g for g in cg if g['map_key'] in sk]
            O = [g for g in cg if g['map_key'] in ok]
            if cutoff == 30:
                keep[code] = (S, O)
                out('[%s] cutoff 30: scarce layouts %d, games %d, pearls ours %d theirs %d, share %s' % (code, len(sk), len(S), sum(g['p'][0] for g in S), sum(g['p'][1] for g in S), bs(S, fp)))
                out('[%s] cutoff 30: other layouts %d, games %d, pearls ours %d theirs %d, share %s' % (code, len(ok), len(O), sum(g['p'][0] for g in O), sum(g['p'][1] for g in O), bs(O, fp)))
                obs, hit, n = perm(S, O, fp)
                out('[%s] scarce minus other = %.3f; game-label permutation: %d of %d shuffles give a gap this large' % (code, obs, hit, n))
                out('[%s] scarce layouts: %s' % (code, sorted(sk)))
            else:
                out('[%s] cutoff %d: scarce layouts %d games %d share %.3f | other layouts %d games %d share %.3f'
                    % (code, cutoff, len(sk), len(S), fp(S) or 0, len(ok), len(O), fp(O) or 0))
        four = [g for g in cg if g['map'] in FOUR]
        out('[%s] the four named layouts together: games %d, ours %d theirs %d, share %s' % (code, len(four), sum(g['p'][0] for g in four), sum(g['p'][1] for g in four), bs(four, fp)))
        rest = [g for g in cg if g['map'] not in FOUR]
        out('[%s] all other layouts together: games %d, share %s' % (code, len(rest), bs(rest, fp)))
        for name in FOUR:
            gs = [g for g in four if g['map'] == name]
            out('[%s]    %-16s games %3d ours %4d theirs %4d share %s; games with our share under 0.5: %d' % (
                code, name, len(gs), sum(g['p'][0] for g in gs), sum(g['p'][1] for g in gs), bs(gs, fp, 500),
                sum(1 for g in gs if sum(g['p']) and g['p'][0] / sum(g['p']) < 0.5)))
        for b in BANDS:
            bg = [g for g in four if g['band'] == b]
            og = [g for g in rest if g['band'] == b]
            out('[%s band %s] four layouts: games %d ours %d theirs %d share %s | other layouts: games %d share %s'
                % (code, b, len(bg), sum(g['p'][0] for g in bg), sum(g['p'][1] for g in bg), bs(bg, fp, 1000), len(og), ('%.3f' % fp(og)) if og and fp(og) is not None else 'n/a'))
        out('[%s] split rounds per layout, median over games reaching r50, ours/theirs (first, second, third; 500 = never):' % code)
        for name in FOUR + ('Maze', 'Trophy', 'weakhold'):
            gs = [g for g in cg if g['map'] == name]
            if gs:
                out('[%s]    %-16s games %3d: %s' % (code, name, len(gs), ', '.join('%s/%s' % (median(nth(g, 'us', k) for g in gs), median(nth(g, 'them', k) for g in gs)) for k in range(3))))
        out('')
    out('--- checks on the 1700-1899 statement')
    mb = [g for g in pool if g['code'] == 'main' and g['map'] in FOUR and g['band'] == '1700-1899']
    mc = [g for g in pool if g['code'] == 'main' and g['map'] in FOUR and g['band'] == '1900-2099']
    vb = [g for g in pool if g['code'] == 'v31' and g['map'] in FOUR and g['band'] == '1700-1899']
    vc = [g for g in pool if g['code'] == 'v31' and g['map'] in FOUR and g['band'] == '1900-2099']
    for la, a, lb, b in (('main 1700-1899', mb, 'main 1900-2099', mc), ('main 1700-1899', mb, 'v31 1700-1899', vb), ('main 1900-2099', mc, 'v31 1900-2099', vc)):
        obs, hit, n = perm(a, b, fp)
        out('%s minus %s on the four layouts = %.3f; permutation of games: %d of %d shuffles as large' % (la, lb, obs, hit, n))
    for label, gs in (('main 1700-1899', mb), ('main 1900-2099', mc), ('v31 1700-1899', vb), ('v31 1900-2099', vc)):
        out('[%s four layouts] by layout (games, ours, theirs, share): ' % label + '; '.join(
            '%s %d %d %d %.3f' % (name, len([g for g in gs if g['map'] == name]), sum(g['p'][0] for g in gs if g['map'] == name),
                                  sum(g['p'][1] for g in gs if g['map'] == name), fp([g for g in gs if g['map'] == name]) or 0) for name in FOUR))
        opp = defaultdict(list)
        for g in gs:
            opp[g['opp']].append(g)
        out('[%s four layouts] by opponent (games, share): ' % label + '; '.join('%s %d %.3f' % (k, len(v), fp(v) or 0) for k, v in sorted(opp.items(), key=lambda kv: -len(kv[1]))))
        vals = [fp([g for g in gs if g['opp'] != k]) for k in opp if len(opp) > 1]
        if vals:
            out('[%s four layouts] leave one opponent out: share %.3f to %.3f' % (label, min(vals), max(vals)))
        top = sorted(gs, key=lambda g: g['p'][1] - g['p'][0])[:3]
        out('[%s four layouts] without our three best games %s: share %.3f' % (label, [(g['game'], g['map'], g['p']) for g in top], fp([g for g in gs if g not in top]) or 0))
        won = [g for g in gs if sum(g['p']) and g['p'][0] / sum(g['p']) >= 0.5]
        out('[%s four layouts] games where we ate at least half by r50: %d of %d; game wins %d of %d' % (label, len(won), len(gs), sum(g['win'] for g in gs), len(gs)))
    out('main 1700-1899 four layouts, each game (game, layout, opponent, ours, theirs): ' + '; '.join('%d %s %s %d %d' % (g['game'], g['map'], g['opp'], g['p'][0], g['p'][1]) for g in mb))
    w = Counter()
    for g in pool:
        if g['code'] == 'main' and g['map'] in FOUR:
            w[g['band'], g['map']] += 1
    out('main four-layout games by band and layout:', dict(w))
    for code in ('main', 'v31'):
        for b in ('1700-1899', '1900-2099'):
            gs = [g for g in pool if g['code'] == code and g['map'] in FOUR and g['band'] == b]
            parts = []
            for name in FOUR:
                ng = [g for g in gs if g['map'] == name]
                if ng:
                    parts.append('%s %d games first split %s/%s' % (name, len(ng), median(nth(g, 'us', 0) for g in ng), median(nth(g, 'them', 0) for g in ng)))
            out('[%s band %s] first split ours/theirs: ' % (code, b) + '; '.join(parts))
    flush('F10')


# ---------------------------------------------------------------- F8
def f8(games):
    pool = [g for g in games if g['code'] in ('main', 'v31')]
    for g in pool:
        m = g['meetings']
        g['m'] = (sum(1 for x in m if x[1] == 'them'), sum(1 for x in m if x[1] == 'us'))
        g['ml'] = (sum(x[2] for x in m), sum(x[3] for x in m))
    fm = pooled('m')

    def ratio(gs):
        u = sum(g['ml'][0] for g in gs)
        t = sum(g['ml'][1] for g in gs)
        return u / t if t else None

    def block(label, gs):
        n = sum(sum(g['m']) for g in gs)
        out('[%s] games %d, meetings %d, their mover share %s, length lost ours %d theirs %d, ours/theirs %s'
            % (label, len(gs), n, bs(gs, fm, 500), sum(g['ml'][0] for g in gs), sum(g['ml'][1] for g in gs), bs(gs, ratio, 500)))
    out('F8 recount from raw replays. Meeting = two reason-3 deaths in one turn, first the non-actor (victim), second the actor (mover), different teams.')
    out('order check: meetings where the first death is the actor or the second is not: %d of %d; same-team head-ons (left out): %d'
        % (sum(1 for g in pool for x in g['meetings'] if not x[4]), sum(len(g['meetings']) for g in pool), sum(g['same_team_head_on'] for g in pool)))
    main = [g for g in pool if g['code'] == 'main']
    v31 = [g for g in pool if g['code'] == 'v31']
    block('main', main)
    for b in BANDS:
        block('main band %s' % b, [g for g in main if g['band'] == b])
    block('main first half', [g for g in main if g['half'] == 'first'])
    block('main second half', [g for g in main if g['half'] == 'second'])
    block('v31', v31)
    for b in BANDS:
        block('v31 band %s' % b, [g for g in v31 if g['band'] == b])
    out('')
    out('--- checks')
    for code, cg in (('main', main), ('v31', v31)):
        opp = defaultdict(list)
        for g in cg:
            opp[g['opp']].append(g)
        big = [(k, v) for k, v in opp.items() if len(v) >= 5]
        out('[%s] opponents with 5+ games: %d; with their mover share above 0.5: %d' % (code, len(big), sum(1 for k, v in big if (fm(v) or 0) > 0.5)))
        out('[%s]    ' % code + '; '.join('%s %d games %d meetings %.3f' % (k, len(v), sum(sum(g['m']) for g in v), fm(v) or 0) for k, v in sorted(big, key=lambda kv: fm(kv[1]) or 0)))
        vals = [fm([g for g in cg if g['opp'] != k]) for k in opp]
        out('[%s] leave one opponent out: share %.3f to %.3f' % (code, min(vals), max(vals)))
        mp = defaultdict(list)
        for g in cg:
            mp[g['map_key']].append(g)
        out('[%s] per layout (games, meetings, share, ours/theirs length): ' % code + '; '.join(
            '%s %d %d %.3f %.2f' % (k, len(v), sum(sum(g['m']) for g in v), fm(v) or 0, ratio(v) or 0) for k, v in sorted(mp.items(), key=lambda kv: fm(kv[1]) or 0)))
        out('[%s] layouts with share above 0.5: %d of %d; layouts where we lose more length than they do: %d'
            % (code, sum(1 for v in mp.values() if (fm(v) or 0) > 0.5), len(mp), sum(1 for v in mp.values() if (ratio(v) or 0) > 1)))
        ev = defaultdict(list)
        for g in cg:
            ev[g['evening']].append(g)
        out('[%s] by evening (games, meetings, share): ' % code + '; '.join('%s %d %d %.3f' % (k, len(v), sum(sum(g['m']) for g in v), fm(v) or 0) for k, v in sorted(ev.items())))
        top = sorted(cg, key=lambda g: g['m'][1] - g['m'][0])[:3]
        out('[%s] without the three games with the biggest surplus of their moves %s: share %.3f'
            % (code, [(g['game'], g['map'], g['m']) for g in top], fm([g for g in cg if g not in top])))
        wm = [g for g in cg if sum(g['m']) >= 5]
        out('[%s] game level: games with 5+ meetings %d; their mover share above 0.5 in %d, below in %d, exactly half %d; median per-game share %.3f'
            % (code, len(wm), sum(1 for g in wm if g['m'][0] > g['m'][1]), sum(1 for g in wm if g['m'][0] < g['m'][1]),
               sum(1 for g in wm if g['m'][0] == g['m'][1]), median(g['m'][0] / sum(g['m']) for g in wm)))
        for lo, hi in ((0, 99), (100, 199), (200, 299), (300, 499)):
            xs = [x for g in cg for x in g['meetings'] if lo <= x[0] <= hi]
            if xs:
                out('[%s] raw rounds %d-%d: meetings %d, their mover share %.3f, length ours %d theirs %d (%.2f)'
                    % (code, lo, hi, len(xs), sum(1 for x in xs if x[1] == 'them') / len(xs), sum(x[2] for x in xs), sum(x[3] for x in xs),
                       sum(x[2] for x in xs) / max(1, sum(x[3] for x in xs))))
        xs = [x for g in cg for x in g['meetings']]
        tm = [x for x in xs if x[1] == 'them']
        um = [x for x in xs if x[1] == 'us']
        out('[%s] when they move (%d): our victim mean length %.2f, their mover mean %.2f; when we move (%d): our mover mean %.2f, their victim mean %.2f'
            % (code, len(tm), sum(x[2] for x in tm) / len(tm), sum(x[3] for x in tm) / len(tm), len(um), sum(x[2] for x in um) / len(um), sum(x[3] for x in um) / len(um)))
        for cap in (1, 2, 3):
            out('[%s]    meetings where both dragons are longer than %d: %d, their mover share %.3f; where our dragon is at most %d long: %d, share %.3f'
                % (code, cap, sum(1 for x in xs if x[2] > cap and x[3] > cap),
                   sum(1 for x in xs if x[2] > cap and x[3] > cap and x[1] == 'them') / max(1, sum(1 for x in xs if x[2] > cap and x[3] > cap)),
                   cap, sum(1 for x in xs if x[2] <= cap), sum(1 for x in xs if x[2] <= cap and x[1] == 'them') / max(1, sum(1 for x in xs if x[2] <= cap))))
        out('[%s] length distribution lost, ours: %s' % (code, dict(sorted(Counter(min(x[2], 8) for x in xs).items()))))
        out('[%s] length distribution lost, theirs: %s' % (code, dict(sorted(Counter(min(x[3], 8) for x in xs).items()))))
        out('[%s] queen as victim: ours %d, theirs %d; queen as mover: ours %d, theirs %d'
            % (code, sum(1 for x in tm if x[5]), sum(1 for x in um if x[5]), sum(1 for x in um if x[6]), sum(1 for x in tm if x[6])))
        al = [(g['marks']['100']['us'][0], g['marks']['100']['them'][0]) for g in cg if '100' in g['marks']]
        out('[%s] for scale, dragons alive after r100 pooled: ours %d theirs %d (our share %.3f)' % (code, sum(a for a, b in al), sum(b for a, b in al), sum(a for a, b in al) / max(1, sum(a + b for a, b in al))))
        out('')
    flush('F8')


# ---------------------------------------------------------------- F15
def f15(games):
    pool = [g for g in games if g['code'] in ('main', 'v31')]
    for g in pool:
        g['d'] = [x for x in g['r4'] if x[0] == 'us']
        g['dt'] = [x for x in g['r4'] if x[0] == 'them']
        d = g['d']
        g['k3'] = (sum(1 for x in d if x[4] is not None and x[4] <= 3), sum(1 for x in d if x[4] is None or x[4] > 3))
        g['k8'] = (sum(1 for x in d if x[4] is not None and x[4] <= 8), sum(1 for x in d if x[4] is None or x[4] > 8))
        g['ke'] = (sum(x[10] for x in d), sum(x[9] - x[10] for x in d))
        g['kt'] = (sum(x[11] for x in d), sum(x[9] - x[11] for x in d))

    def block(label, gs, key='d', mine=10, theirs=11):
        d = [x for g in gs for x in g[key]]
        n = len(d)
        if not n:
            out('[%s] no such deaths in %d games' % (label, len(gs)))
            return
        drop = sum(x[9] for x in d)
        out('[%s] games %d, deaths %d, within 3: %s, within 8: %s, no dragon twice as long: %s (%d), length given up %d, pearls dropped %d'
            % (label, len(gs), n, pct(sum(1 for x in d if x[4] is not None and x[4] <= 3), n), pct(sum(1 for x in d if x[4] is not None and x[4] <= 8), n),
               pct(sum(1 for x in d if x[4] is None), n), sum(1 for x in d if x[4] is None), sum(x[2] for x in d), drop))
        out('[%s]    drop eaten within 15 rounds by own side %d (%s), by the other side %d (%s), later %d, never %d, game ended first %d; before r300: %d, before r200: %d, first at r%d'
            % (label, sum(x[mine] for x in d), pct(sum(x[mine] for x in d), drop), sum(x[theirs] for x in d), pct(sum(x[theirs] for x in d), drop),
               sum(x[12] for x in d), sum(x[13] for x in d), sum(x[14] for x in d), sum(1 for x in d if x[1] < 300), sum(1 for x in d if x[1] < 200), min(x[1] for x in d)))
    out('F15 recount from raw replays. Deaths with reason 4 of our dragons; distance = wrapped Manhattan head to head; big = our living dragon at least twice as long.')
    main = [g for g in pool if g['code'] == 'main']
    v31 = [g for g in pool if g['code'] == 'v31']
    block('main', main)
    for b in BANDS:
        block('main band %s' % b, [g for g in main if g['band'] == b])
    block('main first half', [g for g in main if g['half'] == 'first'])
    block('main second half', [g for g in main if g['half'] == 'second'])
    block('v31', v31)
    for b in BANDS:
        block('v31 band %s' % b, [g for g in v31 if g['band'] == b])
    out('')
    out('--- checks')
    for code, cg in (('main', main), ('v31', v31)):
        d = [x for g in cg for x in g['d']]
        n = len(d)
        out('[%s] what the dying dragon had sent (kind 2 = no action in the shared decoder): %s; of them the queen: %d; dying outside its own turn: %d'
            % (code, dict(Counter(x[3] for x in d)), sum(x[15] for x in d), sum(1 for x in d if x[3] == 'not the actor')))
        out('[%s] game bootstrap: within 3 %s; within 8 %s' % (code, bs(cg, pooled('k3'), 300), bs(cg, pooled('k8'), 300)))
        out('[%s] game bootstrap: drop eaten by us %s; by them %s' % (code, bs(cg, pooled('ke'), 300), bs(cg, pooled('kt'), 300)))
        out('[%s] length of the dying dragon: %s' % (code, dict(sorted(Counter(min(x[2], 8) for x in d).items()))))
        out('[%s] our other living dragons at that moment: mean %.1f, of them at least twice as long: mean %.1f; deaths with exactly one such dragon: %d'
            % (code, sum(x[8] for x in d) / n, sum(x[7] for x in d) / n, sum(1 for x in d if x[7] == 1)))
        out('[%s] controls: any own head within 3: %s, within 8: %s; nearest ENEMY head within 3: %s, within 8: %s'
            % (code, pct(sum(1 for x in d if x[5] is not None and x[5] <= 3), n), pct(sum(1 for x in d if x[5] is not None and x[5] <= 8), n),
               pct(sum(1 for x in d if x[6] is not None and x[6] <= 3), n), pct(sum(1 for x in d if x[6] is not None and x[6] <= 8), n)))
        out('[%s] distance to the big dragon: %s' % (code, dict(sorted(Counter('none' if x[4] is None else str(min(x[4], 9)) if x[4] < 9 else '9+' for x in d).items()))))
        out('[%s] by 50-round bin: %s' % (code, dict(sorted(Counter(x[1] // 50 * 50 for x in d).items()))))
        gw = [g for g in cg if g['d']]
        out('[%s] games with at least one such death: %d of %d; games reaching r200: %d; per game median %s, max %d'
            % (code, len(gw), len(cg), sum(1 for g in cg if g['last_round'] >= 200), median(len(g['d']) for g in gw), max(len(g['d']) for g in gw)))
        for key in ('opp', 'map_key', 'evening'):
            tab = defaultdict(list)
            for g in cg:
                tab[g[key]].append(g)
            rows = [(k, sum(len(g['d']) for g in v), pooled('k8')(v), pooled('ke')(v), pooled('kt')(v)) for k, v in tab.items()]
            rows = [r for r in rows if r[1] >= 50]
            out('[%s] by %s, groups with 50+ deaths: %d; within 8 from %.3f to %.3f; eaten by us from %.3f to %.3f; eaten by them from %.3f to %.3f'
                % (code, key, len(rows), min(r[2] for r in rows), max(r[2] for r in rows), min(r[3] for r in rows), max(r[3] for r in rows),
                   min(r[4] for r in rows), max(r[4] for r in rows)))
            if key != 'opp':
                out('[%s]    ' % code + '; '.join('%s %d %.3f %.3f %.3f' % r for r in sorted(rows, key=lambda r: r[3])))
        top = sorted(cg, key=lambda g: -len(g['d']))[:3]
        rest = [g for g in cg if g not in top]
        out('[%s] without the three games with most such deaths %s: within 8 %.3f, eaten by us %.3f, by them %.3f'
            % (code, [(g['game'], g['map'], len(g['d'])) for g in top], pooled('k8')(rest), pooled('ke')(rest), pooled('kt')(rest)))
        far = [x for x in d if x[4] is None or x[4] > 8]
        near = [x for x in d if x[4] is not None and x[4] <= 3]
        out('[%s] drop eaten by us within 15 when the big dragon is within 3: %s of %d pearls; when beyond 8 or absent: %s of %d pearls (by them %s)'
            % (code, pct(sum(x[10] for x in near), sum(x[9] for x in near)), sum(x[9] for x in near),
               pct(sum(x[10] for x in far), sum(x[9] for x in far)), sum(x[9] for x in far), pct(sum(x[11] for x in far), sum(x[9] for x in far))))
        out('[%s] THEIR reason-4 deaths, same measures from their side:' % code)
        block('%s opponents' % code, cg, 'dt', 11, 10)
        dt = [x for g in cg for x in g['dt']]
        out('[%s]    what their dying dragons had sent: %s' % (code, dict(Counter(x[3] for x in dt).most_common())))
        out('')
    flush('F15')


def main():
    games, bad = load()
    out('games loaded', len(games), 'errors', len(bad))
    out('')
    what = sys.argv[1]
    if what == 'F10':
        f10(games)
    elif what == 'F8':
        f8(games)
    else:
        f15(games)


main()
