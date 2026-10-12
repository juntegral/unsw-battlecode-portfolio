#!/usr/bin/env python3
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
"""Verifier claims 10 (run of 2026-10-07 10:21 KST), F39 new part: short dragons of the other side within 12 path
steps of a lone queen (part A) and how fresh the last sighting of her is (part B). Reads the x10 shards (own
extraction from the raw replays) and writes f39-1021-numbers.txt. maps.json is read for the free-layout flag;
rows.jsonl is read only in the last section, to compare."""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')
CUT = '2026-10-06T14:48:15Z'
LINES = []
NV = 29


def say(*a):
    s = ' '.join(str(x) for x in a)
    LINES.append(s)
    print(s)


def load():
    games = []
    for k in range(6):
        for line in (V / ('x10-%d.jsonl' % k)).read_text().splitlines():
            if line.strip():
                games.append(json.loads(line))
    bad = [g for g in games if 'error' in g]
    games = [g for g in games if 'error' not in g]
    order = sorted(games, key=lambda g: (g.get('completedAt') or '', g['game']))
    maps = json.loads(Path('data/analysis/ladder/maps.json').read_text())
    seen = {}
    for g in order:
        lst = seen.setdefault(g['map'], [])
        if g['layout'] not in lst:
            lst.append(g['layout'])
        g['map_key'] = '%s #%d' % (g['map'], lst.index(g['layout']) + 1)
        e = g.get('opponentElo') or 0
        g['band'] = '<1700' if e < 1700 else '1700-1899' if e < 1900 else '1900-2099' if e < 2100 else '2100+'
        g['free'] = not maps[g['map_key']]['queen_spawn_dead_end']
        g['full'] = g['last_round'] == 499
        g['big'] = g['W'] * g['H'] > 1200
        g['grow'] = 151 if g['big'] else 301
        g['half'] = 1 if g['completedAt'][:19] < CUT[:19] else 2
        g['p1'] = g['map_key'] == 'Portals #1'
        g['opp'] = '%s (%s)' % (g.get('opponent'), g.get('opponentId'))
        g['rows'] = [[], []]
        last_a = [None, None]
        last_h = [None, None]
        for r in g['lone']:
            (s, rnd, es, s12, s6, eall, any12, incomp, seers, seers_head, seer_s12, sx, sxh, reach, qlen, csize) = r
            seen_now = seers > 0
            if seen_now:
                last_a[s] = rnd
            if seers_head > 0:
                last_h[s] = rnd
            fresh_a = last_a[s] is not None and rnd - last_a[s] <= 20
            never_a = last_a[s] is None
            fresh_h = last_h[s] is not None and rnd - last_h[s] <= 20
            fresh_x = sx != -1 and sx <= 20
            never_x = sx == -1
            fresh_e = fresh_a or fresh_x
            ex = es * reach / g['n_open']
            v = [1, es, s12, 1 if s12 > 0 else 0, 1 if seen_now else 0, 1 if fresh_a else 0, 1 if never_a else 0,
                 s12 if fresh_a else 0, 0 if fresh_a else s12, 1 if fresh_x else 0, 1 if never_x else 0,
                 s12 if fresh_x else 0, 0 if fresh_x else s12, ex, incomp, qlen, reach,
                 (s12 - seer_s12) if fresh_a else 0, es if fresh_a else 0, ex if fresh_a else 0,
                 1 if seers_head > 0 else 0, 1 if fresh_h else 0, s12 if fresh_h else 0, s6,
                 1 if (fresh_a and s12 >= 2) else 0, 1 if fresh_e else 0, s12 if fresh_e else 0,
                 seer_s12 if seen_now else 0, eall]
            g['rows'][s].append((rnd, v))
    return order, bad, maps


def cl(gs, s, pred=None):
    out = []
    for g in gs:
        acc = None
        for rnd, v in g['rows'][s]:
            if pred is not None and not pred(g, rnd):
                continue
            if acc is None:
                acc = list(v)
            else:
                for i in range(NV):
                    acc[i] += v[i]
        if acc is not None:
            out.append((g, acc))
    return out


def tot(cs):
    t = [0] * NV
    for g, v in cs:
        for i in range(NV):
            t[i] += v[i]
    return t


def dv(a, b):
    return (a / b) if b else None


def f(x, d=3):
    return 'none' if x is None else ('%.' + str(d) + 'f') % x


def lineA(t, n_games):
    return '%d turns in %d games: short of the other side alive %s a turn, share within 12 %s (%d of %d), any within 12 in %s of turns, within 12 a turn %s' % (
        t[0], n_games, f(dv(t[1], t[0]), 1), f(dv(t[2], t[1])), t[2], t[1], f(dv(t[3], t[0]), 2), f(dv(t[2], t[0]), 2))


def A(label, gs, pred=None):
    c1, c0 = cl(gs, 1, pred), cl(gs, 0, pred)
    t1, t0 = tot(c1), tot(c0)
    say('%s' % label)
    say('    their lone queen (ours near her): %s' % lineA(t1, len(c1)))
    say('    our lone queen (theirs near her): %s' % lineA(t0, len(c0)))
    a, b = dv(t1[2], t1[1]), dv(t0[2], t0[1])
    say('    ratio of the shares, ours over theirs: %s' % f(dv(a, b) if a is not None and b else None))
    return c1, c0


def lineB(t, n_games):
    nf = t[5]
    ns = t[0] - t[5]
    return ('%d turns in %d games: seen now %s, fresh %s, never seen yet %s, short within 12 at fresh turns %s, at stale turns %s'
            ' | exact sighting: fresh %s, never %s, at fresh %s, at stale %s | either: fresh %s, at fresh %s') % (
        t[0], n_games, f(dv(t[4], t[0])), f(dv(nf, t[0])), f(dv(t[6], t[0])), f(dv(t[7], nf)), f(dv(t[8], ns)),
        f(dv(t[9], t[0])), f(dv(t[10], t[0])), f(dv(t[11], t[9])), f(dv(t[12], t[0] - t[9])),
        f(dv(t[25], t[0])), f(dv(t[26], t[25])))


def predB(g, rnd):
    return rnd >= 100


def B(label, gs, pred=predB):
    gs = [g for g in gs if not g['p1']]
    c1, c0 = cl(gs, 1, pred), cl(gs, 0, pred)
    t1, t0 = tot(c1), tot(c0)
    say('%s' % label)
    say('    their lone queen: %s' % lineB(t1, len(c1)))
    say('    our lone queen:   %s' % lineB(t0, len(c0)))
    a, b = dv(t1[7], t1[5]), dv(t0[7], t0[5])
    say('    short within 12 at fresh turns, ours over theirs: %s' % f(dv(a, b) if a is not None and b else None, 2))
    return c1, c0


def shuffle_test(c1, c0, stat, n=5000, seed=7):
    """label shuffle among the game clusters; returns observed and the count of shuffles at or below it"""
    rng = random.Random(seed)
    allc = c1 + c0
    k = len(c1)
    obs = stat(tot(c1), tot(c0))
    if obs is None:
        return None, None, None
    lo = 0
    done = 0
    for _ in range(n):
        rng.shuffle(allc)
        v = stat(tot(allc[:k]), tot(allc[k:]))
        if v is None:
            continue
        done += 1
        if v <= obs + 1e-12:
            lo += 1
    return obs, lo, done


def boot_ratio(c1, c0, stat, n=2000, seed=3):
    """battle bootstrap: resample battles, both sides' clusters go with their battle"""
    rng = random.Random(seed)
    byb = defaultdict(lambda: [[], []])
    for g, v in c1:
        byb[g['battle']][0].append((g, v))
    for g, v in c0:
        byb[g['battle']][1].append((g, v))
    keys = list(byb)
    vals = []
    for _ in range(n):
        a, b = [], []
        for _k in range(len(keys)):
            e = byb[keys[rng.randrange(len(keys))]]
            a.extend(e[0])
            b.extend(e[1])
        v = stat(tot(a), tot(b))
        if v is not None:
            vals.append(v)
    vals.sort()
    if not vals:
        return None
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]


def ratio_share(t1, t0):
    a, b = dv(t1[2], t1[1]), dv(t0[2], t0[1])
    return dv(a, b) if a is not None and b else None


def diff_share(t1, t0):
    a, b = dv(t1[2], t1[1]), dv(t0[2], t0[1])
    return (a - b) if a is not None and b is not None else None


def diff_fresh(t1, t0):
    a, b = dv(t1[5], t1[0]), dv(t0[5], t0[0])
    return (a - b) if a is not None and b is not None else None


def ratio_atfresh(t1, t0):
    a, b = dv(t1[7], t1[5]), dv(t0[7], t0[5])
    return dv(a, b) if a is not None and b else None


def diff_atfresh(t1, t0):
    a, b = dv(t1[7], t1[5]), dv(t0[7], t0[5])
    return (a - b) if a is not None and b is not None else None


def by_key(cs, key):
    d = defaultdict(list)
    for g, v in cs:
        d[g[key]].append((g, v))
    return d


def main():
    games, bad, maps = load()
    say('F39 new part, verifier recount, run of 2026-10-07 10:21 KST')
    say('games read %d, unreadable %d; final state equals the result block in %d; ownership consistent in %d; games with anomalies %d; bad portals %d' % (
        len(games), len(bad), sum(1 for g in games if g['final_ok']), sum(1 for g in games if g['own_ok']),
        sum(1 for g in games if g['anomalies']), sum(g['bad_portals'] for g in games)))
    free = [g for g in games if g['free'] and g['code'] in ('main', 'v31')]
    main_g = [g for g in free if g['code'] == 'main']
    old_g = [g for g in free if g['code'] == 'v31']
    say('free games: main %d (half 1 %d, half 2 %d), v31 %d; codes of all games %s' % (
        len(main_g), sum(1 for g in main_g if g['half'] == 1), sum(1 for g in main_g if g['half'] == 2), len(old_g),
        dict(Counter(g['code'] for g in games))))
    say('layouts above 1200 cells: %s' % sorted(set(g['map_key'] + ' %dx%d' % (g['W'], g['H']) for g in free if g['big'])))
    say('layouts at or under 1200 cells: %s' % sorted(set(g['map_key'] + ' %dx%d' % (g['W'], g['H']) for g in free if not g['big'])))
    say('layouts with more than one kelp-bounded area of two or more tiles: %s' % sorted(set('%s (%d areas, largest %d of %d open)' % (g['map_key'], g['n_comp'], g['big_comp'], g['n_open']) for g in free if g['n_comp'] > 1)))

    say('')
    say('=== PART A: all lone turns ===')
    for name, gs in (('main', main_g), ('v31', old_g)):
        A('%s, all endings' % name, gs)
        A('%s, without Portals #1' % name, [g for g in gs if not g['p1']])
        A('%s, full games' % name, [g for g in gs if g['full']])
        A('%s, full games without Portals #1' % name, [g for g in gs if g['full'] and not g['p1']])
        A('%s, games ended by elimination' % name, [g for g in gs if not g['full']])
        A('%s, before grow_round' % name, gs, lambda g, r: r < g['grow'])
        A('%s, from grow_round' % name, gs, lambda g, r: r >= g['grow'])
        A('%s, layouts above 1200 cells' % name, [g for g in gs if g['big']])
        A('%s, layouts at or under 1200 cells' % name, [g for g in gs if not g['big']])
        A('%s, layouts at or under 1200 cells without Portals #1' % name, [g for g in gs if not g['big'] and not g['p1']])
        if name == 'main':
            A('main half 1', [g for g in gs if g['half'] == 1])
            A('main half 2', [g for g in gs if g['half'] == 2])
        for band in ('1700-1899', '1900-2099', '2100+'):
            A('%s, band %s' % (name, band), [g for g in gs if g['band'] == band])
        say('')

    say('--- A: what the gap is made of (all endings, without Portals #1) ---')
    for name, gs in (('main', main_g), ('v31', old_g)):
        gs = [g for g in gs if not g['p1']]
        c1, c0 = cl(gs, 1), cl(gs, 0)
        for lab, cs in (('their lone queen', c1), ('our lone queen', c0)):
            t = tot(cs)
            say('%s %s: tiles within 12 steps %s, queen length %s, all dragons of the other side alive %s, short in her kelp-bounded area %s of short alive, expected within 12 if short heads sat on random open tiles %s a turn, seen %s a turn, seen over expected %s, within 6 a turn %s' % (
                name, lab, f(dv(t[16], t[0]), 1), f(dv(t[15], t[0]), 1), f(dv(t[28], t[0]), 1), f(dv(t[14], t[1])), f(dv(t[13], t[0]), 2), f(dv(t[2], t[0]), 2),
                f(dv(t[2], t[13]), 2), f(dv(t[23], t[0]), 2)))
    say('')
    say('--- A: per layout, both codes, all endings: share within 12 (short within 12 of short alive), lone turns, games ---')
    c1, c0 = cl(free, 1), cl(free, 0)
    k1, k0 = by_key(c1, 'map_key'), by_key(c0, 'map_key')
    higher = [0, 0]
    for mk in sorted(set(k1) | set(k0)):
        t1, t0 = tot(k1.get(mk, [])), tot(k0.get(mk, []))
        a, b = dv(t1[2], t1[1]), dv(t0[2], t0[1])
        if a is not None and b is not None:
            higher[0 if a < b else 1] += 1
        say('%-22s ours near their queen %s (%d turns, %d games, %.1f short alive) | theirs near ours %s (%d turns, %d games, %.1f short alive) | ratio %s' % (
            mk, f(a), t1[0], len(k1.get(mk, [])), dv(t1[1], t1[0]) or 0, f(b), t0[0], len(k0.get(mk, [])), dv(t0[1], t0[0]) or 0,
            f(dv(a, b) if a is not None and b else None, 2)))
    say('layouts where ours is the lower share: %d, where theirs is: %d' % (higher[0], higher[1]))
    for name, gs in (('main', main_g), ('v31', old_g)):
        c1, c0 = cl(gs, 1), cl(gs, 0)
        k1, k0 = by_key(c1, 'map_key'), by_key(c0, 'map_key')
        say('%s per layout: %s' % (name, '; '.join('%s %s/%s' % (mk, f(dv(tot(k1.get(mk, []))[2], tot(k1.get(mk, []))[1])), f(dv(tot(k0.get(mk, []))[2], tot(k0.get(mk, []))[1]))) for mk in sorted(set(k1) | set(k0)))))
        # layout mix held: weights = lone turns of one side per layout
        for wl, wk in (('their mix', k1), ('our mix', k0)):
            num1 = num0 = den = 0.0
            for mk in set(k1).intersection(set(k0)):
                t1, t0 = tot(k1[mk]), tot(k0[mk])
                if t1[1] == 0 or t0[1] == 0:
                    continue
                w = tot(wk[mk])[0]
                num1 += w * t1[2] / t1[1]
                num0 += w * t0[2] / t0[1]
                den += w
            say('%s layout mix held to %s: %s against %s, ratio %s' % (name, wl, f(dv(num1, den)), f(dv(num0, den)), f(dv(num1, num0), 2)))
        # per game mean share
        m1 = [v[2] / v[1] for g, v in c1 if v[1]]
        m0 = [v[2] / v[1] for g, v in c0 if v[1]]
        say('%s per game mean share: %s (%d games) against %s (%d games), ratio %s; median %s against %s' % (
            name, f(sum(m1) / len(m1)), len(m1), f(sum(m0) / len(m0)), len(m0), f(sum(m1) / len(m1) / (sum(m0) / len(m0)), 2),
            f(sorted(m1)[len(m1) // 2]), f(sorted(m0)[len(m0) // 2])))
        obs, lo, done = shuffle_test(c1, c0, diff_share)
        say('%s label shuffle among games, share ours minus theirs %s: %s of %s shuffles at or below' % (name, f(obs), lo, done))
        say('%s battle bootstrap of the ratio, 95 percent: %s' % (name, boot_ratio(c1, c0, ratio_share)))
        # without Portals
        c1n = [(g, v) for g, v in c1 if not g['p1']]
        c0n = [(g, v) for g, v in c0 if not g['p1']]
        obs, lo, done = shuffle_test(c1n, c0n, diff_share)
        say('%s without Portals #1: label shuffle %s: %s of %s; bootstrap of the ratio %s' % (name, f(obs), lo, done, boot_ratio(c1n, c0n, ratio_share)))
        # leave one opponent out
        opps = sorted(set(g['opp'] for g, v in c1 + c0))
        rs = []
        for o in opps:
            r = ratio_share(tot([(g, v) for g, v in c1n if g['opp'] != o]), tot([(g, v) for g, v in c0n if g['opp'] != o]))
            if r is not None:
                rs.append((r, o))
        say('%s without Portals #1, one opponent left out at a time: ratio %s to %s (%d opponents)' % (name, f(min(rs)[0], 2), f(max(rs)[0], 2), len(opps)))
        mks = sorted(set(g['map_key'] for g, v in c1n + c0n))
        rs = []
        for mk in mks:
            r = ratio_share(tot([(g, v) for g, v in c1n if g['map_key'] != mk]), tot([(g, v) for g, v in c0n if g['map_key'] != mk]))
            if r is not None:
                rs.append((r, mk))
        say('%s without Portals #1, one layout left out at a time: ratio %s (%s) to %s (%s)' % (name, f(min(rs)[0], 2), min(rs)[1], f(max(rs)[0], 2), max(rs)[1]))
        top = sorted(c0n, key=lambda c: -c[1][2])[:3]
        ids = set(g['game'] for g, v in top)
        say('%s without Portals #1, without the three games of our lone queen with the most short heads within 12 (%s): ratio %s' % (
            name, ', '.join('%d %s %d' % (g['game'], g['map_key'], v[2]) for g, v in top),
            f(ratio_share(tot(c1n), tot([(g, v) for g, v in c0n if g['game'] not in ids])), 2)))
        zero = sorted(c1n, key=lambda c: -(c[1][1] - 40 * c[1][2]))[:3]
        ids = set(g['game'] for g, v in zero)
        say('%s without Portals #1, without the three games of their lone queen with the most short dragons of ours alive and few near (%s): ratio %s' % (
            name, ', '.join('%d %s %d of %d' % (g['game'], g['map_key'], v[2], v[1]) for g, v in zero),
            f(ratio_share(tot([(g, v) for g, v in c1n if g['game'] not in ids]), tot(c0n)), 2)))
        ev = defaultdict(lambda: [[], []])
        for g, v in c1n:
            ev[(g.get('at_kst') or '?')[:10]][0].append((g, v))
        for g, v in c0n:
            ev[(g.get('at_kst') or '?')[:10]][1].append((g, v))
        say('%s without Portals #1 by KST date: %s' % (name, '; '.join('%s %s' % (d, f(ratio_share(tot(ev[d][0]), tot(ev[d][1])), 2)) for d in sorted(ev))))
        say('')

    say('=== PART B: lone turns from raw round 100, Portals #1 left out ===')
    for name, gs in (('main', main_g), ('v31', old_g)):
        B('%s' % name, gs)
        B('%s, layouts above 1200 cells' % name, [g for g in gs if g['big']])
        B('%s, layouts at or under 1200 cells' % name, [g for g in gs if not g['big']])
        B('%s, full games' % name, [g for g in gs if g['full']])
        B('%s, games ended by elimination' % name, [g for g in gs if not g['full']])
        B('%s, before grow_round' % name, gs, lambda g, r: r >= 100 and r < g['grow'])
        B('%s, from grow_round' % name, gs, lambda g, r: r >= 100 and r >= g['grow'])
        if name == 'main':
            B('main half 1', [g for g in gs if g['half'] == 1])
            B('main half 2', [g for g in gs if g['half'] == 2])
        B('%s, band 1700-1899' % name, [g for g in gs if g['band'] == '1700-1899'])
        B('%s, band 1900 and above' % name, [g for g in gs if g['band'] in ('1900-2099', '2100+')])
        B('%s, band 1900-2099' % name, [g for g in gs if g['band'] == '1900-2099'])
        say('')

    say('--- B: what the fresh turns hold (from raw round 100, without Portals #1) ---')
    for name, gs in (('main', main_g), ('v31', old_g)):
        gs = [g for g in gs if not g['p1']]
        c1, c0 = cl(gs, 1, predB), cl(gs, 0, predB)
        for lab, cs in (('their lone queen', c1), ('our lone queen', c0)):
            t = tot(cs)
            nf = t[5]
            say('%s %s: queen length %s; at fresh turns: short of the other side alive %s, expected within 12 on random open tiles %s, seen %s, short within 12 that do not have her in view now %s a fresh turn, fresh turns with two or more short within 12 %s; seen now with her HEAD in the window %s of turns, fresh by head sightings %s, short within 12 at such turns %s; short within 12 a turn at turns she is seen now %s (of them in view %s)' % (
                name, lab, f(dv(t[15], t[0]), 1), f(dv(t[18], nf), 1), f(dv(t[19], nf), 2), f(dv(t[7], nf), 2), f(dv(t[17], nf), 2), f(dv(t[24], nf)),
                f(dv(t[20], t[0])), f(dv(t[21], t[0])), f(dv(t[22], t[21]), 2),
                'n/a', f(dv(t[27], t[4]), 2)))
        # per layout
        k1, k0 = by_key(c1, 'map_key'), by_key(c0, 'map_key')
        for mk in sorted(set(k1) | set(k0)):
            t1, t0 = tot(k1.get(mk, [])), tot(k0.get(mk, []))
            say('    %s %-22s their queen: %d turns %d games fresh %s at fresh %s | our queen: %d turns %d games fresh %s at fresh %s' % (
                name, mk, t1[0], len(k1.get(mk, [])), f(dv(t1[5], t1[0])), f(dv(t1[7], t1[5]), 2),
                t0[0], len(k0.get(mk, [])), f(dv(t0[5], t0[0])), f(dv(t0[7], t0[5]), 2)))
        for wl, wk in (('their mix', k1), ('our mix', k0)):
            fa = fb = den = 0.0
            na = nb = den2 = 0.0
            for mk in set(k1).intersection(set(k0)):
                t1, t0 = tot(k1[mk]), tot(k0[mk])
                w = tot(wk[mk])[0]
                fa += w * t1[5] / t1[0]
                fb += w * t0[5] / t0[0]
                den += w
                if t1[5] and t0[5]:
                    w2 = tot(wk[mk])[5]
                    na += w2 * t1[7] / t1[5]
                    nb += w2 * t0[7] / t0[5]
                    den2 += w2
            say('%s layout mix held to %s: fresh share %s against %s; short within 12 at fresh turns %s against %s (ratio %s)' % (
                name, wl, f(dv(fa, den)), f(dv(fb, den)), f(dv(na, den2), 2), f(dv(nb, den2), 2), f(dv(na, nb), 2)))
        m1 = [v[5] / v[0] for g, v in c1]
        m0 = [v[5] / v[0] for g, v in c0]
        say('%s per game mean fresh share: their queen %s (%d games, median %s), our queen %s (%d games, median %s)' % (
            name, f(sum(m1) / len(m1)), len(m1), f(sorted(m1)[len(m1) // 2]), f(sum(m0) / len(m0)), len(m0), f(sorted(m0)[len(m0) // 2])))
        a1 = [v[7] / v[5] for g, v in c1 if v[5]]
        a0 = [v[7] / v[5] for g, v in c0 if v[5]]
        say('%s per game mean short within 12 at fresh turns: ours near their queen %s (%d games, median %s), theirs near ours %s (%d games, median %s)' % (
            name, f(sum(a1) / len(a1), 2), len(a1), f(sorted(a1)[len(a1) // 2], 2), f(sum(a0) / len(a0), 2), len(a0), f(sorted(a0)[len(a0) // 2], 2)))
        obs, lo, done = shuffle_test(c1, c0, diff_fresh)
        say('%s label shuffle among games, fresh share theirs minus ours %s: %s of %s shuffles at or below' % (name, f(obs), lo, done))
        obs, lo, done = shuffle_test(c1, c0, diff_atfresh)
        say('%s label shuffle among games, short within 12 at fresh turns, ours near their queen minus theirs near ours %s: %s of %s shuffles at or below' % (name, f(obs, 2), lo, done))
        say('%s battle bootstrap, 95 percent: fresh share difference %s; ratio at fresh turns %s' % (name, boot_ratio(c1, c0, diff_fresh), boot_ratio(c1, c0, ratio_atfresh)))
        bt = boot_ratio(c1, [], lambda t1, t0: dv(t1[5], t1[0]))
        say('%s battle bootstrap of the fresh share of their lone queen alone, 95 percent: %s' % (name, bt))
        opps = sorted(set(g['opp'] for g, v in c1 + c0))
        rs, fs = [], []
        for o in opps:
            a = tot([(g, v) for g, v in c1 if g['opp'] != o])
            b = tot([(g, v) for g, v in c0 if g['opp'] != o])
            r = ratio_atfresh(a, b)
            if r is not None:
                rs.append(r)
            fs.append(a[5] / a[0])
        say('%s one opponent left out at a time: ratio at fresh turns %s to %s; fresh share of their queen %s to %s' % (name, f(min(rs), 2), f(max(rs), 2), f(min(fs)), f(max(fs))))
        top = sorted(c0, key=lambda c: -c[1][7])[:3]
        ids = set(g['game'] for g, v in top)
        say('%s without the three games of our lone queen with the most short heads within 12 at fresh turns (%s): at fresh %s against %s, ratio %s' % (
            name, ', '.join('%d %s %d in %d' % (g['game'], g['map_key'], v[7], v[5]) for g, v in top),
            f(dv(tot(c1)[7], tot(c1)[5]), 2), f(dv(tot([(g, v) for g, v in c0 if g['game'] not in ids])[7], tot([(g, v) for g, v in c0 if g['game'] not in ids])[5]), 2),
            f(ratio_atfresh(tot(c1), tot([(g, v) for g, v in c0 if g['game'] not in ids])), 2)))
        topf = sorted(c1, key=lambda c: -c[1][5])[:3]
        ids = set(g['game'] for g, v in topf)
        t = tot([(g, v) for g, v in c1 if g['game'] not in ids])
        say('%s without the three games of their lone queen with the most fresh turns (%s): fresh share %s' % (
            name, ', '.join('%d %s %d of %d' % (g['game'], g['map_key'], v[5], v[0]) for g, v in topf), f(dv(t[5], t[0]))))
        say('')

    say('--- B: fresh share by how long she has been alone and by her length (main and v31 pooled, from raw round 100, without Portals #1) ---')
    gsn = [g for g in free if not g['p1']]
    for name, gs in (('main', [g for g in gsn if g['code'] == 'main']), ('v31', [g for g in gsn if g['code'] == 'v31'])):
        for s, lab in ((1, 'their lone queen'), (0, 'our lone queen')):
            bins = defaultdict(lambda: [0, 0, 0])
            lb = defaultdict(lambda: [0, 0, 0])
            for g in gs:
                od = g['qdeath'][1 - s]
                if od is None:
                    continue
                for rnd, v in g['rows'][s]:
                    if rnd < 100:
                        continue
                    k = min((rnd - od['round']) // 50, 4)
                    bins[k][0] += 1
                    bins[k][1] += v[5]
                    bins[k][2] += v[7]
                    q = v[15]
                    kq = 0 if q <= 4 else 1 if q <= 9 else 2 if q <= 19 else 3
                    lb[kq][0] += 1
                    lb[kq][1] += v[5]
                    lb[kq][2] += v[7]
            say('%s %s by 50 rounds alone (turns, fresh share, short within 12 at fresh): %s' % (name, lab, '; '.join('%d: %d %s %s' % (k * 50, bins[k][0], f(dv(bins[k][1], bins[k][0]), 2), f(dv(bins[k][2], bins[k][1]), 2)) for k in sorted(bins))))
            say('%s %s by her length 1-4, 5-9, 10-19, 20 on (turns, fresh share, short within 12 at fresh): %s' % (name, lab, '; '.join('%d: %d %s %s' % (k, lb[k][0], f(dv(lb[k][1], lb[k][0]), 2), f(dv(lb[k][2], lb[k][1]), 2)) for k in sorted(lb))))
    say('')

    say('=== rows.jsonl, read only now ===')
    rows = {}
    for line in Path('data/analysis/ladder/rows.jsonl').read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            rows[r['game']] = r
    diff = Counter()
    for g in games:
        r = rows.get(g['game'])
        if r is None:
            diff['game not in rows'] += 1
            continue
        if r['map_key'] != g['map_key']:
            diff['map_key'] += 1
        if r['our_code'] != g['code'] and not (g['code'] == 'other' and r['our_code'] not in ('main', 'v31')):
            diff['code'] += 1
        if r['last_round'] != g['last_round']:
            diff['last round'] += 1
        if r['win'] != g['win']:
            diff['win'] += 1
        for s, sn in ((0, 'us'), (1, 'them')):
            d = g['qdeath'][s]
            if (d['round'] if d else None) != r['queen'][sn]['death_round']:
                diff['queen death round'] += 1
    say('games compared %d of %d rows, differences: %s' % (len(games), len(rows), dict(diff) if diff else 'none'))
    Path(P + 'f39-1021-numbers.txt').write_text('\n'.join(LINES) + '\n')


main()
