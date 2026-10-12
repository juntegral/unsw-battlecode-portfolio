"""Scratch (diag-one1): 25-round bins. Usage: o1_bins.py <set[+set]> <big|small|all|gid>"""
import json, sys
from collections import Counter
sys.path.insert(0, '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work')
name, cls = sys.argv[1], sys.argv[2]
from o1_ledger import load, snap
gs = []
for nm in name.split('+'):
    gs += [g for g in load(nm) if cls == 'all' or (cls.isdigit() and g['gid'] == int(cls)) or (not cls.isdigit() and (g['cells'] > 1200) == (cls == 'big'))]
n = len(gs)
B = [Counter(), Counter()]
for g in gs:
    for r, s, role, origin, kd, L0 in g['eats']:
        b = (r - 1) // 25 if r > 0 else 0
        B[s][(b, 'eat_' + origin)] += 1
        if role == 't':
            B[s][(b, 'eat_top')] += 1
    for d in g['deaths']:
        b = (d[0] - 1) // 25 if d[0] > 0 else 0
        k = d[4] if d[4] in ('rammed', 'rams') else 'boxed' if d[5] == 0 else 'stopfree' if d[4] == 'stop' else 'other'
        B[d[1]][(b, 'L_' + k)] += d[2]
        B[d[1]][(b, 'n_' + k)] += 1
        if d[2] >= 10:
            B[d[1]][(b, 'L10_' + k)] += d[2]
    for r, s, Lb, Lp, Lc, q in g['splits']:
        B[s][((r - 1) // 25 if r > 0 else 0, 'split')] += 1
cols = ['eat_n', 'eat_foe', 'eat_own', 'eat_top', 'split', 'n_rammed', 'L_rammed', 'n_rams', 'L_rams', 'n_boxed', 'L_boxed', 'n_stopfree', 'L_stopfree', 'L_other']
print('==', name, cls, n, 'games; per game; rounds | units total longest |', ' '.join(cols))
for s in (0, 1):
    print('-- ours' if s == 0 else '-- theirs')
    for b in range(20):
        hi = min(499, b * 25 + 25)
        v = [sum(snap(g, hi)[s][k] for g in gs) / n for k in (0, 1, 2)]
        print('%3d-%3d | %5.1f %6.1f %5.1f | ' % (b * 25 + 1, hi, *v) + ' '.join('%6.1f' % (B[s][(b, c)] / n) for c in cols))
