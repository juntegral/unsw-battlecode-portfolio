#!/usr/bin/env python3
"""Verifier claims 8, extra checks for F35 and F37 (run of 2026-10-07 08:23 KST), from the x8 shards.
Writes f35-f37-extras.txt."""
import sys, json, math
from pathlib import Path
from collections import Counter
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
LINES = []
WIN = ((0, 100), (101, 200), (201, 300), (301, 499))
WN = ('r0-100', 'r101-200', 'r201-300', 'r301-499')
SIDE = ('ours', 'theirs')


def say(*a):
    s = ' '.join(str(x) for x in a)
    LINES.append(s)
    print(s)


def fisher(a, b, c, d):
    n = a + b + c + d
    r1 = a + b
    c1 = a + c
    if n == 0:
        return 1.0

    def pr(x):
        return math.comb(r1, x) * math.comb(n - r1, c1 - x) / math.comb(n, c1)
    p0 = pr(a)
    return sum(pr(x) for x in range(max(0, c1 - (n - r1)), min(r1, c1) + 1) if pr(x) <= p0 * (1 + 1e-9))


def sh(k, n):
    return '%d of %d (%s)' % (k, n, ('%.3f' % (k / n)) if n else '-')


def lone(g, s):
    d = g['d']
    return d[1 - s] is not None and (d[s] is None or d[1 - s] < d[s])


def stratum(g):
    if g['last_round'] < 100:
        return 'ended before r100'
    a, b = g['total'][0][100], g['total'][1][100]
    if min(a, b) >= 0.8 * max(a, b):
        return 'level at r100'
    return 'we are ahead by more' if a > b else 'they are ahead by more'


ST = ('ended before r100', 'we are ahead by more', 'level at r100', 'they are ahead by more')


def main():
    games = []
    for k in range(6):
        for line in (V / ('x8-%d.jsonl' % k)).read_text().splitlines():
            if line.strip():
                games.append(json.loads(line))
    for g in games:
        g['free'] = g['map'] not in ('Schooltime', 'Slithery Fight')
        g['full'] = g['last_round'] == 499
        g['d'] = [q['round'] if q else None for q in g['qdeath']]
    free = [g for g in games if g['free'] and g['code'] in ('main', 'v31')]
    say('Extras for F35 and F37, verifier run 2026-10-07 08:23 KST.')
    say('')
    say('== F35: all free games split by the standing in total length at raw round 100 (level = smaller total at least 0.8 of the larger) ==')
    for c in ('main', 'v31', 'both'):
        gs = [g for g in free if c == 'both' or g['code'] == c]
        num = den = 0.0
        for st in ST:
            ss = [g for g in gs if stratum(g) == st]
            ku = sum(1 for g in ss if lone(g, 0) and g['d'][0] is None)
            nu = sum(1 for g in ss if lone(g, 0))
            kt = sum(1 for g in ss if lone(g, 1) and g['d'][1] is None)
            nt = sum(1 for g in ss if lone(g, 1))
            du = nu - ku
            dt = nt - kt
            tu = sum(g['lone_turns'][0] for g in ss)
            tt = sum(g['lone_turns'][1] for g in ss)
            if tu + tt:
                num += du * tt / (tu + tt)
                den += dt * tu / (tu + tt)
            say('  %-5s %-24s games %3d (full %3d, we won early %3d, they won early %3d)  alive at end: ours %-18s theirs %-18s per 1,000 lone turns: ours %s (%d, %d) theirs %s (%d, %d)' % (
                c, st, len(ss), sum(1 for g in ss if g['full']), sum(1 for g in ss if not g['full'] and g['win']), sum(1 for g in ss if not g['full'] and not g['win']),
                sh(ku, nu), sh(kt, nt), ('%.2f' % (1000 * du / tu)) if tu else '-', du, tu, ('%.2f' % (1000 * dt / tt)) if tt else '-', dt, tt))
        say('  %-5s rate ratio pooled over the four groups (Mantel-Haenszel): %.2f' % (c, num / den if den else float('nan')))
    say('')
    say('== F37: deaths per queen alive at the start of the window, full games ==')
    for c in ('main', 'v31'):
        gs = [g for g in free if g['code'] == c and g['full']]
        for name, test in (('wall or own body', lambda q: q['reason'] in (0, 1)),
                           ('mover with no free tile, any reason', lambda q: q['actor'] and q.get('start_legal') == 0)):
            out = []
            for w in range(4):
                lo, hi = WIN[w]
                kk = []
                for s in (0, 1):
                    n = sum(1 for g in gs if g['d'][s] is None or g['d'][s] >= lo)
                    k = sum(1 for g in gs if g['qdeath'][s] and lo <= g['qdeath'][s]['round'] <= hi and test(g['qdeath'][s]))
                    kk.append((k, n))
                out.append('%s ours %s theirs %s p %.3f' % (WN[w], sh(kk[0][0], kk[0][1]), sh(kk[1][0], kk[1][1]), fisher(kk[0][0], kk[0][1] - kk[0][0], kk[1][0], kk[1][1] - kk[1][0])))
            say('  %s full, %s:' % (c, name))
            for o in out:
                say('      ' + o)
    say('')
    say('== F37: what a queen with no free tile ran into when the engine recorded a head-on or another body (r101-200, games that reached r200) ==')
    for c in ('main', 'v31'):
        for s in (0, 1):
            rc = Counter()
            for g in free:
                if g['code'] != c or g['last_round'] < 200:
                    continue
                q = g['qdeath'][s]
                if q and 101 <= q['round'] <= 200 and q['actor'] and q.get('start_legal') == 0 and q['reason'] in (2, 3) and 'fatal_dir' in q:
                    x = q['start_cls'][q['fatal_dir']]
                    rc[('head-on into ' if q['reason'] == 3 else 'body of ') + ('an enemy' if x[0] in 'EH' else 'her own team')] += 1
            say('  %s %s: %s' % (c, SIDE[s], dict(rc)))
    say('')
    say('== F37: their 16 deaths of the wider set (every free main or v31 game, r101-200, wall or own body) ==')
    for g in sorted(free, key=lambda g: g['game']):
        q = g['qdeath'][1]
        if q and 101 <= q['round'] <= 200 and q['reason'] in (0, 1):
            say('  %d %-16s %-4s r%-3d reason %d  N E S W: %-14s len %d last round %d' % (g['game'], g['map'], g['code'], q['round'], q['reason'], ' '.join(q['start_cls']), q['length'], g['last_round']))
    say('')
    say('== F37: length of the queen at a no-free-tile turn start does not come from the shards; length at death (r101-200, mover with no free tile) ==')
    for c in ('main', 'v31'):
        for s in (0, 1):
            ls = Counter()
            for g in free:
                if g['code'] != c or g['last_round'] < 200:
                    continue
                q = g['qdeath'][s]
                if q and 101 <= q['round'] <= 200 and q['actor'] and q.get('start_legal') == 0:
                    ls[q['length']] += 1
            say('  %s %s: length at death %s (a queen of length 2 or 3 cannot split)' % (c, SIDE[s], dict(sorted(ls.items()))))
    f = open(P + 'f35-f37-extras.txt', 'w')
    f.write('\n'.join(LINES) + '\n')
    f.close()


main()
