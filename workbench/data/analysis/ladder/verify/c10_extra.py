#!/usr/bin/env python3
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
"""Verifier claims 10, extra checks for F39 and F38 (run of 2026-10-07 10:21 KST). Reads the x10 shards and writes
f38-f39-1021-extras.txt."""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')
CUT = '2026-10-06T14:48:15'
LINES = []


def say(*a):
    s = ' '.join(str(x) for x in a)
    LINES.append(s)
    print(s)


def dv(a, b):
    return (a / b) if b else None


def f(x, d=3):
    return 'none' if x is None else ('%.' + str(d) + 'f') % x


def window(r):
    return 0 if r <= 100 else 1 if r <= 200 else 2 if r <= 300 else 3


def load():
    games = []
    for k in range(6):
        for line in (V / ('x10-%d.jsonl' % k)).read_text().splitlines():
            if line.strip():
                games.append(json.loads(line))
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
        g['half'] = 1 if g['completedAt'][:19] < CUT else 2
        g['p1'] = g['map_key'] == 'Portals #1'
    return order


def main():
    games = load()
    free = [g for g in games if g['free'] and g['code'] in ('main', 'v31')]
    codes = (('main', [g for g in free if g['code'] == 'main']), ('v31', [g for g in free if g['code'] == 'v31']))
    say('F39 and F38 extras, verifier, run of 2026-10-07 10:21 KST')
    say('main halves with the cut read as a time: %s' % dict(Counter(g['half'] for g in codes[0][1])))

    say('')
    say('=== F39 a. layout mix held, counted per turn and per short dragon (Portals #1 left out) ===')
    for name, gs0 in codes:
        for lab, gs in (('all endings', [g for g in gs0 if not g['p1']]), ('full games', [g for g in gs0 if not g['p1'] and g['full']]),
                        ('games ended by elimination', [g for g in gs0 if not g['p1'] and not g['full']])):
            L = defaultdict(lambda: [[0, 0, 0], [0, 0, 0]])
            for g in gs:
                for r in g['lone']:
                    e = L[g['map_key']][r[0]]
                    e[0] += 1
                    e[1] += r[3]
                    e[2] += r[2]
            both = [mk for mk in L if L[mk][0][0] and L[mk][1][0]]
            T1 = sum(L[mk][1][0] for mk in L)
            T0 = sum(L[mk][0][0] for mk in L)
            say('%s %s: lone turns on layouts where both sides have some: their queen %d of %d, our queen %d of %d' % (
                name, lab, sum(L[mk][1][0] for mk in both), T1, sum(L[mk][0][0] for mk in both), T0))
            for wl, ws in (('their queen', 1), ('our queen', 0)):
                w = {mk: L[mk][ws][0] for mk in both}
                den = sum(w.values())
                c1 = sum(w[mk] * L[mk][1][1] / L[mk][1][0] for mk in both) / den
                c0 = sum(w[mk] * L[mk][0][1] / L[mk][0][0] for mk in both) / den
                say('    short within 12 a turn, layouts weighted by the lone turns of %s: ours near their queen %s, theirs near ours %s, ratio %s' % (wl, f(c1, 2), f(c0, 2), f(dv(c1, c0), 2)))
                we = {mk: L[mk][ws][2] for mk in both if L[mk][1][2] and L[mk][0][2]}
                den = sum(we.values())
                p1 = sum(we[mk] * L[mk][1][1] / L[mk][1][2] for mk in we) / den
                p0 = sum(we[mk] * L[mk][0][1] / L[mk][0][2] for mk in we) / den
                say('    share within 12, layouts weighted by the short-dragon turns facing %s: ours %s, theirs %s, ratio %s' % (wl, f(p1), f(p0), f(dv(p1, p0), 2)))
            lower = sum(1 for mk in both if L[mk][1][1] / L[mk][1][0] < L[mk][0][1] / L[mk][0][0])
            say('    layouts where ours has fewer within 12 a turn: %d of %d; per layout (ours a turn / theirs a turn): %s' % (
                lower, len(both), '; '.join('%s %s/%s' % (mk, f(L[mk][1][1] / L[mk][1][0], 2), f(L[mk][0][1] / L[mk][0][0], 2)) for mk in sorted(both))))
    say('')
    say('=== F39 b. how a lone spell ends (Portals #1 left out) ===')
    RE = ('wall', 'own body', 'other dragon body', 'head-on', 'no action')
    for name, gs0 in codes:
        gs = [g for g in gs0 if not g['p1']]
        for s, lab in ((1, 'their lone queen'), (0, 'our lone queen')):
            spells = turns = deaths = near_rows = far_rows = near_d = far_d = 0
            reasons = Counter()
            lens = []
            for g in gs:
                rows = [r for r in g['lone'] if r[0] == s]
                if not rows:
                    continue
                spells += 1
                turns += len(rows)
                lens.append(len(rows))
                for r in rows:
                    if r[3] > 0:
                        near_rows += 1
                    else:
                        far_rows += 1
                d = g['qdeath'][s]
                if d is not None:
                    deaths += 1
                    reasons[RE[d['reason']] + (' (her own move)' if d['actor'] else ' (hit)')] += 1
                    if rows[-1][3] > 0:
                        near_d += 1
                    else:
                        far_d += 1
            lens.sort()
            say('%s %s: %d spells, %d turns, median %d turns, she dies in %d (%s), %s deaths per 1,000 lone turns; with a short head within 12 at the turn start %s per 1,000 (%d in %d), with none %s per 1,000 (%d in %d); how: %s' % (
                name, lab, spells, turns, lens[len(lens) // 2], deaths, f(dv(deaths, spells), 2), f(1000 * deaths / turns, 1),
                f(1000 * dv(near_d, near_rows), 1), near_d, near_rows, f(1000 * dv(far_d, far_rows), 1), far_d, far_rows, dict(reasons)))
    say('')
    say('=== F39 c. part B on main by band, chance (from raw round 100, Portals #1 left out) ===')
    for name, gs0 in codes:
        gs1 = [g for g in gs0 if not g['p1']]
        for lab, gs in (('all', gs1), ('1700-1899', [g for g in gs1 if g['band'] == '1700-1899']), ('1900 and above', [g for g in gs1 if g['band'] in ('1900-2099', '2100+')]),
                        ('full games', [g for g in gs1 if g['full']]), ('ended by elimination', [g for g in gs1 if not g['full']]),
                        ('half 1', [g for g in gs1 if g['half'] == 1]), ('half 2', [g for g in gs1 if g['half'] == 2])):
            if name == 'v31' and lab in ('half 1', 'half 2'):
                continue
            cl = [[], []]
            for g in gs:
                for s in (0, 1):
                    last = None
                    n = nf = sf = 0
                    for r in g['lone']:
                        if r[0] != s:
                            continue
                        if r[8] > 0:
                            last = r[1]
                        if r[1] < 100:
                            continue
                        n += 1
                        if last is not None and r[1] - last <= 20:
                            nf += 1
                            sf += r[3]
                    if n:
                        cl[s].append((n, nf, sf))
            def stat(a, b):
                fa = sum(x[1] for x in a)
                fb = sum(x[1] for x in b)
                if not fa or not fb:
                    return None
                return sum(x[2] for x in a) / fa - sum(x[2] for x in b) / fb
            obs = stat(cl[1], cl[0])
            rng = random.Random(17)
            allc = cl[1] + cl[0]
            k = len(cl[1])
            lo = done = 0
            for _ in range(5000):
                rng.shuffle(allc)
                v = stat(allc[:k], allc[k:])
                if v is None:
                    continue
                done += 1
                if v <= obs + 1e-12:
                    lo += 1
            t1 = [sum(x[i] for x in cl[1]) for i in range(3)]
            t0 = [sum(x[i] for x in cl[0]) for i in range(3)]
            say('%s %s: fresh share %s against %s; short within 12 at fresh turns %s (%d games) against %s (%d games), ratio %s; label shuffle among games %d of %d at or below' % (
                name, lab, f(dv(t1[1], t1[0])), f(dv(t0[1], t0[0])), f(dv(t1[2], t1[1]), 2), len(cl[1]), f(dv(t0[2], t0[1]), 2), len(cl[0]),
                f(dv(dv(t1[2], t1[1]), dv(t0[2], t0[1])), 2), lo, done))

    say('')
    say('=== F38 g. chances with a free narrow neighbour and no free wider one, r0-200 ===')
    for name, gs in codes:
        cat = [Counter(), Counter()]
        ent = [Counter(), Counter()]
        lay = defaultdict(lambda: [0, 0, 0, 0])
        for g in gs:
            for r in g['chances']:
                (s, rnd, nopen, n_nar, n_fn, n_fw, n_p, n_pw, e, onp, onfn, onnb, died, qlen) = r
                if rnd > 200 or n_fn < 1:
                    continue
                if n_fw >= 1:
                    key = 'a wider neighbour is free'
                else:
                    wide = nopen - n_nar
                    key = 'no wider neighbour exists' if wide <= 0 else 'one wider neighbour, taken' if wide == 1 else 'two or more wider neighbours, all taken'
                    lay[g['map_key']][s] += 1
                    lay[g['map_key']][2 + s] += e
                cat[s][key] += 1
                ent[s][key] += e
        for key in ('a wider neighbour is free', 'no wider neighbour exists', 'one wider neighbour, taken', 'two or more wider neighbours, all taken'):
            say('%s %-42s ours %d of %d (%s), theirs %d of %d (%s)' % (name, key, ent[0][key], cat[0][key], f(dv(ent[0][key], cat[0][key])), ent[1][key], cat[1][key], f(dv(ent[1][key], cat[1][key]))))
        say('%s chances with no free wider neighbour per layout (ours, theirs): %s' % (name, '; '.join('%s %d, %d' % (mk, lay[mk][0], lay[mk][1]) for mk in sorted(lay))))
        four = ('Maze #1', 'weakhold #1', 'Prisoners Dilemma #1', 'Prisoners Dilemma #2')
        say('%s of them on Maze, weakhold and both Prisoners: ours %d of %d, theirs %d of %d' % (
            name, sum(lay[mk][0] for mk in four), sum(v[0] for v in lay.values()), sum(lay[mk][1] for mk in four), sum(v[1] for v in lay.values())))
    say('')
    say('=== F38 h. pearl chances r101-200, both codes pooled ===')
    units = []
    for g in free:
        o = [0, 0, 0]
        t = [0, 0, 0]
        for r in g['chances']:
            if 101 <= r[1] <= 200 and r[6] >= 1:
                e = o if r[0] == 0 else t
                e[0] += 1
                e[1] += r[8]
                e[2] += r[9]
        if o[0] or t[0]:
            units.append((o, t))
    for idx, lab in ((1, 'entered'), (2, 'entered onto the pearl tile')):
        def stat(sel):
            on = od = tn = td = 0
            for (o, t), k in zip(units, sel):
                a, b = (t, o) if k else (o, t)
                on += a[idx]
                od += a[0]
                tn += b[idx]
                td += b[0]
            if not od or not td:
                return None
            return on / od - tn / td
        obs = stat([0] * len(units))
        rng = random.Random(23)
        hi = done = 0
        for _ in range(10000):
            v = stat([rng.random() < 0.5 for _u in units])
            if v is None:
                continue
            done += 1
            if v >= obs - 1e-12:
                hi += 1
        so = [sum(o[i] for o, t in units) for i in range(3)]
        st = [sum(t[i] for o, t in units) for i in range(3)]
        say('%s: ours %d of %d (%s), theirs %d of %d (%s), %s times; side swap by game %d of %d at least as large; games %d' % (
            lab, so[idx], so[0], f(dv(so[idx], so[0])), st[idx], st[0], f(dv(st[idx], st[0])), f(dv(dv(so[idx], so[0]), dv(st[idx], st[0])), 2), hi, done, len(units)))
    lay = defaultdict(lambda: [0, 0, 0, 0])
    for g in free:
        for r in g['chances']:
            if 101 <= r[1] <= 200 and r[6] >= 1:
                lay[g['map_key']][r[0] * 2] += 1
                lay[g['map_key']][r[0] * 2 + 1] += r[8]
    say('per layout, pearl chances r101-200 entered (ours, theirs): %s' % '; '.join('%s %d of %d, %d of %d' % (mk, v[1], v[0], v[3], v[2]) for mk, v in sorted(lay.items())))
    rest = [v for mk, v in lay.items() if mk not in ('Maze #1', 'weakhold #1')]
    say('without Maze and weakhold: ours %d of %d, theirs %d of %d' % (sum(v[1] for v in rest), sum(v[0] for v in rest), sum(v[3] for v in rest), sum(v[2] for v in rest)))
    say('')
    say('=== F38 i. entries per chance with the cut read as a time, main r0-200 ===')
    for h in (1, 2):
        o = [0, 0]
        t = [0, 0]
        for g in codes[0][1]:
            if g['half'] != h:
                continue
            for r in g['chances']:
                if r[1] <= 200:
                    e = o if r[0] == 0 else t
                    e[0] += 1
                    e[1] += r[8]
        say('main half %d: ours %d of %d (%s), theirs %d of %d (%s), %s times' % (h, o[1], o[0], f(dv(o[1], o[0])), t[1], t[0], f(dv(t[1], t[0])), f(dv(dv(o[1], o[0]), dv(t[1], t[0])), 2)))
    Path(P + 'f38-f39-1021-extras.txt').write_text('\n'.join(LINES) + '\n')


main()
