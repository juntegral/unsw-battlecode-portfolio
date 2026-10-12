"""cluster2.py — a second clustering on what decides the game (Claude, 2026-10-01).

analyze.py (Codex) clusters maps on the elite winners' behaviour levels (11 features). Here the features are the standardized
winner-minus-loser differences of the same games (what separates winners from losers on the map) plus the elimination rate
and whether the halves are connected. Same method as analyze.py: z-scored features, Euclidean distance / sqrt(features),
Ward merges, silhouettes for k = 2..6. Output: cache/cluster2.json and a printed table.
"""
import json, pathlib, math, itertools
O = pathlib.Path(__file__).resolve().parent / 'cache'
S = json.loads((O / 'stats.json').read_text())['atlas']; G = json.loads((O / 'geometry.json').read_text())
FEATS = ['heads100', 'vor100', 'nat100', 'raid100', 'lineSac300', 'sac300Len', 'lateBirths', 'exposure6']
labels = sorted(S)
X0 = []
for k in labels:
    p = S[k]['paired']; row = []
    for f in FEATS:
        v = p.get(f, {}).get('standardized'); row.append(v if v is not None else 0.0)
    row.append(S[k]['eliminationRate']['value']); row.append(0.0 if G[k]['headPath'] is None else 1.0)
    X0.append(row)
names = FEATS + ['elimination', 'connected']
m = [sum(r[j] for r in X0) / len(X0) for j in range(len(names))]
sd = [math.sqrt(sum((r[j] - m[j]) ** 2 for r in X0) / len(X0)) or 1 for j in range(len(names))]
X = [[(r[j] - m[j]) / sd[j] for j in range(len(names))] for r in X0]
D = [[math.sqrt(sum((a - b) ** 2 for a, b in zip(x, y)) / len(names)) for y in X] for x in X]
groups = [[i] for i in range(len(labels))]; cuts = {len(groups): [g[:] for g in groups]}; merges = []
cen = lambda g: [sum(X[i][j] for i in g) / len(g) for j in range(len(names))]
while len(groups) > 1:
    best = None
    for i, j in itertools.combinations(range(len(groups)), 2):
        a, b = groups[i], groups[j]; c = len(a) * len(b) / (len(a) + len(b)) * sum((x - y) ** 2 for x, y in zip(cen(a), cen(b)))
        if best is None or c < best[0]: best = (c, i, j)
    c, i, j = best; merges.append([[labels[v] for v in groups[i]], [labels[v] for v in groups[j]], c])
    groups = [g for k, g in enumerate(groups) if k not in (i, j)] + [sorted(groups[i] + groups[j])]; cuts[len(groups)] = [g[:] for g in groups]
sil = {}
for k in range(2, 7):
    gs = cuts[k]; v = []
    for i in range(len(labels)):
        own = next(g for g in gs if i in g)
        if len(own) == 1: v.append(0); continue
        a = sum(D[i][j] for j in own if j != i) / (len(own) - 1); b = min(sum(D[i][j] for j in g) / len(g) for g in gs if g is not own); v.append((b - a) / max(a, b))
    sil[k] = sum(v) / len(v)
out = {'features': names, 'raw': dict(zip(labels, X0)), 'z': dict(zip(labels, X)), 'cuts': {k: [[labels[i] for i in g] for g in cuts[k]] for k in range(2, 7)},
       'silhouettes': sil, 'merges': merges, 'distances': {labels[i]: {labels[j]: D[i][j] for j in range(len(labels))} for i in range(len(labels))}}
(O / 'cluster2.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
print('features', names)
for k in labels: print(f'{k:22s}', ' '.join(f'{v:6.2f}' for v in dict(zip(labels, X0))[k]))
print('silhouettes', {k: round(v, 3) for k, v in sil.items()})
for k in range(2, 6): print(k, out['cuts'][k])
