#!/usr/bin/env python3
"""Verifier counts for the 03:25 queue, part 1 (F13, F11), from x2-*.jsonl written by extract2.py.
Usage: python3 claims_a.py <F13|F11|rows>"""
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
    if name == 'F13':
        f = open(P + 'f13-numbers.txt', 'w')
    elif name == 'F11':
        f = open(P + 'f11-numbers.txt', 'w')
    else:
        f = open(P + 'rows-compare.txt', 'w')
    f.write('\n'.join(LINES) + '\n')
    f.close()


# ---------------------------------------------------------------- F13
DEAD = ('Schooltime', 'Slithery Fight')
REASON = ('wall', 'own body', 'other dragon body', 'head-on', 'other')


def qround(g, s):
    d = g['queen_death'][s]
    return None if d is None else d['round']


def qcause(g, s):
    d = g['queen_death'][s]
    if d is None:
        return 'none'
    if d['reason'] == 3:
        if d['role'] == 'victim':
            return 'rammed by enemy' if d['other_side'] != s else 'rammed by own team'
        if d['role'] == 'mover':
            return 'she rammed enemy' if d['other_side'] != s else 'she rammed own team'
        return 'head-on unresolved'
    return REASON[d['reason']]


def split13(gs):
    ft, fu, same, neither = [], [], [], []
    for g in gs:
        ro, rt = qround(g, 'us'), qround(g, 'them')
        if ro is None and rt is None:
            neither.append(g)
        elif rt is not None and (ro is None or ro > rt):
            ft.append(g)
        elif ro is not None and (rt is None or rt > ro):
            fu.append(g)
        else:
            same.append(g)
    return ft, fu, same, neither


def block13(label, gs):
    ft, fu, same, neither = split13(gs)
    die = [g for g in ft if qround(g, 'us') is not None]
    live = [g for g in ft if qround(g, 'us') is None]
    out('[%s] games %d (wins %d) | theirs first %d | ours first %d | same round %d | neither dies %d'
        % (label, len(gs), sum(g['win'] for g in gs), len(ft), len(fu), len(same), len(neither)))
    out('   theirs first: ours dies later', ws(len(die), len(ft)), '| wins among', ws(sum(g['win'] for g in die), len(die)),
        '| survives %d, wins %d' % (len(live), sum(g['win'] for g in live)))
    out('   causes of our queen death (dies later):', dict(Counter(qcause(g, 'us') for g in die).most_common()))
    mdie = [g for g in fu if qround(g, 'them') is not None]
    mlive = [g for g in fu if qround(g, 'them') is None]
    out('   mirror (ours first): theirs dies later', ws(len(mdie), len(fu)), '| our wins among', ws(sum(g['win'] for g in mdie), len(mdie)),
        '| theirs survives %d, our wins %d' % (len(mlive), sum(g['win'] for g in mlive)))
    out('   causes of their queen death (mirror, dies later):', dict(Counter(qcause(g, 'them') for g in mdie).most_common()))
    return ft, fu, die, live, mdie, mlive


def hazard(gs, me, other):
    expo = Counter()
    dead = Counter()
    for g in gs:
        rm, rx = qround(g, me), qround(g, other)
        last = g['last_round'] if rm is None else rm
        for r in range(last + 1):
            st = 'after' if rx is not None and rx < r else 'before'
            expo[r // 100, st] += 1
        if rm is not None:
            st = 'after' if rx is not None and rx < rm else 'before'
            dead[rm // 100, st] += 1
    return expo, dead


def f13(games):
    allg = [g for g in games if g['code'] in ('main', 'v31')]
    out('F13 recount from raw replays. Queen = lowest initial dragon id of a side. Rounds are raw.')
    out('layouts of the excluded names:', dict(Counter(g['map_key'] for g in allg if g['map'] in DEAD)))
    out('queen deaths on excluded layouts (ours, theirs):', sum(1 for g in allg if g['map'] in DEAD and qround(g, 'us') is not None),
        sum(1 for g in allg if g['map'] in DEAD and qround(g, 'them') is not None), 'in', sum(1 for g in allg if g['map'] in DEAD), 'games')
    pool = [g for g in allg if g['map'] not in DEAD]
    res = {}
    for code in ('main', 'v31'):
        cg = [g for g in pool if g['code'] == code]
        res[code] = block13(code, cg)
        for b in BANDS:
            block13('%s band %s' % (code, b), [g for g in cg if g['band'] == b])
        if code == 'main':
            block13('main first half (before %sZ)' % CUT, [g for g in cg if g['half'] == 'first'])
            block13('main second half', [g for g in cg if g['half'] == 'second'])
            out('   main games exactly on the cut second:', sum(1 for g in cg if g['completedAt'][:19] == CUT))
    out('')
    out('--- checks')
    for code in ('main', 'v31'):
        ft, fu, die, live, mdie, mlive = res[code]
        cg = [g for g in pool if g['code'] == code]
        out('[%s] survivors (ours alive, theirs dead): %d games, ended at r499 %d, earlier (elimination) %d, wins %d'
            % (code, len(live), sum(1 for g in live if g['last_round'] == 499), sum(1 for g in live if g['last_round'] < 499), sum(g['win'] for g in live)))
        out('[%s] our side: dies later %d of %d; their side in the mirror: %d of %d; Fisher two-sided p = %.3f'
            % (code, len(die), len(ft), len(mdie), len(fu), fisher(len(die), len(ft) - len(die), len(mdie), len(fu) - len(mdie))))
        out('[%s] when both queens die: we win %s after theirs-first, %s after ours-first; Fisher p = %.3f; all non-excluded games win rate %s'
            % (code, ws(sum(g['win'] for g in die), len(die)), ws(sum(g['win'] for g in mdie), len(mdie)),
               fisher(sum(g['win'] for g in die), len(die) - sum(g['win'] for g in die), sum(g['win'] for g in mdie), len(mdie) - sum(g['win'] for g in mdie)),
               ws(sum(g['win'] for g in cg), len(cg))))
        out('[%s] queen ever dies: ours %s, theirs %s' % (code, ws(sum(1 for g in cg if qround(g, 'us') is not None), len(cg)),
                                                       ws(sum(1 for g in cg if qround(g, 'them') is not None), len(cg))))
        for me, other in (('us', 'them'), ('them', 'us')):
            expo, dead = hazard(cg, me, other)
            parts = []
            for band in range(5):
                parts.append('r%d-%d before %d/%d=%.4f after %d/%d=%.4f' % (
                    band * 100, band * 100 + 99, dead[band, 'before'], expo[band, 'before'],
                    dead[band, 'before'] / expo[band, 'before'] if expo[band, 'before'] else 0,
                    dead[band, 'after'], expo[band, 'after'], dead[band, 'after'] / expo[band, 'after'] if expo[band, 'after'] else 0))
            out('[%s] death rate per queen-round of the %s queen, before / after the other queen is dead: ' % (code, 'our' if me == 'us' else 'their') + '; '.join(parts))
        gaps = sorted(qround(g, 'us') - qround(g, 'them') for g in die)
        out('[%s] theirs-first, ours dies later: their death round median %s, ours median %s, gap median %s, gaps under 25 rounds: %d, gaps of 100+: %d'
            % (code, median(qround(g, 'them') for g in die), median(qround(g, 'us') for g in die), median(gaps),
               sum(1 for x in gaps if x < 25), sum(1 for x in gaps if x >= 100)))
        out('[%s] theirs-first, ours survives: their death round median %s' % (code, median(qround(g, 'them') for g in live) if live else None))
        for key in ('opp', 'map_key', 'evening', 'band'):
            tab = defaultdict(lambda: [0, 0, 0])
            for g in ft:
                t = tab[g[key]]
                t[0] += 1
                if qround(g, 'us') is not None:
                    t[1] += 1
                    t[2] += g['win']
            out('[%s] theirs-first by %s (games, ours dies later, wins among those):' % (code, key),
                '; '.join('%s %d/%d/%d' % (k, v[0], v[1], v[2]) for k, v in sorted(tab.items(), key=lambda kv: -kv[1][0])))
            lo = []
            for k in tab:
                rest = [g for g in ft if g[key] != k]
                rd = [g for g in rest if qround(g, 'us') is not None]
                if rest and rd:
                    lo.append((len(rd) / len(rest), sum(g['win'] for g in rd) / len(rd)))
            if lo:
                out('[%s]    leave one %s out: dies-later share %.3f to %.3f, win share among them %.3f to %.3f'
                    % (code, key, min(x[0] for x in lo), max(x[0] for x in lo), min(x[1] for x in lo), max(x[1] for x in lo)))
        w = sum(g['win'] for g in die)
        out('[%s] drop three supporting games: dies later %s; wins among (three losses removed) %s'
            % (code, ws(len(die) - 3, len(ft) - 3), ws(w, len(die) - 3)))
        rl = [g['queen_death']['us'] for g in die if qcause(g, 'us') == 'rammed by enemy']
        out('[%s] rammed by enemy: %d; rammer was their queen %d (cannot be, she is dead); rammer length median %s; our queen length at death median %s (all causes %s)'
            % (code, len(rl), sum(1 for d in rl if d.get('other_is_queen')), median(d['other_length'] for d in rl) if rl else None,
               median(d['length'] for d in rl) if rl else None, median(g['queen_death']['us']['length'] for g in die) if die else None))
        out('[%s] our queen death causes in ALL non-excluded games where she dies:' % code,
            dict(Counter(qcause(g, 'us') for g in cg if qround(g, 'us') is not None).most_common()))
        out('[%s] their queen death causes in ALL non-excluded games where she dies:' % code,
            dict(Counter(qcause(g, 'them') for g in cg if qround(g, 'them') is not None).most_common()))
        out('')
    flush('F13')


# ---------------------------------------------------------------- F11
def f11(games):
    pool = [g for g in games if g['code'] in ('main', 'v31')]
    for g in pool:
        g['w'] = eaten(g, 101, 300)
        g['w0'] = eaten(g, 0, 100)
        g['w3'] = eaten(g, 301, 499)
        g['large'] = g['open_tiles'] >= 2000
        g['a100'] = tuple(g['marks']['100'][s][0] for s in ('us', 'them')) if '100' in g['marks'] else (0, 0)
        g['a200'] = tuple(g['marks']['200'][s][0] for s in ('us', 'them')) if '200' in g['marks'] else (0, 0)
        g['t100'] = tuple(g['marks']['100'][s][1] for s in ('us', 'them')) if '100' in g['marks'] else (0, 0)
    fw = pooled('w')
    out('F11 recount from raw replays. Share = our pearls / both sides, raw rounds 101-300, pooled (sum then divide).')
    lay = {}
    for g in pool:
        lay.setdefault(g['map_key'], [g['W'], g['H'], g['open_tiles'], g['start']['us'], 0])[4] += 1
    out('layouts (W, H, open tiles by my own count, dragons per side at start, games):')
    for k, v in sorted(lay.items(), key=lambda kv: -kv[1][2]):
        out('   %-22s %s%s' % (k, v, '  LARGE' if v[2] >= 2000 else ''))
    res = {}
    for code in ('main', 'v31'):
        cg = [g for g in pool if g['code'] == code]
        L = [g for g in cg if g['large']]
        O = [g for g in cg if not g['large']]
        res[code] = (L, O)
        for label, gs in (('large', L), ('other', O)):
            u = sum(g['w'][0] for g in gs)
            t = sum(g['w'][1] for g in gs)
            out('[%s %s] games %d, wins %d, pearls r101-300 ours %d theirs %d, share %s; games that never reached r101: %d'
                % (code, label, len(gs), sum(g['win'] for g in gs), u, t, bs(gs, fw), sum(1 for g in gs if g['last_round'] < 101)))
        obs, hit, n = perm(L, O, fw)
        out('[%s] large minus other = %.3f; game-label permutation: %d of %d shuffles give a gap this large' % (code, obs, hit, n))
        out('[%s] wins: large %s, other %s, Fisher p = %.4f' % (code, ws(sum(g['win'] for g in L), len(L)), ws(sum(g['win'] for g in O), len(O)),
                                                              fisher(sum(g['win'] for g in L), len(L) - sum(g['win'] for g in L), sum(g['win'] for g in O), len(O) - sum(g['win'] for g in O))))
        tab = {}
        for g in cg:
            t = tab.setdefault(g['map_key'], [0, 0, 0, g['large'], 0])
            t[0] += 1
            t[1] += g['w'][0]
            t[2] += g['w'][1]
            t[4] += g['win']
        rows = sorted(tab.items(), key=lambda kv: kv[1][1] / max(1, kv[1][1] + kv[1][2]))
        out('[%s] per layout, lowest share first (games, wins, ours, theirs, share):' % code)
        for rank, (k, v) in enumerate(rows):
            out('   %2d %-22s %3d %3d %6d %6d %.3f%s' % (rank + 1, k, v[0], v[4], v[1], v[2], v[1] / max(1, v[1] + v[2]), '  LARGE' if v[3] else ''))
        keys = list(tab)
        nl = sum(1 for k in keys if tab[k][3])
        lu = sum(tab[k][1] for k in keys if tab[k][3])
        lt = sum(tab[k][2] for k in keys if tab[k][3])
        target = lu / (lu + lt)
        le = tot = 0
        for combo in combinations(keys, nl):
            u = sum(tab[k][1] for k in combo)
            t = sum(tab[k][2] for k in combo)
            tot += 1
            if u / (u + t) <= target + 1e-12:
                le += 1
        out('[%s] layout-level check: of %d ways to pick %d of %d layouts, %d give a pooled share as low as the large set (%.3f)' % (code, tot, nl, len(keys), le, target))
        for b in BANDS:
            for label, gs in (('large', L), ('other', O)):
                bg = [g for g in gs if g['band'] == b]
                u = sum(g['w'][0] for g in bg)
                t = sum(g['w'][1] for g in bg)
                out('[%s band %s %s] games %d, ours %d theirs %d, share %s' % (code, b, label, len(bg), u, t, bs(bg, fw, 500)))
        for wname, key in (('r0-100', 'w0'), ('r301-499', 'w3')):
            out('[%s] other windows, %s: large %s, other %s' % (code, wname, bs(L, pooled(key), 300), bs(O, pooled(key), 300)))
        for wname, key in (('dragons alive after r100', 'a100'), ('dragons alive after r200', 'a200'), ('total length after r100', 't100')):
            out('[%s] our share of %s (pooled): large %.3f, other %.3f' % (code, wname, pooled(key)(L), pooled(key)(O)))
        ns = [g for g in L if g['map'] != 'Schooltime']
        out('[%s] large without Schooltime (the sealed-queen layouts): games %d, share %s' % (code, len(ns), bs(ns, fw, 500)))
        worst = sorted(L, key=lambda g: g['w'][0] - g['w'][1])[:3]
        rest = [g for g in L if g not in worst]
        out('[%s] large without the three games with the biggest deficit %s: share %.3f' % (code, [(g['game'], g['map'], g['w']) for g in worst], fw(rest)))
        for key in ('opp', 'evening'):
            tab2 = defaultdict(list)
            for g in L:
                tab2[g[key]].append(g)
            vals = []
            for k, gs in tab2.items():
                rest = [g for g in L if g[key] != k]
                if rest:
                    vals.append(fw(rest))
            out('[%s] large, leave one %s out: share %.3f to %.3f (%d groups)' % (code, key, min(vals), max(vals), len(tab2)))
            if key == 'evening':
                out('[%s] large by evening (games, share): ' % code + '; '.join('%s %d %.3f' % (k, len(gs), fw(gs) or 0) for k, gs in sorted(tab2.items())))
            else:
                big = [(k, gs) for k, gs in tab2.items() if len(gs) >= 3]
                out('[%s] opponents with 3+ large games: %d; of them with share under 0.45: %d; under 0.40: %d'
                    % (code, len(big), sum(1 for k, gs in big if (fw(gs) or 0) < 0.45), sum(1 for k, gs in big if (fw(gs) or 0) < 0.40)))
        gl = [g for g in L if sum(g['w']) > 0]
        go = [g for g in O if sum(g['w']) > 0]
        out('[%s] per-game share median: large %.3f (%d games with pearls), other %.3f (%d); large games with share under 0.5: %d'
            % (code, median(g['w'][0] / sum(g['w']) for g in gl), len(gl), median(g['w'][0] / sum(g['w']) for g in go), len(go),
               sum(1 for g in gl if g['w'][0] / sum(g['w']) < 0.5)))
        out('')
    flush('F11')


# ---------------------------------------------------------------- compare with rows.jsonl (only after counting)
def rows(games):
    mine = {g['game']: g for g in games}
    rr = {}
    for line in Path('data/analysis/ladder/rows.jsonl').read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            rr[r['game']] = r
    out('games: mine %d, rows.jsonl %d, in both %d' % (len(mine), len(rr), len(set(mine) - (set(mine) - set(rr)))))
    out('my codes:', dict(Counter(g['code'] for g in games)), '| rows our_code main/v31/other:',
        dict(Counter(r['our_code'] if r['our_code'] in ('main', 'v31') else 'other' for r in rr.values())))
    diff = Counter()
    n = 0
    for gid, g in mine.items():
        r = rr.get(gid)
        if r is None:
            diff['not in rows'] += 1
            continue
        rc = r['our_code'] if r['our_code'] in ('main', 'v31') else 'other'
        if rc != g['code']:
            diff['code'] += 1
        if r['map_key'] != g['map_key']:
            diff['map_key'] += 1
        if r['win'] != g['win']:
            diff['win'] += 1
        if (r['opponent_rating'] != g.get('opponentElo')):
            diff['rating'] += 1
        if r['time'] != g['completedAt']:
            diff['time'] += 1
        if g['code'] == 'other':
            continue
        n += 1
        if r['last_round'] != g['last_round']:
            diff['last_round'] += 1
        for s in ('us', 'them'):
            if r['queen'][s]['death_round'] != qround(g, s):
                diff['queen death round ' + s] += 1
            if r['pearls']['r101-300']['eaten'][s] != sum(g['eat'][s][101:301]):
                diff['pearls r101-300 ' + s] += 1
            if r['pearls']['r0-100']['eaten'][s] != sum(g['eat'][s][0:101]):
                diff['pearls r0-100 ' + s] += 1
            c50 = r['curves']['50']
            if c50 is not None and c50[s]['pearls'] != sum(g['eat'][s][0:51]):
                diff['pearls by r50 ' + s] += 1
            if (c50 is None) != (g['last_round'] < 50):
                diff['reached r50 flag ' + s] += 1
        if r['head_on']['count'] != len(g['meetings']):
            diff['head-on meetings'] += 1
        oth = sum(r['deaths'][w]['us']['other'] for w in r['deaths'])
        if oth != sum(1 for x in g['r4'] if x[0] == 'us'):
            diff['our reason-4 deaths'] += 1
        if not g['final_ok'] or g['drop_mismatch'] or g['anomalies']:
            diff['my own rebuild flags'] += 1
    out('main and v31 games compared field by field:', n)
    out('differences:', dict(diff) if diff else 'none')
    flush('rows')


def main():
    games, bad = load()
    out('games loaded', len(games), 'errors', len(bad), [b['game'] for b in bad][:10])
    out('codes:', dict(Counter(g['code'] for g in games)), '| unranked:', sum(1 for g in games if not g.get('ranked')),
        '| no battle record:', sum(1 for g in games if g.get('opponentElo') is None))
    full = [g for g in games if g['code'] != 'other']
    out('rebuild checks over main and v31 games: final state differs from result block in %d, drop count mismatches %d, anomalies %s'
        % (sum(1 for g in full if not g['final_ok']), sum(g['drop_mismatch'] for g in full), dict(sum((Counter(g['anomalies']) for g in full), Counter()))))
    out('')
    what = sys.argv[1]
    if what == 'F13':
        f13(games)
    elif what == 'F11':
        f11(games)
    else:
        rows(games)


main()
