#!/usr/bin/env python3
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
"""Verifier claims 10 (run of 2026-10-07 10:21 KST), F38 new part: how often a queen steps onto a narrow tile when
one is next to her, whether a pearl is what draws her, and how long her stays on narrow tiles are. Reads the x10
shards (own extraction from the raw replays) and writes f38-1021-numbers.txt. maps.json is read for the free-layout
flag; rows.jsonl is read only in the last section, to compare."""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')
CUT = '2026-10-06T14:48:15Z'
LINES = []
NV = 29
WN = ('r0-100', 'r101-200', 'r201-300', 'r301 on')


def say(*a):
    s = ' '.join(str(x) for x in a)
    LINES.append(s)
    print(s)


def window(r):
    return 0 if r <= 100 else 1 if r <= 200 else 2 if r <= 300 else 3


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
        g['half'] = 1 if g['completedAt'][:19] < CUT[:19] else 2
        g['opp'] = '%s (%s)' % (g.get('opponent'), g.get('opponentId'))
        cv = [[[0] * NV for _ in range(4)] for _ in range(2)]
        for r in g['chances']:
            (s, rnd, nopen, n_nar, n_fn, n_fw, n_p, n_pw, ent, onp, onfn, onnb, died, qlen) = r
            v = cv[s][window(rnd)]
            v[0] += 1
            v[1] += ent
            v[2] += onp
            if n_p >= 1:
                v[3] += 1
                v[4] += ent
                v[5] += onp
            if n_fn >= 1:
                v[6] += 1
                v[7] += ent
                if n_fw >= 1:
                    v[8] += 1
                    v[9] += ent
                else:
                    v[10] += 1
                    v[11] += ent
                if n_p >= 1 and n_pw == 0:
                    v[16] += 1
                    v[17] += ent
                elif n_p == 0 and n_pw >= 1:
                    v[18] += 1
                    v[19] += ent
                elif n_p >= 1 and n_pw >= 1:
                    v[20] += 1
                    v[21] += ent
                else:
                    v[22] += 1
                    v[23] += ent
                    if n_fw >= 1:
                        v[27] += 1
                        v[28] += ent
            else:
                v[12] += 1
                v[13] += ent
            v[14] += died
            v[15] += onnb
            if nopen == 4:
                v[24] += 1
                v[25] += ent
            v[26] += onfn
        g['cv'] = cv
        st = [[[] for _ in range(4)] for _ in range(2)]
        for s, first, n, death, endg in g['stays']:
            st[s][window(first)].append((n, death, endg))
        g['st'] = st
    return order, bad, maps


def vec(gs, s, ws):
    t = [0] * NV
    for g in gs:
        for w in ws:
            v = g['cv'][s][w]
            for i in range(NV):
                t[i] += v[i]
    return t


def dv(a, b):
    return (a / b) if b else None


def f(x, d=3):
    return 'none' if x is None else ('%.' + str(d) + 'f') % x


def sh(k, n):
    return '%d of %d (%s)' % (k, n, f(dv(k, n)))


def rr(a, b, c, d):
    x, y = dv(a, b), dv(c, d)
    return dv(x, y) if x is not None and y else None


def entry(label, gs, ws=(0, 1), a=1, b=0):
    o, t = vec(gs, 0, ws), vec(gs, 1, ws)
    say('%-46s ours %s, theirs %s, %s times' % (label, sh(o[a], o[b]), sh(t[a], t[b]), f(rr(o[a], o[b], t[a], t[b]), 2)))


def swap_test(gs, ws, a, b, n=10000, seed=5):
    """in each game the two queens trade labels with probability one half; rate ours minus theirs"""
    rng = random.Random(seed)
    units = []
    for g in gs:
        o = [sum(g['cv'][0][w][i] for w in ws) for i in (a, b)]
        t = [sum(g['cv'][1][w][i] for w in ws) for i in (a, b)]
        if o[1] or t[1]:
            units.append((o[0], o[1], t[0], t[1]))
    def stat(sel):
        on = od = tn = td = 0
        for u, k in zip(units, sel):
            if k:
                on += u[2]
                od += u[3]
                tn += u[0]
                td += u[1]
            else:
                on += u[0]
                od += u[1]
                tn += u[2]
                td += u[3]
        if od == 0 or td == 0:
            return None
        return on / od - tn / td
    obs = stat([0] * len(units))
    hi = 0
    done = 0
    for _ in range(n):
        v = stat([rng.random() < 0.5 for _u in units])
        if v is None:
            continue
        done += 1
        if v >= obs - 1e-12:
            hi += 1
    return obs, hi, done


def boot(gs, ws, a, b, n=2000, seed=11):
    rng = random.Random(seed)
    byb = defaultdict(lambda: [0, 0, 0, 0])
    for g in gs:
        e = byb[g['battle']]
        for w in ws:
            e[0] += g['cv'][0][w][a]
            e[1] += g['cv'][0][w][b]
            e[2] += g['cv'][1][w][a]
            e[3] += g['cv'][1][w][b]
    units = list(byb.values())
    vals = []
    for _ in range(n):
        s = [0, 0, 0, 0]
        for _k in range(len(units)):
            u = units[rng.randrange(len(units))]
            for i in range(4):
                s[i] += u[i]
        r = rr(s[0], s[1], s[2], s[3])
        if r is not None:
            vals.append(r)
    vals.sort()
    return (round(vals[int(0.025 * len(vals))], 2), round(vals[int(0.975 * len(vals)) - 1], 2))


def stay_stats(lst):
    if not lst:
        return 'no stays'
    ns = sorted(n for n, d, e in lst)
    tot = sum(ns)
    deaths = sum(d for n, d, e in lst)
    alive = [n for n, d, e in lst if not d]
    return '%d stays, %.2f turns a stay (%d turns), %d end in her death, one turn long %s, median %d, nine in ten at or under %d, longest %d, without the three longest %.2f, stays she leaves alive %.2f' % (
        len(ns), tot / len(ns), tot, deaths, f(sum(1 for n in ns if n == 1) / len(ns), 2), ns[len(ns) // 2], ns[int(0.9 * (len(ns) - 1))], ns[-1],
        (sum(ns[:-3]) / max(1, len(ns) - 3)), (sum(alive) / len(alive)) if alive else 0)


def stays_of(gs, s, ws):
    out = []
    for g in gs:
        for w in ws:
            out.extend(g['st'][s][w])
    return out


def stay_swap(gs, ws, n=10000, seed=9):
    rng = random.Random(seed)
    units = []
    for g in gs:
        o = stays_of([g], 0, ws)
        t = stays_of([g], 1, ws)
        if o or t:
            units.append((sum(x[0] for x in o), len(o), sum(x[0] for x in t), len(t)))
    def stat(sel):
        on = od = tn = td = 0
        for u, k in zip(units, sel):
            if k:
                on += u[2]
                od += u[3]
                tn += u[0]
                td += u[1]
            else:
                on += u[0]
                od += u[1]
                tn += u[2]
                td += u[3]
        if od == 0 or td == 0:
            return None
        return on / od - tn / td
    obs = stat([0] * len(units))
    hi = done = 0
    for _ in range(n):
        v = stat([rng.random() < 0.5 for _u in units])
        if v is None:
            continue
        done += 1
        if v >= obs - 1e-12:
            hi += 1
    return obs, hi, done


def main():
    games, bad, maps = load()
    say('F38 new part, verifier recount, run of 2026-10-07 10:21 KST')
    say('games read %d, unreadable %d; final state equals the result block in %d; games with anomalies %d (%s)' % (
        len(games), len(bad), sum(1 for g in games if g['final_ok']), sum(1 for g in games if g['anomalies']),
        dict(sum((Counter(g['anomalies']) for g in games), Counter()))))
    free = [g for g in games if g['free'] and g['code'] in ('main', 'v31')]
    main_g = [g for g in free if g['code'] == 'main']
    old_g = [g for g in free if g['code'] == 'v31']
    say('free games: main %d (half 1 %d, half 2 %d), v31 %d' % (len(main_g), sum(1 for g in main_g if g['half'] == 1), sum(1 for g in main_g if g['half'] == 2), len(old_g)))
    R = (0, 1)

    say('')
    say('=== 1. entries per chance ===')
    for name, gs in (('main', main_g), ('v31', old_g)):
        entry('%s r0-200' % name, gs)
        entry('%s r0-100' % name, gs, (0,))
        entry('%s r101-200' % name, gs, (1,))
        entry('%s r201-300' % name, gs, (2,))
        entry('%s r301 on' % name, gs, (3,))
        if name == 'main':
            entry('main half 1 r0-200', [g for g in gs if g['half'] == 1])
            entry('main half 2 r0-200', [g for g in gs if g['half'] == 2])
        for band in ('1700-1899', '1900-2099', '2100+'):
            entry('%s %s r0-200' % (name, band), [g for g in gs if g['band'] == band])
        o, t = vec(gs, 0, R), vec(gs, 1, R)
        say('%s r0-200: she died before her next turn in %d of ours and %d of theirs chances; the narrow tile she ends on is a neighbour in %d of %d and %d of %d entries; head tile with four open sides in %d and %d chances' % (
            name, o[14], t[14], o[15], o[1], t[15], t[1], o[24], t[24]))
        obs, hi, done = swap_test(gs, R, 1, 0)
        say('%s r0-200 side swap by game: rate ours minus theirs %s, %d of %d swaps at least as large; battle bootstrap of the ratio %s' % (name, f(obs), hi, done, boot(gs, R, 1, 0)))
        obs, hi, done = swap_test(gs, (1,), 1, 0)
        say('%s r101-200 side swap by game: %s, %d of %d; battle bootstrap of the ratio %s' % (name, f(obs), hi, done, boot(gs, (1,), 1, 0)))
        say('')

    say('--- 1b. which chances are real: a narrow neighbour with no body on it ---')
    for name, gs in (('main', main_g), ('v31', old_g)):
        for wl, ws in (('r0-200', R), ('r0-100', (0,)), ('r101-200', (1,))):
            entry('%s %s no narrow neighbour is free' % (name, wl), gs, ws, 13, 12)
            entry('%s %s some narrow neighbour is free' % (name, wl), gs, ws, 7, 6)
            entry('%s %s   and a wider neighbour is free too' % (name, wl), gs, ws, 9, 8)
            entry('%s %s   and no wider neighbour is free' % (name, wl), gs, ws, 11, 10)
            entry('%s %s   free both ways, no pearl beside her' % (name, wl), gs, ws, 28, 27)
        obs, hi, done = swap_test(gs, R, 9, 8)
        say('%s r0-200 free both ways, side swap by game: %s, %d of %d; battle bootstrap of the ratio %s' % (name, f(obs), hi, done, boot(gs, R, 9, 8)))
        obs, hi, done = swap_test(gs, R, 7, 6)
        say('%s r0-200 some narrow neighbour free, side swap by game: %s, %d of %d; battle bootstrap of the ratio %s' % (name, f(obs), hi, done, boot(gs, R, 7, 6)))
        say('')

    say('--- 1c. per layout, r0-200 (chances ours against theirs; entered) ---')
    for name, gs in (('both codes', free), ('main', main_g), ('v31', old_g)):
        bym = defaultdict(list)
        for g in gs:
            bym[g['map_key']].append(g)
        num_o = num_t = 0.0
        hi = lo = 0
        for mk in sorted(bym):
            o, t = vec(bym[mk], 0, R), vec(bym[mk], 1, R)
            r = rr(o[1], o[0], t[1], t[0])
            if r is not None:
                if r > 1:
                    hi += 1
                else:
                    lo += 1
            say('%-11s %-22s %d games: all chances ours %s, theirs %s, %s times | some narrow neighbour free: ours %s, theirs %s, %s times | free both ways: ours %s, theirs %s, %s times' % (
                name, mk, len(bym[mk]), sh(o[1], o[0]), sh(t[1], t[0]), f(r, 2), sh(o[7], o[6]), sh(t[7], t[6]), f(rr(o[7], o[6], t[7], t[6]), 2),
                sh(o[9], o[8]), sh(t[9], t[8]), f(rr(o[9], o[8], t[9], t[8]), 2)))
        say('%s: layouts where ours enters more often %d, less often %d' % (name, hi, lo))
        for a, b, lab in ((1, 0, 'all chances'), (7, 6, 'some narrow neighbour free'), (9, 8, 'free both ways')):
            # layout mix held: Mantel-Haenszel rate ratio over layouts
            mh_n = mh_d = 0.0
            for mk in bym:
                o, t = vec(bym[mk], 0, R), vec(bym[mk], 1, R)
                n = o[b] + t[b]
                if n == 0:
                    continue
                mh_n += o[a] * t[b] / n
                mh_d += t[a] * o[b] / n
            say('%s %s, layout mix held (Mantel-Haenszel ratio over layouts): %s' % (name, lab, f(dv(mh_n, mh_d), 2)))
            rs = []
            for mk in bym:
                rest = [g for g in gs if g['map_key'] != mk]
                o, t = vec(rest, 0, R), vec(rest, 1, R)
                rs.append((rr(o[a], o[b], t[a], t[b]), mk))
            say('%s %s, one layout left out at a time: %s (%s) to %s (%s)' % (name, lab, f(min(rs)[0], 2), min(rs)[1], f(max(rs)[0], 2), max(rs)[1]))
        four = ('Maze #1', 'weakhold #1', 'Prisoners Dilemma #1', 'Prisoners Dilemma #2')
        rest = [g for g in gs if g['map_key'] not in four]
        entry('%s without Maze, weakhold, both Prisoners' % name, rest)
        entry('%s   same, some narrow neighbour free' % name, rest, R, 7, 6)
        rest = [g for g in gs if g['map_key'] != 'weakhold #1']
        entry('%s without weakhold' % name, rest)
        opps = sorted(set(g['opp'] for g in gs))
        rs = []
        for op in opps:
            rest = [g for g in gs if g['opp'] != op]
            o, t = vec(rest, 0, R), vec(rest, 1, R)
            rs.append(rr(o[1], o[0], t[1], t[0]))
        say('%s one opponent left out at a time (%d): %s to %s' % (name, len(opps), f(min(rs), 2), f(max(rs), 2)))
        top = sorted(gs, key=lambda g: -(sum(g['cv'][0][w][1] for w in R) - sum(g['cv'][1][w][1] for w in R)))[:3]
        ids = set(g['game'] for g in top)
        rest = [g for g in gs if g['game'] not in ids]
        o, t = vec(rest, 0, R), vec(rest, 1, R)
        say('%s without the three games with the largest surplus of our entries (%s): %s times' % (
            name, ', '.join('%d %s %d against %d' % (g['game'], g['map_key'], sum(g['cv'][0][w][1] for w in R), sum(g['cv'][1][w][1] for w in R)) for g in top),
            f(rr(o[1], o[0], t[1], t[0]), 2)))
        pg_o = [dv(sum(g['cv'][0][w][1] for w in R), sum(g['cv'][0][w][0] for w in R)) for g in gs]
        pg_t = [dv(sum(g['cv'][1][w][1] for w in R), sum(g['cv'][1][w][0] for w in R)) for g in gs]
        both = [(a, b) for a, b in zip(pg_o, pg_t) if a is not None and b is not None]
        say('%s per game: ours the higher rate in %d games, theirs in %d, equal in %d; mean rate %s against %s' % (
            name, sum(1 for a, b in both if a > b), sum(1 for a, b in both if a < b), sum(1 for a, b in both if a == b),
            f(sum(a for a, b in both) / len(both)), f(sum(b for a, b in both) / len(both))))
        say('')

    say('=== 2. pearls ===')
    for name, gs in (('main', main_g), ('v31', old_g)):
        for wl, ws in (('r0-200', R), ('r0-100', (0,)), ('r101-200', (1,))):
            o, t = vec(gs, 0, ws), vec(gs, 1, ws)
            say('%s %s entries onto a tile that held a pearl: ours %s, theirs %s' % (name, wl, sh(o[2], o[1]), sh(t[2], t[1])))
            say('%s %s pearl chances (a pearl on a free narrow neighbour): ours entered %s, theirs %s, %s times; entered onto the pearl tile: ours %s, theirs %s, %s times' % (
                name, wl, sh(o[4], o[3]), sh(t[4], t[3]), f(rr(o[4], o[3], t[4], t[3]), 2), sh(o[5], o[3]), sh(t[5], t[3]), f(rr(o[5], o[3], t[5], t[3]), 2)))
            say('%s %s some narrow neighbour free, by where a pearl lies beside her:' % (name, wl))
            for a, b, lab in ((17, 16, 'pearl on a narrow neighbour only'), (21, 20, 'pearl on a narrow and on a wider neighbour'),
                              (19, 18, 'pearl on a wider neighbour only'), (23, 22, 'no pearl beside her')):
                say('        %-44s ours %s, theirs %s, %s times' % (lab, sh(o[a], o[b]), sh(t[a], t[b]), f(rr(o[a], o[b], t[a], t[b]), 2)))
            say('        within a side, pearl on a narrow neighbour only over no pearl beside her: ours %s times, theirs %s times' % (
                f(rr(o[17], o[16], o[23], o[22]), 2), f(rr(t[17], t[16], t[23], t[22]), 2)))
        obs, hi, done = swap_test(gs, (1,), 4, 3)
        say('%s r101-200 pearl chances, side swap by game: rate ours minus theirs %s, %d of %d at least as large; battle bootstrap of the ratio %s' % (name, f(obs), hi, done, boot(gs, (1,), 4, 3)))
        obs, hi, done = swap_test(gs, R, 4, 3)
        say('%s r0-200 pearl chances, side swap by game: %s, %d of %d; battle bootstrap of the ratio %s' % (name, f(obs), hi, done, boot(gs, R, 4, 3)))
        say('')

    say('=== 3. stays on narrow tiles ===')
    for name, gs in (('main', main_g), ('v31', old_g)):
        for wl, ws in (('r0-100', (0,)), ('r101-200', (1,)), ('r201-300', (2,))):
            say('%s %s ours:   %s' % (name, wl, stay_stats(stays_of(gs, 0, ws))))
            say('%s %s theirs: %s' % (name, wl, stay_stats(stays_of(gs, 1, ws))))
        obs, hi, done = stay_swap(gs, (1,))
        say('%s r101-200 side swap by game, turns a stay ours minus theirs %s: %d of %d swaps at least as large' % (name, f(obs, 2), hi, done))
        if name == 'main':
            for h in (1, 2):
                hs = [g for g in gs if g['half'] == h]
                say('main half %d r101-200 ours: %s' % (h, stay_stats(stays_of(hs, 0, (1,)))))
                say('main half %d r101-200 theirs: %s' % (h, stay_stats(stays_of(hs, 1, (1,)))))
        for band in ('1700-1899', '1900-2099'):
            hs = [g for g in gs if g['band'] == band]
            say('%s %s r101-200 ours: %s' % (name, band, stay_stats(stays_of(hs, 0, (1,)))))
            say('%s %s r101-200 theirs: %s' % (name, band, stay_stats(stays_of(hs, 1, (1,)))))
        say('')
    say('--- 3b. stays r101-200 per layout, both codes ---')
    bym = defaultdict(list)
    for g in free:
        bym[g['map_key']].append(g)
    longer = shorter = 0
    for mk in sorted(bym):
        o, t = stays_of(bym[mk], 0, (1,)), stays_of(bym[mk], 1, (1,))
        mo = dv(sum(x[0] for x in o), len(o))
        mt = dv(sum(x[0] for x in t), len(t))
        if mo is not None and mt is not None:
            if mo > mt:
                longer += 1
            else:
                shorter += 1
        say('%-22s ours %d stays %s turns a stay, %d deaths | theirs %d stays %s, %d deaths' % (mk, len(o), f(mo, 2), sum(x[1] for x in o), len(t), f(mt, 2), sum(x[1] for x in t)))
    say('layouts where our stays are the longer %d, the shorter or equal %d' % (longer, shorter))
    for name, gs in (('main', main_g), ('v31', old_g)):
        rs = []
        for mk in bym:
            rest = [g for g in gs if g['map_key'] != mk]
            o, t = stays_of(rest, 0, (1,)), stays_of(rest, 1, (1,))
            rs.append((dv(sum(x[0] for x in o), len(o)) / dv(sum(x[0] for x in t), len(t)), mk, dv(sum(x[0] for x in o), len(o)), dv(sum(x[0] for x in t), len(t))))
        say('%s r101-200 one layout left out at a time: ours over theirs %s (%s: %s against %s) to %s (%s: %s against %s)' % (
            name, f(min(rs)[0], 2), min(rs)[1], f(min(rs)[2], 2), f(min(rs)[3], 2), f(max(rs)[0], 2), max(rs)[1], f(max(rs)[2], 2), f(max(rs)[3], 2)))
        two = [g for g in gs if g['map_key'] not in ('Maze #1', 'weakhold #1')]
        say('%s r101-200 without Maze and weakhold: ours %s' % (name, stay_stats(stays_of(two, 0, (1,)))))
        say('%s r101-200 without Maze and weakhold: theirs %s' % (name, stay_stats(stays_of(two, 1, (1,)))))

    say('')
    say('=== 4. share of queen turn starts on a narrow tile and chances per turn (context) ===')
    for name, gs in (('main', main_g), ('v31', old_g)):
        for w in (0, 1):
            to = sum(g['turns'][0][w] for g in gs)
            tt = sum(g['turns'][1][w] for g in gs)
            no = sum(g['narrow_turns'][0][w] for g in gs)
            nt = sum(g['narrow_turns'][1][w] for g in gs)
            o, t = vec(gs, 0, (w,)), vec(gs, 1, (w,))
            say('%s %s: turn starts ours %d theirs %d; on a narrow tile %s against %s; chances per turn start %s against %s; chances with a free narrow neighbour per turn start %s against %s' % (
                name, WN[w], to, tt, f(dv(no, to)), f(dv(nt, tt)), f(dv(o[0], to)), f(dv(t[0], tt)), f(dv(o[6], to)), f(dv(t[6], tt))))

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
    Path(P + 'f38-1021-numbers.txt').write_text('\n'.join(LINES) + '\n')


main()
