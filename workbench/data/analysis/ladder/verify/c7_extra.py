#!/usr/bin/env python3
"""Verifier claims 7, extra checks for F31 (run of 2026-10-07 07:35 KST), from the x7 shards. Writes f31-extras.txt."""
import sys, json, math
from pathlib import Path
from collections import Counter, defaultdict
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
LINES = []


def say(*a):
    s = ' '.join(str(x) for x in a)
    LINES.append(s)
    print(s)


def sm(g, key, s, a, b):
    return sum(g[key][s][a:b + 1])


def div(a, b):
    return a / b if b else float('nan')


def lr(gs, s, a, b):
    L = sum(sm(g, 'adjL', s, a, b) for g in gs)
    T = sum(sm(g, 'adjT', s, a, b) for g in gs)
    return '%.2f/%d' % (div(L, T), T) if T else '-'


def fisher(a, b, c, d):
    n = a + b + c + d
    r1 = a + b
    c1 = a + c

    def pr(x):
        return math.comb(r1, x) * math.comb(n - r1, c1 - x) / math.comb(n, c1)
    p0 = pr(a)
    return sum(pr(x) for x in range(max(0, c1 - (n - r1)), min(r1, c1) + 1) if pr(x) <= p0 * (1 + 1e-9))


def main():
    games = []
    for k in range(6):
        with open(V / ('x7-%d.jsonl' % k)) as f:
            for line in f:
                if line.strip():
                    games.append(json.loads(line))
    order = sorted(games, key=lambda g: (g.get('completedAt') or '', g['game']))
    seen = {}
    for g in order:
        lst = seen.setdefault(g['map'], [])
        if g['layout'] not in lst:
            lst.append(g['layout'])
        g['map_key'] = '%s #%d' % (g['map'], lst.index(g['layout']) + 1)
        g['opp'] = '%s (%s)' % (g.get('opponent'), g.get('opponentId'))
    codes = {c: [g for g in games if g['code'] == c] for c in ('main', 'v31', 'other')}
    both = codes['main'] + codes['v31']

    say('== 1. splits at round 300 on the other layouts: which game set gives the analyst 48 and 74 games ==')
    for c in ('main', 'v31'):
        oth = [g for g in codes[c] if not g['big']]
        for lab, sel in (('reached 325, 10 or more of ours at the start of round 300 (the definition)', lambda g: g['last_round'] >= 325 and g['alive'][0][299] >= 10),
                         ('reached 325, 20 or more at the start of round 300', lambda g: g['last_round'] >= 325 and g['alive'][0][299] >= 20),
                         ('reached 325, 20 or more after round 300', lambda g: g['last_round'] >= 325 and g['alive'][0][300] >= 20),
                         ('reached 325, 20 or more at the start of round 150 and 10 or more at the start of round 300', lambda g: g['last_round'] >= 325 and g['alive'][0][149] >= 20 and g['alive'][0][299] >= 10),
                         ('reached 325, 25 or more at the start of round 300', lambda g: g['last_round'] >= 325 and g['alive'][0][299] >= 25),
                         ('reached 325, 30 or more at the start of round 300', lambda g: g['last_round'] >= 325 and g['alive'][0][299] >= 30)):
            gs = [g for g in oth if sel(g)]
            o1 = sum(sm(g, 'spl', 0, 275, 299) for g in gs)
            o2 = sum(sm(g, 'spl', 0, 300, 324) for g in gs)
            t1 = sum(sm(g, 'spl', 1, 275, 299) for g in gs)
            t2 = sum(sm(g, 'spl', 1, 300, 324) for g in gs)
            say('  %s, %s: %d games, ours %.3f (%d then %d), theirs %.3f (%d then %d)' % (c, lab, len(gs), div(o2, o1), o1, o2, div(t2, t1), t1, t2))

    say('')
    say('== 2. where the step is on each layout: our left rate / turns per bin, main and v31 together; then theirs ==')
    bins = ((101, 125), (126, 150), (151, 175), (176, 200), (201, 250), (251, 300), (301, 325), (326, 350), (351, 400), (401, 450))
    say('  bins: ' + ' '.join('r%d-%d' % b for b in bins))
    keys = sorted(set(g['map_key'] for g in both), key=lambda k: (-max(g['W'] * g['H'] for g in both if g['map_key'] == k), k))
    for k in keys:
        gs = [g for g in both if g['map_key'] == k]
        say('  %-22s %4d cells n=%3d ours   %s' % (k, gs[0]['W'] * gs[0]['H'], len(gs), ' '.join(lr(gs, 0, a, b) for a, b in bins)))
        say('  %-22s                  theirs %s' % ('', ' '.join(lr(gs, 1, a, b) for a, b in bins)))
    say('  per code on the two doubtful layouts and their neighbours:')
    for k in ('Schooltime #1', 'Schooltime #2', 'Devil #1', 'Portals #1', 'Tower Defense #1'):
        for c in ('main', 'v31'):
            gs = [g for g in codes[c] if g['map_key'] == k]
            say('  %-18s %-4s n=%3d ours %s | games still running at round 150: %d, at 300: %d; our dragons after round 150 (median) %s, after 300 %s' % (
                k, c, len(gs), ' '.join(lr(gs, 0, a, b) for a, b in bins), sum(1 for g in gs if g['last_round'] >= 150), sum(1 for g in gs if g['last_round'] >= 300),
                sorted(g['alive'][0][150] for g in gs if g['last_round'] >= 150)[sum(1 for g in gs if g['last_round'] >= 150) // 2] if any(g['last_round'] >= 150 for g in gs) else '-',
                sorted(g['alive'][0][300] for g in gs if g['last_round'] >= 300)[sum(1 for g in gs if g['last_round'] >= 300) // 2] if any(g['last_round'] >= 300 for g in gs) else '-'))
    for k, r0, r1 in (('Schooltime #1', 146, 156), ('Devil #1', 296, 306), ('Devil #1', 146, 156), ('Maze #1', 296, 306), ('Trauma #1', 296, 306)):
        gs = [g for g in both if g['map_key'] == k and g['last_round'] >= r1]
        say('  %s single rounds %d-%d (%d games), ours: %s' % (k, r0, r1, len(gs), ' '.join(lr(gs, 0, r, r) for r in range(r0, r1 + 1))))

    say('')
    say('== 3. per opponent, big layouts, our left rate r126-150 then r151-175 and theirs (opponents with 3 or more big games) ==')
    for c in ('main', 'v31'):
        big = [g for g in codes[c] if g['big']]
        rows = []
        for o, n in Counter(g['opp'] for g in big).most_common():
            if n < 3:
                continue
            gs = [g for g in big if g['opp'] == o]
            a = (sum(sm(g, 'adjL', 0, 126, 150) for g in gs), sum(sm(g, 'adjT', 0, 126, 150) for g in gs))
            b = (sum(sm(g, 'adjL', 0, 151, 175) for g in gs), sum(sm(g, 'adjT', 0, 151, 175) for g in gs))
            rows.append((div(b[0], b[1]) - div(a[0], a[1]), o, n, lr(gs, 0, 126, 150), lr(gs, 0, 151, 175), lr(gs, 1, 126, 150), lr(gs, 1, 151, 175)))
        rows.sort()
        say('  %s: %d opponents with 3 or more big games; rise smallest %.3f, largest %.3f; opponents with a rise under 0.05: %d' % (c, len(rows), rows[0][0], rows[-1][0], sum(1 for r in rows if r[0] < 0.05)))
        for r in rows[:4]:
            say('     smallest: %s n=%d ours %s to %s, theirs %s to %s' % (r[1], r[2], r[3], r[4], r[5], r[6]))
        for r in rows:
            if 'calc' in r[1] or 'Knight' in r[1]:
                say('     named: %s n=%d ours %s to %s, theirs %s to %s' % (r[1], r[2], r[3], r[4], r[5], r[6]))
        allo = sorted(set(g['opp'] for g in big))
        up = 0
        tot = 0
        for o in allo:
            gs = [g for g in big if g['opp'] == o]
            a = (sum(sm(g, 'adjL', 0, 126, 150) for g in gs), sum(sm(g, 'adjT', 0, 126, 150) for g in gs))
            b = (sum(sm(g, 'adjL', 0, 151, 175) for g in gs), sum(sm(g, 'adjT', 0, 151, 175) for g in gs))
            if a[1] >= 20 and b[1] >= 20:
                tot += 1
                if div(b[0], b[1]) > div(a[0], a[1]):
                    up += 1
        say('     all opponents with 20 or more such turns in both windows: our left rate rose against %d of %d' % (up, tot))

    say('')
    say('== 4. own length against a longer own dragon within 9 (big layouts, ours): left rate / turns ==')
    for c in ('main', 'v31'):
        big = [g for g in codes[c] if g['big']]
        for a, b in ((101, 150), (151, 199)):
            t = defaultdict(lambda: [0, 0])
            for g in big:
                for r in g['recs']:
                    if r[1] == 0 and a <= r[0] <= b:
                        lb = '1-2' if r[6] <= 2 else '3' if r[6] == 3 else '4-5' if r[6] <= 5 else '6+'
                        nb = 'near' if r[12] <= 9 else 'far' if r[12] < 99 else 'none longer'
                        t[lb, nb][0] += r[2]
                        t[lb, nb][1] += 1
                        t[lb, 'all'][0] += r[2]
                        t[lb, 'all'][1] += 1
            say('  %s r%d-%d: %s' % (c, a, b, '; '.join('length %s: %s' % (lb, ', '.join('%s %.3f of %d' % (nb, div(t[lb, nb][0], t[lb, nb][1]), t[lb, nb][1]) for nb in ('near', 'far', 'none longer', 'all'))) for lb in ('1-2', '3', '4-5', '6+'))))
    say('  other layouts, ours, by own length, r251-300 then r301-350:')
    for c in ('main', 'v31'):
        oth = [g for g in codes[c] if not g['big']]
        for a, b in ((251, 300), (301, 350)):
            t = defaultdict(lambda: [0, 0])
            for g in oth:
                for r in g['recs']:
                    if r[1] == 0 and a <= r[0] <= b:
                        lb = '1-2' if r[6] <= 2 else '3' if r[6] == 3 else '4-5' if r[6] <= 5 else '6+'
                        t[lb][0] += r[2]
                        t[lb][1] += 1
            say('  %s r%d-%d: %s' % (c, a, b, ', '.join('length %s %.3f of %d' % (lb, div(t[lb][0], t[lb][1]), t[lb][1]) for lb in ('1-2', '3', '4-5', '6+'))))

    say('')
    say('== 5. the 40 games of other builds: is there a build without the step ==')
    for bot, n in Counter(g['bot'] for g in codes['other']).most_common():
        gs = [g for g in codes['other'] if g['bot'] == bot]
        big = [g for g in gs if g['big']]
        oth = [g for g in gs if not g['big']]
        say('  bot %s: %d games (%d big, %d other), won %d; big left rate ours r126-150 %s, r151-175 %s; other layouts r251-300 %s, r301-350 %s' % (
            bot, n, len(big), len(oth), sum(1 for g in gs if g['win']), lr(big, 0, 126, 150), lr(big, 0, 151, 175), lr(oth, 0, 251, 300), lr(oth, 0, 301, 350)))

    say('')
    say('== 6. cost bar again, medians within layout and code ==')
    lw = ln = uw = un = 0
    for c in ('main', 'v31'):
        for k in sorted(set(g['map_key'] for g in codes[c] if g['big'])):
            gs = [g for g in codes[c] if g['map_key'] == k and g['last_round'] >= 200 and g['alive'][0][150] >= 20 and sm(g, 'eat', 0, 101, 150) > 0]
            rs = sorted(sm(g, 'eat', 0, 151, 200) / sm(g, 'eat', 0, 101, 150) for g in gs)
            if len(rs) < 2:
                continue
            med = rs[len(rs) // 2] if len(rs) % 2 else (rs[len(rs) // 2 - 1] + rs[len(rs) // 2]) / 2
            for g in gs:
                x = sm(g, 'eat', 0, 151, 200) / sm(g, 'eat', 0, 101, 150)
                if x < med:
                    ln += 1
                    lw += 1 if g['win'] else 0
                elif x > med:
                    un += 1
                    uw += 1 if g['win'] else 0
    say('  big layouts, median within layout and code: lower halves won %d of %d, upper halves %d of %d; Fisher p = %.2f' % (lw, ln, uw, un, fisher(lw, ln - lw, uw, un - uw)))
    say('  median within layout only (from the numbers file): lower 44 of 95, upper 38 of 95; Fisher p = %.2f' % fisher(44, 51, 38, 57))
    lw = ln = uw = un = 0
    for c in ('main', 'v31'):
        for k in sorted(set(g['map_key'] for g in codes[c] if not g['big'])):
            gs = [g for g in codes[c] if g['map_key'] == k and g['last_round'] >= 400 and g['alive'][0][300] >= 10 and sm(g, 'eat', 0, 201, 300) > 0]
            rs = sorted(sm(g, 'eat', 0, 301, 400) / sm(g, 'eat', 0, 201, 300) for g in gs)
            if len(rs) < 2:
                continue
            med = rs[len(rs) // 2] if len(rs) % 2 else (rs[len(rs) // 2 - 1] + rs[len(rs) // 2]) / 2
            for g in gs:
                x = sm(g, 'eat', 0, 301, 400) / sm(g, 'eat', 0, 201, 300)
                if x < med:
                    ln += 1
                    lw += 1 if g['win'] else 0
                elif x > med:
                    un += 1
                    uw += 1 if g['win'] else 0
    say('  other layouts at 300 (pearls 301-400 / 201-300), median within layout and code: lower halves won %d of %d, upper halves %d of %d; Fisher p = %.2f' % (lw, ln, uw, un, fisher(lw, ln - lw, uw, un - uw)))
    for c in ('main', 'v31'):
        for grp, name, m0, m1 in ((True, 'big', 150, 300), (False, 'other', 300, 450)):
            gs = [g for g in codes[c] if g['big'] == grp and g['last_round'] >= m1]
            say('  %s %s, %d games reaching round %d: our share of all length after round %d %.3f, after round %d %.3f; our longest longer / theirs longer after round %d: %d / %d, after round %d: %d / %d; our share of dragons alive %.3f then %.3f' % (
                c, name, len(gs), m1, m0, div(sum(g['total'][0][m0] for g in gs), sum(g['total'][0][m0] + g['total'][1][m0] for g in gs)),
                m1, div(sum(g['total'][0][m1] for g in gs), sum(g['total'][0][m1] + g['total'][1][m1] for g in gs)),
                m0, sum(1 for g in gs if g['longest'][0][m0] > g['longest'][1][m0]), sum(1 for g in gs if g['longest'][0][m0] < g['longest'][1][m0]),
                m1, sum(1 for g in gs if g['longest'][0][m1] > g['longest'][1][m1]), sum(1 for g in gs if g['longest'][0][m1] < g['longest'][1][m1]),
                div(sum(g['alive'][0][m0] for g in gs), sum(g['alive'][0][m0] + g['alive'][1][m0] for g in gs)),
                div(sum(g['alive'][0][m1] for g in gs), sum(g['alive'][0][m1] + g['alive'][1][m1] for g in gs))))
    open(P + 'f31-extras.txt', 'w').write('\n'.join(LINES) + '\n')


main()
