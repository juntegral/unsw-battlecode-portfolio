# Scratch (diag-spawn): tables from sp_f-*.jsonl (or sp_test.jsonl with the argument "test").
# Every rate is printed as: pooled O, pooled R, equal-layout mean O, equal-layout mean R, layouts where R is higher / valid.
# O = meow as focal side in its 500 ladder games; R = rank-1 as focal side in its 597 games.
# Side "F" = the focal team, "X" = its opponents. Windows: a = rounds 0-100, b = rounds 101-300.
# Usage: python3 data/analysis/ladder/dossier/work/sp_agg.py [test]
import sys, json
sys.dont_write_bytecode = True
from collections import Counter, defaultdict
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
GROUPS = {'every': (0,), 'fast': (1, 2), 'mid': (3,), 'slow': (4,), 'rare': (5,), 'all': (0, 1, 2, 3, 4, 5), 'e+f': (0, 1, 2)}
CG = {0: ('every', 'e+f', 'all'), 1: ('fast', 'e+f', 'all'), 2: ('fast', 'e+f', 'all'), 3: ('mid', 'all'), 4: ('slow', 'all'), 5: ('rare', 'all'), -1: ('all',)}
WN = 'ab'
LINES = []


def out(*a):
    LINES.append(' '.join(str(x) for x in a))


A = defaultdict(Counter)       # (team, layout) -> key -> value
games = Counter()


def digit(ch):
    return 9 if ch == 'x' else int(ch)


def post_kind(p):
    # p: distance of the eater's head to the tile at the starts of rounds e+1 .. e+12
    if len(p) < 8:
        return None
    q = p[:8]
    if 'x' in q:
        return 'died'
    d = [digit(c) for c in p]
    if max(d[:8]) <= 2:
        return 'stay'
    first = next(i for i, v in enumerate(d) if v >= 3)
    if any(v <= 1 for v in d[first + 1:]):
        return 'back'
    return 'leave'


def load(names):
    for name in names:
        for line in Path(OUT + name).read_text().splitlines():
            g = json.loads(line)
            a = A[(g['team'], g['layout'])]
            games[(g['team'], g['layout'])] += 1
            last_eat = {}
            recs = g['births']
            for rec in recs:
                r, t, c, fd, od, zone, nlen, n2f, n2o, e, es, eid, elen, eage, ed, post = rec
                z = WN[0 if r <= 100 else 1]
                for cg in CG[c]:
                    for s, ds, n2 in ((0, fd, n2f), (1, od, n2o)):
                        k = (s, z, cg)
                        a[k + ('n',)] += 1
                        d0 = int(ds[0])
                        a[k + ('d0le1',)] += d0 <= 1
                        a[k + ('d0le2',)] += d0 <= 2
                        a[k + ('d0le3',)] += d0 <= 3
                        if len(ds) >= 4:
                            a[k + ('n4',)] += 1
                            a[k + ('stood1',)] += max(ds[1:4]) <= '1'
                            a[k + ('stood2',)] += max(ds[1:4]) <= '2'
                            d3 = int(ds[3])
                            b3 = '1' if d3 <= 1 else '2' if d3 == 2 else '3' if d3 == 3 else '4-6' if d3 <= 6 else 'far'
                            b0 = '1' if d0 <= 1 else '2' if d0 == 2 else '3+'
                            a[k + ('tr', b3, b0)] += 1
                            a[k + ('tr', b3)] += 1
                        a[k + ('n2', min(n2, 3))] += 1
                        if es == s:
                            a[k + ('eat',)] += 1
                            a[k + ('wait',)] += e - r
                            a[k + ('eat0',)] += e == r
                            a[k + ('eat2',)] += e - r <= 2
                            a[k + ('ed', min(ed, 4) if ed <= 6 else 'far')] += 1
                            a[k + ('elen',)] += elen
                            a[k + ('young',)] += eage < 15
                            a[k + ('len', min(elen, 9))] += 1
                            pk = post_kind(post)
                            if pk:
                                a[k + ('pk',)] += 1
                                a[k + ('pk', pk)] += 1
                                d = [digit(ch) for ch in post]
                                lead = 0
                                for v in d:
                                    if v > 1:
                                        break
                                    lead += 1
                                a[k + ('lead1',)] += lead
                                a[k + ('in1',)] += sum(1 for v in d[:8] if v <= 1)
                                a[k + ('in2',)] += sum(1 for v in d[:8] if v <= 2)
                                for i in (1, 2, 3, 5, 7):
                                    a[k + ('pd', i, min(d[i], 4))] += 1
                            if s == 0:
                                prev = last_eat.get(t)
                                if prev is not None:
                                    a[k + ('chain',)] += 1
                                    a[k + ('chain_same',)] += prev[1] == eid and r - prev[0] <= 12
                                    a[k + ('chain_side12',)] += prev[2] == 0 and r - prev[0] <= 12
                        elif es < 0:
                            a[k + ('nobody',)] += 1
                    if zone and z == 'b':
                        a[(0, z, cg, 'zone_n')] += 1
                        a[(0, z, cg, 'zone_eat')] += es == 0
                        a[(0, z, cg, 'zone_d1')] += int(fd[0]) <= 1
                if es >= 0:
                    last_eat[t] = (e, eid, es)
            for zi in range(2):
                z = WN[zi]
                for c in range(6):
                    tt = g['tot'][zi][c]
                    for cg in CG[c]:
                        for j, nm in enumerate(('free', 'pearl', 'bodyF', 'bodyX', 'births', 'stepF', 'stepX', 'eatF', 'eatX', 'tiles')):
                            a[('t', z, cg, nm)] += tt[j]
                        for s in range(2):
                            for j, nm in enumerate(('beside', 'on', 'otherbody', 'free', 'born')):
                                a[('adj', s, z, cg, nm)] += g['adj'][zi][s][c][j]
                for s in range(2):
                    for n in range(5):
                        a[('ch', s, z, n)] += g['chist'][zi][s][n]
                a[('cboth', z)] += g['cboth'][zi]
            for zi in range(3):
                z = 'abc'[zi]
                for s in range(2):
                    a[('turns', s, z)] += g['turns'][zi][s]
                    for kst in range(3):
                        a[('expo', s, z, kst)] += g['expo'][zi][s][kst]
                        a[('explen', s, z, kst)] += g['explen'][zi][s][kst]
                        a[('ramlen', s, z, kst)] += g['ram_len'][zi][s][kst]
                        for cause, v in g['deaths'][zi][s][kst].items():
                            a[('death', s, z, kst, cause)] += v
            a[('clusters',)] += g['nclusters']
            a[('games',)] += 1


LAY = []


def val(team, lay, key):
    return A[(team, lay)].get(key, 0)


def cmp(label, num, den, scale=100.0, fmt='%6.1f'):
    """num, den: keys, or lists of keys to sum. Prints pooled and equal-layout rates for O and R."""
    nums = num if isinstance(num, list) else [num]
    dens = den if isinstance(den, list) else [den]
    pooled, per = {}, {}
    for tm in 'OR':
        n = sum(val(tm, l, k) for l in LAY for k in nums)
        d = sum(val(tm, l, k) for l in LAY for k in dens)
        pooled[tm] = (scale * n / d if d else None, n, d)
        per[tm] = {}
        for l in LAY:
            dd = sum(val(tm, l, k) for k in dens)
            if dd:
                per[tm][l] = scale * sum(val(tm, l, k) for k in nums) / dd
    shared = [l for l in LAY if l in per['O'] and l in per['R']]
    mo = sum(per['O'][l] for l in shared) / len(shared) if shared else None
    mr = sum(per['R'][l] for l in shared) / len(shared) if shared else None
    hi = sum(1 for l in shared if per['R'][l] > per['O'][l])
    f = lambda v: (fmt % v) if v is not None else '    NA'
    out('%-58s O %s (%d/%d)  R %s (%d/%d) | layout mean O %s R %s | R higher %d/%d' % (
        label, f(pooled['O'][0]), pooled['O'][1], pooled['O'][2], f(pooled['R'][0]), pooled['R'][1], pooled['R'][2],
        f(mo), f(mr), hi, len(shared)))
    return per


def main():
    names = ['sp_test.jsonl'] if len(sys.argv) > 1 else ['sp_f-%d.jsonl' % n for n in range(6)]
    load(names)
    LAY.extend(sorted({l for (tm, l) in A}))
    out('games O %d R %d; layouts %d' % (sum(v for (tm, l), v in games.items() if tm == 'O'),
                                         sum(v for (tm, l), v in games.items() if tm == 'R'), len(LAY)))
    out('\n== tiles and births per class (pooled over the games of each team) ==')
    for cg in ('every', 'fast', 'mid', 'slow', 'rare'):
        for tm in 'OR':
            row = []
            for z in WN:
                b = sum(val(tm, l, ('t', z, cg, 'births')) for l in LAY)
                fr = sum(val(tm, l, ('t', z, cg, 'free')) for l in LAY)
                row.append('%s: births %d, per free round-start %.3f' % (z, b, b / fr if fr else 0))
            tiles = sum(val(tm, l, ('t', 'a', cg, 'tiles')) for l in LAY)
            gm = sum(val(tm, l, ('games',)) for l in LAY)
            out('%-6s %s tiles/game %.1f  %s' % (cg, tm, tiles / gm, '; '.join(row)))
    for side, sn in ((0, 'F'), (1, 'X')):
        for z in WN:
            for cg in ('every', 'fast', 'mid', 'slow', 'rare', 'all'):
                k = (side, z, cg)
                out('\n-- job 1: births, side %s, window %s, class %s --' % (sn, z, cg))
                cmp('nearest head within 1 step at birth %', k + ('d0le1',), k + ('n',))
                cmp('nearest head within 2 steps at birth %', k + ('d0le2',), k + ('n',))
                cmp('nearest head within 3 steps at birth %', k + ('d0le3',), k + ('n',))
                cmp('a head within 1 step in each of the 3 rounds before %', k + ('stood1',), k + ('n4',))
                cmp('a head within 2 steps in each of the 3 rounds before %', k + ('stood2',), k + ('n4',))
                cmp('eaten by the side %', k + ('eat',), k + ('n',))
                cmp('eaten by the side in the birth round %', k + ('eat0',), k + ('n',))
                cmp('eaten by the side within 2 rounds %', k + ('eat2',), k + ('n',))
                cmp('eaten by nobody %', k + ('nobody',), k + ('n',))
                cmp('wait until eaten, rounds (the side eats)', k + ('wait',), k + ('eat',), 1.0, '%6.2f')
                cmp('of its eaten: in the birth round %', k + ('eat0',), k + ('eat',))
                cmp('of its eaten: eater within 1 step at birth %', k + ('ed', 1), k + ('eat',))
                cmp('of its eaten: eater 2 steps away at birth %', k + ('ed', 2), k + ('eat',))
                cmp('of its eaten: eater more than 6 steps away at birth %', k + ('ed', 'far'), k + ('eat',))
                cmp('eater length (mean)', k + ('elen',), k + ('eat',), 1.0, '%6.2f')
                cmp('eater split off under 15 rounds ago %', k + ('young',), k + ('eat',))
                for n in range(4):
                    cmp('heads of the side within 2 steps at birth = %d%s %%' % (n, '+' if n == 3 else ''), k + ('n2', n), k + ('n',))
                for b3 in ('1', '2', '3', '4-6'):
                    for b0 in ('1', '2', '3+'):
                        cmp('nearest at %s three rounds before -> %s at birth %%' % (b3, b0), k + ('tr', b3, b0), k + ('tr', b3))
                if cg in ('every', 'fast', 'mid', 'e+f', 'slow'):
                    out('   after eating there (job 2):')
                    for pk in ('stay', 'back', 'leave', 'died'):
                        cmp('   %s %%' % pk, k + ('pk', pk), k + ('pk',))
                    cmp('   rounds within 1 step before first going further', k + ('lead1',), k + ('pk',), 1.0, '%6.2f')
                    cmp('   of the next 8 round-starts within 1 step', k + ('in1',), k + ('pk',), 1.0, '%6.2f')
                    cmp('   of the next 8 round-starts within 2 steps', k + ('in2',), k + ('pk',), 1.0, '%6.2f')
                    for i in (1, 2, 3, 5, 7):
                        cmp('   %d rounds after the meal: within 1 step %%' % (i + 1), [k + ('pd', i, 0), k + ('pd', i, 1)], k + ('pk',))
                        cmp('   %d rounds after the meal: 4 or more steps away %%' % (i + 1), k + ('pd', i, 4), k + ('pk',))
                    if side == 0:
                        cmp('   pearl follows a meal on the same tile: same dragon ate both within 12 %', k + ('chain_same',), k + ('chain',))
                        cmp('   same, any dragon of the side within 12 %', k + ('chain_side12',), k + ('chain',))
    out('\n== leader zone (focal births in window b within 9 tiles of the focal longest dragon) ==')
    for cg in ('e+f', 'mid', 'all'):
        cmp('births inside the zone %% (%s)' % cg, (0, 'b', cg, 'zone_n'), (0, 'b', cg, 'n'))
        cmp('  eaten by the side, inside %', (0, 'b', cg, 'zone_eat'), (0, 'b', cg, 'zone_n'))
        cmp('  head within 1 at birth, inside %', (0, 'b', cg, 'zone_d1'), (0, 'b', cg, 'zone_n'))
    out('\n== neighbour test: a head beside an empty spawning tile at the start of a round ==')
    for z in WN:
        for cg in ('every', 'fast', 'mid', 'slow', 'rare'):
            for side, sn in ((0, 'F'), (1, 'X')):
                k = ('adj', side, z, cg)
                out('-- window %s class %s side %s' % (z, cg, sn))
                cmp('its body is on the tile one round later %', k + ('on',), k + ('beside',))
                cmp('tile still free one round later %', k + ('free',), k + ('beside',))
                cmp('pearl born on it then, % of still free', k + ('born',), k + ('free',))
            cmp('all free round-starts of the class: pearl born %', ('t', z, cg, 'births'), ('t', z, cg, 'free'))
    out('\n== class totals ==')
    for z in WN:
        for cg in ('every', 'fast', 'mid', 'slow'):
            out('-- window %s class %s' % (z, cg))
            tk = lambda nm: ('t', z, cg, nm)
            allr = [tk('free'), tk('pearl'), tk('bodyF'), tk('bodyX')]
            cmp('tile round-starts under a focal body %', tk('bodyF'), allr)
            cmp('tile round-starts under an opponent body %', tk('bodyX'), allr)
            cmp('tile round-starts with a pearl lying %', tk('pearl'), allr)
            cmp('focal body round-starts per focal meal on the tile', tk('bodyF'), tk('eatF'), 1.0, '%6.2f')
            cmp('opponent body round-starts per opponent meal', tk('bodyX'), tk('eatX'), 1.0, '%6.2f')
            cmp('focal steps onto the empty tile per focal meal there', tk('stepF'), tk('eatF'), 1.0, '%6.2f')
            cmp('opponent steps onto the empty tile per opponent meal', tk('stepX'), tk('eatX'), 1.0, '%6.2f')
            cmp('focal share of the meals on these tiles %', tk('eatF'), [tk('eatF'), tk('eatX')])
    out('\n== heads within 2 steps of one cluster of fast tiles (classes every+fast), per cluster and round ==')
    for z in WN:
        for side, sn in ((0, 'F'), (1, 'X')):
            den = [('ch', side, z, n) for n in range(5)]
            for n in range(5):
                cmp('window %s side %s: %d%s heads %%' % (z, sn, n, '+' if n == 4 else ''), ('ch', side, z, n), den)
            cmp('window %s side %s: 2 or more, %% of clusters with any' % (z, sn), [('ch', side, z, n) for n in (2, 3, 4)], [('ch', side, z, n) for n in (1, 2, 3, 4)])
        cmp('window %s: both sides present %%' % z, ('cboth', z), [('ch', 0, z, n) for n in range(5)])
    out('\n== deaths by where the dragon stood (2 = third round or more in a row within 1 step of one cluster; 1 = first or second; 0 = elsewhere) ==')
    for z in 'abc':
        for side, sn in ((0, 'F'), (1, 'X')):
            for kst in range(3):
                e = ('expo', side, z, kst)
                out('-- window %s side %s state %d' % (z, sn, kst))
                cmp('share of the side dragon-rounds %', e, [('expo', side, z, q) for q in range(3)])
                cmp('mean length', ('explen', side, z, kst), e, 1.0, '%6.2f')
                cmp('rammed by the other team per 1000 dragon-rounds', ('death', side, z, kst, 'rvx'), e, 1000.0, '%6.2f')
                cmp('rammed by a team mate per 1000', ('death', side, z, kst, 'rvs'), e, 1000.0, '%6.2f')
                cmp('died as the rammer per 1000', ('death', side, z, kst, 'rm'), e, 1000.0, '%6.2f')
                cmp('wall, own body or another body per 1000', [('death', side, z, kst, c) for c in 'wob'], e, 1000.0, '%6.2f')
                cmp('no action / illegal split per 1000', ('death', side, z, kst, 'n'), e, 1000.0, '%6.2f')
                cmp('all deaths per 1000', [('death', side, z, kst, c) for c in ('rvx', 'rvs', 'rm', 'w', 'o', 'b', 'n', '?')], e, 1000.0, '%6.2f')
                cmp('length of the rammed (mean)', ('ramlen', side, z, kst), [('death', side, z, kst, 'rvx'), ('death', side, z, kst, 'rvs')], 1.0, '%6.2f')
    out('\n== per layout: the two marks, classes every+fast and mid, window b, focal side ==')
    for cg in ('e+f', 'mid', 'all'):
        out('class', cg, ' layout: games O/R | births per game O/R | head within 1 at birth % O/R | eaten in birth round % O/R | wait O/R | eaten by side % O/R')
        for l in LAY:
            row = []
            for tm in 'OR':
                a = A[(tm, l)]
                k = (0, 'b', cg)
                n = a.get(k + ('n',), 0)
                eat = a.get(k + ('eat',), 0)
                row.append((games[(tm, l)], n / max(1, games[(tm, l)]), 100.0 * a.get(k + ('d0le1',), 0) / n if n else -1,
                            100.0 * a.get(k + ('eat0',), 0) / n if n else -1, a.get(k + ('wait',), 0) / eat if eat else -1,
                            100.0 * eat / n if n else -1))
            o, r = row
            out('  %-22s %2d/%2d | %6.1f/%6.1f | %5.1f/%5.1f | %5.1f/%5.1f | %5.2f/%5.2f | %5.1f/%5.1f' % (
                l, o[0], r[0], o[1], r[1], o[2], r[2], o[3], r[3], o[4], r[4], o[5], r[5]))


main()
if len(sys.argv) > 1:
    Path(OUT + 'sp_agg-test.txt').write_text('\n'.join(LINES) + '\n')
else:
    Path(OUT + 'sp_agg.txt').write_text('\n'.join(LINES) + '\n')
sys.stdout.write('lines %d\n' % len(LINES))
