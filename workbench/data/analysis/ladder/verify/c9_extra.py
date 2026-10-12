#!/usr/bin/env python3
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
"""Verifier claims 9, extra checks for F38 and F39 (run of 2026-10-07 09:18 KST). Reads the x9 shards and writes
f38-f39-extras.txt."""
import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timedelta
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')
LINES = []
SIDE = ('ours', 'theirs')
WN = ('r0-100', 'r101-200', 'r201-300', 'r301 on')
CUT = datetime.fromisoformat('2026-10-06T14:48:15+00:00')


def say(*a):
    s = ' '.join(str(x) for x in a)
    LINES.append(s)
    print(s)


def load():
    games = []
    for k in range(6):
        for line in (V / ('x9-%d.jsonl' % k)).read_text().splitlines():
            if line.strip():
                games.append(json.loads(line))
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
        g['t'] = datetime.fromisoformat(g['completedAt'][:-1] + '+00:00')
        g['late'] = g['t'] >= CUT
        k9 = g['t'] + timedelta(hours=9)
        g['evening'] = (k9 - timedelta(hours=6)).strftime('%m-%d') + ('a' if k9.hour < 6 or k9.hour >= 18 else 'b')
        g['cl'] = [None, None]
        for s in (0, 1):
            rows = [r for r in g['lone'] if r[0] == s]
            if rows:
                g['cl'][s] = dict(n=len(rows), flag=sum(1 for r in rows if r[2] > 0), own5=sum(r[5] for r in rows),
                                  own_alive=sum(r[6] for r in rows), zero=sum(1 for r in rows if r[5] == 0))
    return order


def T(gs, s, key):
    return sum(g['cl'][s][key] for g in gs if g['cl'][s] is not None)


def fmt(x, d=3):
    return 'none' if x is None else ('%.' + str(d) + 'f') % x


def div(a, b):
    return a / b if b else None


def standard(label, gs, key='flag'):
    lay = sorted(set(g['map_key'] for g in gs))
    a = b = wa = wb = 0.0
    fa = fb = 0.0
    used = []
    for mk in lay:
        sub = [g for g in gs if g['map_key'] == mk]
        n0, n1 = T(sub, 0, 'n'), T(sub, 1, 'n')
        if n0 == 0 or n1 == 0:
            continue
        r0, r1 = T(sub, 0, key) / n0, T(sub, 1, key) / n1
        used.append(mk)
        a += r0 * n1
        fb += r1 * n1
        wb += n1
        b += r1 * n0
        fa += r0 * n0
        wa += n0
    say('  %-22s layouts with lone turns on both sides %2d | on their mix of layouts: ours %s, theirs %s, ratio %s (covers %d of %d of their turns) | on our mix: ours %s, theirs %s, ratio %s (covers %d of %d of our turns)' % (
        label, len(used), fmt(div(a, wb)), fmt(div(fb, wb)), fmt(div(a, fb), 2), wb, T(gs, 1, 'n'), fmt(div(fa, wa)), fmt(div(b, wa)), fmt(div(fa, b), 2), wa, T(gs, 0, 'n')))


def shuffle_test(gs, key, n=10000, seed=4):
    cs0 = [g['cl'][0] for g in gs if g['cl'][0] is not None]
    cs1 = [g['cl'][1] for g in gs if g['cl'][1] is not None]
    allc = [(c[key], c['n']) for c in cs0 + cs1]
    k = len(cs0)

    def stat(lst):
        na = sum(x[1] for x in lst[:k])
        nb = sum(x[1] for x in lst[k:])
        return sum(x[0] for x in lst[:k]) / na - sum(x[0] for x in lst[k:]) / nb
    obs = stat(allc)
    rng = random.Random(seed)
    le = 0
    lst = list(allc)
    for _ in range(n):
        rng.shuffle(lst)
        if stat(lst) <= obs + 1e-12:
            le += 1
    return obs, le, n


def main():
    games = load()
    F = [g for g in games if g['code'] in ('main', 'v31') and g['free']]
    M = [g for g in F if g['code'] == 'main']
    O = [g for g in F if g['code'] == 'v31']
    sets = (('main full', [g for g in M if g['full']]), ('v31 full', [g for g in O if g['full']]), ('main all endings', M), ('v31 all endings', O),
            ('main level', [g for g in M if g['level']]), ('v31 level', [g for g in O if g['level']]))
    say('== F39: the flagged share with the layout mix held equal ==')
    for label, gs in sets:
        standard(label, gs)
    say('')
    say('== F39: without Portals #1 (two kelp-sealed halves) ==')
    for label, gs in sets:
        sub = [g for g in gs if g['map_key'] != 'Portals #1']
        n0, n1 = T(sub, 0, 'n'), T(sub, 1, 'n')
        say('  %-18s flagged ours %s of %d, theirs %s of %d, ratio %s | own heads within 5: %.2f against %.2f' % (
            label, fmt(div(T(sub, 0, 'flag'), n0)), n0, fmt(div(T(sub, 1, 'flag'), n1)), n1, fmt(div(div(T(sub, 0, 'flag'), n0), div(T(sub, 1, 'flag'), n1)), 2),
            T(sub, 0, 'own5') / n0, T(sub, 1, 'own5') / n1))
    P1 = [g for g in F if g['map_key'] == 'Portals #1']
    say('  Portals #1 itself: lone turns ours %d (flagged %d), theirs %d (flagged %d); with both queens alive: turns %d and %d, flagged %d and %d; short enemy heads within 6 in any turn: %d' % (
        T(P1, 0, 'n'), T(P1, 0, 'flag'), T(P1, 1, 'n'), T(P1, 1, 'flag'),
        sum(g['base'][0][w][0] for g in P1 for w in range(4)), sum(g['base'][1][w][0] for g in P1 for w in range(4)),
        sum(g['base'][0][w][1] for g in P1 for w in range(4)), sum(g['base'][1][w][1] for g in P1 for w in range(4)),
        sum(g['base'][s][w][4] for g in P1 for w in range(4) for s in (0, 1)) + sum(r[2] for g in P1 for r in g['lone'])))
    say('  other layouts where the flag never fires for either side in any queen turn:',
        [mk for mk in sorted(set(g['map_key'] for g in F)) if sum(g['base'][s][w][1] for g in F if g['map_key'] == mk for w in range(4) for s in (0, 1)) + sum(1 for g in F if g['map_key'] == mk for r in g['lone'] if r[2] > 0) == 0])
    say('')
    say('== F39: by evening, both codes (KST day, a = 18h to 06h, b = 06h to 18h) ==')
    for label, gs in (('full games', [g for g in F if g['full']]), ('all endings', F)):
        for ev in sorted(set(g['evening'] for g in gs)):
            sub = [g for g in gs if g['evening'] == ev]
            n0, n1 = T(sub, 0, 'n'), T(sub, 1, 'n')
            say('  %-12s %s games %3d | ours %s of %d ; theirs %s of %d | ratio %s' % (label, ev, len(sub), fmt(div(T(sub, 0, 'flag'), n0)), n0, fmt(div(T(sub, 1, 'flag'), n1)), n1,
                                                                             fmt(div(div(T(sub, 0, 'flag'), n0) or 0, div(T(sub, 1, 'flag'), n1)), 2)))
    say('  main full, before and from 2026-10-06T14:48:15Z:')
    for late in (False, True):
        sub = [g for g in M if g['full'] and g['late'] == late]
        n0, n1 = T(sub, 0, 'n'), T(sub, 1, 'n')
        say('     %s: games %d | ours %s of %d ; theirs %s of %d | ratio %s | own heads within 5 %.2f against %.2f' % ('from' if late else 'before', len(sub), fmt(div(T(sub, 0, 'flag'), n0)), n0, fmt(div(T(sub, 1, 'flag'), n1)), n1,
              fmt(div(div(T(sub, 0, 'flag'), n0) or 0, div(T(sub, 1, 'flag'), n1)), 2), T(sub, 0, 'own5') / n0, T(sub, 1, 'own5') / n1))
    say('')
    say('== F39: own heads within 5, chance and layout mix ==')
    for label, gs in sets:
        obs, le, n = shuffle_test(gs, 'own5')
        say('  %-18s mean ours minus theirs %.2f; label shuffle over games: %d of %d shuffles at least as far below' % (label, obs, le, n))
        standard(label + ' own5', gs, key='own5')
    say('')
    say('== F39: base rate to four places ==')
    for label, gs in (('main all endings', M), ('v31 all endings', O)):
        parts = []
        for w in range(4):
            x = []
            for s in (0, 1):
                n = sum(g['base'][s][w][0] for g in gs)
                f = sum(g['base'][s][w][1] for g in gs)
                x.append('%.4f (%d of %d)' % (f / n, f, n))
            parts.append('%s %s against %s' % (WN[w], x[0], x[1]))
        say('  %-17s %s' % (label, ' | '.join(parts)))
    say('')
    say('== F38: mover deaths from a narrow tile in r101-200 by engine reason and by legal first steps at the turn start ==')
    for s in (0, 1):
        tab = Counter()
        for g in F:
            d = g['qdeath'][s]
            if d is None or not d['actor'] or d['round'] < 101 or d['round'] > 200 or d['start_open'] > 2:
                continue
            tab[(d['reason'], d['start_legal'])] += 1
        say('  %s: (reason, legal first steps) -> deaths %s' % (SIDE[s], dict(sorted(tab.items()))))
    say('  queen deaths in r101-200 while standing (not the mover), last turn start on a narrow tile:')
    for s in (0, 1):
        tab = Counter()
        for g in F:
            d = g['qdeath'][s]
            if d is None or d['actor'] or d['round'] < 101 or d['round'] > 200 or d.get('start_open', 9) > 2:
                continue
            tab[d['reason']] += 1
        say('     %s: by reason %s' % (SIDE[s], dict(sorted(tab.items()))))
    say('== F38: all rounds together, wall or own-body deaths from a narrow tile per narrow turn start ==')
    for label, gs in (('main', M), ('v31', O), ('pooled', F)):
        parts = []
        res = []
        for s in (0, 1):
            k = 0
            for g in gs:
                d = g['qdeath'][s]
                if d is not None and d['reason'] in (0, 1) and d['start_open'] <= 2:
                    k += 1
            nt = 0
            for g in gs:
                for w in range(4):
                    for key, c in g['hist'][s][w].items():
                        if int(key.split(',')[0]) <= 2:
                            nt += c
            res.append((k, nt))
            parts.append('%s %d in %d (%.1f per 1,000)' % (SIDE[s], k, nt, 1000.0 * k / nt))
        say('  %-7s %s | ratio %.2f' % (label, ' ; '.join(parts), (res[0][0] / res[0][1]) / (res[1][0] / res[1][1])))
    say('== F38: narrow share r0-200 on the five layouts where ours is far higher, and on the rest ==')
    five = ('Maze #1', 'weakhold #1', 'Portals #1', 'Prisoners Dilemma #1', 'Prisoners Dilemma #2')
    for label, gs in (('the five', [g for g in F if g['map_key'] in five]), ('the other eleven', [g for g in F if g['map_key'] not in five])):
        x = []
        for s in (0, 1):
            a = b = 0
            for g in gs:
                for w in (0, 1):
                    for key, c in g['hist'][s][w].items():
                        b += c
                        if int(key.split(',')[0]) <= 2:
                            a += c
            x.append((a, b))
        say('  %-17s games %d | ours %.3f of %d ; theirs %.3f of %d' % (label, len(gs), x[0][0] / x[0][1], x[0][1], x[1][0] / x[1][1], x[1][1]))
    Path(P + 'f38-f39-extras.txt').write_text('\n'.join(LINES) + '\n')


main()
