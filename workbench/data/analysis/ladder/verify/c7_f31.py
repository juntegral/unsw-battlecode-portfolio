#!/usr/bin/env python3
"""Verifier claims 7 (run of 2026-10-07 07:35 KST), queue F31: recount from the x7 shards (extract7.py, own rebuild
from the raw replays). Side 0 = ours, 1 = theirs. Writes f31-numbers.txt."""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timedelta
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
LINES = []
CUT = '2026-10-06T14:48:15'


def say(*a):
    s = ' '.join(str(x) for x in a)
    LINES.append(s)
    print(s)


def load():
    games = []
    for k in range(6):
        with open(V / ('x7-%d.jsonl' % k)) as f:
            for line in f:
                if line.strip():
                    games.append(json.loads(line))
    bad = [g for g in games if 'error' in g]
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
        g['evening'] = (datetime.fromisoformat(g['at_kst']) - timedelta(hours=6)).strftime('%m-%d') if g.get('at_kst') else '?'
        g['opp'] = '%s (%s)' % (g.get('opponent'), g.get('opponentId'))
        g['late'] = (g.get('completedAt') or '') >= CUT
    return order, bad


def sm(g, key, s, a, b):
    return sum(g[key][s][a:b + 1])


def div(a, b):
    return a / b if b else float('nan')


def f3(x):
    return '%.3f' % x


def sign(k, n):
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1)) / 2 ** n)


def four(g, key, w1, w2):
    return (sm(g, key, 0, w1[0], w1[1]), sm(g, key, 0, w2[0], w2[1]), sm(g, key, 1, w1[0], w1[1]), sm(g, key, 1, w2[0], w2[1]))


def rb(gs, key, w1, w2):
    q = [four(g, key, w1, w2) for g in gs]
    o1 = sum(x[0] for x in q)
    o2 = sum(x[1] for x in q)
    t1 = sum(x[2] for x in q)
    t2 = sum(x[3] for x in q)
    lower = sum(1 for x in q if x[1] * x[2] < x[3] * x[0])
    higher = sum(1 for x in q if x[1] * x[2] > x[3] * x[0])
    return dict(n=len(gs), o1=o1, o2=o2, t1=t1, t2=t2, ro=div(o2, o1), rt=div(t2, t1), lower=lower, higher=higher)


def fr(r):
    return 'ours %s (%d then %d), theirs %s (%d then %d), %d games; ours lower in %d, higher in %d' % (
        f3(r['ro']), r['o1'], r['o2'], f3(r['rt']), r['t1'], r['t2'], r['n'], r['lower'], r['higher'])


def short(r):
    return '%s/%s[%d]' % ('%.2f' % r['ro'], '%.2f' % r['rt'], r['n'])


def boot_gap(gs, key, w1, w2, n=1000, seed=1):
    acc = {}
    for g in gs:
        f = four(g, key, w1, w2)
        c = acc.get(g['battle'])
        acc[g['battle']] = f if c is None else tuple(x + y for x, y in zip(c, f))
    units = list(acc.values())
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        a = b = c = d = 0
        for _k in range(len(units)):
            u = units[rng.randrange(len(units))]
            a += u[0]
            b += u[1]
            c += u[2]
            d += u[3]
        if a and c:
            vals.append(b / a - d / c)
    vals.sort()
    if not vals:
        return None
    return 'ours minus theirs 95%% interval %.3f to %.3f over %d battles, share of resamples at or above zero %.3f' % (
        vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1], len(units), sum(1 for v in vals if v >= 0) / len(vals))


def lt(gs, s, a, b):
    return (sum(sm(g, 'adjL', s, a, b) for g in gs), sum(sm(g, 'adjT', s, a, b) for g in gs))


def lr(gs, s, a, b):
    L, T = lt(gs, s, a, b)
    return '%s of %d' % (f3(div(L, T)), T)


def boot_step(gs, w1, w2, n=1000, seed=1):
    acc = {}
    for g in gs:
        f = (sm(g, 'adjL', 0, w1[0], w1[1]), sm(g, 'adjT', 0, w1[0], w1[1]), sm(g, 'adjL', 0, w2[0], w2[1]), sm(g, 'adjT', 0, w2[0], w2[1]),
             sm(g, 'adjL', 1, w1[0], w1[1]), sm(g, 'adjT', 1, w1[0], w1[1]), sm(g, 'adjL', 1, w2[0], w2[1]), sm(g, 'adjT', 1, w2[0], w2[1]))
        c = acc.get(g['battle'])
        acc[g['battle']] = f if c is None else tuple(x + y for x, y in zip(c, f))
    units = list(acc.values())
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        t = [0] * 8
        for _k in range(len(units)):
            u = units[rng.randrange(len(units))]
            for z in range(8):
                t[z] += u[z]
        if t[1] and t[3] and t[5] and t[7]:
            vals.append((t[2] / t[3] - t[0] / t[1]) - (t[6] / t[7] - t[4] / t[5]))
    vals.sort()
    if not vals:
        return None
    return 'our step minus their step 95%% interval %.3f to %.3f over %d battles, share at or below zero %.3f' % (
        vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1], len(units), sum(1 for v in vals if v <= 0) / len(vals))


def p150(g):
    return g['last_round'] >= 200 and g['alive'][0][150] >= 20


def p300(g):
    return g['last_round'] >= 400 and g['alive'][0][300] >= 10


def s150(g):
    return g['last_round'] >= 175 and g['alive'][0][149] >= 20


def s300(g):
    return g['last_round'] >= 325 and g['alive'][0][299] >= 10


PW1, PW2 = (101, 150), (151, 200)
QW1, QW2 = (201, 300), (301, 400)
SW1, SW2 = (125, 149), (150, 174)
UW1, UW2 = (275, 299), (300, 324)


def headline(gs, label):
    big = [g for g in gs if g['big']]
    oth = [g for g in gs if not g['big']]
    say('  ' + label + ': %d games (%d big, %d other)' % (len(gs), len(big), len(oth)))
    say('    big   pearls 151-200 / 101-150: ' + fr(rb([g for g in big if p150(g)], 'eat', PW1, PW2)))
    say('    big   splits 150-174 / 125-149: ' + fr(rb([g for g in big if s150(g)], 'spl', SW1, SW2)))
    say('    big   left rate ours ' + ', '.join(lr(big, 0, a, b) for a, b in ((101, 125), (126, 150), (151, 175), (176, 199))))
    say('    big   left rate theirs ' + ', '.join(lr(big, 1, a, b) for a, b in ((101, 125), (126, 150), (151, 175), (176, 199))))
    say('    big   pearls 301-400 / 201-300: ' + fr(rb([g for g in big if p300(g)], 'eat', QW1, QW2)))
    say('    other pearls 151-200 / 101-150: ' + fr(rb([g for g in oth if p150(g)], 'eat', PW1, PW2)))
    say('    other splits 150-174 / 125-149: ' + fr(rb([g for g in oth if s150(g)], 'spl', SW1, SW2)))
    say('    other pearls 301-400 / 201-300: ' + fr(rb([g for g in oth if p300(g)], 'eat', QW1, QW2)))
    say('    other splits 300-324 / 275-299: ' + fr(rb([g for g in oth if s300(g)], 'spl', UW1, UW2)))
    say('    other left rate ours 251-300 %s, 301-350 %s; theirs %s, %s' % (lr(oth, 0, 251, 300), lr(oth, 0, 301, 350), lr(oth, 1, 251, 300), lr(oth, 1, 301, 350)))
    say('    other left rate ours 126-150 %s, 151-175 %s; theirs %s, %s' % (lr(oth, 0, 126, 150), lr(oth, 0, 151, 175), lr(oth, 1, 126, 150), lr(oth, 1, 151, 175)))


def main():
    games, bad = load()
    say('F31 recount, verifier run of 2026-10-07 07:35 KST')
    say('games read %d, unreadable %d, final state not equal to the result block %d, body count check failed %d' % (
        len(games), len(bad), sum(1 for g in games if not g['final_ok']), sum(1 for g in games if not g['occ_ok'])))
    an = Counter()
    for g in games:
        for k, v in g['anomalies'].items():
            an[k] += v
    say('parse anomalies:', dict(an))
    say('by code:', dict(Counter(g['code'] for g in games)))
    codes = {c: [g for g in games if g['code'] == c] for c in ('main', 'v31')}
    both = codes['main'] + codes['v31']
    say('big layouts (cells > 1200):', sorted(set('%s %dx%d' % (g['map_key'], g['W'], g['H']) for g in games if g['big'])))
    say('other layouts:', sorted(set('%s %dx%d' % (g['map_key'], g['W'], g['H']) for g in games if not g['big'])))
    say('greatest number of our dragons alive at the end of any round, any game: %d; theirs %d' % (
        max(max(g['alive'][0]) for g in both), max(max(g['alive'][1]) for g in both)))

    say('')
    say('== A. headline numbers per code ==')
    for c in ('main', 'v31'):
        headline(codes[c], c)
    say('')
    say('== B. slices of main ==')
    m = codes['main']
    headline([g for g in m if g['band'] == '1700-1899'], 'main, opponents 1700-1899')
    headline([g for g in m if g['band'] == '1900-2099'], 'main, opponents 1900-2099')
    headline([g for g in m if g['band'] not in ('1700-1899', '1900-2099')], 'main, other ratings')
    headline([g for g in m if not g['late']], 'main, before ' + CUT)
    headline([g for g in m if g['late']], 'main, from ' + CUT)

    say('')
    say('== C. per layout (ours/theirs[games]); p150 = pearls 151-200 / 101-150, s150 = splits 150-174 / 125-149, L150 = left rate 126-150 to 151-175 ours | theirs; the same at 300: pearls 301-400 / 201-300, splits 300-324 / 275-299, left 251-300 to 301-350 ==')
    for c in ('main', 'v31'):
        say('  code ' + c)
        keys = sorted(set(g['map_key'] for g in codes[c]), key=lambda k: (-max(g['W'] * g['H'] for g in codes[c] if g['map_key'] == k), k))
        for k in keys:
            gs = [g for g in codes[c] if g['map_key'] == k]
            g0 = gs[0]
            say('    %-22s %2dx%2d=%4d n=%3d | p150 %s s150 %s L150 %s>%s | %s>%s || p300 %s s300 %s L300 %s>%s | %s>%s' % (
                k, g0['W'], g0['H'], g0['W'] * g0['H'], len(gs),
                short(rb([g for g in gs if p150(g)], 'eat', PW1, PW2)), short(rb([g for g in gs if s150(g)], 'spl', SW1, SW2)),
                lr(gs, 0, 126, 150), lr(gs, 0, 151, 175), lr(gs, 1, 126, 150), lr(gs, 1, 151, 175),
                short(rb([g for g in gs if p300(g)], 'eat', QW1, QW2)), short(rb([g for g in gs if s300(g)], 'spl', UW1, UW2)),
                lr(gs, 0, 251, 300), lr(gs, 0, 301, 350), lr(gs, 1, 251, 300), lr(gs, 1, 301, 350)))

    say('')
    say('== D. where is the step: 25-round bins and single rounds ==')
    bins = [(51, 75), (76, 100), (101, 125), (126, 150), (151, 175), (176, 200), (201, 225), (226, 250), (251, 275), (276, 300), (301, 325), (326, 350), (351, 375), (376, 400)]
    for c in ('main', 'v31'):
        for grp, name in ((True, 'big'), (False, 'other')):
            gs = [g for g in codes[c] if g['big'] == grp and g['last_round'] >= 400]
            say('  %s %s, the %d games that reached round 400 (same games in every bin)' % (c, name, len(gs)))
            for a, b in bins:
                eo = sum(sm(g, 'eat', 0, a, b) for g in gs)
                et = sum(sm(g, 'eat', 1, a, b) for g in gs)
                ao = sum(sm(g, 'alive', 0, a - 1, b - 1) for g in gs)
                at = sum(sm(g, 'alive', 1, a - 1, b - 1) for g in gs)
                so = sum(sm(g, 'spl', 0, a, b) for g in gs)
                st = sum(sm(g, 'spl', 1, a, b) for g in gs)
                say('    r%3d-%3d pearls ours %5d theirs %5d | per dragon-round ours %s theirs %s | splits ours %4d theirs %4d | left ours %s theirs %s | our dragons per game %.1f theirs %.1f' % (
                    a, b, eo, et, f3(div(eo, ao)), f3(div(et, at)), so, st, lr(gs, 0, a, b), lr(gs, 1, a, b),
                    div(ao, len(gs) * (b - a + 1)), div(at, len(gs) * (b - a + 1))))
    for c in ('main', 'v31'):
        for grp, name, r0, r1 in ((True, 'big', 143, 158), (False, 'other', 143, 158), (False, 'other', 293, 308), (True, 'big', 293, 308)):
            gs = [g for g in codes[c] if g['big'] == grp and g['last_round'] >= r1]
            say('  %s %s single rounds, %d games reaching round %d: round, our pearls, their pearls, our splits, their splits, our left rate, their left rate' % (c, name, len(gs), r1))
            for r in range(r0, r1 + 1):
                say('    r%d  %4d %4d  %3d %3d  %s  %s' % (r, sum(g['eat'][0][r] for g in gs), sum(g['eat'][1][r] for g in gs),
                                                    sum(g['spl'][0][r] for g in gs), sum(g['spl'][1][r] for g in gs), lr(gs, 0, r, r), lr(gs, 1, r, r)))

    say('')
    say('== E. chance and leave-outs (big layouts) ==')
    for c in ('main', 'v31'):
        big = [g for g in codes[c] if g['big']]
        pg = [g for g in big if p150(g)]
        sg = [g for g in big if s150(g)]
        r = rb(pg, 'eat', PW1, PW2)
        say('  %s pearls: %s' % (c, fr(r)))
        say('     sign test, ours lower in %d of %d untied games: p = %.2g; %s' % (r['lower'], r['lower'] + r['higher'], sign(r['lower'], r['lower'] + r['higher']), boot_gap(pg, 'eat', PW1, PW2)))
        r = rb(sg, 'spl', SW1, SW2)
        say('  %s splits: %s' % (c, fr(r)))
        say('     sign test, ours lower in %d of %d untied games: p = %.2g; %s' % (r['lower'], r['lower'] + r['higher'], sign(r['lower'], r['lower'] + r['higher']), boot_gap(sg, 'spl', SW1, SW2)))
        say('  %s left rate 126-150 to 151-175: ours %s to %s, theirs %s to %s; %s' % (c, lr(big, 0, 126, 150), lr(big, 0, 151, 175), lr(big, 1, 126, 150), lr(big, 1, 151, 175), boot_step(big, (126, 150), (151, 175))))
        up = 0
        dn = 0
        for g in big:
            a = lt([g], 0, 126, 150)
            b = lt([g], 0, 151, 175)
            if a[1] >= 10 and b[1] >= 10:
                if b[0] * a[1] > a[0] * b[1]:
                    up += 1
                elif b[0] * a[1] < a[0] * b[1]:
                    dn += 1
        say('     games (10 or more such turns in both windows) in which our left rate rose %d, fell %d; sign p = %.2g' % (up, dn, sign(up, up + dn)))
        for key in ('map_key', 'opp', 'evening'):
            vals = sorted(set(g[key] for g in big))
            outp = []
            outs = []
            outl = []
            for v in vals:
                rp = rb([g for g in pg if g[key] != v], 'eat', PW1, PW2)
                rs = rb([g for g in sg if g[key] != v], 'spl', SW1, SW2)
                rest = [g for g in big if g[key] != v]
                a = lt(rest, 0, 126, 150)
                b = lt(rest, 0, 151, 175)
                a2 = lt(rest, 1, 126, 150)
                b2 = lt(rest, 1, 151, 175)
                outp.append((rp['rt'] - rp['ro'], rp['ro'], rp['rt'], v))
                outs.append((rs['rt'] - rs['ro'], rs['ro'], rs['rt'], v))
                outl.append(((div(b[0], b[1]) - div(a[0], a[1])) - (div(b2[0], b2[1]) - div(a2[0], a2[1])), div(a[0], a[1]), div(b[0], b[1]), v))
            wp = min(outp)
            ws = min(outs)
            wl = min(outl)
            say('     leaving out one %s (%d values): smallest pearl gap theirs minus ours %.3f (ours %.3f, theirs %.3f, without %s); smallest split gap %.3f (ours %.3f, theirs %.3f, without %s); smallest left step ours minus theirs %.3f (ours %.3f to %.3f, without %s)' % (
                key, len(vals), wp[0], wp[1], wp[2], wp[3], ws[0], ws[1], ws[2], ws[3], wl[0], wl[1], wl[2], wl[3]))
        top = sorted(pg, key=lambda g: sm(g, 'eat', 0, 151, 200) - sm(g, 'eat', 0, 101, 150))[:3]
        ids = set(g['game'] for g in top)
        say('     without the three games with the largest fall in our pearls (%s): %s' % (sorted(ids), fr(rb([g for g in pg if g['game'] not in ids], 'eat', PW1, PW2))))
        top = sorted(sg, key=lambda g: sm(g, 'spl', 0, 150, 174) - sm(g, 'spl', 0, 125, 149))[:3]
        ids = set(g['game'] for g in top)
        say('     without the three games with the largest fall in our splits (%s): %s' % (sorted(ids), fr(rb([g for g in sg if g['game'] not in ids], 'spl', SW1, SW2))))
        say('     per opponent (3 or more big games), pearls: ' + '; '.join('%s %s' % (o, short(rb([g for g in pg if g['opp'] == o], 'eat', PW1, PW2))) for o, n in Counter(g['opp'] for g in pg).most_common() if n >= 3))
        say('     per evening, pearls: ' + '; '.join('%s %s' % (o, short(rb([g for g in pg if g['evening'] == o], 'eat', PW1, PW2))) for o in sorted(set(g['evening'] for g in pg))))
    say('  other layouts at 300:')
    for c in ('main', 'v31'):
        oth = [g for g in codes[c] if not g['big']]
        pg = [g for g in oth if p300(g)]
        sg = [g for g in oth if s300(g)]
        r = rb(pg, 'eat', QW1, QW2)
        say('  %s pearls 301-400 / 201-300: %s' % (c, fr(r)))
        say('     sign p = %.2g; %s' % (sign(r['lower'], r['lower'] + r['higher']), boot_gap(pg, 'eat', QW1, QW2)))
        r = rb(sg, 'spl', UW1, UW2)
        say('  %s splits 300-324 / 275-299: %s' % (c, fr(r)))
        say('     sign p = %.2g; %s' % (sign(r['lower'], r['lower'] + r['higher']), boot_gap(sg, 'spl', UW1, UW2)))
        say('  %s left rate 251-300 to 301-350: ours %s to %s, theirs %s to %s; %s' % (c, lr(oth, 0, 251, 300), lr(oth, 0, 301, 350), lr(oth, 1, 251, 300), lr(oth, 1, 301, 350), boot_step(oth, (251, 300), (301, 350))))
        for key in ('map_key', 'opp'):
            vals = sorted(set(g[key] for g in oth))
            outp = []
            for v in vals:
                rp = rb([g for g in pg if g[key] != v], 'eat', QW1, QW2)
                outp.append((rp['rt'] - rp['ro'], rp['ro'], rp['rt'], v))
            wp = min(outp)
            say('     leaving out one %s: smallest pearl gap theirs minus ours %.3f (ours %.3f, theirs %.3f, without %s)' % (key, wp[0], wp[1], wp[2], wp[3]))
        r = rb([g for g in oth if p150(g)], 'eat', PW1, PW2)
        say('  %s other layouts pearls at 150: %s; %s' % (c, fr(r), boot_gap([g for g in oth if p150(g)], 'eat', PW1, PW2)))
        say('  %s other layouts left rate 126-150 to 151-175: %s' % (c, boot_step(oth, (126, 150), (151, 175))))

    say('')
    say('== F. adjacent pearls from the turn records (big layouts) ==')
    names = {10: 'top length without the actor, all free adjacent pearls', 11: 'top length of the whole side, all free adjacent pearls',
             14: 'top length without the actor, uncontested pearls only', 15: 'top length of the whole side, uncontested pearls only'}
    for c in ('main', 'v31'):
        big = [g for g in codes[c] if g['big']]
        say('  %s, %d big games, %d with a record' % (c, len(big), sum(1 for g in big if g['recs'])))
        for idx in (10, 11, 14, 15):
            t = [[[0, 0], [0, 0]], [[0, 0], [0, 0]]]
            for g in big:
                for r in g['recs']:
                    if 151 <= r[0] <= 199:
                        cell = t[r[1]][0 if r[idx] <= 9 else 1]
                        cell[0] += r[2]
                        cell[1] += 1
            say('    zone r151-199 (%s): ours inside %s of %d, outside %s of %d; theirs inside %s of %d, outside %s of %d' % (
                names[idx], f3(div(t[0][0][0], t[0][0][1])), t[0][0][1], f3(div(t[0][1][0], t[0][1][1])), t[0][1][1],
                f3(div(t[1][0][0], t[1][0][1])), t[1][0][1], f3(div(t[1][1][0], t[1][1][1])), t[1][1][1]))
        for idx, nm in ((12, 'all free adjacent pearls'), (16, 'uncontested pearls only'), (13, 'own queen head instead of a longer dragon, all free pearls')):
            t = [[[[0, 0], [0, 0]], [[0, 0], [0, 0]]], [[[0, 0], [0, 0]], [[0, 0], [0, 0]]]]
            for g in big:
                for r in g['recs']:
                    if 101 <= r[0] <= 199:
                        cell = t[r[1]][0 if r[0] <= 150 else 1][0 if r[idx] <= 9 else 1]
                        cell[0] += r[2]
                        cell[1] += 1
            say('    longer own dragon within 9 (%s): ours r151-199 near %s of %d, not near %s of %d; r101-150 near %s of %d, not near %s of %d; theirs r151-199 %s of %d and %s of %d; r101-150 %s of %d and %s of %d' % (
                nm, f3(div(t[0][1][0][0], t[0][1][0][1])), t[0][1][0][1], f3(div(t[0][1][1][0], t[0][1][1][1])), t[0][1][1][1],
                f3(div(t[0][0][0][0], t[0][0][0][1])), t[0][0][0][1], f3(div(t[0][0][1][0], t[0][0][1][1])), t[0][0][1][1],
                f3(div(t[1][1][0][0], t[1][1][0][1])), t[1][1][0][1], f3(div(t[1][1][1][0], t[1][1][1][1])), t[1][1][1][1],
                f3(div(t[1][0][0][0], t[1][0][0][1])), t[1][0][0][1], f3(div(t[1][0][1][0], t[1][0][1][1])), t[1][0][1][1]))
        # what the dragon did on the turns it left the pearl
        for s, sn in ((0, 'ours'), (1, 'theirs')):
            for a, b in ((126, 150), (151, 175)):
                cnt = Counter()
                for g in big:
                    for r in g['recs']:
                        if r[1] == s and a <= r[0] <= b:
                            if r[2] == 0:
                                cnt['ate'] += 1
                            elif r[4]:
                                cnt['left, died in the turn'] += 1
                            elif r[3] == 1:
                                cnt['left, split'] += 1
                            elif r[3] == 0 and r[5] > 0:
                                cnt['left, moved elsewhere'] += 1
                            elif r[3] == 0:
                                cnt['left, move of no steps'] += 1
                            else:
                                cnt['left, no action and alive'] += 1
                n = sum(cnt.values())
                say('    what the dragon did, %s r%d-%d (%d turns): %s' % (sn, a, b, n, ', '.join('%s %d (%.3f)' % (k, v, v / n) for k, v in sorted(cnt.items()))))
        # by length of the acting dragon and by number of own dragons alive
        for a, b in ((126, 150), (151, 175)):
            t = defaultdict(lambda: [0, 0])
            u = defaultdict(lambda: [0, 0])
            for g in big:
                for r in g['recs']:
                    if r[1] == 0 and a <= r[0] <= b:
                        k = '1-2' if r[6] <= 2 else '3' if r[6] == 3 else '4-5' if r[6] <= 5 else '6-9' if r[6] <= 9 else '10+'
                        t[k][0] += r[2]
                        t[k][1] += 1
                        k = '<40' if r[7] < 40 else '40-54' if r[7] < 55 else '55-59' if r[7] < 60 else '60+'
                        u[k][0] += r[2]
                        u[k][1] += 1
            say('    ours r%d-%d left rate by own length: %s' % (a, b, ', '.join('%s %s of %d' % (k, f3(div(t[k][0], t[k][1])), t[k][1]) for k in ('1-2', '3', '4-5', '6-9', '10+'))))
            say('    ours r%d-%d left rate by own dragons alive at the turn: %s' % (a, b, ', '.join('%s %s of %d' % (k, f3(div(u[k][0], u[k][1])), u[k][1]) for k in ('<40', '40-54', '55-59', '60+'))))
        say('    share of non-queen turns with such a pearl, ours: ' + ', '.join('r%d-%d %s' % (a, b, f3(div(sum(sm(g, 'adjT', 0, a, b) for g in big), sum(sm(g, 'turns', 0, a, b) for g in big)))) for a, b in ((101, 125), (126, 150), (151, 175), (176, 199))) +
            '; theirs: ' + ', '.join('r%d-%d %s' % (a, b, f3(div(sum(sm(g, 'adjT', 1, a, b) for g in big), sum(sm(g, 'turns', 1, a, b) for g in big)))) for a, b in ((101, 125), (126, 150), (151, 175), (176, 199))))

    say('')
    say('== G. can the 60-dragon limit produce it ==')
    for c in ('main', 'v31'):
        for grp, name in ((True, 'big'), (False, 'other')):
            gs = [g for g in codes[c] if g['big'] == grp]
            sg = [g for g in gs if s150(g)]
            say('  %s %s: our dragons alive at the start of round 150 in the %d split-count games: %s' % (c, name, len(sg), dict(sorted(Counter(
                '<40' if g['alive'][0][149] < 40 else '40-54' if g['alive'][0][149] < 55 else '55-59' if g['alive'][0][149] < 60 else '60+' for g in sg).items()))))
            for lab, sel in (('never above 54 of ours in rounds 100-200', lambda g: max(g['alive'][0][100:201]) <= 54),
                             ('never above 44', lambda g: max(g['alive'][0][100:201]) <= 44),
                             ('55 or more at some round in 100-200', lambda g: max(g['alive'][0][100:201]) >= 55)):
                say('    %s: pearls %s' % (lab, fr(rb([g for g in gs if p150(g) and sel(g)], 'eat', PW1, PW2))))
                say('    %s: splits %s' % (lab, fr(rb([g for g in sg if sel(g)], 'spl', SW1, SW2))))
            # split and pearl rates per dragon-round by the number alive at the round start
            for a, b in ((125, 149), (150, 174)):
                t = defaultdict(lambda: [0, 0, 0])
                for g in sg:
                    for r in range(a, b + 1):
                        n0 = g['alive'][0][r - 1]
                        k = '<40' if n0 < 40 else '40-54' if n0 < 55 else '55-59' if n0 < 60 else '60+'
                        t[k][0] += g['spl'][0][r]
                        t[k][1] += g['eat'][0][r]
                        t[k][2] += n0
                say('    ours r%d-%d by own dragons at the round start, splits and pearls per dragon-round: %s' % (a, b, ', '.join(
                    '%s %s and %s over %d' % (k, f3(div(t[k][0], t[k][2])), f3(div(t[k][1], t[k][2])), t[k][2]) for k in ('<40', '40-54', '55-59', '60+'))))
    pool = [g for g in both if g['big'] and p150(g) and 20 <= g['alive'][0][150] <= 44]
    say('  big, 20 to 44 of our dragons after round 150, main and v31 together: pearls ' + fr(rb(pool, 'eat', PW1, PW2)))
    say('  splits per own length band is not in this extraction; the per dragon-round rates above hold the number of dragons fixed')

    say('')
    say('== H. cost ==')
    for c in ('main', 'v31'):
        for grp, name in ((True, 'big'), (False, 'other')):
            gs = [g for g in codes[c] if g['big'] == grp]
            w = sum(1 for g in gs if g['win'])
            full = [g for g in gs if g['last_round'] >= 400]
            say('  %s %s: won %d of %d (%.3f); in the %d games reaching 400, our share of all length after rounds 100, 150, 200, 250, 300, 400: %s; our share of pearls r101-150 %s, r151-200 %s, r201-300 %s, r301-400 %s' % (
                c, name, w, len(gs), div(w, len(gs)), len(full),
                ', '.join(f3(div(sum(g['total'][0][r] for g in full), sum(g['total'][0][r] + g['total'][1][r] for g in full))) for r in (100, 150, 200, 250, 300, 400)),
                f3(div(sum(sm(g, 'eat', 0, 101, 150) for g in full), sum(sm(g, 'eat', 0, 101, 150) + sm(g, 'eat', 1, 101, 150) for g in full))),
                f3(div(sum(sm(g, 'eat', 0, 151, 200) for g in full), sum(sm(g, 'eat', 0, 151, 200) + sm(g, 'eat', 1, 151, 200) for g in full))),
                f3(div(sum(sm(g, 'eat', 0, 201, 300) for g in full), sum(sm(g, 'eat', 0, 201, 300) + sm(g, 'eat', 1, 201, 300) for g in full))),
                f3(div(sum(sm(g, 'eat', 0, 301, 400) for g in full), sum(sm(g, 'eat', 0, 301, 400) + sm(g, 'eat', 1, 301, 400) for g in full)))))
    lowW = lowN = upW = upN = 0
    for k in sorted(set(g['map_key'] for g in both if g['big'])):
        gs = [g for g in both if g['map_key'] == k and p150(g) and sm(g, 'eat', 0, 101, 150) > 0]
        rs = sorted(sm(g, 'eat', 0, 151, 200) / sm(g, 'eat', 0, 101, 150) for g in gs)
        if not rs:
            continue
        med = rs[len(rs) // 2] if len(rs) % 2 else (rs[len(rs) // 2 - 1] + rs[len(rs) // 2]) / 2
        lo = [g for g in gs if sm(g, 'eat', 0, 151, 200) / sm(g, 'eat', 0, 101, 150) < med]
        up = [g for g in gs if sm(g, 'eat', 0, 151, 200) / sm(g, 'eat', 0, 101, 150) > med]
        say('    %s: median of our pearl ratio %.3f; below it won %d of %d, above it won %d of %d' % (k, med, sum(1 for g in lo if g['win']), len(lo), sum(1 for g in up if g['win']), len(up)))
        lowW += sum(1 for g in lo if g['win'])
        lowN += len(lo)
        upW += sum(1 for g in up if g['win'])
        upN += len(up)
    say('  within layouts at the layout median of our pearl ratio (main and v31 together): lower halves won %d of %d, upper halves %d of %d' % (lowW, lowN, upW, upN))
    for c in ('main', 'v31'):
        gs = [g for g in codes[c] if g['big'] and g['last_round'] >= 300]
        a = sum(1 for g in gs if g['longest'][0][300] > g['longest'][1][300])
        b = sum(1 for g in gs if g['longest'][0][300] < g['longest'][1][300])
        fg = [g for g in codes[c] if g['big'] and g['last_round'] == 499]
        a2 = sum(1 for g in fg if g['longest'][0][499] > g['longest'][1][499])
        b2 = sum(1 for g in fg if g['longest'][0][499] < g['longest'][1][499])
        a1 = sum(1 for g in gs if g['longest'][0][150] > g['longest'][1][150])
        b1 = sum(1 for g in gs if g['longest'][0][150] < g['longest'][1][150])
        say('  %s big: longest dragon after round 300 ours longer in %d, theirs in %d (of %d reaching 300); after round 150 in the same games %d against %d; at the end of full games %d against %d (of %d)' % (c, a, b, len(gs), a1, b1, a2, b2, len(fg)))

    say('')
    say('== I. against rows.jsonl (comparison only) ==')
    rows = {}
    with open('data/analysis/ladder/rows.jsonl') as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                rows[r['game']] = r
    mk = cd = al = pe = n = 0
    miss = 0
    for g in games:
        r = rows.get(g['game'])
        if r is None:
            miss += 1
            continue
        n += 1
        if r.get('map_key') != g['map_key']:
            mk += 1
        rc = r.get('our_code')
        if (rc if rc in ('main', 'v31') else 'other') != g['code']:
            cd += 1
        for key in ('100', '150', '200', '300', '400'):
            cv = (r.get('curves') or {}).get(key)
            if cv is None:
                continue
            rr = int(key)
            if cv['us']['alive'] != g['alive'][0][rr] or cv['them']['alive'] != g['alive'][1][rr]:
                al += 1
            if cv['us']['pearls'] != sum(g['eat'][0][:rr + 1]) or cv['them']['pearls'] != sum(g['eat'][1][:rr + 1]):
                pe += 1
    say('  games in both %d, mine without a row %d, rows without mine %d; layout key differs in %d, code differs in %d; snapshot marks with a different number alive %d, with different cumulative pearls %d' % (
        n, miss, len(rows) - n, mk, cd, al, pe))
    open(P + 'f31-numbers.txt', 'w').write('\n'.join(LINES) + '\n')


main()
