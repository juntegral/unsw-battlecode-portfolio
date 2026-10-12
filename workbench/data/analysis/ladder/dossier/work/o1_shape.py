"""Scratch (diag-one1): swarm shape over time (mean per game). Usage: o1_shape.py <set> <big|small|all>"""
import json, sys
sys.path.insert(0, '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work')
name, cls = sys.argv[1], sys.argv[2]
from o1_ledger import load, snap
gs = []
for nm in name.split('+'):
    gs += [g for g in load(nm) if cls == 'all' or (g['cells'] > 1200) == (cls == 'big')]
print('==', name, cls, len(gs), 'games: round | ours n T longest Q n2 n3 n4 n5-9 n10+ len10+ | theirs')
for r in (50, 100, 150, 200, 250, 300, 350, 400, 450, 499):
    row = []
    for s in (0, 1):
        v = [sum(snap(g, r)[s][k] for g in gs) / len(gs) for k in range(10)]
        row.append(' '.join('%5.1f' % x for x in v))
    print('%3d | %s | %s' % (r, row[0], row[1]))
