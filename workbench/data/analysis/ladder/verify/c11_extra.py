#!/usr/bin/env python3
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
"""Verifier extras 11 (run of 2026-10-07 11:17 KST) for F39: is bring a trait of the opponent or of the layouts its
lone spells fell on; does the kind predict deaths in other games of the same pair. Reads the x11 shards and writes
f39-1117-extras.txt."""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')
LINES = []


def say(*a):
    s = ' '.join(str(x) for x in a)
    LINES.append(s)
    print(s)


def f(x, d=2):
    return 'n/a' if x is None else ('%.' + str(d) + 'f') % x


def lone_stats(g, s):
    od = g['qdeath'][1 - s]
    if od is None:
        return None
    d_other = od['round']
    me = g['qdeath'][s]
    my_d = me['round'] if me else None
    T = F = S = 0
    last = None
    for r in g['lone']:
        if r[0] != s:
            continue
        rnd = r[1]
        if r[7] > 0:
            last = rnd
        if rnd <= d_other or rnd < 100:
            continue
        T += 1
        if last is not None and rnd - last <= 20:
            F += 1
            S += r[3]
    D = 1 if (my_d is not None and my_d >= 100 and d_other < my_d) else 0
    return dict(T=T, F=F, S=S, D=D)


def spearman(xs, ys):
    def rank(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for k in range(i, j + 1):
                r[o[k]] = (i + j) / 2.0
            i = j + 1
        return r
    if len(xs) < 3:
        return None
    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else None


def main():
    games = []
    for k in range(6):
        for line in (V / ('x11-%d.jsonl' % k)).read_text().splitlines():
            if line.strip():
                games.append(json.loads(line))
    order = sorted(games, key=lambda g: (g.get('completedAt') or '', g['game']))
    maps = json.loads(Path('data/analysis/ladder/maps.json').read_text())
    seen = {}
    for g in order:
        lst = seen.setdefault(g['map'], [])
        if g['layout'] not in lst:
            lst.append(g['layout'])
        g['map_key'] = '%s #%d' % (g['map'], lst.index(g['layout']) + 1)
        g['free'] = not maps[g['map_key']]['queen_spawn_dead_end']
        g['p1'] = g['map_key'] == 'Portals #1'
        g['opp'] = '%s (%s)' % (g.get('opponent'), g.get('opponentId'))
        g['st'] = lone_stats(g, 0)
    SET = [g for g in order if g['code'] in ('main', 'v31') and g['free'] and not g['p1']]
    pr = defaultdict(list)
    for g in SET:
        if g['st'] is not None:
            pr[(g['opponentId'], g['code'])].append(g)
    tot = {}
    for k, gl in pr.items():
        tot[k] = dict(T=sum(g['st']['T'] for g in gl), F=sum(g['st']['F'] for g in gl), S=sum(g['st']['S'] for g in gl),
                      D=sum(g['st']['D'] for g in gl), opp=gl[0]['opp'], code=k[1],
                      lone_games=sum(1 for g in gl if g['st']['T'] > 0))
    big = [k for k in tot if tot[k]['F'] >= 150]

    def kind(k):
        b = tot[k]['S'] / tot[k]['F']
        return 'A' if b >= 3.0 else 'B' if b < 1.5 else 'mid'
    A = [k for k in big if kind(k) == 'A']
    B = [k for k in big if kind(k) == 'B']
    say('pairs with 150 or more fresh turns:', len(big), '; A', len(A), '; B', len(B))
    lg = sorted(tot[k]['lone_games'] for k in big)
    say('games with lone turns from r100 per such pair: least %d, median %d, most %d; pairs with 3 or fewer: %d' % (lg[0], lg[len(lg) // 2], lg[-1], sum(1 for x in lg if x <= 3)))
    say('    A pairs:', sorted(tot[k]['lone_games'] for k in A), ' B pairs:', sorted(tot[k]['lone_games'] for k in B))
    say('')
    say('=== bring by layout (all games of the set, our lone queen, fresh turns from r100) ===')
    lay = defaultdict(lambda: [0, 0, 0, 0])
    for g in SET:
        if g['st'] is None:
            continue
        v = lay[g['map_key']]
        v[0] += g['st']['S']
        v[1] += g['st']['F']
        v[2] += g['st']['D']
        v[3] += g['st']['T']
    for k, v in sorted(lay.items(), key=lambda kv: -(kv[1][0] / kv[1][1] if kv[1][1] else 0)):
        say('    %-24s bring %s over %5d fresh turns; deaths %2d in %5d lone turns (%s per 1,000)' % (k, f(v[0] / v[1] if v[1] else None), v[1], v[2], v[3], f(1000 * v[2] / v[3] if v[3] else None, 1)))
    say('')
    say('=== each pair: bring seen, and bring expected from the layouts of its fresh turns (layout bring taken from all other pairs) ===')
    exp = {}
    for k in big:
        num = den = 0.0
        for g in pr[k]:
            st = g['st']
            if st['F'] == 0:
                continue
            S_o = lay[g['map_key']][0] - sum(x['st']['S'] for x in pr[k] if x['map_key'] == g['map_key'])
            F_o = lay[g['map_key']][1] - sum(x['st']['F'] for x in pr[k] if x['map_key'] == g['map_key'])
            if F_o <= 0:
                continue
            num += st['F'] * S_o / F_o
            den += st['F']
        exp[k] = num / den if den else None
    for k in sorted(big, key=lambda k: -tot[k]['S'] / tot[k]['F']):
        t = tot[k]
        layc = Counter()
        for g in pr[k]:
            layc[g['map_key'][:-3]] += g['st']['F']
        say('    %-30s %-4s kind %-3s bring %s, layouts alone give %s; fresh turns on: %s' % (t['opp'][:30], t['code'], kind(k), f(t['S'] / t['F']), f(exp[k]),
            ', '.join('%s %d' % (a, b) for a, b in layc.most_common(4) if b)))
    ok = [k for k in big if exp[k] is not None]
    say('rank correlation of a pair bring with what its layouts alone give: %s over %d pairs' % (f(spearman([tot[k]['S'] / tot[k]['F'] for k in ok], [exp[k] for k in ok])), len(ok)))
    say('A pairs: bring seen %s, layouts alone give %s; B pairs: %s and %s' % (
        f(sum(tot[k]['S'] for k in A) / sum(tot[k]['F'] for k in A)), f(sum(exp[k] * tot[k]['F'] for k in A if exp[k] is not None) / sum(tot[k]['F'] for k in A if exp[k] is not None)),
        f(sum(tot[k]['S'] for k in B) / sum(tot[k]['F'] for k in B)), f(sum(exp[k] * tot[k]['F'] for k in B if exp[k] is not None) / sum(tot[k]['F'] for k in B if exp[k] is not None))))
    say('')
    say('=== A against B with the layout held ===')
    for lab, keyf in (('layout', lambda g: g['map_key']), ('layout and code', lambda g: (g['map_key'], g['code']))):
        cell = defaultdict(lambda: [0, 0, 0, 0])
        for kk, idx in ((A, 0), (B, 2)):
            for k in kk:
                for g in pr[k]:
                    c = cell[keyf(g)]
                    c[idx] += g['st']['D']
                    c[idx + 1] += g['st']['T']
        num = den = 0.0
        both = 0
        for c in cell.values():
            T = c[1] + c[3]
            if not T:
                continue
            num += c[0] * c[3] / T
            den += c[2] * c[1] / T
            if c[1] and c[3]:
                both += 1
        say('held by %s (Mantel-Haenszel rate ratio): %s; cells with turns of both kinds %d of %d' % (lab, f(num / den if den else None), both, len(cell)))
    cell = defaultdict(lambda: [0, 0, 0, 0])
    for kk, idx in ((A, 0), (B, 2)):
        for k in kk:
            for g in pr[k]:
                c = cell[g['map_key']]
                c[idx] += g['st']['D']
                c[idx + 1] += g['st']['T']
    for k, c in sorted(cell.items()):
        say('    %-24s A %2d in %4d (%s) | B %2d in %4d (%s)' % (k, c[0], c[1], f(1000 * c[0] / c[1] if c[1] else None, 1), c[2], c[3], f(1000 * c[2] / c[3] if c[3] else None, 1)))
    say('')
    say('=== does the kind hold in other games of the same pair? random halves, 1,000 times ===')
    rng = random.Random(23)
    ratios = []
    sums = {'A': [0, 0], 'B': [0, 0], 'mid': [0, 0]}
    rel = []
    same = [0, 0]
    for _ in range(1000):
        acc = {'A': [0, 0], 'B': [0, 0], 'mid': [0, 0]}
        xs, ys = [], []
        for k, gl in pr.items():
            idx = list(range(len(gl)))
            rng.shuffle(idx)
            h = [[gl[i] for i in idx[:len(idx) // 2]], [gl[i] for i in idx[len(idx) // 2:]]]
            br = []
            for z in (0, 1):
                F = sum(g['st']['F'] for g in h[z])
                S = sum(g['st']['S'] for g in h[z])
                br.append((F, S))
                if F < 75:
                    continue
                b = S / F
                kd = 'A' if b >= 3.0 else 'B' if b < 1.5 else 'mid'
                acc[kd][0] += sum(g['st']['D'] for g in h[1 - z])
                acc[kd][1] += sum(g['st']['T'] for g in h[1 - z])
            if br[0][0] >= 75 and br[1][0] >= 75:
                b0, b1 = br[0][1] / br[0][0], br[1][1] / br[1][0]
                xs.append(b0)
                ys.append(b1)
                k0 = 'A' if b0 >= 3.0 else 'B' if b0 < 1.5 else 'mid'
                k1 = 'A' if b1 >= 3.0 else 'B' if b1 < 1.5 else 'mid'
                same[1] += 1
                same[0] += 1 if k0 == k1 else 0
        for kd in acc:
            sums[kd][0] += acc[kd][0]
            sums[kd][1] += acc[kd][1]
        if acc['A'][1] and acc['B'][0] and acc['B'][1]:
            ratios.append((acc['A'][0] / acc['A'][1]) / (acc['B'][0] / acc['B'][1]))
        sp = spearman(xs, ys)
        if sp is not None:
            rel.append((sp, len(xs)))
    ratios.sort()
    say('kind from one random half of a pair games (75 or more fresh turns there), deaths and turns from the other half: pooled over the splits A %s per 1,000, B %s, between %s' % (
        f(1000 * sums['A'][0] / sums['A'][1]), f(1000 * sums['B'][0] / sums['B'][1]), f(1000 * sums['mid'][0] / sums['mid'][1])))
    say('ratio A over B per split: median %s, 5th to 95th percentile %s to %s; at or above 1.0 in %d of %d splits; at or above 1.9 in %d' % (
        f(ratios[len(ratios) // 2]), f(ratios[int(0.05 * len(ratios))]), f(ratios[int(0.95 * len(ratios))]), sum(1 for r in ratios if r >= 1.0), len(ratios), sum(1 for r in ratios if r >= 1.9)))
    say('bring in one half against bring in the other half of the same pair (both halves 75 or more fresh turns): mean rank correlation %s over a mean of %s pairs; same kind in both halves in %s of such pairs' % (
        f(sum(r[0] for r in rel) / len(rel)), f(sum(r[1] for r in rel) / len(rel), 1), f(same[0] / same[1] if same[1] else None)))
    say('')
    say('=== the pairs left out by the 150 fresh turns bar ===')
    small = [k for k in tot if tot[k]['F'] < 150]
    say('%d pairs: %d deaths in %d lone turns (%s per 1,000), fresh turns %d, bring %s; lone games %d' % (
        len(small), sum(tot[k]['D'] for k in small), sum(tot[k]['T'] for k in small), f(1000 * sum(tot[k]['D'] for k in small) / max(1, sum(tot[k]['T'] for k in small))),
        sum(tot[k]['F'] for k in small), f(sum(tot[k]['S'] for k in small) / max(1, sum(tot[k]['F'] for k in small))), sum(tot[k]['lone_games'] for k in small)))
    for lab, pred in (('bring 3.0 or more', lambda b: b >= 3.0), ('1.5 to 3.0', lambda b: 1.5 <= b < 3.0), ('under 1.5', lambda b: b < 1.5)):
        ks = [k for k in small if tot[k]['F'] > 0 and pred(tot[k]['S'] / tot[k]['F'])]
        say('    left-out pairs with %s: %d pairs, %d deaths in %d lone turns (%s per 1,000)' % (lab, len(ks), sum(tot[k]['D'] for k in ks), sum(tot[k]['T'] for k in ks),
            f(1000 * sum(tot[k]['D'] for k in ks) / max(1, sum(tot[k]['T'] for k in ks)))))
    say('with no bar at all (every pair with a fresh turn): ' + ' | '.join('%s: %d pairs, %d in %d (%s)' % (lab, len(ks), sum(tot[k]['D'] for k in ks), sum(tot[k]['T'] for k in ks),
        f(1000 * sum(tot[k]['D'] for k in ks) / max(1, sum(tot[k]['T'] for k in ks)))) for lab, ks in (
            ('3.0 or more', [k for k in tot if tot[k]['F'] > 0 and tot[k]['S'] / tot[k]['F'] >= 3.0]),
            ('1.5 to 3.0', [k for k in tot if tot[k]['F'] > 0 and 1.5 <= tot[k]['S'] / tot[k]['F'] < 3.0]),
            ('under 1.5', [k for k in tot if tot[k]['F'] > 0 and tot[k]['S'] / tot[k]['F'] < 1.5]))))
    say('')
    say('=== the game as the unit: bring of a game (25 or more fresh turns) and whether she dies in it ===')
    for lab, pred in (('bring 3.0 or more', lambda b: b >= 3.0), ('1.5 to 3.0', lambda b: 1.5 <= b < 3.0), ('under 1.5', lambda b: b < 1.5)):
        gs = [g for g in SET if g['st'] is not None and g['st']['F'] >= 25 and pred(g['st']['S'] / g['st']['F'])]
        d = sum(g['st']['D'] for g in gs)
        t = sum(g['st']['T'] for g in gs)
        say('    games with %s: %d games, she dies in %d (%s), %d lone turns, %s per 1,000' % (lab, len(gs), d, f(d / len(gs) if gs else None), t, f(1000 * d / t if t else None)))
    out = open(P + 'f39-1117-extras.txt', 'w')
    out.write('\n'.join(LINES) + '\n')
    out.close()


main()
