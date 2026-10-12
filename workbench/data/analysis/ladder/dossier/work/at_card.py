"""Scratch (diag-attack): the candidate switches applied to the chance rows.
R  = a non-queen dragon of length 2-4 with an enemy head that shows at least twice its length in parts inside its 7x7 view,
     within its plain sprint reach (ceil(L/4)+L-2 steps, capped at 4, or 3 on layouts of 1200 cells or fewer), 8 or more of
     its side alive on layouts above 1200 cells. "New" = R holds and our rule as it is today says no.
Usage: python3 data/analysis/ladder/dossier/work/at_card.py"""
import sys, json
from collections import Counter, defaultdict
from pathlib import Path

D = Path('data/analysis/ladder/dossier/work')
G = []
for n in range(5):
    with open(D / ('at_scan-%d.jsonl' % n)) as f:
        for line in f:
            G.append(json.loads(line))
NG = len(G)
for g in G:
    g['grow'] = 150 if g['cells'] > 1200 else 300
    s300 = g['series'].get('300')
    g['feed'] = 300 if (g['cells'] > 600 and s300 and s300[3] > 0) else 400
    g['aggr'] = g['cells'] <= 1200
    g['hox'] = dict(((x['r'], x['mid'], x['vid']), x) for x in g['hos'] if x['cross'])
    g['band'] = '<1900' if g['rating'] < 1900 else '1900-2099' if g['rating'] < 2100 else '2100+'


def phase(g, r, n_ours):
    if r > g['feed']:
        return 'C after feed round'
    if r > 200 and n_ours >= 56:
        return 'F full board'
    return 'A before switch' if r <= g['grow'] else 'B after switch'


def fails(g, r, even=False):
    rnd, L, q, Lt, dist, free, ov, ev, vis, n_own, lng, big, pe = r[0], r[3], r[4], r[7], r[10], r[11], r[12], r[13], r[16], r[17], r[19], r[20], r[24]
    feeding = rnd > g['feed'] or (rnd > 200 and n_own >= 56)
    plain_reach = free + L - 2
    if not q and L <= 10 and dist <= plain_reach and dist <= 8:
        if (vis >= 10 and vis >= L + 4) or big:
            return ()
        if feeding and vis >= 6 and vis * 2 >= L and lng > 0:
            return ()
    f = []
    if q:
        f.append('queen')
    if L > 4:
        f.append('len>4')
    if rnd > g['feed']:
        f.append('feedround')
    if n_own < (1 if g['aggr'] else 8):
        f.append('units')
    if ov + 1 - ev < 1:
        f.append('count')
    cap = n_own >= 59
    need = L if (cap or g['aggr'] or even) else max(5, L + 2)
    if vis < need:
        f.append('size')
    if dist > min(plain_reach, 3 if g['aggr'] else 4):
        f.append('steps')
    return tuple(f)


def R(g, r):
    L = r[3]
    return (not r[4]) and L <= 4 and r[16] >= 2 * L and r[10] <= min(r[11] + L - 2, 3 if g['aggr'] else 4) and r[17] >= (1 if g['aggr'] else 8)


def swing(x):
    return (x['mm'] + x['vm'] - x['L0']) - (x['mv'] + x['vv'] - x['Lv'])


def table(title, keyf):
    c = defaultdict(Counter)
    for g in G:
        for r in g['chs']:
            k = keyf(g, r)
            if k is None:
                continue
            a = c[k]
            s = r[1]
            a[(s, 'n')] += 1
            a[(s, 'fate')] += int(r[22] != 1 and r[23] > 0)
            a[(s, 'fate1')] += int(r[22] != 1 and r[23] == 1)
            a[(s, 'ref')] += int(r[22] != 1)
            if r[22] == 1:
                a[(s, 'took')] += 1
                x = g['hox'].get((r[0], r[2], r[6]))
                if x is not None:
                    a[(s, 'hn')] += 1
                    a[(s, 'sw')] += swing(x)
                    a[(s, 'L0')] += x['L0']; a[(s, 'Lv')] += x['Lv']
                    a[(s, 'gm')] += x['mm'] + x['vm']; a[(s, 'gv')] += x['mv'] + x['vv']
                    a[(s, 'drop')] += x['dm'] + x['dv']
                    a[(s, 'vtop')] += x['vtop']; a[(s, 'vq')] += x['vq']
    print()
    print(title)
    print('  class | OURS: chances a game, take | THEIRS: chances a game, take | extra rams a game at their rate | their meetings: mover, victim length; drops; eaten by mover side, victim side; swing | ours taken: mover, victim; swing | refused by ours: rammed before next turn (by that head)')
    for k in sorted(c):
        a = c[k]
        no, nt = a[(0, 'n')], a[(1, 'n')]
        ro, rt = a[(0, 'took')] / max(1, no), a[(1, 'took')] / max(1, nt)
        ht, hn = max(1, a[(1, 'hn')]), max(1, a[(0, 'hn')])
        print('  %-30s | %6.2f %.3f | %6.2f %.3f | %+5.2f | %.1f %.1f; %.1f; %.2f %.2f; %+.2f (n=%d) | %.1f %.1f; %+.2f (n=%d) | %.3f (%.3f)' % (
            ' '.join(str(z) for z in k), no / NG, ro, nt / NG, rt, (rt - ro) * no / NG,
            a[(1, 'L0')] / ht, a[(1, 'Lv')] / ht, a[(1, 'drop')] / ht, a[(1, 'gm')] / ht, a[(1, 'gv')] / ht, a[(1, 'sw')] / ht, a[(1, 'hn')],
            a[(0, 'L0')] / hn, a[(0, 'Lv')] / hn, a[(0, 'sw')] / hn, a[(0, 'hn')],
            a[(0, 'fate')] / max(1, a[(0, 'ref')]), a[(0, 'fate1')] / max(1, a[(0, 'ref')])))


def cls(g, r, even):
    if not R(g, r):
        return None
    f = fails(g, r, even)
    return 'allowed today' if not f else 'new: ' + '+'.join(f)


print('games', NG, '| ended_by', Counter(g['ended_by'] for g in G), '| queens', Counter(g['queens_at_end'] for g in G))
table('R by what our rule says today (TRADE_EVEN off)', lambda g, r: (cls(g, r, False),) if cls(g, r, False) else None)
table('R by what our rule says with TRADE_EVEN on', lambda g, r: (cls(g, r, True),) if cls(g, r, True) else None)
new = lambda g, r: R(g, r) and bool(fails(g, r, True))
table('R new (TRADE_EVEN on), total', lambda g, r: ('new',) if new(g, r) else None)
table('R new by phase', lambda g, r: (phase(g, r[0], r[17] if r[1] == 0 else r[18]),) if new(g, r) else None)
table('R new by layout size', lambda g, r: ('small' if g['aggr'] else 'big',) if new(g, r) else None)
table('R new by own length', lambda g, r: ('L%d' % r[3],) if new(g, r) else None)
table('R new by target length', lambda g, r: ('4-5' if r[7] <= 5 else '6-9' if r[7] <= 9 else '10-19' if r[7] <= 19 else '20+',) if new(g, r) else None)
table('R new by opponent rating', lambda g, r: (g['band'],) if new(g, r) else None)
table('R new by result of the game', lambda g, r: (g['result'],) if new(g, r) else None)
table('R new: free or paid', lambda g, r: ('pay %d' % max(0, r[10] - r[11]),) if new(g, r) else None)
table('R new: enemy heads minus own heads in the 7x7 view (own includes the actor)', lambda g, r: ('enemy-own %+d' % max(-2, min(3, r[13] - r[12] - 1)),) if new(g, r) else None)
table('R new: target is the longest dragon of its side', lambda g, r: ('longest' if r[9] else 'not longest',) if new(g, r) else None)
table('R new: can the target reach the actor (0 no, 1 by paying, 2 free)', lambda g, r: ('back %d' % r[21],) if new(g, r) else None)
# alternatives
f0 = lambda g, r: fails(g, r, True)
table('ALT 1: trades after the feed round (feedround is the only failing clause, TRADE_EVEN on)', lambda g, r: ('alt1',) if f0(g, r) == ('feedround',) else None)
table('ALT 2: any count, target at least own length (count the only failing clause, TRADE_EVEN on) by target relation',
      lambda g, r: ('alt2', 'twice' if r[16] >= 2 * r[3] else 'under twice') if f0(g, r) == ('count',) else None)
table('ALT 3: a longer dragon rams a shorter head (size the only failing clause, target shorter), by own length',
      lambda g, r: ('alt3', 'L%d' % r[3]) if f0(g, r) == ('size',) and r[7] < r[3] else None)
table('ALT 4: eat a pearl on the way (steps the only failing clause)', lambda g, r: ('alt4',) if f0(g, r) == ('steps',) and r[24] > 0 else None)
table('ALT 5: dragons of length 5 to 7 trade as the short ones do (len>4 the only failing clause)', lambda g, r: ('alt5',) if f0(g, r) == ('len>4',) and r[3] <= 7 else None)

# games reached
print()
lost_rule = [g for g in G if g['result'] == 'loss' and g['ended_by'] != 'elimination']
reach = Counter()
for g in G:
    n_new = n_top = n_late = 0
    for r in g['chs']:
        if r[1] == 0 and new(g, r) and r[22] != 1:
            n_new += 1
            if r[9] and r[7] >= 8:
                n_top += 1
                if r[0] > 300:
                    n_late += 1
    key = g['result'] + '|' + g['ended_by'] + '|' + g['queens_at_end']
    reach[(key, 'games')] += 1
    reach[(key, 'any')] += int(n_new > 0)
    reach[(key, 'top')] += int(n_top > 0)
    reach[(key, 'late')] += int(n_late > 0)
    reach[(key, 'n')] += n_new
print('games with refused R-new chances of ours: result|ended_by|queens: games, with any, with one against their longest dragon (8+), the same after round 300, refused chances a game')
for key in sorted(set(k for k, _ in reach)):
    print('  %-50s %4d %4d %4d %4d %6.2f' % (key, reach[(key, 'games')], reach[(key, 'any')], reach[(key, 'top')], reach[(key, 'late')], reach[(key, 'n')] / reach[(key, 'games')]))
