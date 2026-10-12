#!/usr/bin/env python3
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
"""Verifier claims 9 (run of 2026-10-07 09:18 KST), F39: the lone queen and short enemy heads near her. Reads the
x9 shards (own extraction from the raw replays) and writes f39-numbers.txt. maps.json is read for the free-layout
flag; rows.jsonl is read only in the last section, to compare."""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timedelta
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')
LINES = []
SIDE = ('ours', 'theirs')
WN = ('r0-100', 'r101-200', 'r201-300', 'r301 on')


def say(*a):
    s = ' '.join(str(x) for x in a)
    LINES.append(s)
    print(s)


def window(r):
    return 0 if r <= 100 else 1 if r <= 200 else 2 if r <= 300 else 3


def near5(W, H):
    seen = set()
    for dx in range(-5, 6):
        for dy in range(-5, 6):
            if abs(dx) + abs(dy) <= 5:
                seen.add((dx % W, dy % H))
    seen.discard((0, 0))
    return len(seen)


def load():
    games = []
    for k in range(6):
        for line in (V / ('x9-%d.jsonl' % k)).read_text().splitlines():
            if line.strip():
                games.append(json.loads(line))
    games = [g for g in games if 'error' not in g]
    order = sorted(games, key=lambda g: (g.get('completedAt') or '', g['game']))
    seen = {}
    maps = json.loads(Path('data/analysis/ladder/maps.json').read_text())
    for g in order:
        lst = seen.setdefault(g['map'], [])
        if g['layout'] not in lst:
            lst.append(g['layout'])
        g['map_key'] = '%s #%d' % (g['map'], lst.index(g['layout']) + 1)
        e = g.get('opponentElo') or 0
        g['band'] = '<1700' if e < 1700 else '1700-1899' if e < 1900 else '1900-2099' if e < 2100 else '2100+'
        g['free'] = not maps[g['map_key']]['queen_spawn_dead_end']
        g['full'] = g['last_round'] == 499
        t = g['total100']
        g['level'] = t is not None and max(t) > 0 and min(t) >= 0.8 * max(t)
        a5 = near5(g['W'], g['H'])
        g['cl'] = [None, None]
        for s in (0, 1):
            rows = [r for r in g['lone'] if r[0] == s]
            if not rows:
                continue
            od = g['qdeath'][1 - s]['round']
            c = dict(game=g, side=s, n=len(rows), flag=0, own5=0, zero=0, e_short=0, e_all=0, reach=0, short6=0,
                     expect=0.0, own_alive=0, own_expect=0.0, any6=0, rows=[])
            for r in rows:
                _, rnd, short6, e_short, e_all, own5, own_alive, reach, qlen, any6, nopen = r
                f = 1 if short6 > 0 else 0
                c['flag'] += f
                c['own5'] += own5
                c['zero'] += 1 if own5 == 0 else 0
                c['e_short'] += e_short
                c['e_all'] += e_all
                c['reach'] += reach
                c['short6'] += short6
                c['any6'] += 1 if any6 > 0 else 0
                c['expect'] += 1.0 - (1.0 - reach / g['n_open']) ** e_short
                c['own_alive'] += own_alive
                c['own_expect'] += own_alive * a5 / (g['W'] * g['H'] - 1)
                c['rows'].append((rnd, rnd - od, f, e_short, own5, own_alive, reach, short6))
            g['cl'][s] = c
    return order, maps


def clusters(gs, s):
    return [g['cl'][s] for g in gs if g['cl'][s] is not None]


def tot(cs, key):
    return sum(c[key] for c in cs)


def sh(cs):
    n = tot(cs, 'n')
    return (tot(cs, 'flag') / n) if n else None


def fmt(x, d=3):
    return 'none' if x is None else ('%.' + str(d) + 'f') % x


def rr(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b


def block(label, gs):
    c0, c1 = clusters(gs, 0), clusters(gs, 1)
    out = []
    for cs in (c0, c1):
        n = tot(cs, 'n')
        if n == 0:
            out.append('no lone turns')
            continue
        out.append('%.3f of %d lone turns in %d games (flagged %d); own heads within 5: sum %d, mean %.2f, none in %.3f' % (
            tot(cs, 'flag') / n, n, len(cs), tot(cs, 'flag'), tot(cs, 'own5'), tot(cs, 'own5') / n, tot(cs, 'zero') / n))
    say('%-30s ours %s' % (label, out[0]))
    say('%-30s theirs %s | ratio of the flagged shares %s' % ('', out[1], fmt(rr(sh(c0), sh(c1)), 2)))


def perm(gs, n=10000, seed=3):
    """cluster permutation: the (game, side) clusters keep their turns and flags, the labels ours / theirs are
    shuffled among them. Statistic: pooled flagged share of ours minus theirs."""
    c0, c1 = clusters(gs, 0), clusters(gs, 1)
    allc = [(c['flag'], c['n']) for c in c0 + c1]
    k = len(c0)

    def stat(lst):
        a = lst[:k]
        b = lst[k:]
        na = sum(x[1] for x in a)
        nb = sum(x[1] for x in b)
        if na == 0 or nb == 0:
            return 0.0
        return sum(x[0] for x in a) / na - sum(x[0] for x in b) / nb
    obs = stat(allc)
    rng = random.Random(seed)
    ge = 0
    lst = list(allc)
    for _ in range(n):
        rng.shuffle(lst)
        if stat(lst) >= obs - 1e-12:
            ge += 1
    return obs, ge, n, len(c0), len(c1)


def boot(gs, n=4000, seed=9):
    by = defaultdict(lambda: [0, 0, 0, 0])
    for g in gs:
        for s in (0, 1):
            c = g['cl'][s]
            if c is not None:
                by[g['battle']][2 * s] += c['flag']
                by[g['battle']][2 * s + 1] += c['n']
    keys = sorted(by)
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        a = [0, 0, 0, 0]
        for _ in keys:
            x = by[keys[rng.randrange(len(keys))]]
            for i in range(4):
                a[i] += x[i]
        if a[1] and a[3] and a[2]:
            vals.append((a[0] / a[1]) / (a[2] / a[3]))
        else:
            vals.append(float('inf'))
    vals.sort()
    return vals[int(0.025 * n)], vals[int(0.975 * n) - 1]


def strata(cs, idx, bins):
    """rows by bins of row[idx]: list of (turns, flagged, own5 sum)"""
    out = [[0, 0, 0] for _ in bins]
    for c in cs:
        for r in c['rows']:
            v = r[idx]
            for i, (lo, hi) in enumerate(bins):
                if lo <= v <= hi:
                    out[i][0] += 1
                    out[i][1] += r[2]
                    out[i][2] += r[4]
                    break
    return out


def main():
    games, maps = load()
    F = [g for g in games if g['code'] in ('main', 'v31') and g['free']]
    M = [g for g in F if g['code'] == 'main']
    O = [g for g in F if g['code'] == 'v31']
    say('games loaded', len(games), '| free main', len(M), '(full', sum(1 for g in M if g['full']), ', level', sum(1 for g in M if g['level']), ') | free v31', len(O),
        '(full', sum(1 for g in O if g['full']), ', level', sum(1 for g in O if g['level']), ')')
    say('flag = at the turn start of a lone queen, a living enemy dragon of length 4 or less has its head within 6 path steps of her head')
    say('')
    say('== lone turns, flagged share, own heads within 5 ==')
    for label, gs in (('main', M), ('v31', O), ('pooled', F)):
        block(label + ' full games', [g for g in gs if g['full']])
    for label, gs in (('main', M), ('v31', O), ('pooled', F)):
        block(label + ' all endings', gs)
    for label, gs in (('pooled', F), ('main', M), ('v31', O)):
        block(label + ' level games, all endings', [g for g in gs if g['level']])
    for label, gs in (('pooled', F), ('main', M), ('v31', O)):
        block(label + ' level and full games', [g for g in gs if g['level'] and g['full']])
    for label, gs in (('main', M), ('v31', O)):
        block(label + ' games that ended early', [g for g in gs if not g['full']])
    say('')
    say('main full games by opponent rating band:')
    for band in ('<1700', '1700-1899', '1900-2099', '2100+'):
        sub = [g for g in M if g['full'] and g['band'] == band]
        if sub:
            block('  ' + band, sub)
    say('v31 full games by opponent rating band:')
    for band in ('<1700', '1700-1899', '1900-2099', '2100+'):
        sub = [g for g in O if g['full'] and g['band'] == band]
        if sub:
            block('  ' + band, sub)
    say('')
    say('by 50 rounds since the other queen died (flagged share of lone turns, ours / theirs):')
    bins = ((0, 49), (50, 99), (100, 149), (150, 199), (200, 299), (300, 9999))
    for label, gs in (('main full', [g for g in M if g['full']]), ('v31 full', [g for g in O if g['full']]), ('main all endings', M), ('v31 all endings', O)):
        a = strata(clusters(gs, 0), 1, bins)
        b = strata(clusters(gs, 1), 1, bins)
        parts = []
        for i, (lo, hi) in enumerate(bins):
            parts.append('%d-%s: %s of %d / %s of %d' % (lo, hi if hi < 9999 else 'on', fmt(a[i][1] / a[i][0] if a[i][0] else None), a[i][0], fmt(b[i][1] / b[i][0] if b[i][0] else None), b[i][0]))
        say('  %-17s %s' % (label, ' | '.join(parts)))
    say('by raw round of the lone turn (flagged share, ours / theirs):')
    wb = ((0, 100), (101, 200), (201, 300), (301, 9999))
    for label, gs in (('main full', [g for g in M if g['full']]), ('v31 full', [g for g in O if g['full']]), ('main all endings', M), ('v31 all endings', O)):
        a = strata(clusters(gs, 0), 0, wb)
        b = strata(clusters(gs, 1), 0, wb)
        parts = []
        for i in range(4):
            parts.append('%s: %s of %d / %s of %d' % (WN[i], fmt(a[i][1] / a[i][0] if a[i][0] else None), a[i][0], fmt(b[i][1] / b[i][0] if b[i][0] else None), b[i][0]))
        say('  %-17s %s' % (label, ' | '.join(parts)))
    say('')
    say('== base rate: the same flag over queen turns with both queens alive ==')
    for label, gs in (('main all endings', M), ('v31 all endings', O), ('main full', [g for g in M if g['full']]), ('v31 full', [g for g in O if g['full']])):
        parts = []
        for w in range(4):
            x = []
            for s in (0, 1):
                n = sum(g['base'][s][w][0] for g in gs)
                f = sum(g['base'][s][w][1] for g in gs)
                x.append('%s of %d' % (fmt(f / n if n else None), n))
            parts.append('%s %s against %s' % (WN[w], x[0], x[1]))
        say('  %-17s %s' % (label, ' | '.join(parts)))
    say('  mean short enemy dragons alive at those turns (ours ; theirs) and the share expected if their heads sat on random open tiles:')
    for label, gs in (('main all endings', M), ('v31 all endings', O)):
        parts = []
        for w in range(4):
            x = []
            for s in (0, 1):
                n = sum(g['base'][s][w][0] for g in gs)
                x.append('%.1f short, expected %s, seen %s' % (sum(g['base'][s][w][2] for g in gs) / n if n else 0, fmt(sum(g['base'][s][w][7] for g in gs) / n if n else None), fmt(sum(g['base'][s][w][1] for g in gs) / n if n else None)))
            parts.append('%s %s ; %s' % (WN[w], x[0], x[1]))
        say('  %-17s %s' % (label, ' | '.join(parts)))

    say('')
    say('== is it only that the two sides have different numbers of short dragons alive? ==')
    eb = ((0, 0), (1, 2), (3, 5), (6, 10), (11, 20), (21, 40), (41, 9999))
    for label, gs in (('main full', [g for g in M if g['full']]), ('v31 full', [g for g in O if g['full']]), ('main all endings', M), ('v31 all endings', O), ('pooled level', [g for g in F if g['level']])):
        c0, c1 = clusters(gs, 0), clusters(gs, 1)
        n0, n1 = tot(c0, 'n'), tot(c1, 'n')
        if not n0 or not n1:
            continue
        say('  %s: short enemy dragons alive per lone turn: ours faces %.1f, theirs faces %.1f | all enemy dragons alive %.1f, %.1f | tiles within 6 path steps of her %.1f, %.1f' % (
            label, tot(c0, 'e_short') / n0, tot(c1, 'e_short') / n1, tot(c0, 'e_all') / n0, tot(c1, 'e_all') / n1, tot(c0, 'reach') / n0, tot(c1, 'reach') / n1))
        say('     short enemy heads within 6 per short enemy dragon alive: ours %.4f (%d of %d), theirs %.4f (%d of %d), ratio %s' % (
            tot(c0, 'short6') / max(1, tot(c0, 'e_short')), tot(c0, 'short6'), tot(c0, 'e_short'), tot(c1, 'short6') / max(1, tot(c1, 'e_short')), tot(c1, 'short6'), tot(c1, 'e_short'),
            fmt(rr(tot(c0, 'short6') / max(1, tot(c0, 'e_short')), tot(c1, 'short6') / max(1, tot(c1, 'e_short'))), 2)))
        say('     flagged share expected if the short enemy heads sat on random open tiles (her reach and their number as they were): ours %.3f, theirs %.3f, ratio %s | seen over expected: ours %.2f, theirs %.2f, ratio of those %s' % (
            tot(c0, 'expect') / n0, tot(c1, 'expect') / n1, fmt(rr(tot(c0, 'expect') / n0, tot(c1, 'expect') / n1), 2),
            tot(c0, 'flag') / tot(c0, 'expect'), tot(c1, 'flag') / tot(c1, 'expect'), fmt(rr(tot(c0, 'flag') / tot(c0, 'expect'), tot(c1, 'flag') / tot(c1, 'expect')), 2)))
        a = strata(c0, 3, eb)
        b = strata(c1, 3, eb)
        parts = []
        std0 = 0.0
        std1 = 0.0
        cov0 = 0
        cov1 = 0
        for i, (lo, hi) in enumerate(eb):
            parts.append('%d-%s: %s of %d / %s of %d' % (lo, hi if hi < 9999 else 'on', fmt(a[i][1] / a[i][0] if a[i][0] else None), a[i][0], fmt(b[i][1] / b[i][0] if b[i][0] else None), b[i][0]))
            if a[i][0] and b[i][0]:
                std0 += (a[i][1] / a[i][0]) * b[i][0]
                cov1 += b[i][0]
                std1 += (b[i][1] / b[i][0]) * a[i][0]
                cov0 += a[i][0]
        say('     by short enemy dragons alive (flagged share ours / theirs): ' + ' | '.join(parts))
        say('     our rate if our lone turns had their spread of short enemy dragons: %s (theirs is %s; strata present on both sides cover %d of %d of their turns)' % (fmt(std0 / cov1 if cov1 else None), fmt(tot(c1, 'flag') / n1), cov1, n1))
        say('     their rate if their lone turns had our spread: %s (ours is %s; cover %d of %d of our turns)' % (fmt(std1 / cov0 if cov0 else None), fmt(tot(c0, 'flag') / n0), cov0, n0))
        say('     any enemy head within 6 path steps, whatever its length: ours %.3f, theirs %.3f, ratio %s' % (tot(c0, 'any6') / n0, tot(c1, 'any6') / n1, fmt(rr(tot(c0, 'any6') / n0, tot(c1, 'any6') / n1), 2)))

    say('')
    say('== one layout or one opponent? ==')
    for label, gs in (('full games, both codes', [g for g in F if g['full']]), ('all endings, both codes', F)):
        say(' ', label, '(flagged share ours of n in k games ; theirs):')
        up = down = 0
        for mk in sorted(set(g['map_key'] for g in gs)):
            sub = [g for g in gs if g['map_key'] == mk]
            c0, c1 = clusters(sub, 0), clusters(sub, 1)
            a, b = sh(c0), sh(c1)
            if a is not None and b is not None:
                if a > b:
                    up += 1
                elif a < b:
                    down += 1
            say('    %-22s ours %s of %5d in %2d ; theirs %s of %5d in %2d | main %s ; %s | v31 %s ; %s' % (mk, fmt(a), tot(c0, 'n'), len(c0), fmt(b), tot(c1, 'n'), len(c1),
                fmt(sh(clusters([g for g in sub if g['code'] == 'main'], 0))), fmt(sh(clusters([g for g in sub if g['code'] == 'main'], 1))),
                fmt(sh(clusters([g for g in sub if g['code'] == 'v31'], 0))), fmt(sh(clusters([g for g in sub if g['code'] == 'v31'], 1)))))
        say('    layouts with ours higher %d, theirs higher %d' % (up, down))
    for label, gs in (('main full', [g for g in M if g['full']]), ('v31 full', [g for g in O if g['full']]), ('main all endings', M), ('v31 all endings', O)):
        rs = []
        for mk in sorted(set(g['map_key'] for g in gs)):
            rest = [g for g in gs if g['map_key'] != mk]
            rs.append((rr(sh(clusters(rest, 0)), sh(clusters(rest, 1))), mk))
        rs = sorted((x for x in rs if x[0] is not None))
        ro = []
        for opp in sorted(set(g['opponentId'] for g in gs)):
            rest = [g for g in gs if g['opponentId'] != opp]
            ro.append((rr(sh(clusters(rest, 0)), sh(clusters(rest, 1))), opp))
        ro = sorted((x for x in ro if x[0] is not None))
        top = sorted(clusters(gs, 0), key=lambda c: -c['flag'])[:3]
        topg = [c['game']['game'] for c in top]
        rest = [g for g in gs if g['game'] not in topg]
        say('  %-17s ratio %s | one layout out: %.2f (without %s) to %.2f (without %s) | one opponent out: %.2f (without %s) to %.2f (without %s) | without our three games with most flagged turns %s: %s' % (
            label, fmt(rr(sh(clusters(gs, 0)), sh(clusters(gs, 1))), 2), rs[0][0], rs[0][1], rs[-1][0], rs[-1][1], ro[0][0], ro[0][1], ro[-1][0], ro[-1][1],
            [(c['game']['game'], c['flag'], c['n']) for c in top], fmt(rr(sh(clusters(rest, 0)), sh(clusters(rest, 1))), 2)))
    say('  per opponent with 500 or more lone turns on each side, all endings, both codes:')
    opps = defaultdict(list)
    for g in F:
        opps[(g['opponentId'], g['opponent'])].append(g)
    up = down = 0
    for key in sorted(opps, key=lambda k: -len(opps[k])):
        c0, c1 = clusters(opps[key], 0), clusters(opps[key], 1)
        if tot(c0, 'n') >= 500 and tot(c1, 'n') >= 500:
            a, b = sh(c0), sh(c1)
            up += 1 if a > b else 0
            down += 1 if a < b else 0
            say('    %-26s games %3d | ours %s of %5d ; theirs %s of %5d' % (str(key[0]) + ' ' + key[1][:16], len(opps[key]), fmt(a), tot(c0, 'n'), fmt(b), tot(c1, 'n')))
    say('    opponents with ours higher %d, theirs higher %d' % (up, down))

    say('')
    say('== chance (lone turns come in runs inside a game, so the game is the unit) ==')
    for label, gs in (('main full', [g for g in M if g['full']]), ('v31 full', [g for g in O if g['full']]), ('main all endings', M), ('v31 all endings', O), ('pooled level', [g for g in F if g['level']]),
                      ('main full 1700-1899', [g for g in M if g['full'] and g['band'] == '1700-1899']), ('main full 1900-2099', [g for g in M if g['full'] and g['band'] == '1900-2099'])):
        obs, ge, n, k0, k1 = perm(gs)
        lo, hi = boot(gs)
        c0, c1 = clusters(gs, 0), clusters(gs, 1)
        m0 = sorted(c['flag'] / c['n'] for c in c0)
        m1 = sorted(c['flag'] / c['n'] for c in c1)
        say('  %-20s games with lone turns: ours %d, theirs %d | per-game flagged share, mean %.3f against %.3f, median %.3f against %.3f | label shuffle: difference %.3f, %d of %d shuffles at least as large | battle bootstrap of the ratio %.2f to %.2f' % (
            label, k0, k1, sum(m0) / len(m0), sum(m1) / len(m1), m0[len(m0) // 2], m1[len(m1) // 2], obs, ge, n, lo, hi))

    say('')
    say('== own heads within 5 tiles of the lone queen ==')
    ob = ((0, 0), (1, 3), (4, 7), (8, 15), (16, 31), (32, 9999))
    for label, gs in (('main full', [g for g in M if g['full']]), ('v31 full', [g for g in O if g['full']]), ('main all endings', M), ('v31 all endings', O), ('pooled level', [g for g in F if g['level']])):
        c0, c1 = clusters(gs, 0), clusters(gs, 1)
        n0, n1 = tot(c0, 'n'), tot(c1, 'n')
        if not n0 or not n1:
            continue
        say('  %s: mean %.2f against %.2f | none within 5: %.3f against %.3f | other own dragons alive %.1f against %.1f | expected if own heads sat anywhere on the board %.2f against %.2f | seen over expected %.2f against %.2f' % (
            label, tot(c0, 'own5') / n0, tot(c1, 'own5') / n1, tot(c0, 'zero') / n0, tot(c1, 'zero') / n1, tot(c0, 'own_alive') / n0, tot(c1, 'own_alive') / n1,
            tot(c0, 'own_expect') / n0, tot(c1, 'own_expect') / n1, tot(c0, 'own5') / tot(c0, 'own_expect'), tot(c1, 'own5') / tot(c1, 'own_expect')))
        a = strata(c0, 5, ob)
        b = strata(c1, 5, ob)
        parts = []
        for i, (lo, hi) in enumerate(ob):
            parts.append('%d-%s: %s of %d / %s of %d' % (lo, hi if hi < 9999 else 'on', fmt(a[i][2] / a[i][0] if a[i][0] else None, 2), a[i][0], fmt(b[i][2] / b[i][0] if b[i][0] else None, 2), b[i][0]))
        say('     mean own heads within 5 by other own dragons alive (ours / theirs): ' + ' | '.join(parts))
        m0 = sorted(c['own5'] / c['n'] for c in c0)
        m1 = sorted(c['own5'] / c['n'] for c in c1)
        say('     per game mean: %.2f against %.2f, median %.2f against %.2f' % (sum(m0) / len(m0), sum(m1) / len(m1), m0[len(m0) // 2], m1[len(m1) // 2]))

    say('')
    say('== comparison with rows.jsonl (read only here) ==')
    rows = {}
    for line_ in Path('data/analysis/ladder/rows.jsonl').read_text().splitlines():
        if line_.strip():
            r = json.loads(line_)
            rows[r['game']] = r
    diff = Counter()
    for g in games:
        r = rows.get(g['game'])
        if r is None:
            diff['missing'] += 1
            continue
        if r['last_round'] != g['last_round']:
            diff['last_round'] += 1
        c = r['curves'].get('100')
        mine = g['total100']
        theirs = [c['us']['total'], c['them']['total']] if c else None
        if mine != theirs:
            diff['total at r100'] += 1
        for s, sn in ((0, 'us'), (1, 'them')):
            d = g['qdeath'][s]
            if (d['round'] if d else None) != r['queen'][sn]['death_round']:
                diff['queen death round'] += 1
    say('games compared %d, differences: %s' % (len(games), dict(diff) if diff else 'none'))
    Path(P + 'f39-numbers.txt').write_text('\n'.join(LINES) + '\n')


main()
