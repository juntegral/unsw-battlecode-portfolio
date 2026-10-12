"""Scratch (diag-theirqueen): exposure and hazard cuts from tq_scan-*.jsonl.
Usage: python3 tq_haz.py online|ladder [group prefixes, comma separated]"""
import sys
import json
from collections import Counter, defaultdict
from pathlib import Path

W = Path('data/analysis/ladder/dossier/work')
F = dict(r=0, head=1, L=2, ds=3, o3=4, o5=5, e3m=6, e5m=7, ep3=8, ne=9, neL=10, nem=11, nom=12, kc=13, fx=14, pk=15, mn=16, inr=17, ob2=18,
         act=19, steps=20, La=21, ate=22, end=23, da=24, died=25, hit=26, ep3n=27, child=28, sep=29, db=30, ep5n=31, o3c=32, nown=33, nen=34,
         pd=35, p3=36, ep3s=37)
ARM = {'agg7-m1': 'MAIN', 'agg7-m2': 'MAIN', 'agg7-b1': 'B7', 'agg7-b2': 'B7', 'agg8-q1': 'B7Q'}


def load(tags):
    games = []
    for t in tags:
        p = W / ('tq_scan-%s.jsonl' % t)
        if p.exists():
            games += [json.loads(x) for x in p.read_text().splitlines() if x]
    return games


def groups_of(games, mode):
    out = defaultdict(list)
    for g in games:
        if mode == 'online':
            arm = ARM[g['label']]
            opp = 'Bob' if g['opp'].startswith('Big') else 'Quiz'
            for a in (arm, 'ALL'):
                out[a + ' ours'].append((g, 0))
                out[a + ' ours/' + opp].append((g, 0))
                out[a + ' ' + opp].append((g, 1))
                out[a + ' theirs'].append((g, 1))
        elif g['label'] == 'ladder':
            out['ours ladder'].append((g, 0))
            out['ladder opp'].append((g, 1))
        else:
            out['rank1'].append((g, 0))
            out['rank1 opp'].append((g, 1))
    if mode == 'online':
        order = [a + ' ' + q for a in ('MAIN', 'B7', 'B7Q', 'ALL') for q in ('ours', 'theirs', 'ours/Bob', 'Bob', 'ours/Quiz', 'Quiz')]
    else:
        order = ['ours ladder', 'ladder opp', 'rank1', 'rank1 opp']
    return [(k, out[k]) for k in order if out[k]]


def pct(n, d):
    return '-' if not d else '%.0f%%' % (100.0 * n / d)


def f1(n, d):
    return '-' if not d else '%.1f' % (n / d)


def man(a, b, w, h):
    dx = abs(a % w - b % w)
    dy = abs(a // w - b // w)
    return min(dx, w - dx) + min(dy, h - dy)


def cut(name, v, keyfn, labels):
    """per bucket: turns, share, threatened turns /100, short-threat /100, rams and own-move deaths /1000, pearls /100, own heads <=5."""
    c = defaultdict(Counter)
    for g, s in v:
        recs = g['recs'][s]
        for t in recs:
            k = keyfn(g, s, t)
            if k is None:
                continue
            b = c[k]
            b['n'] += 1
            b['thr'] += 1 if t[F['ep3n']] > 0 else 0
            b['thr5'] += 1 if t[F['ep5n']] > 0 else 0
            b['ram'] += t[F['hit']]
            b['self'] += 1 if t[F['died']] else 0
            b['ate'] += t[F['ate']]
            b['o5'] += t[F['o5']]
            b['kelp2'] += 1 if t[F['kc']] >= 2 else 0
    tot = sum(b['n'] for b in c.values())
    print('  %s' % name)
    for k in labels:
        b = c.get(k)
        if not b:
            continue
        n = b['n']
        print('    %-10s turns %6d (%s)  head<=3 steps %s/100  <=5 %s/100  rammed %s/1000 (%d)  own-move death %s/1000 (%d)  pearls %s/100  own<=5 %s  kelp2+ %s' % (
            k, n, pct(n, tot), f1(100.0 * b['thr'], n), f1(100.0 * b['thr5'], n), f1(1000.0 * b['ram'], n), b['ram'], f1(1000.0 * b['self'], n), b['self'],
            f1(100.0 * b['ate'], n), f1(b['o5'], n), pct(b['kelp2'], n)))


def kds(g, s, t):
    x = t[F['ds']] / (g['w'] // 2 + g['h'] // 2)
    return '<0.15' if x < 0.15 else '0.15-0.3' if x < 0.3 else '0.3-0.5' if x < 0.5 else '0.5+'


def kdt(g, s, t):
    x = t[F['ds']]
    return '0-4' if x <= 4 else '5-8' if x <= 8 else '9-12' if x <= 12 else '13+'


def kround(g, s, t):
    r = t[0]
    return 'r0-50' if r <= 50 else 'r51-100' if r <= 100 else 'r101-200' if r <= 200 else 'r201-300' if r <= 300 else 'r301+'


def khalf(g, s, t):
    a = t[F['ds']]
    b = man(t[F['head']], g['start'][1 - s], g['w'], g['h'])
    return 'own half' if a < b else 'midline' if a == b else 'enemy half'


def ko5(g, s, t):
    x = t[F['o5']]
    return 'own5=0' if x == 0 else 'own5=1-2' if x <= 2 else 'own5=3+'


def krd(g, s, t):
    r = t[0]
    x = t[F['ds']]
    a = 'r0-50' if r <= 50 else 'r51-150' if r <= 150 else 'r151-300' if r <= 300 else 'r301+'
    b = 'd0-6' if x <= 6 else 'd7-12' if x <= 12 else 'd13+'
    return a + ' ' + b


def klen(g, s, t):
    L = t[F['L']]
    return 'L2' if L == 2 else 'L3' if L == 3 else 'L4' if L == 4 else 'L5-8' if L <= 8 else 'L9+'


def leash(g):
    return min(8, (g['w'] + g['h']) // 8)


def kleash(g, s, t):
    x = t[F['ds']] - leash(g)
    return 'inside R' if x <= 0 else 'R+1..R+4' if x <= 4 else 'beyond R+4'


def krleash(g, s, t):
    r = t[0]
    a = 'r0-50' if r <= 50 else 'r51-150' if r <= 150 else 'r151-300' if r <= 300 else 'r301+'
    return a + ' ' + kleash(g, s, t)


def kcleash(g, s, t):
    return kcells(g, s, t) + ' ' + kleash(g, s, t)


def kro5(g, s, t):
    r = t[0]
    a = 'r0-50' if r <= 50 else 'r51-150' if r <= 150 else 'r151-300' if r <= 300 else 'r301+'
    return a + ' ' + ko5(g, s, t)


def density(v):
    c = defaultdict(lambda: [0, 0.0, 0, 0])
    for g, s in v:
        for t in g['recs'][s]:
            if len(t) <= F['nown']:
                continue
            x = c[kround(g, s, t)]
            x[0] += 1
            x[1] += t[F['o5']]
            x[2] += t[F['nown']] - 1
            x[3] += t[F['nen']]
    print('  own heads within 5 tiles as a share of all own other dragons, by round (own others, enemy dragons alive)')
    for k in ('r0-50', 'r51-100', 'r101-200', 'r201-300', 'r301+'):
        x = c.get(k)
        if x and x[2]:
            print('    %-9s %s of %s own (%s)  enemies %s' % (k, f1(x[1], x[0]), f1(x[2], x[0]), pct(x[1], x[2]), f1(x[3], x[0])))


def kcells(g, s, t):
    c = g['cells']
    return '<=700' if c <= 700 else '701-1200' if c <= 1200 else '>1200'


def endstate(v):
    c = defaultdict(lambda: [0, 0, 0, 0])
    for g, s in v:
        a, b = g['final'][s][0], g['final'][1 - s][0]
        k = ('alive' if a else 'dead') + '/' + ('alive' if b else 'dead')
        x = c[k]
        x[0] += 1
        won = (g['win'] == 1) == (s == 0) and g['win'] is not None
        x[1] += 1 if won else 0
        x[2] += a
        x[3] += b
    print('  end states (this queen / the other queen): games, this side won, mean lengths')
    for k in ('alive/alive', 'alive/dead', 'dead/alive', 'dead/dead'):
        x = c[k]
        if x[0]:
            print('    %-12s %3d  won %3d  len %s / %s' % (k, x[0], x[1], f1(x[2], x[0]), f1(x[3], x[0])))
    dq = [(g, s) for g, s in v if g['decided'] == 'queen']
    won = sum(1 for g, s in dq if (g['win'] == 1) == (s == 0))
    both = [(g, s) for g, s in dq if g['final'][s][0] and g['final'][1 - s][0]]
    print('    decided on queen length: %d, this side won %d; both alive in %d (won %d)' % (
        len(dq), won, len(both), sum(1 for g, s in both if (g['win'] == 1) == (s == 0))))


def pearls(v):
    c = defaultdict(Counter)
    for g, s in v:
        for t in g['recs'][s]:
            b = c[kround(g, s, t)]
            b['n'] += 1
            pd = t[F['pd']]
            b['pd1'] += 1 if pd == 1 else 0
            b['pd1ate'] += 1 if pd == 1 and t[F['ate']] else 0
            b['pd3'] += 1 if pd <= 3 else 0
            b['pd3safe'] += 1 if pd <= 3 and t[F['ep5n']] == 0 else 0
            b['pd1safe'] += 1 if pd == 1 and t[F['ep5n']] == 0 else 0
            b['pd1safeate'] += 1 if pd == 1 and t[F['ep5n']] == 0 and t[F['ate']] else 0
            b['ate'] += t[F['ate']]
            b['L'] += t[F['L']]
            b['nown'] += t[F['nown']]
    print('  pearls by round band: turns, mean L, own dragons, pearl beside her (share; eaten), same with no enemy head <=5 steps, pearl <=3 steps, eaten /100')
    for k in ('r0-50', 'r51-100', 'r101-200', 'r201-300', 'r301+'):
        b = c.get(k)
        if b:
            n = b['n']
            print('    %-9s %6d  L %s  own %s  beside %s eaten %s | safe: %d eaten %s | <=3 steps %s | ate %s/100' % (
                k, n, f1(b['L'], n), f1(b['nown'], n), pct(b['pd1'], n), pct(b['pd1ate'], b['pd1']), b['pd1safe'], pct(b['pd1safeate'], b['pd1safe']),
                pct(b['pd3'], n), f1(100.0 * b['ate'], n)))


def firsts(v):
    first, firstthr = [], []
    for g, s in v:
        r5 = next((t[0] for t in g['recs'][s] if t[F['ep5n']] > 0), None)
        r3 = next((t[0] for t in g['recs'][s] if t[F['ep3n']] > 0), None)
        first.append(r5)
        firstthr.append(r3)
    a = sorted(x for x in first if x is not None)
    b = sorted(x for x in firstthr if x is not None)
    print('  first enemy head <=5 steps: in %d of %d games, median round %s; <=3 steps: %d games, median round %s' % (
        len(a), len(v), a[len(a) // 2] if a else '-', len(b), b[len(b) // 2] if b else '-'))
    thr = [sum(1 for t in g['recs'][s] if t[F['ep3n']] > 0) for g, s in v]
    print('  threatened turns per game: mean %s; games with 0: %d, 1-5: %d, 6-15: %d, 16+: %d' % (
        f1(sum(thr), len(thr)), sum(1 for x in thr if x == 0), sum(1 for x in thr if 1 <= x <= 5), sum(1 for x in thr if 6 <= x <= 15), sum(1 for x in thr if x > 15)))


def deaths(v):
    c = Counter()
    for g, s in v:
        f = g['fate'][s]
        if f is None:
            continue
        x = f['ds'] / (g['w'] // 2 + g['h'] // 2)
        own = f['ds']
        other = man(f['head'], g['start'][1 - s], g['w'], g['h'])
        kind = 'self' if f['own_move'] else 'ram'
        c[kind, 'n'] += 1
        c[kind, 'far'] += 1 if x >= 0.3 else 0
        c[kind, 'near'] += 1 if x < 0.15 else 0
        c[kind, 'd>8'] += 1 if own > 8 else 0
        c[kind, 'd>6'] += 1 if own > 6 else 0
        c[kind, 'd>12'] += 1 if own > 12 else 0
        c[kind, 'enemy half'] += 1 if other < own else 0
        c[kind, 'o5=0'] += 1 if f['o5'] == 0 else 0
        c[kind, 'kelp2'] += 1 if f['kelp'] >= 2 else 0
        c[kind, 'pocket'] += 1 if f['pocket'] > 0 else 0
        c[kind, 'outR'] += 1 if own > leash(g) else 0
        c[kind, 'outR2'] += 1 if own > leash(g) + 2 else 0
        c[kind, 'outR4'] += 1 if own > leash(g) + 4 else 0
    for kind in ('ram', 'self'):
        n = c[kind, 'n']
        if n:
            print('  deaths %-4s %3d: from start <0.15 of span %d, >=0.3 %d; >6 tiles %d, >8 %d, >12 %d; on the enemy half %d; no own head <=5 %d; kelp 2+ sides %d; in a pocket %d; beyond R %d, R+2 %d, R+4 %d' % (
                kind, n, c[kind, 'near'], c[kind, 'far'], c[kind, 'd>6'], c[kind, 'd>8'], c[kind, 'd>12'], c[kind, 'enemy half'], c[kind, 'o5=0'], c[kind, 'kelp2'], c[kind, 'pocket'], c[kind, 'outR'], c[kind, 'outR2'], c[kind, 'outR4']))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'online'
    games = load(('m1', 'm2', 'b1', 'b2', 'q1', 'q2', 'm3')) if mode == 'online' else load(('L0', 'L1', 'T0', 'T1'))
    groups = groups_of(games, mode)
    sel = sys.argv[2].split(',') if len(sys.argv) > 2 else None
    what = sys.argv[3].split(',') if len(sys.argv) > 3 else ['ds', 'dt', 'round', 'half', 'o5', 'cells', 'end', 'pearls', 'first', 'deaths']
    filt = sys.argv[4] if len(sys.argv) > 4 else 'all'
    if filt == 'open':
        groups = [(k, [(g, s) for g, s in v if g['scomp'][s] * 2 >= g['cells']]) for k, v in groups]
    elif filt == 'closed':
        groups = [(k, [(g, s) for g, s in v if g['scomp'][s] * 2 < g['cells']]) for k, v in groups]
    for k, v in groups:
        if sel and not any(k == x for x in sel):
            continue
        print('== %s: %d games, %d turns' % (k, len(v), sum(len(g['recs'][s]) for g, s in v)))
        if 'ds' in what:
            cut('by distance from start / half-span of the board', v, kds, ('<0.15', '0.15-0.3', '0.3-0.5', '0.5+'))
        if 'dt' in what:
            cut('by distance from start, tiles', v, kdt, ('0-4', '5-8', '9-12', '13+'))
        if 'round' in what:
            cut('by round', v, kround, ('r0-50', 'r51-100', 'r101-200', 'r201-300', 'r301+'))
        if 'half' in what:
            cut('by half of the board (nearer own start or the enemy queen start)', v, khalf, ('own half', 'midline', 'enemy half'))
        if 'o5' in what:
            cut('by own heads within 5 tiles', v, ko5, ('own5=0', 'own5=1-2', 'own5=3+'))
        if 'rd' in what:
            cut('by round and distance from start (tiles)', v, krd, [a + ' ' + b for a in ('r0-50', 'r51-150', 'r151-300', 'r301+') for b in ('d0-6', 'd7-12', 'd13+')])
        if 'len' in what:
            cut('by her length', v, klen, ('L2', 'L3', 'L4', 'L5-8', 'L9+'))
        if 'leash' in what:
            lab = ('inside R', 'R+1..R+4', 'beyond R+4')
            cut('by distance from start against R = min(8, (w+h)/8)', v, kleash, lab)
            cut('same by round', v, krleash, [a + ' ' + b for a in ('r0-50', 'r51-150', 'r151-300', 'r301+') for b in lab])
            cut('same by board size', v, kcleash, [a + ' ' + b for a in ('<=700', '701-1200', '>1200') for b in lab])
        if 'ro5' in what:
            cut('by round and own heads within 5 tiles', v, kro5, [a + ' ' + b for a in ('r0-50', 'r51-150', 'r151-300', 'r301+') for b in ('own5=0', 'own5=1-2', 'own5=3+')])
        if 'density' in what:
            density(v)
        if 'cells' in what:
            cut('by board size', v, kcells, ('<=700', '701-1200', '>1200'))
        if 'end' in what:
            endstate(v)
        if 'pearls' in what:
            pearls(v)
        if 'first' in what:
            firsts(v)
        if 'deaths' in what:
            deaths(v)


main()
