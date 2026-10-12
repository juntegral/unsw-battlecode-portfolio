"""Scratch (diag-one1): head-on collisions across sides in a window: rammer start length x steps x paid, victim length."""
import sys, json
from collections import Counter
sys.path.insert(0, '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/')
from o1_ledger import load
name, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
cls = sys.argv[4] if len(sys.argv) > 4 else 'all'
gs = []
for nm in name.split('+'):
    gs += load(nm)
gs = [g for g in gs if cls == 'all' or (cls == 'big') == (g['cells'] > 1200)]
n = len(gs)
for s in (0, 1):
    C, V, S, D = Counter(), Counter(), Counter(), Counter()
    tot = 0
    for g in gs:
        for d in g['deaths']:
            if d[4] == 'rammed' and d[1] == s and lo < d[0] <= hi:
                L0, steps, paid, gp, q = d[18]
                tot += 1
                C[(min(L0, 6), min(steps, 4), min(paid, 3))] += 1
                V[min(d[2], 11) if d[2] < 5 else 5 if d[2] < 10 else 10] += 1
                S[min(steps, 5)] += 1
                D[(min(L0, 6), 'longer' if d[2] > L0 else 'equal' if d[2] == L0 else 'shorter')] += 1
    print('==', name, cls, 'rams ON', 'ours' if s == 0 else 'theirs', 'per game %.1f' % (tot / n), 'games', n)
    print(' victim length:', {k: round(v / n, 1) for k, v in sorted(V.items())})
    print(' rammer steps:', {k: round(v / n, 1) for k, v in sorted(S.items())})
    print(' rammer (L0, steps, paid):', {k: round(v / n, 1) for k, v in sorted(C.items()) if v / n >= 0.3})
    print(' rammer L0 vs victim:', {k: round(v / n, 1) for k, v in sorted(D.items())})
