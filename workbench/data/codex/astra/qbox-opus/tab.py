"""Per game: our queen's death, pearls by r100, dragons at r100. Usage (from ROOT): tab.py <arm> [<arm> ...]"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from o1_local import rows, snap
from collections import defaultdict
agg = defaultdict(lambda: defaultdict(list))
for arm in sys.argv[1:]:
    for g in rows(arm):
        qd = [d for d in g['deaths'] if d[1] == 0 and d[6]]
        oq = [d for d in g['deaths'] if d[1] == 1 and d[6]]
        p100 = sum(1 for e in g['eats'] if e[1] == 0 and e[0] <= 100)
        u100 = snap(g, 100)[0][0]
        q = 'r%d L%d %s free %d' % (qd[0][0], qd[0][2], qd[0][4], qd[0][5]) if qd else 'alive L%d' % g['ends'][0][3]
        print('%-9s %-44s %-5s %-7s queen %-28s | pearls<=r100 %3d dragons@r100 %2d | end T %d/%d longest %d/%d | foe queen %s' % (
            arm, g['folder'], g['result'], g['how'], q, p100, u100, g['ends'][0][1], g['ends'][1][1], g['ends'][0][2], g['ends'][1][2],
            ('dead r%d' % oq[0][0]) if oq else 'alive L%d' % g['ends'][1][3]))
        m = g['folder'].split('-seed')[0]
        a = agg[arm][m]
        a.append((p100, u100, qd[0][0] if qd else 999, 1 if g['result'] == 'win' else 0, 1 if qd and qd[0][0] <= 50 else 0))
print()
for arm in sys.argv[1:]:
    for m, a in sorted(agg[arm].items()):
        n = len(a)
        print('%-9s %-28s n=%d pearls<=r100 %.1f dragons@r100 %.1f queen alive at end %d/%d dead<=r50 %d wins %d' % (
            arm, m, n, sum(x[0] for x in a) / n, sum(x[1] for x in a) / n, sum(1 for x in a if x[2] == 999), n, sum(x[4] for x in a), sum(x[3] for x in a)))
