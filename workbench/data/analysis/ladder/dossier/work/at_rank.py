"""Scratch (diag-attack): rank the classes of chance by (their take rate - ours) x our chances a game x swing per meeting.
swing = length the victim side is down after 15 rounds minus length the mover side is down (drops eaten counted), from the
meetings THEY start in that class. Usage: python3 data/analysis/ladder/dossier/work/at_rank.py [classes|clauses|size]"""
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


def phase(g, r, n_ours):
    if r > g['feed']:
        return 'C'
    if r > 200 and n_ours >= 56:
        return 'F'
    return 'A' if r <= g['grow'] else 'B'


def fails(g, r):
    rnd, L, q, Lt, dist, free, ov, ev, vis, n_own, lng, big, pe = r[0], r[3], r[4], r[7], r[10], r[11], r[12], r[13], r[16], r[17], r[19], r[20], r[24]
    feeding = rnd > g['feed'] or (rnd > 200 and n_own >= 56)
    plain_reach = free + L - 2
    if not q and L <= 10 and dist - pe <= plain_reach and dist <= 8:
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
    need = L if (cap or g['aggr']) else max(5, L + 2)
    if vis < need:
        if Lt < L:
            f.append('shorter')
        elif vis >= L:
            f.append('size-even')
        else:
            f.append('size-hidden')
    if dist > min(plain_reach, 3 if g['aggr'] else 4) or (pe > 0 and dist > plain_reach):
        f.append('steps')
    return tuple(f)


def swing(x):
    return (x['mm'] + x['vm'] - x['L0']) - (x['mv'] + x['vv'] - x['Lv'])


def rank(title, keyf, top=30, minn=100):
    c = defaultdict(Counter)
    for g in G:
        for r in g['chs']:
            k = keyf(g, r)
            if k is None:
                continue
            a = c[k]
            s = r[1]
            a[(s, 'n')] += 1
            if r[22] == 1:
                a[(s, 'took')] += 1
                x = g['hox'].get((r[0], r[2], r[6]))
                if x is not None:
                    a[(s, 'sw')] += swing(x)
                    a[(s, 'L0')] += x['L0']
                    a[(s, 'Lv')] += x['Lv']
                    a[(s, 'hn')] += 1
    out = []
    for k, a in c.items():
        if a[(0, 'n')] + a[(1, 'n')] < minn:
            continue
        ro = a[(0, 'took')] / max(1, a[(0, 'n')])
        rt = a[(1, 'took')] / max(1, a[(1, 'n')])
        wt = a[(1, 'sw')] / a[(1, 'hn')] if a[(1, 'hn')] else 0.0
        wo = a[(0, 'sw')] / a[(0, 'hn')] if a[(0, 'hn')] else float('nan')
        extra = (rt - ro) * a[(0, 'n')] / NG
        out.append((extra * wt, k, a[(0, 'n')] / NG, ro, a[(1, 'n')] / NG, rt, extra, wt, wo, a[(1, 'hn')], a[(0, 'hn')],
                    a[(1, 'L0')] / max(1, a[(1, 'hn')]), a[(1, 'Lv')] / max(1, a[(1, 'hn')])))
    out.sort(reverse=True)
    print()
    print(title)
    print('  score | class | ours: chances a game, take | theirs: chances a game, take | extra rams a game at their rate | swing per meeting: theirs (n), ours (n) | their mover and victim length')
    tot = 0.0
    for sc, k, no, ro, nt, rt, extra, wt, wo, hn_t, hn_o, l0, lv in out[:top]:
        tot += sc
        print('  %6.2f | %-34s | %7.2f %.3f | %7.2f %.3f | %+6.2f | %+6.2f (%d) %+6.2f (%d) | %.1f %.1f' % (
            sc, ' '.join(str(z) for z in k), no, ro, nt, rt, extra, wt, hn_t, wo, hn_o, l0, lv))
    print('  sum of the listed scores %.1f; all classes %.1f' % (tot, sum(o[0] for o in out)))


al = lambda r: ('2' if r[3] <= 2 else '3' if r[3] == 3 else '4' if r[3] == 4 else '5-10' if r[3] <= 10 else '11+')
rel = lambda r: 'queen' if r[8] else 'shorter' if r[7] < r[3] else 'eq-2x' if r[7] < 2 * r[3] else '2x<10' if r[7] < 10 else '10+'
edge = lambda r: 'edge' if r[12] >= r[13] else 'outnum'
paid = lambda r: 'pay' if r[10] > r[11] else 'free'
ph = lambda g, r: phase(g, r[0], r[17] if r[1] == 0 else r[18])
sec = sys.argv[1] if len(sys.argv) > 1 else 'classes'
if sec == 'classes':
    rank('classes: own length, target relation, local count, phase (non-queen actors)', lambda g, r: (al(r), rel(r), edge(r), ph(g, r)) if not r[4] else None)
    rank('own length x target relation', lambda g, r: (al(r), rel(r)) if not r[4] else None)
    rank('target relation x local count, actor 2-4', lambda g, r: (rel(r), edge(r)) if not r[4] and r[3] <= 4 else None)
    rank('target relation x phase, actor 2-4', lambda g, r: (rel(r), ph(g, r)) if not r[4] and r[3] <= 4 else None)
    rank('target relation x pay, actor 2-4', lambda g, r: (rel(r), paid(r)) if not r[4] and r[3] <= 4 else None)
    rank('layout size x phase, actor 2-4', lambda g, r: ('small' if g['aggr'] else 'big', ph(g, r)) if not r[4] and r[3] <= 4 else None)
    rank('layout size x at 59 dragons x target relation, actor 2-4, before the feed round', lambda g, r: ('small' if g['aggr'] else 'big', 'cap' if r[17] >= 59 else 'below', rel(r)) if not r[4] and r[3] <= 4 and r[0] <= g['feed'] else None)
if sec == 'clauses':
    rank('failing clauses of our rule (all actors)', lambda g, r: fails(g, r) or ('allowed',), top=40)
    rank('failing clauses, actor 2-4 non-queen, by layout size', lambda g, r: (('small' if g['aggr'] else 'big'),) + (fails(g, r) or ('allowed',)) if not r[4] and r[3] <= 4 else None, top=40)

if sec == 't2':
    big2 = lambda r: not r[4] and r[3] <= 4 and r[7] >= 2 * r[3]
    rank('actor 2-4, target at least twice its length: failing clauses of our rule', lambda g, r: (fails(g, r) or ('allowed',)) if big2(r) else None, top=40, minn=40)
    rank('same, with TRADE_EVEN on (size-even no longer fails): failing clauses', lambda g, r: (tuple(x for x in fails(g, r) if x != 'size-even') or ('allowed',)) if big2(r) else None, top=40, minn=40)
    rank('same class by target length', lambda g, r: ('5-9' if r[7] < 10 else '10-19' if r[7] < 20 else '20+', 'L%d' % r[3]) if big2(r) and r[7] >= 5 else ('4', 'L2') if big2(r) else None, top=40, minn=40)
    rank('same class: target is the longest of its side / not', lambda g, r: ('their longest' if r[9] else 'not longest', edge(r)) if big2(r) else None, top=40, minn=40)
    rank('same class by phase and count, TRADE_EVEN counted as on', lambda g, r: (ph(g, r), edge(r)) if big2(r) else None, top=40, minn=40)
    rank('same class by visible parts of the target in the 7x7 view', lambda g, r: ('vis %d' % min(r[16], 10),) if big2(r) else None, top=40, minn=40)
    rank('same class by distance and pay', lambda g, r: ('d%d' % min(r[10], 5), paid(r), 'pearl' if r[24] else 'plain') if big2(r) else None, top=40, minn=40)
