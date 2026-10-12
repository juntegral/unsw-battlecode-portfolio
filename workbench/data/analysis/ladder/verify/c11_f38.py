#!/usr/bin/env python3
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
"""Verifier claims 11 (run of 2026-10-07 11:17 KST), F38: long stays (3 or more turn starts) of a queen on narrow
tiles. Reads the x11 shards (own extraction from the raw replays) and writes f38-1117-numbers.txt. maps.json is read
for the dead-end flag of a layout; rows.jsonl is read only in the last section, to compare."""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')
CUT = '2026-10-06T14:48:15'
LINES = []
REASON = ['wall', 'own body', 'other dragon body', 'head-on', 'other']
THREE = ('Maze', 'weakhold', 'Tower Defense')


def say(*a):
    s = ' '.join(str(x) for x in a)
    LINES.append(s)
    print(s)


def load():
    games = []
    for k in range(6):
        for line in (V / ('x11-%d.jsonl' % k)).read_text().splitlines():
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
        g['band'] = 'under 1700' if e < 1700 else '1700-1899' if e < 1900 else '1900-2099' if e < 2100 else '2100 on'
        g['free'] = not maps[g['map_key']]['queen_spawn_dead_end']
        g['half'] = 1 if g['completedAt'][:19] < CUT else 2
        g['p1'] = g['map_key'] == 'Portals #1'
        g['opp'] = '%s (%s)' % (g.get('opponent'), g.get('opponentId'))
        # c[s][w] = [stays, long stays] begun in window w (0 r0-100, 1 r101-200, 2 r201-300, 3 r301 on)
        c = [[[0, 0] for _ in range(4)] for _ in range(2)]
        for st in g['stays']:
            r = st[1]
            w = 0 if r <= 100 else 1 if r <= 200 else 2 if r <= 300 else 3
            c[st[0]][w][0] += 1
            if st[2] >= 3:
                c[st[0]][w][1] += 1
        g['c'] = c
    return order, bad, maps


def sh(a, n):
    return '%d of %d (%s)' % (a, n, '%.3f' % (a / n) if n else 'n/a')


def ratio(a1, n1, a0, n0):
    if not n1 or not n0 or not a0:
        return None
    return (a1 / n1) / (a0 / n0)


def f(x, d=2):
    return 'n/a' if x is None else ('%.' + str(d) + 'f') % x


def tally(gs, w=1):
    a1 = sum(g['c'][0][w][1] for g in gs)
    n1 = sum(g['c'][0][w][0] for g in gs)
    a0 = sum(g['c'][1][w][1] for g in gs)
    n0 = sum(g['c'][1][w][0] for g in gs)
    return a1, n1, a0, n0


def line(label, gs, w=1):
    a1, n1, a0, n0 = tally(gs, w)
    say('%-46s ours %s, theirs %s, %s times  [%d games]' % (label, sh(a1, n1), sh(a0, n0), f(ratio(a1, n1, a0, n0)), len(gs)))


def swap_test(gs, w=1, n=10000, seed=11):
    rng = random.Random(seed)
    rows = [(g['c'][0][w][1], g['c'][0][w][0], g['c'][1][w][1], g['c'][1][w][0]) for g in gs]

    def stat(rs):
        a1 = sum(r[0] for r in rs)
        n1 = sum(r[1] for r in rs)
        a0 = sum(r[2] for r in rs)
        n0 = sum(r[3] for r in rs)
        if not n1 or not n0:
            return None
        return a1 / n1 - a0 / n0
    obs = stat(rows)
    hi = done = 0
    for _ in range(n):
        rs = [r if rng.random() < 0.5 else (r[2], r[3], r[0], r[1]) for r in rows]
        v = stat(rs)
        if v is None:
            continue
        done += 1
        if v >= obs - 1e-12:
            hi += 1
    return obs, hi, done


def boot(gs, w=1, n=2000, seed=5):
    rng = random.Random(seed)
    by = defaultdict(list)
    for g in gs:
        by[g['battle']].append(g)
    keys = sorted(by)
    out = []
    for _ in range(n):
        pick = [by[keys[rng.randrange(len(keys))]] for _ in keys]
        a1 = n1 = a0 = n0 = 0
        for lst in pick:
            for g in lst:
                a1 += g['c'][0][w][1]
                n1 += g['c'][0][w][0]
                a0 += g['c'][1][w][1]
                n0 += g['c'][1][w][0]
        r = ratio(a1, n1, a0, n0)
        if r is not None:
            out.append(r)
    out.sort()
    if not out:
        return 'n/a'
    return '%s to %s (%d of %d resamples with a ratio)' % (f(out[int(0.025 * len(out))]), f(out[min(len(out) - 1, int(0.975 * len(out)))]), len(out), n)


def mh(gs, w=1, key='map_key'):
    by = defaultdict(list)
    for g in gs:
        by[g[key]].append(g)
    num = den = 0.0
    for k, lst in by.items():
        a1, n1, a0, n0 = tally(lst, w)
        N = n1 + n0
        if not N:
            continue
        num += a1 * n0 / N
        den += a0 * n1 / N
    return num / den if den else None


def longs(gs, s, lo=0, hi=10 ** 6):
    out = []
    for g in gs:
        for st in g['stays']:
            if st[0] == s and st[2] >= 3 and lo <= st[1] <= hi:
                out.append((g, st))
    return out


def main():
    games, bad, maps = load()
    say('games read', len(games), 'errors', len(bad), '; final state equals the result block in',
        sum(1 for g in games if g['final_ok']), '; body map consistent in', sum(1 for g in games if g['own_ok']),
        '; games with anomalies', sum(1 for g in games if g['anomalies']))
    say('codes:', dict(Counter(g['code'] for g in games)))
    say('dead-end layouts by maps.json:', sorted(set(g['map_key'] for g in games if not g['free'])))
    M = [g for g in games if g['code'] == 'main' and g['free'] and not g['p1']]
    O = [g for g in games if g['code'] == 'v31' and g['free'] and not g['p1']]
    say('main games in the set', len(M), '(half 1:', sum(1 for g in M if g['half'] == 1), ', half 2:', sum(1 for g in M if g['half'] == 2), '); v31', len(O))
    say('main with Portals #1 kept:', len([g for g in games if g['code'] == 'main' and g['free']]), '; v31:', len([g for g in games if g['code'] == 'v31' and g['free']]))
    say('main bands:', dict(Counter(g['band'] for g in M)), ' v31 bands:', dict(Counter(g['band'] for g in O)))
    say('')
    say('=== 1. long share of stays begun in raw rounds 101-200 ===')
    line('main', M)
    line('main half 1 (before the cut)', [g for g in M if g['half'] == 1])
    line('main half 2 (from the cut)', [g for g in M if g['half'] == 2])
    for b in ('under 1700', '1700-1899', '1900-2099', '2100 on'):
        line('main ' + b, [g for g in M if g['band'] == b])
    line('v31', O)
    line('v31 half 1', [g for g in O if g['half'] == 1])
    line('v31 half 2', [g for g in O if g['half'] == 2])
    for b in ('under 1700', '1700-1899', '1900-2099', '2100 on'):
        line('v31 ' + b, [g for g in O if g['band'] == b])
    line('main with Portals #1 kept', [g for g in games if g['code'] == 'main' and g['free']])
    say('')
    say('--- other windows ---')
    for name, gs in (('main', M), ('v31', O)):
        for w, lab in ((0, 'r0-100'), (2, 'r201-300'), (3, 'r301 on')):
            line('%s %s' % (name, lab), gs, w)
    say('')
    say('--- leave one out, main, r101-200 ---')
    for key, lab in (('opp', 'opponent'), ('map_key', 'layout'), ('battle', 'battle')):
        rs = []
        for k in sorted(set(g[key] for g in M)):
            rest = [g for g in M if g[key] != k]
            a1, n1, a0, n0 = tally(rest)
            rs.append((ratio(a1, n1, a0, n0) or 0, k, a1, n1, a0, n0))
        rs.sort()
        say('one %s left out: ratio %s (without %s: %d of %d against %d of %d) to %s (without %s: %d of %d against %d of %d); %d kinds' % (
            lab, f(rs[0][0]), rs[0][1], rs[0][2], rs[0][3], rs[0][4], rs[0][5], f(rs[-1][0]), rs[-1][1], rs[-1][2], rs[-1][3], rs[-1][4], rs[-1][5], len(rs)))
    say('--- leave one out, v31, r101-200 ---')
    for key, lab in (('opp', 'opponent'), ('map_key', 'layout')):
        rs = []
        for k in sorted(set(g[key] for g in O)):
            rest = [g for g in O if g[key] != k]
            a1, n1, a0, n0 = tally(rest)
            rs.append((ratio(a1, n1, a0, n0) or 0, k))
        rs.sort()
        say('one %s left out: ratio %s (without %s) to %s (without %s)' % (lab, f(rs[0][0]), rs[0][1], f(rs[-1][0]), rs[-1][1]))
    say('')
    say('--- by layout, r101-200: ours long of stays, theirs long of stays ---')
    keys = sorted(set(g['map_key'] for g in M + O))
    for name, gs in (('both codes', M + O), ('main', M), ('v31', O)):
        say(name + ':')
        higher = lower = 0
        for k in keys:
            lst = [g for g in gs if g['map_key'] == k]
            a1, n1, a0, n0 = tally(lst)
            if n1 and n0:
                if a1 / n1 > a0 / n0:
                    higher += 1
                elif a1 / n1 < a0 / n0:
                    lower += 1
            say('    %-24s ours %s, theirs %s, %s times  [%d games]' % (k, sh(a1, n1), sh(a0, n0), f(ratio(a1, n1, a0, n0)), len(lst)))
        say('    ours the higher share on %d layouts, the lower on %d' % (higher, lower))
        say('    layout mix held (Mantel-Haenszel over layouts): %s times' % f(mh(gs)))
        say('    opponent mix held (Mantel-Haenszel over opponents): %s times' % f(mh(gs, 1, 'opp')))
    for name, gs in (('main', M), ('v31', O), ('both codes', M + O)):
        line('%s on Maze, weakhold, Tower Defense' % name, [g for g in gs if g['map'] in THREE])
        line('%s without the three' % name, [g for g in gs if g['map'] not in THREE])
    for mp in THREE:
        line('main on %s' % mp, [g for g in M if g['map'] == mp])
        line('v31 on %s' % mp, [g for g in O if g['map'] == mp])
    say('share of the stays (r101-200) that lie on the three layouts: main ours %s, theirs %s; v31 ours %s, theirs %s' % (
        sh(tally([g for g in M if g['map'] in THREE])[1], tally(M)[1]), sh(tally([g for g in M if g['map'] in THREE])[3], tally(M)[3]),
        sh(tally([g for g in O if g['map'] in THREE])[1], tally(O)[1]), sh(tally([g for g in O if g['map'] in THREE])[3], tally(O)[3])))
    say('')
    say('--- chance ---')
    for name, gs in (('main', M), ('main half 1', [g for g in M if g['half'] == 1]), ('main half 2', [g for g in M if g['half'] == 2]),
                     ('main 1700-1899', [g for g in M if g['band'] == '1700-1899']), ('main 1900-2099', [g for g in M if g['band'] == '1900-2099']),
                     ('main on the three layouts', [g for g in M if g['map'] in THREE]), ('main without the three', [g for g in M if g['map'] not in THREE]),
                     ('v31', O), ('v31 on the three layouts', [g for g in O if g['map'] in THREE]), ('v31 without the three', [g for g in O if g['map'] not in THREE])):
        obs, hi, done = swap_test(gs)
        say('%s: side swap by game, long share ours minus theirs %s: %d of %d swaps at least as large; battle bootstrap of the ratio, 95 percent: %s' % (
            name, f(obs, 3), hi, done, boot(gs)))
    say('')
    say('--- the three games that support it most (main, r101-200) ---')
    top = sorted(M, key=lambda g: -(g['c'][0][1][1] - g['c'][1][1][1]))[:3]
    say('games:', [(g['game'], g['map_key'], g['opp'], 'ours long %d of %d' % (g['c'][0][1][1], g['c'][0][1][0]), 'theirs %d of %d' % (g['c'][1][1][1], g['c'][1][1][0])) for g in top])
    ids = set(g['game'] for g in top)
    line('main without them', [g for g in M if g['game'] not in ids])
    say('')
    say('--- unit: games ---')
    for name, gs in (('main', M), ('v31', O)):
        g1 = sum(1 for g in gs if g['c'][0][1][1] > 0)
        g0 = sum(1 for g in gs if g['c'][1][1][1] > 0)
        gb = sum(1 for g in gs if g['c'][0][1][1] > 0 and g['c'][1][1][1] > 0)
        t1 = sum(g['turns'][0][1] for g in gs)
        t0 = sum(g['turns'][1][1] for g in gs)
        nt1 = sum(g['narrow_turns'][0][1] for g in gs)
        nt0 = sum(g['narrow_turns'][1][1] for g in gs)
        a1, n1, a0, n0 = tally(gs)
        say('%s: games with a long stay begun in r101-200: ours %d, theirs %d, both %d of %d games; most in one game ours %d, theirs %d' % (
            name, g1, g0, gb, len(gs), max(g['c'][0][1][1] for g in gs), max(g['c'][1][1][1] for g in gs)))
        say('%s: queen turn starts in r101-200 ours %d, theirs %d; on narrow tiles %s and %s; long stays per 1,000 queen turn starts %s against %s (%s times); stays per 1,000 turn starts %s against %s' % (
            name, t1, t0, sh(nt1, t1), sh(nt0, t0), f(1000 * a1 / t1), f(1000 * a0 / t0), f((a1 / t1) / (a0 / t0) if a0 else None),
            f(1000 * n1 / t1, 1), f(1000 * n0 / t0, 1)))
    say('')
    say('--- by KST date (main, r101-200) ---')
    for d in sorted(set((g.get('at_kst') or '')[:10] for g in M)):
        line('main ' + d, [g for g in M if (g.get('at_kst') or '')[:10] == d])
    say('')
    say('=== 2. what is inside the long stays begun in r101-200 (both codes, as the queue has it) ===')
    for name, gs in (('both codes', M + O), ('main', M), ('v31', O)):
        for s, lab in ((0, 'ours'), (1, 'theirs')):
            L = longs(gs, s, 101, 200)
            n = len(L)
            own = [x for x in L if x[1][6]]
            say('%s %s: long stays %d; ended in her death %d; own dragon body beside her head at some turn start %d (of them ended in her death %d); own beside at the first turn start %d; enemy head within 3 columns and rows of her head at some turn start %d (at the first %d; of any body tile %d; a short enemy head %d); enemy body beside her head %d; a dead-end tile (one open side) at some turn start %d; mean length %s; stays with a tile seen twice %d; with a turn start with no free exit %d' % (
                name, lab, n, sum(1 for x in L if x[1][3]), len(own), sum(1 for x in own if x[1][3]), sum(1 for x in L if x[1][7]),
                sum(1 for x in L if x[1][8]), sum(1 for x in L if x[1][9]), sum(1 for x in L if x[1][10]), sum(1 for x in L if x[1][17]),
                sum(1 for x in L if x[1][11]), sum(1 for x in L if x[1][12] == 1), f(sum(x[1][2] for x in L) / n if n else None),
                sum(1 for x in L if x[1][15] < x[1][2]), sum(1 for x in L if x[1][16] > 0)))
            dead = [x for x in L if x[1][3]]
            say('    deaths by engine reason: %s; deaths with an own dragon beside her at some turn start: %d of %d, by reason %s; deaths without: by reason %s' % (
                dict(Counter(REASON[x[1][5]] for x in dead)), sum(1 for x in dead if x[1][6]), len(dead),
                dict(Counter(REASON[x[1][5]] for x in dead if x[1][6])), dict(Counter(REASON[x[1][5]] for x in dead if not x[1][6]))))
            say('    long stays that she leaves alive: %d, of them with an own dragon beside her %d' % (
                sum(1 for x in L if not x[1][3]), sum(1 for x in L if not x[1][3] and x[1][6])))
    say('')
    say('--- the own-dragon flag in short stays and by window (both codes) ---')
    for s, lab in ((0, 'ours'), (1, 'theirs')):
        allst = [(g, st) for g in M + O for st in g['stays'] if st[0] == s and 101 <= st[1] <= 200]
        short = [x for x in allst if x[1][2] < 3]
        say('%s r101-200: stays of 1 or 2 turn starts %d, own dragon beside her in %d, ended in her death %d (with own beside %d)' % (
            lab, len(short), sum(1 for x in short if x[1][6]), sum(1 for x in short if x[1][3]), sum(1 for x in short if x[1][3] and x[1][6])))
        L = longs(M + O, s)
        say('%s all rounds: long stays %d, own beside %d, ended in death %d, own beside among the deaths %d' % (
            lab, len(L), sum(1 for x in L if x[1][6]), sum(1 for x in L if x[1][3]), sum(1 for x in L if x[1][3] and x[1][6])))
    say('')
    say('=== 3. all rounds ===')
    for name, gs in (('main', M), ('v31', O)):
        for s, lab in ((0, 'ours'), (1, 'theirs')):
            L = longs(gs, s)
            dead = [x for x in L if x[1][3]]
            inside = sum(x[1][2] for x in L)
            allturns = sum(sum(g['turns'][s]) for g in gs)
            qd = sum(1 for g in gs if g['qdeath'][s] is not None)
            lost = sum(1 for x in dead if not x[0]['win'])
            lost_strict = sum(1 for x in dead if not x[0]['win'] and not x[0]['drawn'])
            ds = len(dead)
            lo = hi = None
            if ds and inside:
                lo = 1000 * ds / inside * math.exp(-1.96 / math.sqrt(ds))
                hi = 1000 * ds / inside * math.exp(1.96 / math.sqrt(ds))
            say('%s %s: long stays %d; ended in her death %d %s; turn starts inside long stays %d; deaths per 1,000 turn starts inside %s (95 percent %s to %s); all queen turn starts %d; all queen deaths %d; deaths per 1,000 turn starts outside long stays %s; her death-ended long stays in games we did not win %d (lost outright %d); at the end of the game %d' % (
                name, lab, len(L), ds, dict(Counter(REASON[x[1][5]] for x in dead)), inside, f(1000 * ds / inside if inside else None, 1), f(lo, 1), f(hi, 1),
                allturns, qd, f(1000 * (qd - ds) / (allturns - inside), 2), lost, lost_strict, sum(1 for x in L if x[1][4])))
        L1 = longs(gs, 0)
        L0 = longs(gs, 1)
        d1 = sum(1 for x in L1 if x[1][3])
        d0 = sum(1 for x in L0 if x[1][3])
        t1 = sum(x[1][2] for x in L1)
        t0 = sum(x[1][2] for x in L0)
        if d1 and d0:
            rr = (d1 / t1) / (d0 / t0)
            se = math.sqrt(1 / d1 + 1 / d0)
            say('%s: deaths per turn inside long stays, ours over theirs %s (95 percent %s to %s); per long stay %s against %s' % (
                name, f(rr), f(rr * math.exp(-1.96 * se)), f(rr * math.exp(1.96 * se)), f(d1 / len(L1), 3), f(d0 / len(L0), 3)))
        for w, lab, lo_r, hi_r in ((0, 'r0-100', 0, 100), (1, 'r101-200', 101, 200), (2, 'r201-300', 201, 300), (3, 'r301 on', 301, 10 ** 6)):
            A = longs(gs, 0, lo_r, hi_r)
            B = longs(gs, 1, lo_r, hi_r)
            say('    %s %s: ours %d long stays, %d turn starts inside, %d deaths; theirs %d, %d, %d' % (
                name, lab, len(A), sum(x[1][2] for x in A), sum(1 for x in A if x[1][3]), len(B), sum(x[1][2] for x in B), sum(1 for x in B if x[1][3])))
        # where the queens died, all rounds
        for s, lab in ((0, 'ours'), (1, 'theirs')):
            qd = [g['qdeath'][s] for g in gs if g['qdeath'][s] is not None]
            say('    %s %s queen deaths %d: in a stay (her last turn start was on a narrow tile) %d; by reason %s' % (
                name, lab, len(qd), sum(1 for d in qd if d['in_stay']), dict(Counter(REASON[d['reason']] for d in qd))))
    say('')
    say('=== 4. is it speed? runs of consecutive head positions on narrow tiles, every step counted ===')
    for name, gs in (('main', M), ('v31', O)):
        for s, lab in ((0, 'ours'), (1, 'theirs')):
            tr = [t for g in gs for t in g['truns'] if t[0] == s and 101 <= t[1] <= 200]
            st = [x for g in gs for x in g['stays'] if x[0] == s and 101 <= x[1] <= 200]
            turns = sum(sum(g['turns'][s]) for g in gs)
            steps = sum(g['steps'][s] for g in gs)
            multi = sum(g['multi_turns'][s] for g in gs)
            say('%s %s: runs begun in r101-200 %d, of 3 or more tiles %d (%s); stays %d, long %d; all rounds: queen turn starts %d, steps %d, turns with two or more steps %d (%s)' % (
                name, lab, len(tr), sum(1 for t in tr if t[2] >= 3), f(sum(1 for t in tr if t[2] >= 3) / len(tr) if tr else None, 3),
                len(st), sum(1 for x in st if x[2] >= 3), turns, steps, multi, f(multi / turns if turns else None, 3)))
        for lab2, sub in (('on the three layouts', [g for g in gs if g['map'] in THREE]), ('without the three', [g for g in gs if g['map'] not in THREE])):
            parts = []
            for s in (0, 1):
                tr = [t for g in sub for t in g['truns'] if t[0] == s and 101 <= t[1] <= 200]
                parts.append('%d of %d' % (sum(1 for t in tr if t[2] >= 3), len(tr)))
            say('    %s %s: runs of 3 or more tiles ours %s, theirs %s' % (name, lab2, parts[0], parts[1]))
    say('')
    say('=== 5. compare with rows.jsonl (read last) ===')
    rows = {}
    for ln in Path('data/analysis/ladder/rows.jsonl').read_text().splitlines():
        if ln.strip():
            r = json.loads(ln)
            rows[r['game']] = r
    agree = Counter()
    for g in games:
        r = rows.get(g['game'])
        if r is None:
            agree['missing in rows'] += 1
            continue
        code = r['our_code'] if r['our_code'] in ('main', 'v31') else 'other'
        ok = (code == g['code'] and r['map_key'] == g['map_key'] and r['win'] == g['win'] and r['last_round'] == g['last_round']
              and r['queen']['us']['death_round'] == (g['qdeath'][0]['round'] if g['qdeath'][0] else None)
              and r['queen']['them']['death_round'] == (g['qdeath'][1]['round'] if g['qdeath'][1] else None)
              and r['opponent_rating'] == g.get('opponentElo') and r['opponent_id'] == g.get('opponentId'))
        agree['agree' if ok else 'differ'] += 1
        if not ok and agree['differ'] <= 5:
            say('   differs:', g['game'], code, g['code'], r['map_key'], g['map_key'], r['win'], g['win'])
    say('code, layout, winner, last round, queen death rounds, opponent and rating against rows.jsonl:', dict(agree), 'rows in rows.jsonl', len(rows))
    out = open(P + 'f38-1117-numbers.txt', 'w')
    out.write('\n'.join(LINES) + '\n')
    out.close()


main()
