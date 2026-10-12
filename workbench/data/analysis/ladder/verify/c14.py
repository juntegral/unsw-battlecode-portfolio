#!/usr/bin/env python3
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
"""Verifier counts 14 (run of 2026-10-07 18:20 KST): F45, F44 (run 1800 additions), F42 (sighting rule).
Reads the shards written by extract14b.py. Usage: python3 c14.py"""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict

G = []
seen_ids = set()
for k in range(6):
    for pre in ('x14b-%d.jsonl', 'x14c-%d.jsonl'):
        fp = Path(P + pre % k)
        if not fp.exists():
            continue
        for line in fp.read_text().splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if rec['game'] not in seen_ids:
                seen_ids.add(rec['game'])
                G.append(rec)
G.sort(key=lambda g: g['game'])
out = open(P + 'c14-numbers.txt', 'w')


def say(*a):
    s = ' '.join(str(x) for x in a)
    print(s)
    out.write(s + '\n')


def wilson(k, n):
    if n == 0:
        return (0.0, 0.0)
    z = 1.96
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))


def fisher(a, b, c, d):
    """two-sided exact test for the table [[a, b], [c, d]]"""
    n = a + b + c + d
    r1, c1 = a + b, a + c
    def pr(x):
        return math.comb(c1, x) * math.comb(n - c1, r1 - x) / math.comb(n, r1)
    p0 = pr(a)
    tot = 0.0
    for x in range(max(0, r1 - (n - c1)), min(r1, c1) + 1):
        q = pr(x)
        if q <= p0 * (1 + 1e-9):
            tot += q
    return round(tot, 5)


def frac(k, n):
    return '%d of %d (%.3f)' % (k, n, k / n if n else float('nan'))


def band(e):
    return 'under 1700' if e < 1700 else '1700-1899' if e < 1900 else '1900-2099' if e < 2100 else '2100+'


BANDS = ['under 1700', '1700-1899', '1900-2099', '2100+']
errors = [g for g in G if 'error' in g]
say('games read', len(G), 'errors', len(errors), [(-1 if 'error' not in g else g['game']) for g in errors][:5])
G = [g for g in G if 'error' not in g]
say('final state equal to the result block', sum(g['final_ok'] for g in G), 'rounds in order', sum(g['rounds_ok'] for g in G),
    'games with anomalies', sum(1 for g in G if g['anomalies']), 'bad portals', sum(g['bad_portals'] for g in G),
    'ranked', sum(1 for g in G if g.get('ranked')), 'no ledger line', sum(1 for g in G if 'opponentElo' not in g))
first = {}
for g in G:
    key = (g['map'], g['layout'])
    if key not in first:
        first[key] = g['game']
vers = defaultdict(list)
for (name, lay), gid in sorted(first.items(), key=lambda kv: kv[1]):
    vers[name].append(lay)
for g in G:
    g['key'] = '%s #%d' % (g['map'], vers[g['map']].index(g['layout']) + 1)
    g['cells'] = g['W'] * g['H']
    g['small'] = g['cells'] <= 1200
    g['band'] = band(g['opponentElo'])
    g['t'] = g['completedAt'][:19]
say('codes', dict(Counter(g['code'] for g in G)))
say('completedAt sample', G[0]['completedAt'], G[-1]['completedAt'])
lay_info = {}
for g in G:
    lay_info.setdefault(g['key'], (g['W'], g['H'], g['cells'], g['qdist'], g['spawn_n'][0]))
for k in sorted(lay_info):
    say('  layout', k, lay_info[k], 'games', sum(1 for g in G if g['key'] == k))
DEAD_END = ('Schooltime #1', 'Schooltime #2', 'Slithery Fight #1')
rng = random.Random(14)


def code_games(code):
    return [g for g in G if g['code'] == code]


def tot(g, s, r):
    return g['total'][s][r] if len(g['total'][s]) > r else None


def behind(g, s, r=100, m=0.8):
    a, b = tot(g, s, r), tot(g, 1 - s, r)
    return a is not None and a < m * b


def late(g, s):
    return g['end_reason'] == 0 and g['final'][s]['alive'] == 0 and g['last_round'] >= 126


def early(g, s):
    return g['end_reason'] == 0 and g['final'][s]['alive'] == 0 and g['last_round'] <= 125


say('')
say('=================== F45 ===================')
say('end reasons', dict(Counter(g['end_reason'] for g in G)), '; eliminations with both sides empty',
    sum(1 for g in G if g['end_reason'] == 0 and g['final'][0]['alive'] == 0 and g['final'][1]['alive'] == 0),
    '; eliminations with neither empty', sum(1 for g in G if g['end_reason'] == 0 and g['final'][0]['alive'] > 0 and g['final'][1]['alive'] > 0),
    '; non-eliminations ending before 499', sum(1 for g in G if g['end_reason'] != 0 and g['last_round'] != 499))
SPLIT = '2026-10-06T14:48:15'
for code in ('main', 'v31'):
    C = code_games(code)
    for s, label in ((0, 'ours wiped late'), (1, 'MIRROR theirs wiped late')):
        L = [g for g in C if late(g, s)]
        B = [g for g in L if behind(g, s)]
        say(code, label, frac(len(B), len(L)), 'interval', wilson(len(B), len(L)))
        if code == 'main':
            h1 = [g for g in L if g['t'] < SPLIT]
            h1e = [g for g in L if g['t'] <= SPLIT]
            h2 = [g for g in L if g['t'] >= SPLIT]
            say('   halves (before / from the split):', frac(sum(behind(g, s) for g in h1), len(h1)), 'and',
                frac(sum(behind(g, s) for g in h2), len(h2)), '; games at the split second', len(h1e) - len(h1),
                '; all main games before / from', sum(1 for g in C if g['t'] < SPLIT), sum(1 for g in C if g['t'] >= SPLIT))
        sm = [g for g in L if g['small']]
        bg = [g for g in L if not g['small']]
        say('   small / big:', frac(sum(behind(g, s) for g in sm), len(sm)), 'and', frac(sum(behind(g, s) for g in bg), len(bg)))
        say('   bands:', ', '.join('%s %s' % (b, frac(sum(behind(g, s) for g in L if g['band'] == b), sum(1 for g in L if g['band'] == b))) for b in BANDS))
        say('   thresholds at r100: ' + ', '.join('under %.1f: %d' % (m, sum(behind(g, s, 100, m) for g in L)) for m in (0.5, 0.6, 0.7, 0.8, 0.9, 1.0)),
            '; equal or ahead', sum(1 for g in L if tot(g, s, 100) >= tot(g, 1 - s, 100)))
        say('   same margin at r50:', sum(behind(g, s, 50) for g in L), 'at r75:', sum(behind(g, s, 75) for g in L), 'at r125:', sum(behind(g, s, 125) for g in L))
        say('   pearls by r50 under half:', sum(1 for g in L if g['eaten'][s][50] < 0.5 * g['eaten'][1 - s][50]),
            '; 6 or fewer alive at r100:', sum(1 for g in L if g['alive'][s][100] <= 6),
            '; 2-dragon-start layouts:', sum(1 for g in L if g['spawn_n'][s] == 2))
        NB = [g for g in L if not behind(g, s)]
        r200 = [g for g in NB if g['last_round'] >= 200]
        say('   not behind:', len(NB), '; reached r200:', len(r200), '; under 0.8 at r200:', sum(behind(g, s, 200) for g in r200),
            '; last rounds of the not-behind', sorted(g['last_round'] for g in NB))
        for lo, hi in ((126, 150), (151, 200), (201, 300), (301, 498)):
            LL = [g for g in L if lo <= g['last_round'] <= hi]
            say('   last round %d-%d:' % (lo, hi), frac(sum(behind(g, s) for g in LL), len(LL)))
        say('   by layout:', ', '.join('%s %d/%d' % (k, sum(behind(g, s) for g in L if g['key'] == k), n) for k, n in sorted(Counter(g['key'] for g in L).items())))
        opp = Counter(g['opponent'] for g in L)
        say('   opponents', len(opp), 'battles', len(set(g['battle'] for g in L)), 'top', opp.most_common(4))
        say('   by day (KST):', ', '.join('%s %d/%d' % (d, sum(behind(g, s) for g in L if g['at_kst'][:10] == d), n) for d, n in sorted(Counter(g['at_kst'][:10] for g in L).items())))
        # battle-resampled interval
        bt = defaultdict(list)
        for g in L:
            bt[g['battle']].append(1 if behind(g, s) else 0)
        keys = sorted(bt)
        vals = []
        for _ in range(4000 if keys else 0):
            pick = [bt[keys[rng.randrange(len(keys))]] for _ in keys]
            n = sum(len(x) for x in pick)
            vals.append(sum(sum(x) for x in pick) / n if n else 0.0)
        vals.sort()
        if vals:
            say('   share with battles resampled: %.3f to %.3f' % (vals[100], vals[3899]))
    # scale
    R = [g for g in C if g['last_round'] >= 100]
    for s, label in ((0, 'we behind'), (1, 'they behind')):
        Bh = [g for g in R if behind(g, s)]
        won = [g for g in Bh if (g['win'] if s == 0 else (not g['win'] and not g['drawn']))]
        say(code, 'SCALE reached r100:', len(R), label, len(Bh), 'won by the side behind', len(won),
            '; small', '%d of %d' % (sum(1 for g in won if g['small']), sum(1 for g in Bh if g['small'])),
            '; big', '%d of %d' % (sum(1 for g in won if not g['small']), sum(1 for g in Bh if not g['small'])),
            '; drawn', sum(1 for g in Bh if g['drawn']))
        say('     behind games ending: late wipe-out of that side', sum(1 for g in Bh if late(g, s)), ', early', sum(1 for g in Bh if early(g, s)),
            '; wipe-out of the other side', sum(1 for g in Bh if g['end_reason'] == 0 and g['final'][1 - s]['alive'] == 0),
            '; full game lost', sum(1 for g in Bh if g['last_round'] == 499 and g not in won and not g['drawn']))
        NBh = [g for g in R if not behind(g, s)]
        say('     not behind:', len(NBh), 'late wipe-out of that side', sum(1 for g in NBh if late(g, s)),
            '; fisher late wipe-out by behind or not', fisher(sum(1 for g in Bh if late(g, s)), sum(1 for g in Bh if not late(g, s)),
                                                              sum(1 for g in NBh if late(g, s)), sum(1 for g in NBh if not late(g, s))))
        # the other losses: how often was the loser behind at r100
        LO = [g for g in R if not g['drawn'] and (g['win'] if s == 1 else not g['win'])]
        full = [g for g in LO if g['last_round'] == 499]
        say('     all games that side lost (reached r100):', frac(sum(behind(g, s) for g in LO), len(LO)), '; lost full games:',
            frac(sum(behind(g, s) for g in full), len(full)), '; lost full games small/big:',
            frac(sum(behind(g, s) for g in full if g['small']), sum(1 for g in full if g['small'])),
            frac(sum(behind(g, s) for g in full if not g['small']), sum(1 for g in full if not g['small'])))
    for sz, lab in ((True, 'small'), (False, 'big')):
        RR = [g for g in R if g['small'] == sz]
        say(code, lab, 'reached r100', len(RR), '; we behind', sum(behind(g, 0) for g in RR), '; they behind', sum(behind(g, 1) for g in RR),
            '; our late wipe-outs', sum(late(g, 0) for g in RR), '; theirs', sum(late(g, 1) for g in RR))
    # late wipe-outs that were ahead at r100 by the same margin
    say(code, 'late wipe-outs of ours in which THEY were behind at r100:', sum(1 for g in C if late(g, 0) and behind(g, 1)),
        '; of theirs in which WE were behind:', sum(1 for g in C if late(g, 1) and behind(g, 0)))
    say(code, 'list of late wipe-outs of ours not behind:', [(g['game'], g['key'], g['opponent'], g['last_round'], tot(g, 0, 100), tot(g, 1, 100)) for g in C if late(g, 0) and not behind(g, 0)])

say('')
say('=================== F44 ===================')
FIVE = ('Stripes #1', 'Trophy #1', 'Devil #1', 'Prisoners Dilemma #1', 'Prisoners Dilemma #2')
NONE4 = ('Default #1', 'Portals #1', 'Tower Defense #1', 'weakhold #1')
allw = [g for g in G if g['code'] in ('main', 'v31') and early(g, 0)]
say('all early wipe-outs of ours (main and v31):', len(allw), '; on the five layouts', sum(1 for g in allw if g['key'] in FIVE),
    '; on Default, Portals, Tower Defense, weakhold', sum(1 for g in allw if g['key'] in NONE4), '; on big layouts', sum(1 for g in allw if not g['small']))
for code in ('main', 'v31'):
    C = code_games(code)
    S = [g for g in C if g['small']]
    EW = [g for g in C if early(g, 0)]
    say(code, 'early wipe-outs', len(EW), 'by layout', dict(Counter(g['key'] for g in EW)), '; up to battle 1316833:', sum(1 for g in EW if int(g['battle']) <= 1316833))
    say(code, '  five layouts, all bands:', frac(sum(1 for g in EW if g['key'] in FIVE), sum(1 for g in C if g['key'] in FIVE)),
        '; the four named layouts:', frac(sum(1 for g in EW if g['key'] in NONE4), sum(1 for g in C if g['key'] in NONE4)))
    for lo, lab in ((1900, '1900+'), (0, 'all ratings'), (-1, 'under 1900')):
        SS = [g for g in S if (g['opponentElo'] >= 1900 if lo == 1900 else True if lo == 0 else g['opponentElo'] < 1900)]
        near = [g for g in SS if g['qdist'] <= 10]
        far = [g for g in SS if g['qdist'] > 10]
        a, b, c, d = sum(early(g, 0) for g in near), len(near), sum(early(g, 0) for g in far), len(far)
        say(code, ' ', lab, 'small layouts: near', frac(a, b), wilson(a, b), 'far', frac(c, d), wilson(c, d), 'fisher', fisher(a, b - a, c, d - c),
            '; MIRROR (theirs wiped early): near', frac(sum(early(g, 1) for g in near), len(near)), 'far', frac(sum(early(g, 1) for g in far), len(far)))
        if lo == 1900:
            # whole battles shuffled between near and far is not possible (a battle mixes layouts); shuffle layout labels instead
            lays = sorted(set(g['key'] for g in SS))
            nn = sum(1 for k in lays if lay_info[k][3] <= 10)
            obs = a / b - c / d
            per = {k: (sum(early(g, 0) for g in SS if g['key'] == k), sum(1 for g in SS if g['key'] == k)) for k in lays}
            import itertools
            ge = 0
            allc = 0
            for comb in itertools.combinations(lays, nn):
                x = sum(per[k][0] for k in comb)
                n1 = sum(per[k][1] for k in comb)
                y = sum(per[k][0] for k in lays) - x
                n2 = sum(per[k][1] for k in lays) - n1
                allc += 1
                if x / n1 - y / n2 >= obs - 1e-12:
                    ge += 1
            say(code, '    layouts', len(lays), 'near layouts', nn, '; choices of', nn, 'layouts with a gap as large:', ge, 'of', allc)
            say(code, '    per layout (wipe-outs/games, queen distance):', ', '.join('%s %d/%d d%d' % (k, per[k][0], per[k][1], lay_info[k][3]) for k in sorted(lays, key=lambda k: lay_info[k][3])))
            for drop in (('Default #1', 'Portals #1'),):
                nr = [g for g in near if g['key'] not in drop]
                dr = [g for g in near if g['key'] in drop]
                say(code, '    near without Default and Portals:', frac(sum(early(g, 0) for g in nr), len(nr)), '; Default and Portals alone:', frac(sum(early(g, 0) for g in dr), len(dr)))
            say(code, '    1900+ small: 2-dragon start', frac(sum(early(g, 0) for g in SS if g['spawn_n'][0] == 2), sum(1 for g in SS if g['spawn_n'][0] == 2)),
                '; more than 2', frac(sum(early(g, 0) for g in SS if g['spawn_n'][0] > 2), sum(1 for g in SS if g['spawn_n'][0] > 2)))
            say(code, '    1900+ small: 600 cells or fewer', frac(sum(early(g, 0) for g in SS if g['cells'] <= 600), sum(1 for g in SS if g['cells'] <= 600)),
                '; 601-1200', frac(sum(early(g, 0) for g in SS if g['cells'] > 600), sum(1 for g in SS if g['cells'] > 600)))
            # three removed
            say(code, '    three near wipe-outs removed:', frac(max(a - 3, 0), b - min(a, 3)), 'fisher', fisher(max(a - 3, 0), b - a, c, d - c))
            opp = Counter(g['opponent'] for g in near if early(g, 0))
            say(code, '    near wipe-outs by opponent', opp.most_common(), '; battles', len(set(g['battle'] for g in near if early(g, 0))))


def meet(g, lo=0, hi=60):
    return [m for m in g['meetings'] if lo <= m[0] <= hi]


def share(games, lo=0, hi=60):
    ms = [m for g in games for m in meet(g, lo, hi)]
    k = sum(1 for m in ms if m[1] == 1)
    return k, len(ms)


def boot(games, lo=0, hi=60, n=4000):
    per = [(sum(1 for m in meet(g, lo, hi) if m[1] == 1), len(meet(g, lo, hi))) for g in games]
    vals = []
    for _ in range(n):
        a = b = 0
        for _ in per:
            x = per[rng.randrange(len(per))]
            a += x[0]
            b += x[1]
        vals.append(a / b if b else 0.5)
    vals.sort()
    return '%.3f to %.3f' % (vals[int(n * 0.025)], vals[int(n * 0.975) - 1])


say('')
say('--- F44 (b): mover in head-on meetings, raw rounds 0-60 ---')
say('whole-game cross-team meetings, all games:', sum(len(g['meetings']) for g in G), '; same-team', sum(g['same_team_meetings'] for g in G))
for code in ('main', 'v31'):
    C = code_games(code)
    W34 = [g for g in C if early(g, 0) and int(g['battle']) <= 1316833]
    Wall = [g for g in C if early(g, 0)]
    lays = set(g['key'] for g in W34)
    ids = set(g['game'] for g in W34)
    O = [g for g in C if g['key'] in lays and g['game'] not in ids]
    O2 = [g for g in O if not early(g, 0)]
    k, n = share(W34)
    say(code, 'wipe-outs up to 1316833:', len(W34), 'games; their dragon the mover', frac(k, n), 'games resampled', boot(W34))
    ko, no = share(O)
    say(code, '  other games on the same layouts:', len(O), 'games', frac(ko, no), 'games resampled', boot(O), '; without the later wipe-outs:', len(O2), frac(*share(O2)))
    ms = [m for g in W34 for m in meet(g) if m[1] == 1]
    say(code, '  their movers 2 or 3 long:', sum(1 for m in ms if m[2] in (2, 3)), 'of', len(ms), '; our victims 2 or 3 long:', sum(1 for m in ms if m[3] in (2, 3)),
        '; our queen the victim:', sum(1 for m in ms if m[4]), '; their queen the mover:', sum(1 for m in ms if m[5]),
        '; mover lengths', sorted(Counter(m[2] for m in ms).items()), '; victim lengths', sorted(Counter(m[3] for m in ms).items()))
    ms0 = [m for g in W34 for m in meet(g) if m[1] == 0]
    say(code, '  our movers in those games:', len(ms0), 'mover lengths', sorted(Counter(m[2] for m in ms0).items()), 'their queen the victim', sum(1 for m in ms0 if m[4]))
    k2, n2 = share(Wall)
    say(code, '  all', len(Wall), 'early wipe-outs:', frac(k2, n2))
    per = sorted(((sum(1 for m in meet(g) if m[1] == 1), len(meet(g)), g['game'], g['key'], g['opponent'], g['last_round']) for g in W34), key=lambda x: -(x[0] - (x[1] - x[0])))
    say(code, '  per game (theirs, all, game, layout, opponent, last round):', per)
    say(code, '  games with their share above half:', sum(1 for x in per if 2 * x[0] > x[1]), 'equal', sum(1 for x in per if 2 * x[0] == x[1] and x[1] > 0),
        'below', sum(1 for x in per if 2 * x[0] < x[1]), 'no meeting', sum(1 for x in per if x[1] == 0))
    top3 = set(x[2] for x in per[:3])
    say(code, '  without the three games with the largest surplus:', frac(*share([g for g in W34 if g['game'] not in top3])))
    for lo, hi in ((0, 20), (21, 40), (41, 60), (0, 30), (0, 100)):
        say(code, '  rounds %d-%d: wipe-outs' % (lo, hi), frac(*share(W34, lo, hi)), '; other games', frac(*share(O, lo, hi)))
    # mirror: the games in which we wipe them out early, same layouts
    M = [g for g in C if early(g, 1)]
    km, nm = share(M)
    say(code, '  MIRROR: games in which theirs are wiped out by r125:', len(M), '; OUR dragon the mover', frac(nm - km, nm), 'games resampled (their share)', boot(M),
        '; on the same layouts only:', frac(share([g for g in M if g['key'] in lays])[1] - share([g for g in M if g['key'] in lays])[0], share([g for g in M if g['key'] in lays])[1]))
    # neither side wiped early, same layouts
    N0 = [g for g in O if not early(g, 0) and not early(g, 1)]
    say(code, '  same layouts, neither side wiped by r125:', len(N0), 'games', frac(*share(N0)))
    # dragons alive when the meeting happens
    for nm_, GG in (('wipe-outs', W34), ('other games', O)):
        ms = [m for g in GG for m in meet(g)]
        more = sum(1 for m in ms if (m[7] - m[6]) * (1 if m[1] == 1 else -1) > 0)
        fewer = sum(1 for m in ms if (m[7] - m[6]) * (1 if m[1] == 1 else -1) < 0)
        say(code, '  ', nm_, ': mover on the side with more dragons', more, 'fewer', fewer, 'equal', len(ms) - more - fewer, 'of', len(ms))
        for lab, test in (('they have more dragons', lambda m: m[7] > m[6]), ('equal', lambda m: m[7] == m[6]), ('we have more', lambda m: m[7] < m[6])):
            sub = [m for m in ms if test(m)]
            say(code, '     when', lab, ': their dragon the mover', frac(sum(1 for m in sub if m[1] == 1), len(sub)))
    # games permuted: label shuffles between wipe-outs and other games
    allg = W34 + O
    per2 = [(sum(1 for m in meet(g) if m[1] == 1), len(meet(g))) for g in allg]
    obs = k / n - ko / no
    ge = 0
    idx = list(range(len(allg)))
    for _ in range(20000):
        rng.shuffle(idx)
        a = sum(per2[i][0] for i in idx[:len(W34)])
        b = sum(per2[i][1] for i in idx[:len(W34)])
        c = sum(per2[i][0] for i in idx[len(W34):])
        d = sum(per2[i][1] for i in idx[len(W34):])
        if b and d and a / b - c / d >= obs:
            ge += 1
    say(code, '  game-label shuffles with a gap as large:', ge, 'of 20000')

say('')
say('--- F44 (c): small layouts, rounds 0-60, by opponent band ---')
for code in ('main', 'v31'):
    S = [g for g in code_games(code) if g['small']]
    for b in BANDS:
        SB = [g for g in S if g['band'] == b]
        k, n = share(SB)
        say(code, b, 'their dragon the mover', frac(k, n), 'games', len(SB), 'battles', len(set(g['battle'] for g in SB)), 'games resampled', boot(SB) if n else '-',
            '; meetings per game %.2f' % (n / len(SB) if SB else 0))
    top = [g for g in S if g['band'] == '2100+']
    low = [g for g in S if g['band'] in ('1700-1899', '1900-2099')]
    ops = sorted(set(g['opponent'] for g in top))
    rows = []
    for o in ops:
        k, n = share([g for g in top if g['opponent'] == o])
        rows.append((o, k, n, sum(1 for g in top if g['opponent'] == o)))
    say(code, '2100+ per opponent (theirs, all, games):', rows)
    say(code, '  opponents', len(ops), '; their share above half:', sum(1 for r in rows if 2 * r[1] > r[2]), '; equal', sum(1 for r in rows if 2 * r[1] == r[2]), '; below', sum(1 for r in rows if 2 * r[1] < r[2]))
    loo = []
    for o in ops:
        k, n = share([g for g in top if g['opponent'] != o])
        loo.append(round(k / n, 3))
    say(code, '  one opponent left out:', min(loo), 'to', max(loo))
    # battles shuffled between 2100+ and the two bands below
    bt = defaultdict(lambda: [0, 0])
    lab = {}
    for g in top + low:
        k, n = share([g])
        bt[g['battle']][0] += k
        bt[g['battle']][1] += n
        lab[g['battle']] = g['band'] == '2100+'
    keys = sorted(bt)
    nt = sum(1 for k in keys if lab[k])
    kt, ntm = share(top)
    kl, nl = share(low)
    obs = kt / ntm - kl / nl
    ge = 0
    for _ in range(20000):
        rng.shuffle(keys)
        a = sum(bt[k][0] for k in keys[:nt])
        b = sum(bt[k][1] for k in keys[:nt])
        c = sum(bt[k][0] for k in keys[nt:])
        d = sum(bt[k][1] for k in keys[nt:])
        if b and d and a / b - c / d >= obs:
            ge += 1
    say(code, '  2100+', frac(kt, ntm), 'against 1700-2099', frac(kl, nl), '; whole battles shuffled, gap as large:', ge, 'of 20000 (battles', len(keys), ', top', nt, ')')
    # layout mix: what the top band would show with the lower bands' share on each layout
    exp = 0.0
    used = 0
    line = []
    for k in sorted(set(g['key'] for g in S)):
        a, b = share([g for g in top if g['key'] == k])
        c, d = share([g for g in low if g['key'] == k])
        line.append('%s %d/%d vs %d/%d' % (k, a, b, c, d))
        if b and d:
            exp += b * c / d
            used += b
    say(code, '  per layout (2100+ against 1700-2099):', '; '.join(line))
    say(code, '  2100+ share expected from the lower bands, layout by layout: %.3f on %d meetings' % (exp / used if used else 0, used))
    # the early wipe-outs taken out
    say(code, '  without the early wipe-outs of ours:', ', '.join('%s %s' % (b, frac(*share([g for g in S if g['band'] == b and not early(g, 0)]))) for b in BANDS[1:]))
    say(code, '  without early wipe-outs of either side:', ', '.join('%s %s' % (b, frac(*share([g for g in S if g['band'] == b and not early(g, 0) and not early(g, 1)]))) for b in BANDS[1:]))
    say(code, '  five layouts only:', ', '.join('%s %s' % (b, frac(*share([g for g in S if g['band'] == b and g['key'] in FIVE]))) for b in BANDS[1:]),
        '; the other small layouts:', ', '.join('%s %s' % (b, frac(*share([g for g in S if g['band'] == b and g['key'] not in FIVE]))) for b in BANDS[1:]))
    for lo, hi in ((0, 30), (31, 60), (61, 150), (0, 499)):
        say(code, '  rounds %d-%d:' % (lo, hi), ', '.join('%s %s' % (b, frac(*share([g for g in S if g['band'] == b], lo, hi))) for b in BANDS[1:]))
    for lab2, test in (('they have more dragons', lambda m: m[7] > m[6]), ('equal', lambda m: m[7] == m[6]), ('we have more', lambda m: m[7] < m[6])):
        parts = []
        for b in BANDS[1:]:
            ms = [m for g in S if g['band'] == b for m in meet(g) if test(m)]
            parts.append('%s %s' % (b, frac(sum(1 for m in ms if m[1] == 1), len(ms))))
        say(code, '  when', lab2, ':', ', '.join(parts))
    big = [g for g in code_games(code) if not g['small']]
    say(code, '  big layouts, rounds 0-60:', ', '.join('%s %s' % (b, frac(*share([g for g in big if g['band'] == b]))) for b in BANDS[1:]))

say('')
say('=================== F42 ===================')
AGES = ['0-20', '21-50', '51-100', 'over 100', 'never']


def pool(games, s):
    t = sum(g['lone'][s]['turns'] for g in games)
    age = [sum(g['lone'][s]['age'][i] for g in games) for i in range(5)]
    n6 = [sum(g['lone'][s]['near6'][i] for g in games) for i in range(5)]
    n12 = [sum(g['lone'][s]['near12'][i] for g in games) for i in range(5)]
    return t, age, n6, n12


def describe(label, games, s):
    t, age, n6, n12 = pool(games, s)
    if not t:
        say(label, len(games), 'games, no turns')
        return
    view = sum(g['lone'][s]['view'] for g in games)
    say(label, len(games), 'games,', t, 'turns: age', ', '.join('%s %.3f' % (AGES[i], age[i] / t) for i in range(5)),
        '; near (6 or less) in', ', '.join('%.3f of %s' % (n6[i] / age[i] if age[i] else float('nan'), AGES[i]) for i in range(4)),
        '; 7 to 12 when 0-20: %.3f' % (n12[0] / age[0] if age[0] else float('nan')), '; in view at that turn %.3f' % (view / t),
        '; near over all turns %.3f' % (sum(n6) / t), '; any head within 12: %.3f' % ((sum(n6) + sum(n12)) / t))
    return t, age, n6, n12


def bootg(games, s, n=4000):
    f1 = []
    f2 = []
    for _ in range(n):
        pick = [games[rng.randrange(len(games))] for _ in games]
        t, age, n6, n12 = pool(pick, s)
        f1.append(age[0] / t if t else 0)
        f2.append(n6[0] / age[0] if age[0] else 0)
    f1.sort()
    f2.sort()
    return 'fresh %.3f to %.3f, near when fresh %.3f to %.3f' % (f1[int(n * 0.025)], f1[int(n * 0.975) - 1], f2[int(n * 0.025)], f2[int(n * 0.975) - 1])


sets = {}
for code in ('main', 'v31'):
    C = [g for g in code_games(code) if g['last_round'] == 499 and g['end_reason'] != 0 and g['key'] not in DEAD_END
         and g['final'][0]['queen'] != g['final'][1]['queen']]
    Lo = [g for g in C if g['final'][0]['queen'] == 0 and g['final'][1]['queen'] > 0]
    Mi = [g for g in C if g['final'][1]['queen'] == 0 and g['final'][0]['queen'] > 0]
    say(code, 'full queen-rule games off dead-end layouts:', len(C), '; only their queen alive', len(Lo), '(lost', sum(1 for g in Lo if not g['win']), ') ; only ours', len(Mi), '(won', sum(1 for g in Mi if g['win']), ')',
        '; games with zero lone turns', sum(1 for g in Lo if g['lone'][1]['turns'] == 0), sum(1 for g in Mi if g['lone'][0]['turns'] == 0))
    LoN = [g for g in Lo if g['map'] != 'Portals']
    LoP = [g for g in Lo if g['map'] == 'Portals']
    sets[code] = (LoN, LoP, Mi)
    describe(code + ' without Portals:', LoN, 1)
    say('    games resampled:', bootg(LoN, 1))
    describe(code + ' Portals:', LoP, 1)
    say('    Portals: turns with a head of ours in her area', sum(g['lone'][1]['turns'] - g['lone'][1]['zero_same'] for g in LoP))
    describe(code + ' with Portals:', Lo, 1)
    describe(code + ' MIRROR (their heads, our lone queen):', Mi, 0)
    say('    games resampled:', bootg(Mi, 0), '; mirror games on Portals', sum(1 for g in Mi if g['map'] == 'Portals'), '; mirror by size small/big', sum(1 for g in Mi if g['small']), sum(1 for g in Mi if not g['small']))
    describe(code + ' big layouts:', [g for g in LoN if not g['small']], 1)
    say('    games resampled:', bootg([g for g in LoN if not g['small']], 1))
    describe(code + ' small without Portals:', [g for g in LoN if g['small']], 1)
    say('    games resampled:', bootg([g for g in LoN if g['small']], 1))
    describe(code + ' MIRROR big:', [g for g in Mi if not g['small']], 0)
    describe(code + ' MIRROR small:', [g for g in Mi if g['small']], 0)
    for nm_, key in (('her body in the box of a head of ours', 'ageX'), ('a body tile of ours in the box of her head', 'ageY')):
        for lab, GG in (('with Portals', Lo), ('without Portals', LoN)):
            t = sum(g['lone'][1]['turns'] for g in GG)
            say(code, '  by body (', nm_, ')', lab, ': fresh %.3f' % (sum(g['lone'][1][key][0] for g in GG) / t), 'never %.3f' % (sum(g['lone'][1][key][4] for g in GG) / t))
    if code == 'main':
        h1 = [g for g in LoN if g['t'] < SPLIT]
        h2 = [g for g in LoN if g['t'] >= SPLIT]
        describe('main first half:', h1, 1)
        describe('main second half:', h2, 1)
    # in view now: is she within 6 path steps
    for lab, GG, s in (('without Portals', LoN, 1), ('small', [g for g in LoN if g['small']], 1), ('big', [g for g in LoN if not g['small']], 1), ('mirror', Mi, 0)):
        v = sum(g['lone'][s]['view'] for g in GG)
        fine = [sum(g['lone'][s]['fine'][i] for g in GG) for i in range(4)]
        fn = [sum(g['lone'][s]['fine_near6'][i] for g in GG) for i in range(4)]
        t = sum(g['lone'][s]['turns'] for g in GG)
        say(code, ' ', lab, ': in view now', v, '; of these within 6 path steps', sum(g['lone'][s]['viewnear6'] for g in GG), ', 7 to 12', sum(g['lone'][s]['viewnear12'] for g in GG),
            '; near by age 0 / 1-5 / 6-10 / 11-20:', ', '.join('%d of %d' % (fn[i], fine[i]) for i in range(4)),
            '; heads of the other side per turn %.1f' % (sum(g['lone'][s]['n_other'] for g in GG) / t if t else 0),
            '; in view by chance (heads on random tiles) %.3f, seen %.3f' % (sum(g['lone'][s]['expV'] for g in GG) / t if t else 0, v / t if t else 0))
    # per layout
    for k in sorted(set(g['key'] for g in Lo)):
        GG = [g for g in Lo if g['key'] == k]
        t, age, n6, n12 = pool(GG, 1)
        say(code, '   layout', k, lay_info[k][2], 'cells:', len(GG), 'games', t, 'turns, fresh %.3f, never %.3f, near when fresh %.3f' % (age[0] / max(t, 1), age[4] / max(t, 1), n6[0] / age[0] if age[0] else float('nan')))
    # per game spread and removals
    pg = sorted(((g['lone'][1]['age'][0] / g['lone'][1]['turns'], g['lone'][1]['near6'][0], g['lone'][1]['age'][0], g['lone'][1]['turns'], g['game'], g['key']) for g in LoN if g['lone'][1]['turns']), reverse=True)
    say(code, '  per game fresh share: above 0.9 in', sum(1 for x in pg if x[0] > 0.9), ', under 0.1 in', sum(1 for x in pg if x[0] < 0.1), 'of', len(pg), '; median %.3f' % pg[len(pg) // 2][0])
    bynear = sorted(LoN, key=lambda g: -g['lone'][1]['near6'][0])
    say(code, '  three games with most fresh-and-near turns:', [(g['game'], g['key'], g['lone'][1]['near6'][0], g['lone'][1]['age'][0], g['lone'][1]['turns']) for g in bynear[:3]])
    t, age, n6, n12 = pool(bynear[3:], 1)
    say(code, '  without them: fresh %.3f, near when fresh %.3f' % (age[0] / t, n6[0] / age[0]))
    byfresh = sorted(LoN, key=lambda g: -g['lone'][1]['age'][0])
    t, age, n6, n12 = pool(byfresh[3:], 1)
    say(code, '  without the three games with most fresh turns: fresh %.3f, near when fresh %.3f' % (age[0] / t, n6[0] / age[0]))
    games0 = sum(1 for g in LoN if g['lone'][1]['near6'][0] == 0)
    say(code, '  games with no fresh-and-near turn:', games0, 'of', len(LoN))
    ops = sorted(set(g['opponent'] for g in LoN))
    lo_ = []
    for o in ops:
        t, age, n6, n12 = pool([g for g in LoN if g['opponent'] != o], 1)
        lo_.append((round(age[0] / t, 3), round(n6[0] / age[0], 3)))
    say(code, '  one opponent left out (', len(ops), 'opponents ): fresh', min(x[0] for x in lo_), 'to', max(x[0] for x in lo_), '; near when fresh', min(x[1] for x in lo_), 'to', max(x[1] for x in lo_))
    say(code, '  by band:', ', '.join('%s %d games fresh %.3f' % (b, len([g for g in LoN if g['band'] == b]), (pool([g for g in LoN if g['band'] == b], 1)[1][0] / max(1, pool([g for g in LoN if g['band'] == b], 1)[0]))) for b in BANDS))
    say(code, '  first lone round: median', sorted(g['lone'][1]['first'] for g in LoN if g['lone'][1]['first'] is not None)[len(LoN) // 2] if LoN else None,
        '; lone turns per game: median', sorted(g['lone'][1]['turns'] for g in LoN)[len(LoN) // 2] if LoN else None)


def shuffle_gap(A, sa, B, sb, which, n=20000):
    """game labels shuffled between two sets; which = 0 fresh share, 1 near when fresh; two-sided count"""
    def stat(rows):
        t = sum(r[0] for r in rows)
        f = sum(r[1] for r in rows)
        nr = sum(r[2] for r in rows)
        if which == 0:
            return f / t if t else 0
        return nr / f if f else 0
    ra = [(g['lone'][sa]['turns'], g['lone'][sa]['age'][0], g['lone'][sa]['near6'][0]) for g in A]
    rb = [(g['lone'][sb]['turns'], g['lone'][sb]['age'][0], g['lone'][sb]['near6'][0]) for g in B]
    obs = abs(stat(ra) - stat(rb))
    allr = ra + rb
    ge = 0
    for _ in range(n):
        rng.shuffle(allr)
        if abs(stat(allr[:len(ra)]) - stat(allr[len(ra):])) >= obs:
            ge += 1
    return ge


mN, mP, mM = sets['main']
vN, vP, vM = sets['v31']
say('main against v31 (without Portals), game labels shuffled: fresh gap as large in', shuffle_gap(mN, 1, vN, 1, 0), 'of 20000; near when fresh', shuffle_gap(mN, 1, vN, 1, 1))
say('main: losses against mirror: fresh', shuffle_gap(mN, 1, mM, 0, 0), 'of 20000; near when fresh', shuffle_gap(mN, 1, mM, 0, 1))
say('v31: losses against mirror: fresh', shuffle_gap(vN, 1, vM, 0, 0), 'of 20000; near when fresh', shuffle_gap(vN, 1, vM, 0, 1))
say('both codes: losses against mirror: fresh', shuffle_gap(mN + vN, 1, mM + vM, 0, 0), 'of 20000; near when fresh', shuffle_gap(mN + vN, 1, mM + vM, 0, 1))
for code, (LoN, LoP, Mi) in sets.items():
    sm = [g for g in LoN if g['small']]
    bg = [g for g in LoN if not g['small']]
    say(code, 'small against big, game labels shuffled: fresh', shuffle_gap(sm, 1, bg, 1, 0), 'of 20000; near when fresh', shuffle_gap(sm, 1, bg, 1, 1))
bothN = mN + vN
describe('both codes without Portals:', bothN, 1)
describe('both codes mirror:', mM + vM, 0)
describe('both codes small:', [g for g in bothN if g['small']], 1)
describe('both codes big:', [g for g in bothN if not g['small']], 1)
describe('both codes mirror small:', [g for g in mM + vM if g['small']], 0)
describe('both codes mirror big:', [g for g in mM + vM if not g['small']], 0)

say('')
say('=================== rows.jsonl (read last) ===================')
rows = {}
for line in Path('data/analysis/ladder/rows.jsonl').read_text().splitlines():
    if line.strip():
        r = json.loads(line)
        rows[r['game']] = r
mm = Counter()
both = 0
for g in G:
    r = rows.get(g['game'])
    if r is None:
        mm['no row'] += 1
        continue
    both += 1
    def chk(name, a, b):
        if a != b:
            mm[name] += 1
    chk('code', g['code'], r['our_code'] if r['our_code'] in ('main', 'v31') else 'other')
    chk('layout key', g['key'], r['map_key'])
    chk('last round', g['last_round'], r['last_round'])
    chk('elimination', g['end_reason'] == 0, r['ended_by'] == 'elimination')
    chk('win', g['win'], r['win'])
    chk('rating', g['opponentElo'], r['opponent_rating'])
    chk('time', g['completedAt'][:19], r['time'][:19])
    chk('final', [(f['alive'], f['total'], f['longest'], f['queen']) for f in g['final']],
        [(r['final'][s]['alive'], r['final'][s]['total'], r['final'][s]['longest'], r['final'][s]['queen_length']) for s in ('us', 'them')])
    for rr in (50, 100, 200):
        c = r['curves'].get(str(rr))
        if c is None:
            chk('curve %d missing' % rr, len(g['total'][0]) > rr, False)
        else:
            chk('curve %d' % rr, [(g['alive'][s][rr], g['total'][s][rr], g['eaten'][s][rr]) for s in (0, 1)],
                [(c[s]['alive'], c[s]['total'], c[s]['pearls']) for s in ('us', 'them')])
    chk('head-on count', len(g['meetings']), r['head_on']['count'])
say('games in both', both, 'of', len(G), '; rows', len(rows), '; disagreements', dict(mm))
maps = json.loads(Path('data/analysis/ladder/maps.json').read_text())
bad = [k for k in lay_info if k not in maps or (maps[k]['width'], maps[k]['height'], maps[k]['queen_spawn_distance'], maps[k]['dragons_at_spawn']) != (lay_info[k][0], lay_info[k][1], lay_info[k][3], lay_info[k][4])]
say('layouts', len(lay_info), 'maps.json entries', len(maps), 'size, queen distance or spawn count different:', bad)
say('dead-end layouts in maps.json:', sorted(k for k in maps if maps[k]['queen_spawn_dead_end']))
out.close()
