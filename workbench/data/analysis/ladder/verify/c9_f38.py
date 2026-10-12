#!/usr/bin/env python3
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
"""Verifier claims 9 (run of 2026-10-07 09:18 KST), F38: narrow tiles under the queen. Reads the x9 shards (own
extraction from the raw replays) and writes f38-numbers.txt. maps.json is read for the free-layout flag and the
corridor share; rows.jsonl is read only in the last section, to compare."""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timedelta
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')
LINES = []
SIDE = ('ours', 'theirs')
CUT = datetime.fromisoformat('2026-10-06T14:48:15+00:00')


def say(*a):
    s = ' '.join(str(x) for x in a)
    LINES.append(s)
    print(s)


def when(z):
    return datetime.fromisoformat(z[:-1] + '+00:00')


def load():
    games = []
    for k in range(6):
        for line in (V / ('x9-%d.jsonl' % k)).read_text().splitlines():
            if line.strip():
                games.append(json.loads(line))
    bad = [g for g in games if 'error' in g]
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
        g['corridor'] = maps[g['map_key']]['corridor_share']
        g['t'] = when(g['completedAt'])
        g['late'] = g['t'] >= CUT
        g['evening'] = (g['t'] + timedelta(hours=9) - timedelta(hours=6)).strftime('%m-%d') + ('a' if (g['t'] + timedelta(hours=9)).hour < 6 or (g['t'] + timedelta(hours=9)).hour >= 18 else 'b')
    return order, bad, maps


def cnt(g, s, ws, lo, hi, beside=None, legal=None):
    """queen turn starts of side s in windows ws on a tile with lo..hi open sides"""
    n = 0
    for w in ws:
        for key, c in g['hist'][s][w].items():
            o, b, l = (int(x) for x in key.split(','))
            if o < lo or o > hi:
                continue
            if beside is not None and b != beside:
                continue
            if legal is not None and l != legal:
                continue
            n += c
    return n


def death(g, s, reasons=(0, 1), lo=101, hi=200):
    d = g['qdeath'][s]
    if d is None or d['reason'] not in reasons or d['round'] < lo or d['round'] > hi:
        return None
    return d


def rate(k, n):
    return '%d in %d (%.1f per 1,000)' % (k, n, 1000.0 * k / n) if n else '%d in 0' % k


def share(k, n):
    return '%.3f of %d' % (k / n, n) if n else 'none of 0'


def wilson(k, n):
    if n == 0:
        return (0.0, 1.0)
    z = 1.96
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def pooled(games):
    """narrow turn starts r101-200 and wall / own-body deaths from a narrow tile, both sides"""
    out = []
    for s in (0, 1):
        n = sum(cnt(g, s, (1,), 0, 2) for g in games)
        k = 0
        for g in games:
            d = death(g, s)
            if d is not None and d['start_open'] <= 2:
                k += 1
        out.append((k, n))
    return out


def ratio(pp):
    (k0, n0), (k1, n1) = pp
    if n0 == 0 or n1 == 0:
        return None
    a, b = k0 / n0, k1 / n1
    if b == 0:
        return float('inf') if a > 0 else None
    return a / b


def fmt_ratio(r):
    return 'none' if r is None else 'inf' if r == float('inf') else '%.2f' % r


def swap_test(games, n=20000, seed=11):
    """side-swap permutation: in each game the two queens trade labels with probability one half. Statistic: our
    deaths per narrow turn minus theirs. Returns the share of permutations at least as large as observed."""
    rows = []
    for g in games:
        r = []
        for s in (0, 1):
            d = death(g, s)
            r.append((1 if d is not None and d['start_open'] <= 2 else 0, cnt(g, s, (1,), 0, 2)))
        if r[0][1] or r[1][1] or r[0][0] or r[1][0]:
            rows.append(r)

    def stat(flips):
        k = [0, 0]
        m = [0, 0]
        for r, f in zip(rows, flips):
            a, b = (r[1], r[0]) if f else (r[0], r[1])
            k[0] += a[0]
            m[0] += a[1]
            k[1] += b[0]
            m[1] += b[1]
        if m[0] == 0 or m[1] == 0:
            return 0.0
        return k[0] / m[0] - k[1] / m[1]
    obs = stat([0] * len(rows))
    rng = random.Random(seed)
    ge = 0
    for _ in range(n):
        if stat([rng.random() < 0.5 for _ in rows]) >= obs - 1e-12:
            ge += 1
    return obs, ge, n


def boot(games, n=4000, seed=5):
    """resample battles with replacement; ratio of our per-narrow-turn death rate to theirs"""
    by = defaultdict(list)
    for g in games:
        by[g['battle']].append(g)
    keys = sorted(by)
    pre = {}
    for b in keys:
        pp = pooled(by[b])
        pre[b] = pp
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        k0 = n0 = k1 = n1 = 0
        for _ in keys:
            pp = pre[keys[rng.randrange(len(keys))]]
            k0 += pp[0][0]
            n0 += pp[0][1]
            k1 += pp[1][0]
            n1 += pp[1][1]
        r = ratio(((k0, n0), (k1, n1)))
        vals.append(float('inf') if r is None else r)
    vals.sort()
    return vals[int(0.025 * n)], vals[int(0.5 * n)], vals[int(0.975 * n) - 1]


def share_boot(games, n=3000, seed=7):
    """resample games; ratio of our narrow share r0-200 to theirs"""
    pre = []
    for g in games:
        pre.append((cnt(g, 0, (0, 1), 0, 2), cnt(g, 0, (0, 1), 0, 4), cnt(g, 1, (0, 1), 0, 2), cnt(g, 1, (0, 1), 0, 4)))
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        a = b = c = d = 0
        for _ in pre:
            x = pre[rng.randrange(len(pre))]
            a += x[0]
            b += x[1]
            c += x[2]
            d += x[3]
        if b and d and c:
            vals.append((a / b) / (c / d))
        else:
            vals.append(float('inf'))
    vals.sort()
    return vals[int(0.025 * n)], vals[int(0.975 * n) - 1]


def main():
    games, bad, maps = load()
    say('games loaded', len(games), 'errors', len(bad))
    say('codes:', dict(Counter(g['code'] for g in games)), '| bot ids:', dict(Counter(g['code'] + ' ' + g['bot'] for g in games)))
    say('rebuild checks: final state differs from result block in', sum(1 for g in games if not g['final_ok']),
        '| owner map differs in', sum(1 for g in games if not g['own_ok']), '| anomalies',
        dict(sum((Counter(g['anomalies']) for g in games), Counter())), '| unfollowable portals', sum(g['bad_portals'] for g in games))
    F = [g for g in games if g['code'] in ('main', 'v31') and g['free']]
    M = [g for g in F if g['code'] == 'main']
    O = [g for g in F if g['code'] == 'v31']
    say('free main games', len(M), '(before the cut', sum(1 for g in M if not g['late']), ', from the cut', sum(1 for g in M if g['late']), ') free v31 games', len(O))
    say('layouts not free:', sorted(set(g['map_key'] for g in games if not g['free'])))
    say('')
    say('== (1) share of queen turn starts on a narrow tile (2 or fewer open sides), r0-200 ==')

    def sh(gs, s, ws=(0, 1)):
        return sum(cnt(g, s, ws, 0, 2) for g in gs), sum(cnt(g, s, ws, 0, 4) for g in gs)

    def line(label, gs):
        a, b = sh(gs, 0)
        c, d = sh(gs, 1)
        r = (a / b) / (c / d) if b and d and c else None
        more = sum(1 for g in gs if cnt(g, 0, (0, 1), 0, 4) and cnt(g, 1, (0, 1), 0, 4) and cnt(g, 0, (0, 1), 0, 2) / cnt(g, 0, (0, 1), 0, 4) > cnt(g, 1, (0, 1), 0, 2) / cnt(g, 1, (0, 1), 0, 4))
        less = sum(1 for g in gs if cnt(g, 0, (0, 1), 0, 4) and cnt(g, 1, (0, 1), 0, 4) and cnt(g, 0, (0, 1), 0, 2) / cnt(g, 0, (0, 1), 0, 4) < cnt(g, 1, (0, 1), 0, 2) / cnt(g, 1, (0, 1), 0, 4))
        say('%-46s games %3d | ours %s | theirs %s | ratio %s | games ours higher %d, theirs higher %d' % (label, len(gs), share(a, b), share(c, d), fmt_ratio(r), more, less))
        return r
    for code, gs in (('main', M), ('v31', O)):
        for mk in ('Maze #1', 'weakhold #1'):
            sub = [g for g in gs if g['map_key'] == mk]
            line(code + ' ' + mk, sub)
            lo, hi = share_boot(sub)
            say('     game bootstrap of the ratio, 95 percent: %s to %s' % (fmt_ratio(lo), fmt_ratio(hi)))
    three = [g for g in F if g['map_key'] in ('Tower Defense #1', 'Trauma #1', 'Devil #1')]
    line('Tower Defense, Trauma, Devil, both codes', three)
    line('  of which main', [g for g in three if g['code'] == 'main'])
    line('  of which v31', [g for g in three if g['code'] == 'v31'])
    line('all free main', M)
    line('all free v31', O)
    say('')
    say('per layout, both codes (corridor share from maps.json; narrow tiles of the layout = tiles with 1 or 2 open sides / tiles with any):')
    for mk in sorted(set(g['map_key'] for g in F), key=lambda k: -maps[k]['corridor_share']):
        sub = [g for g in F if g['map_key'] == mk]
        tb = sub[0]['tiles_by_open']
        say('  corridor %.2f, narrow tiles %.2f (dead-end tiles %d):' % (maps[mk]['corridor_share'], (tb[1] + tb[2]) / sum(tb[1:]), tb[1]))
        line('    ' + mk, sub)
        line('      main', [g for g in sub if g['code'] == 'main'])
        line('      v31', [g for g in sub if g['code'] == 'v31'])
    say('')
    say('Maze and weakhold by opponent band, both codes pooled:')
    for mk in ('Maze #1', 'weakhold #1'):
        for band in ('<1700', '1700-1899', '1900-2099', '2100+'):
            sub = [g for g in F if g['map_key'] == mk and g['band'] == band]
            if sub:
                line('  %s %s' % (mk, band), sub)
    say('Maze and weakhold, the three games with most of our narrow turns removed, per code:')
    for code, gs in (('main', M), ('v31', O)):
        for mk in ('Maze #1', 'weakhold #1'):
            sub = sorted([g for g in gs if g['map_key'] == mk], key=lambda g: -cnt(g, 0, (0, 1), 0, 2))
            say('   removed', [(g['game'], cnt(g, 0, (0, 1), 0, 2)) for g in sub[:3]])
            line('  %s %s without them' % (code, mk), sub[3:])
    say('Maze and weakhold by window, both codes: share narrow ours / theirs')
    for mk in ('Maze #1', 'weakhold #1'):
        sub = [g for g in F if g['map_key'] == mk]
        parts = []
        for w, wn in enumerate(('r0-100', 'r101-200', 'r201-300', 'r301 on')):
            a, b = sh(sub, 0, (w,))
            c, d = sh(sub, 1, (w,))
            parts.append('%s %s / %s' % (wn, share(a, b), share(c, d)))
        say('  ', mk, ' | '.join(parts))
    say('Maze and weakhold: one opponent left out at a time, both codes, range of the ratio')
    for mk in ('Maze #1', 'weakhold #1'):
        sub = [g for g in F if g['map_key'] == mk]
        rs = []
        for opp in sorted(set(g['opponentId'] for g in sub)):
            rest = [g for g in sub if g['opponentId'] != opp]
            a, b = sh(rest, 0)
            c, d = sh(rest, 1)
            rs.append(((a / b) / (c / d), opp, sum(1 for g in sub if g['opponentId'] == opp)))
        rs.sort()
        say('  ', mk, 'opponents', len(rs), 'lowest %.2f (without %s, %d games) highest %.2f (without %s, %d games)' % (rs[0][0], rs[0][1], rs[0][2], rs[-1][0], rs[-1][1], rs[-1][2]))

    say('')
    say('== (2) queen deaths by wall (0) or own body (1) in r101-200, by the open sides of her head tile at the start of her last turn ==')

    def deaths_table(label, gs):
        out = {}
        for s in (0, 1):
            ds = [death(g, s) for g in gs]
            ds = [d for d in ds if d is not None]
            nar = [d for d in ds if d['start_open'] <= 2]
            nt = sum(cnt(g, s, (1,), 0, 2) for g in gs)
            ot = sum(cnt(g, s, (1,), 3, 4) for g in gs)
            out[s] = (len(ds), len(nar), nt, ot)
            say('%-34s %-6s deaths %2d (wall %d, own body %d; as the mover %d) | from a narrow tile %s | from an open tile %s | open sides at start %s' % (
                label, SIDE[s], len(ds), sum(1 for d in ds if d['reason'] == 0), sum(1 for d in ds if d['reason'] == 1), sum(1 for d in ds if d['actor']),
                rate(len(nar), nt), rate(len(ds) - len(nar), ot), dict(sorted(Counter(d['start_open'] for d in ds).items()))))
        r = ratio(((out[0][1], out[0][2]), (out[1][1], out[1][2])))
        say('%-34s ratio of the per-narrow-turn rates %s' % (label, fmt_ratio(r)))
        return out
    deaths_table('main', M)
    deaths_table('v31', O)
    deaths_table('pooled', F)
    deaths_table('main before 10-06T14:48:15Z', [g for g in M if not g['late']])
    deaths_table('main from 10-06T14:48:15Z', [g for g in M if g['late']])
    NP = [g for g in F if g['map_key'] != 'Portals #1']
    deaths_table('pooled without Portals', NP)
    deaths_table('main without Portals', [g for g in M if g['map_key'] != 'Portals #1'])
    deaths_table('v31 without Portals', [g for g in O if g['map_key'] != 'Portals #1'])
    deaths_table('pooled without Maze', [g for g in F if g['map_key'] != 'Maze #1'])
    deaths_table('pooled without Maze, Portals, weakhold', [g for g in F if g['map_key'] not in ('Maze #1', 'Portals #1', 'weakhold #1')])
    say('')
    say('where the fatal step went (head at the fatal step differs from the head at the turn start in',
        sum(1 for g in F for s in (0, 1) if death(g, s) is not None and death(g, s)['start_head'] != death(g, s)['now_head']), 'of',
        sum(1 for g in F for s in (0, 1) if death(g, s) is not None), 'deaths)')
    say('legal first steps at the start of the fatal turn, ours:', dict(Counter(death(g, 0)['start_legal'] for g in F if death(g, 0) is not None)),
        'theirs:', dict(Counter(death(g, 1)['start_legal'] for g in F if death(g, 1) is not None)))
    say('')
    say('chance:')
    for label, gs in (('main', M), ('v31', O), ('pooled', F), ('pooled without Portals', NP)):
        obs, ge, n = swap_test(gs)
        lo, mid, hi = boot(gs)
        say('  %-24s side-swap permutation: observed difference %.4f per narrow turn, %d of %d permutations at least as large | battle bootstrap of the ratio: %s to %s (median %s)' % (label, obs, ge, n, fmt_ratio(lo), fmt_ratio(hi), fmt_ratio(mid)))
    say('')
    say('per layout, pooled codes: deaths from a narrow tile / narrow turn starts r101-200 (ours ; theirs)')
    for mk in sorted(set(g['map_key'] for g in F)):
        sub = [g for g in F if g['map_key'] == mk]
        pp = pooled(sub)
        say('  %-22s games %3d | ours %s ; theirs %s' % (mk, len(sub), rate(*pp[0]), rate(*pp[1])))
    say('one layout left out at a time, pooled: range of the ratio')
    rs = []
    for mk in sorted(set(g['map_key'] for g in F)):
        rs.append((ratio(pooled([g for g in F if g['map_key'] != mk])), mk))
    rs.sort()
    say('   lowest %s (without %s), highest %s (without %s)' % (fmt_ratio(rs[0][0]), rs[0][1], fmt_ratio(rs[-1][0]), rs[-1][1]))
    say('per opponent with at least one such death of ours or theirs, pooled codes:')
    opps = defaultdict(list)
    for g in F:
        opps[(g['opponentId'], g['opponent'])].append(g)
    tab = []
    for key, sub in opps.items():
        pp = pooled(sub)
        tab.append((pp[0][0], key, len(sub), pp))
    tab.sort(key=lambda x: (-x[0], -x[3][1][0]))
    for k0, key, n, pp in tab:
        if pp[0][0] or pp[1][0]:
            say('   %-28s games %3d | ours %s ; theirs %s' % (str(key[0]) + ' ' + key[1][:18], n, rate(*pp[0]), rate(*pp[1])))
    say('opponents:', len(tab), '| with a death of ours:', sum(1 for x in tab if x[0]), '| largest share of our deaths from one opponent: %d of %d' % (tab[0][0], sum(x[0] for x in tab)))
    rs = []
    for key in opps:
        rs.append((ratio(pooled([g for g in F if g['opponentId'] != key[0]])), key))
    rs.sort(key=lambda x: x[0])
    say('one opponent left out at a time, pooled: ratio lowest %s (without %s), highest %s (without %s)' % (fmt_ratio(rs[0][0]), rs[0][1][0], fmt_ratio(rs[-1][0]), rs[-1][1][0]))
    for code, gs in (('main', M), ('v31', O)):
        rs = []
        for key in set((g['opponentId'], g['opponent']) for g in gs):
            rs.append((ratio(pooled([g for g in gs if g['opponentId'] != key[0]])), key))
        rs.sort(key=lambda x: x[0])
        say('   %s alone: lowest %s (without %s), highest %s (without %s)' % (code, fmt_ratio(rs[0][0]), rs[0][1][0], fmt_ratio(rs[-1][0]), rs[-1][1][0]))
    say('by opponent band, pooled codes:')
    for band in ('<1700', '1700-1899', '1900-2099', '2100+'):
        sub = [g for g in F if g['band'] == band]
        if sub:
            pp = pooled(sub)
            say('   %-10s games %3d | ours %s ; theirs %s | ratio %s' % (band, len(sub), rate(*pp[0]), rate(*pp[1]), fmt_ratio(ratio(pp))))
    say('by evening (KST day, a = 18h to 06h, b = 06h to 18h), pooled codes:')
    for ev in sorted(set(g['evening'] for g in F)):
        sub = [g for g in F if g['evening'] == ev]
        pp = pooled(sub)
        say('   %-8s games %3d (main %d) | ours %s ; theirs %s | ratio %s' % (ev, len(sub), sum(1 for g in sub if g['code'] == 'main'), rate(*pp[0]), rate(*pp[1]), fmt_ratio(ratio(pp))))
    say('')
    say('plainer counts of the same deaths:')
    for label, gs in (('main', M), ('v31', O), ('pooled', F)):
        parts = []
        for s in (0, 1):
            reach = sum(1 for g in gs if g['last_round'] >= 101 and (g['qdeath'][s] is None or g['qdeath'][s]['round'] >= 101))
            withn = sum(1 for g in gs if cnt(g, s, (1,), 0, 2) > 0)
            ep = sum(g['episodes'][s][1] for g in gs)
            k = sum(1 for g in gs if death(g, s) is not None and death(g, s)['start_open'] <= 2)
            parts.append('%s: %d deaths; queens alive at r101 %d (%.3f); games with a narrow turn in the window %d (%.3f); narrow episodes %d (%.1f per 1,000 episodes); narrow turns per episode %.1f' % (
                SIDE[s], k, reach, k / reach if reach else 0, withn, k / withn if withn else 0, ep, 1000.0 * k / ep if ep else 0, sum(cnt(g, s, (1,), 0, 2) for g in gs) / ep if ep else 0))
        say('  ', label, '|', ' || '.join(parts))
    say('every queen death as the mover from a narrow tile in r101-200, whatever the engine reason (0 wall, 1 own body, 2 other body, 3 head-on, 4 no action):')
    for label, gs in (('main', M), ('v31', O), ('pooled', F)):
        parts = []
        res = []
        for s in (0, 1):
            ds = [death(g, s, reasons=(0, 1, 2, 3, 4)) for g in gs]
            ds = [d for d in ds if d is not None and d['actor'] and d['start_open'] <= 2]
            nt = sum(cnt(g, s, (1,), 0, 2) for g in gs)
            res.append((len(ds), nt))
            parts.append('%s %s, reasons %s, hit side for reason 2 %s' % (SIDE[s], rate(len(ds), nt), dict(sorted(Counter(d['reason'] for d in ds).items())),
                                                           dict(Counter(('own' if d.get('hit_side') == s else 'enemy' if d.get('hit_side') == 1 - s else 'unknown') for d in ds if d['reason'] == 2))))
        say('  ', label, '|', ' || '.join(parts), '| ratio', fmt_ratio(ratio(res)))
    say('narrow turn starts r101-200 with no legal first step (no free neighbour tile):')
    for label, gs in (('main', M), ('v31', O), ('pooled', F)):
        parts = []
        for s in (0, 1):
            z = sum(cnt(g, s, (1,), 0, 2, legal=0) for g in gs)
            nt = sum(cnt(g, s, (1,), 0, 2) for g in gs)
            parts.append('%s %d of %d narrow turns (%.3f)' % (SIDE[s], z, nt, z / nt if nt else 0))
        say('  ', label, '|', ' ; '.join(parts))
    say('turn starts on a dead-end tile (one open side) r101-200, and wall / own-body deaths from one:')
    for label, gs in (('main', M), ('v31', O), ('pooled', F)):
        parts = []
        for s in (0, 1):
            z = sum(cnt(g, s, (1,), 0, 1) for g in gs)
            k = sum(1 for g in gs if death(g, s) is not None and death(g, s)['start_open'] <= 1)
            parts.append('%s %d turn starts, %d deaths' % (SIDE[s], z, k))
        say('  ', label, '|', ' ; '.join(parts))

    say('')
    say('== (3) an own dragon beside her (a body tile of another dragon of her team across an open side) ==')
    for label, gs in (('main', M), ('v31', O), ('pooled', F), ('pooled without Portals', NP)):
        parts = []
        for s in (0, 1):
            nb = sum(cnt(g, s, (1,), 0, 2, beside=1) for g in gs)
            nt = sum(cnt(g, s, (1,), 0, 2) for g in gs)
            ds = [death(g, s) for g in gs]
            ds = [d for d in ds if d is not None and d['start_open'] <= 2]
            both = sum(1 for d in ds if d['start_beside'] and d['start_open'] == 1)
            bes = sum(1 for d in ds if d['start_beside'])
            de = sum(1 for d in ds if d['start_open'] == 1)
            oth = sum(1 for d in ds if not d['start_beside'] and d['start_open'] != 1)
            parts.append('%s: narrow turn starts with an own dragon beside %d of %d; deaths from a narrow tile %d: own dragon beside %d, dead-end tile %d, both %d, neither %d' % (
                SIDE[s], nb, nt, len(ds), bes, de, both, oth))
        say('  ', label, '|', ' || '.join(parts))
    say('open-tile turn starts r101-200 with an own dragon beside her, for scale:')
    for label, gs in (('main', M), ('v31', O)):
        parts = []
        for s in (0, 1):
            nb = sum(cnt(g, s, (1,), 3, 4, beside=1) for g in gs)
            nt = sum(cnt(g, s, (1,), 3, 4) for g in gs)
            parts.append('%s %d of %d (%.4f)' % (SIDE[s], nb, nt, nb / nt if nt else 0))
        say('  ', label, '|', ' ; '.join(parts))
    say('the fatal turns of ours from a narrow tile, what stood on each open side at the turn start (K kelp, F free, T own tail, S own body, C child, M team mate, H enemy head, E enemy body; h = that dragon head, p = through a portal):')
    pat = Counter()
    for g in F:
        d = death(g, 0)
        if d is not None and d['start_open'] <= 2:
            pat[' '.join(sorted(c for c in d['start_cls'] if c != 'K'))] += 1
    say('   ours:', dict(pat.most_common()))
    pat = Counter()
    for g in F:
        d = death(g, 1)
        if d is not None and d['start_open'] <= 2:
            pat[' '.join(sorted(c for c in d['start_cls'] if c != 'K'))] += 1
    say('   theirs:', dict(pat.most_common()))
    say('own dragon beside her at the fatal turn start: is it her own child?')
    for s in (0, 1):
        ds = [death(g, s) for g in F]
        ds = [d for d in ds if d is not None and d['start_open'] <= 2 and d['start_beside']]
        say('   %s: %d deaths, a direct child of hers beside in %d, another team mate only in %d' % (SIDE[s], len(ds), sum(1 for d in ds if any(c[0] == 'C' for c in d['start_cls'])), sum(1 for d in ds if not any(c[0] == 'C' for c in d['start_cls']))))

    say('')
    say('== other numbers in the queue ==')
    for s in (0, 1):
        ds = [death(g, s, lo=0, hi=9999) for g in M]
        ds = [d for d in ds if d is not None]
        say('all rounds, main, wall or own-body queen deaths %s: %d, from a narrow tile %d, from a dead-end tile %d' % (SIDE[s], len(ds), sum(1 for d in ds if d['start_open'] <= 2), sum(1 for d in ds if d['start_open'] == 1)))
    for s in (0, 1):
        ds = [death(g, s, lo=0, hi=9999) for g in O]
        ds = [d for d in ds if d is not None]
        say('all rounds, v31, wall or own-body queen deaths %s: %d, from a narrow tile %d' % (SIDE[s], len(ds), sum(1 for d in ds if d['start_open'] <= 2)))
    for label, gs in (('main', M), ('v31', O)):
        sub = [g for g in gs if death(g, 0) is not None and death(g, 0)['start_open'] <= 2]
        rest = [g for g in gs if g not in sub and g['last_round'] >= 101]
        say('games with such a death of ours (narrow tile, r101-200) %s: %d, won %d | other games that reached r101: %d, won %d' % (label, len(sub), sum(1 for g in sub if g['win']), len(rest), sum(1 for g in rest if g['win'])))
        sub2 = [g for g in gs if death(g, 0) is not None]
        say('   counting every wall or own-body death in the window: %d games, won %d' % (len(sub2), sum(1 for g in sub2 if g['win'])))
    say('by window, pooled codes: wall or own-body deaths from a narrow tile / narrow turn starts (ours ; theirs)')
    for w, (lo, hi, wn) in enumerate(((0, 100, 'r0-100'), (101, 200, 'r101-200'), (201, 300, 'r201-300'), (301, 9999, 'r301 on'))):
        for label, gs in (('main', M), ('v31', O)):
            parts = []
            for s in (0, 1):
                k = sum(1 for g in gs if death(g, s, lo=lo, hi=hi) is not None and death(g, s, lo=lo, hi=hi)['start_open'] <= 2)
                nt = sum(cnt(g, s, (w,), 0, 2) for g in gs)
                parts.append(rate(k, nt))
            say('   %-9s %-5s %s ; %s' % (wn, label, parts[0], parts[1]))

    say('')
    say('== comparison with rows.jsonl (read only here) ==')
    rows = {}
    for line_ in Path('data/analysis/ladder/rows.jsonl').read_text().splitlines():
        if line_.strip():
            r = json.loads(line_)
            rows[r['game']] = r
    mine = {g['game']: g for g in games}
    say('games: mine %d, rows.jsonl %d, in both %d' % (len(mine), len(rows), len(set(mine).intersection(rows))))
    diff = Counter()
    for gid, g in mine.items():
        r = rows.get(gid)
        if r is None:
            continue
        rc = r['our_code'] if r['our_code'] in ('main', 'v31') else 'other'
        if rc != g['code']:
            diff['code'] += 1
        if r['map_key'] != g['map_key']:
            diff['map_key'] += 1
        if r['win'] != g['win']:
            diff['win'] += 1
        if r['last_round'] != g['last_round']:
            diff['last_round'] += 1
        for s, sn in ((0, 'us'), (1, 'them')):
            d = g['qdeath'][s]
            q = r['queen'][sn]
            if (d['round'] if d else None) != q['death_round']:
                diff['queen death round'] += 1
            cause = ('wall', 'own body', 'other dragon body', 'head-on', 'other')[d['reason']] if d else 'none'
            if cause != q['death_cause']:
                diff['queen death cause'] += 1
    say('differences:', dict(diff) if diff else 'none')
    Path(P + 'f38-numbers.txt').write_text('\n'.join(LINES) + '\n')


main()
