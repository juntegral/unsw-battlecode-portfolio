# Scratch (early-growth brief): first aggregate of eg_rows-*.jsonl. Prints to the screen only.
# Usage: python3 data/analysis/ladder/losses/work/eg_agg.py [last round, default 60]
import sys, json
from collections import Counter, defaultdict
from statistics import median, mean
from pathlib import Path

R1 = int(sys.argv[1]) if len(sys.argv) > 1 else 60
games = []
for n in range(4):
    for line in Path('data/analysis/ladder/losses/work/eg_rows-%d.jsonl' % n).read_text().splitlines():
        games.append(json.loads(line))
print('games', len(games))


def pct(a, b):
    return '%5.1f%% (%d/%d)' % (100.0 * a / b, a, b) if b else '   n/a (0/0)'


def bucket(d):
    return 'none' if d is None else '1' if d <= 1 else '2-7' if d <= 7 else '8-15' if d <= 15 else '16+'


def table(gs, label):
    print()
    print('=====', label, len(gs), 'games', dict(Counter(g['result'] for g in gs)), 'rounds 0-%d' % R1)
    if not gs:
        return
    for s, name in (('u', 'OURS'), ('t', 'THEIRS')):
        T = [t for g in gs for t in g['turns'] if t[1] == s and t[0] <= R1]
        n = len(T)
        print('--', name, 'dragon turns', n, 'per game %.1f' % (n / len(gs)))
        eaten = [sum(1 for p in g['pearls'] if p[7] == s and p[8] <= R1) for g in gs]
        print('   pearls eaten by r%d: mean %.2f median %s; by r20 %.2f; by r40 %.2f' % (
            R1, mean(eaten), median(eaten),
            mean(sum(1 for p in g['pearls'] if p[7] == s and p[8] <= 20) for g in gs),
            mean(sum(1 for p in g['pearls'] if p[7] == s and p[8] <= 40) for g in gs)))
        k = 1 if s == 'u' else 4
        for rr in (20, 40, 60, 100):
            v = [sn[k] for g in gs for sn in g['snaps'] if sn[0] == rr]
            tl = [sn[k + 1] for g in gs for sn in g['snaps'] if sn[0] == rr]
            if v:
                print('   end of r%d: dragons mean %.2f, total length mean %.2f (%d games reached)' % (rr, mean(v), mean(tl), len(v)))
        print('   pearl in view at turn start', pct(sum(t[9] is not None for t in T), n),
              '| known (seen by this dragon, still there)', pct(sum(t[10] is not None for t in T), n),
              '| any on board', pct(sum(t[11] is not None for t in T), n))
        for fld, cl, nm in ((10, 14, 'nearest KNOWN pearl'), (11, 15, 'nearest pearl ON BOARD')):
            c, a, e = Counter(), Counter(), Counter()
            for t in T:
                b = bucket(t[fld])
                c[b] += 1
                a[b] += int(t[cl] == 1)
                e[b] += int(t[19] > 0)
            print('   by distance to', nm, '(turns: stepped closer / ate):')
            for b in ('1', '2-7', '8-15', '16+', 'none'):
                if c[b]:
                    print('      %-5s %6d turns %5.1f%% | closer %s | ate %s' % (b, c[b], 100.0 * c[b] / n, pct(a[b], c[b]), pct(e[b], c[b])))
        far = [t for t in T if (t[10] is None or t[10] > 7) and t[3] <= 4 and t[18] >= 1]
        print('   no known pearl within 7, length<=4, moved:', len(far), 'turns; step lowers centre distance', pct(sum(t[8] < t[7] for t in far), len(far)),
              '| raises', pct(sum(t[8] > t[7] for t in far), len(far)), '| mean centre distance %.2f' % (mean(t[7] for t in far) if far else 0),
              '| within 3 of centre', pct(sum(t[7] <= 3 for t in far), len(far)))
        for lo, hi in ((0, 9), (10, 19), (20, 29), (30, 44), (45, 59), (60, 79), (80, 99), (100, 120)):
            X = [t for g in gs for t in g['turns'] if t[1] == s and lo <= t[0] <= hi and t[3] <= 4]
            if X:
                print('      r%3d-%3d len<=4: turns %5d mean centre dist %5.2f | within 3: %s | ate per turn %.3f | new tiles/turn %.2f' % (
                    lo, hi, len(X), mean(t[7] for t in X), pct(sum(t[7] <= 3 for t in X), len(X)), sum(t[19] for t in X) / len(X), mean(t[20] for t in X)))
        blind = [t for t in T if t[9] is None and t[18] >= 1]
        st = Counter(t[22] for t in blind)
        den = st['S'] + st['T'] + st['R']
        print('   no pearl in view, moved:', len(blind), 'turns | straight', pct(st['S'], den), '| turn', pct(st['T'], den), '| reverse', pct(st['R'], den),
              '| onto a tile it stood on in its last 12 steps', pct(sum(t[24] == 1 for t in blind), len(blind)),
              '| new tiles (side) per turn %.2f' % (mean(t[20] for t in blind) if blind else 0))
        cov = [sum(t[20] for t in g['turns'] if t[1] == s and t[0] <= R1) / (g['w'] * g['h']) for g in gs]
        print('   share of the board seen by the side by r%d: mean %.3f median %.3f' % (R1, mean(cov), median(cov)))
        adj = [t for t in T if t[25] == 1]
        adjp = [t for t in T if t[25] == 2]
        print('   pearl on an open neighbour: %d turns, not eaten %s | only through a portal: %d turns, not eaten %s' % (
            len(adj), pct(sum(t[19] == 0 for t in adj), len(adj)), len(adjp), pct(sum(t[19] == 0 for t in adjp), len(adjp))))
        print('   portal steps', sum(t[23] for t in T), '| turns with 2+ steps', sum(t[18] >= 2 for t in T), '| turns with no step', sum(t[18] == 0 for t in T),
              '| enemy head in view', pct(sum(t[16] for t in T), n), '| splits', sum(t[28] for t in T))
        print('   deaths', dict(Counter(t[27] for t in T if t[27])), '| kills made', sum(t[29] for t in T))
        for role, nm in ((1, 'queen (id 0/1)'), (0, 'other starting dragon')):
            X = [t for t in T if t[4] == 1 and t[5] == role]
            dead = sum(1 for t in X if t[27])
            print('   %-22s turns %5d ate %4d (%.2f per game) deaths %d %s | portal steps %d | mean centre dist %.2f' % (
                nm, len(X), sum(t[19] for t in X), sum(t[19] for t in X) / len(gs), dead, dict(Counter(t[27] for t in X if t[27])), sum(t[23] for t in X),
                mean(t[7] for t in X) if X else 0))
        X = [t for t in T if t[4] == 0]
        print('   %-22s turns %5d ate %4d (%.2f per game)' % ('children', len(X), sum(t[19] for t in X), sum(t[19] for t in X) / len(gs)))
    P = [p for g in gs for p in g['pearls'] if p[2] == 'n' and p[1] <= R1]
    print('-- natural pearls born r0-%d: %d (%.1f per game)' % (R1, len(P), len(P) / len(gs)))
    print('   nearer to us at birth', pct(sum(p[3] < p[4] for p in P), len(P)), '| nearer to them', pct(sum(p[4] < p[3] for p in P), len(P)),
          '| median path distance at birth: ours %s theirs %s' % (median(p[3] for p in P), median(p[4] for p in P)))
    for s, name, dk, sk in (('u', 'OURS', 3, 5), ('t', 'THEIRS', 4, 6)):
        seen = [p for p in P if p[sk] is not None and p[sk] <= R1]
        mine = [p for p in seen if p[7] == s and p[8] <= R1]
        other = [p for p in seen if p[7] not in (None, s) and p[8] <= R1]
        print('   %s: seen by r%d %s | of those seen: eaten by this side %s, by the other side %s, still there %s | median rounds seen-to-eaten %s' % (
            name, R1, pct(len(seen), len(P)), pct(len(mine), len(seen)), pct(len(other), len(seen)), pct(len(seen) - len(mine) - len(other), len(seen)),
            median(p[8] - p[sk] for p in mine) if mine else None))
        for lo, hi in ((0, 7), (8, 15), (16, 999)):
            X = [p for p in P if lo <= p[dk] <= hi]
            print('      born %d-%d path steps from a head of this side: %d | eaten by this side by r%d %s | by the other %s' % (
                lo, hi, len(X), R1, pct(sum(p[7] == s and p[8] <= R1 for p in X), len(X)), pct(sum(p[7] not in (None, s) and p[8] <= R1 for p in X), len(X))))


sel = [g for g in games if g['group'] == 'never_grew' and g['L0'] == 2]
table(sel, 'never grew, start length 2 (all)')
table([g for g in sel if g['map_key'].startswith('Tower')], 'never grew, Tower Defense')
table([g for g in sel if g['map_key'].startswith('Stripes')], 'never grew, Stripes')
if len(sys.argv) > 2:
    table([g for g in games if g['group'] == 'grew' and g['L0'] == 2], 'grew, start length 2')
    table([g for g in games if g['map_key'].startswith('weakhold')], 'weakhold (centre layout, start length 4)')
    table([g for g in games if g['map_key'].startswith('Trophy')], 'Trophy (start length 3)')
    table([g for g in games if g['map_key'].startswith('Queen')], 'Queen Of Spades (start length 3)')
    table([g for g in games if g['map_key'].startswith('Trauma')], 'Trauma (start length 4)')
    table([g for g in games if g['map_key'].startswith('Maze')], 'Maze (start length 4)')
