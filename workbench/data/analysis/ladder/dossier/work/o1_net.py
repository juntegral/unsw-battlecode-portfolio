"""Scratch (diag-one1): net length account of a window by game class. Usage: o1_net.py <set> <lo> <hi> [all|small|big|full|gid,...]"""
import sys, json
from collections import Counter
sys.path.insert(0, '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/')
from o1_ledger import load, snap
name, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
cls = sys.argv[4] if len(sys.argv) > 4 else 'all'
gs = []
for nm in name.split('+'):
    gs += load(nm)
if cls == 'small':
    gs = [g for g in gs if g['cells'] <= 1200]
elif cls == 'big':
    gs = [g for g in gs if g['cells'] > 1200]
elif cls == 'full':
    gs = [g for g in gs if g['last'] >= hi]
elif cls != 'all':
    ids = set(map(int, cls.split(',')))
    gs = [g for g in gs if g['gid'] in ids]
n = len(gs)


def group(d):
    k = d[4]
    if k in ('rammed', 'rams', 'mate head'):
        return k
    if d[5] == 0:
        return 'boxed'
    return 'stop free' if k == 'stop' else 'misstep'


G = ('rammed', 'rams', 'boxed', 'stop free', 'misstep', 'mate head')
acc = [Counter(), Counter()]
for g in gs:
    a, b = snap(g, lo), snap(g, hi)
    for s in (0, 1):
        c = acc[s]
        c['T0'] += a[s][1]; c['T1'] += b[s][1]; c['n0'] += a[s][0]; c['n1'] += b[s][0]
        c['long0'] += a[s][2]; c['long1'] += b[s][2]
        for r, sd, role, origin, kd, L0 in g['eats']:
            if sd == s and lo < r <= hi:
                c['eat_' + origin] += 1
                c['eat'] += 1
                c['eat_by_' + role] += 1
        for d in g['deaths']:
            if d[1] == s and lo < d[0] <= hi:
                k = group(d)
                c['n:' + k] += 1
                c['L:' + k] += d[2]
                c['drop:' + k] += d[15]
                c['own:' + k] += d[10]
                c['foe:' + k] += d[11]
                c['dead'] += d[2]
                c['L2-3:' + k] += d[2] if d[2] <= 3 else 0
                c['L4-9:' + k] += d[2] if 4 <= d[2] <= 9 else 0
                c['L10+:' + k] += d[2] if d[2] >= 10 else 0
        for r, sd, L0, paid, e, ram, q, died in g['paids']:
            if sd == s and lo < r <= hi:
                c['paid'] += paid
print('set', name, 'class', cls, 'games', n, 'rounds %d-%d' % (lo + 1, hi), 'per game; ours | theirs')
o, t = acc
row = lambda lab, f: print('%-34s %8.1f %8.1f' % (lab, f(o) / n, f(t) / n))
row('dragons at start', lambda c: c['n0'])
row('dragons at end', lambda c: c['n1'])
row('total length at start', lambda c: c['T0'])
row('total length at end', lambda c: c['T1'])
row('longest at start', lambda c: c['long0'])
row('longest at end', lambda c: c['long1'])
row('change', lambda c: c['T1'] - c['T0'])
row('+ natural pearls', lambda c: c['eat_n'])
row('+ pearls of their dead', lambda c: c['eat_foe'])
row('(own dead eaten again)', lambda c: c['eat_own'])
row('(eaten by queen)', lambda c: c['eat_by_q'])
row('(eaten by longest 5+)', lambda c: c['eat_by_t'])
for k in G:
    row('- %s: dragons' % k, lambda c: c['n:' + k])
    row('  length', lambda c: c['L:' + k])
    row('  of it L2-3 / L4-9 / L10+ ...', lambda c: c['L2-3:' + k])
    row('  ', lambda c: c['L4-9:' + k])
    row('  ', lambda c: c['L10+:' + k])
    row('  pearls dropped', lambda c: c['drop:' + k])
    row('  eaten by own side', lambda c: c['own:' + k])
    row('  eaten by other side', lambda c: c['foe:' + k])
    row('  net loss (length - own eaten)', lambda c: c['L:' + k] - c['own:' + k])
row('- paid sprint segments', lambda c: c['paid'])
row('all deaths length', lambda c: c['dead'])
row('check: nat+foe+own-dead-paid', lambda c: c['eat'] - c['dead'] - c['paid'])
