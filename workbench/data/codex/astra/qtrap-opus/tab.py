import sys, os, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from o1_local import rows, snap
tab = {}
base = {}


def first_diff(a, b):
    if a is None:
        return 'n/a'
    ev_a = sorted([e[0], 'e', e[1]] for e in a[0]) + sorted([d[0], 'd', d[1], d[2]] for d in a[1])
    ev_b = sorted([e[0], 'e', e[1]] for e in b[0]) + sorted([d[0], 'd', d[1], d[2]] for d in b[1])
    ev_a.sort(key=str)
    ev_b.sort(key=str)
    sa, sb = set(map(str, ev_a)), set(map(str, ev_b))
    odd = [eval(x)[0] for x in sa ^ sb]
    return 'same' if not odd else 'r%d' % min(odd)


for arm in ('qt_off', 'qt_m', 'qt_t'):
    for g in rows(arm):
        qd = [(d[0], d[4]) for d in g['deaths'] if d[1] == 0 and d[6] == 1]
        s = snap(g, 100)
        pearls = sum(1 for e in g['eats'] if e[1] == 0 and e[0] <= 100)
        base[(g['folder'], arm)] = [g['eats'], g['deaths']]
        div = first_diff(base.get((g['folder'], 'qt_off')), base[(g['folder'], arm)])
        tab[(g['folder'], arm)] = '%s/%s r%d qdeath=%s pearls100=%d drag100=%d qlen100=%d endq=%d:%d diverges=%s' % (
            g['result'], g['how'], g['last'], '%d %s' % qd[0] if qd else '-', pearls, s[0][0], s[0][3], g['ends'][0][3], g['ends'][1][3], div)
for k in sorted(tab):
    print('%-18s %-6s %s' % (k[0].replace('-seed1-side0', ''), k[1], tab[k]))
