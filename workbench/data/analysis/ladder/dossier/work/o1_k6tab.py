"""Scratch (meow-main07): two-dragon-start maps, local arms: first split round, heads and length at r50/r100, result.
Usage (repo root): o1_k6tab.py <arm>..."""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from o1_local import rows, snap
arms = sys.argv[1:]
R = {a: {g['folder']: g for g in rows(a)} for a in arms}
common = sorted(set.intersection(*[set(R[a]) for a in arms]))
common = [f for f in common if f.startswith(('gx_', 'ladder_tower', 'ladder_stripes', 'ladder_portals')) and ('24x12' in f or f.startswith('ladder_'))]
print('games', len(common))
tot = {a: [0, 0, 0, 0, 0] for a in arms}
for f in common:
    row = []
    for a in arms:
        g = R[a][f]
        s50, s100 = snap(g, 50)[0], snap(g, 100)[0]
        t = tot[a]
        t[0] += g['result'] == 'win'; t[1] += s50[0]; t[2] += s100[0]; t[3] += s100[1]
        row.append('%s %2d/%3d %2d/%3d' % (g['result'][:1], s50[0], s50[1], s100[0], s100[1]))
    print('%-40s' % f[:40], ' | '.join(row))
n = max(1, len(common))
for a in arms:
    t = tot[a]
    print('%-8s wins %d/%d  heads r50 %.1f  r100 %.1f  length r100 %.1f' % (a, t[0], n, t[1] / n, t[2] / n, t[3] / n))
