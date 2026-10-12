"""Scratch (diag-one1): length ledger of a round window, per game and summed. Usage: o1_ledger.py <set> [lo hi] [-g]"""
import sys, json
from collections import Counter
W = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
name = sys.argv[1] if len(sys.argv) > 1 else ''
lo, hi = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 and sys.argv[2].isdigit() else (100, 300)
pg = '-g' in sys.argv
KINDS = ('rammed', 'rams', 'stop', 'wall', 'own body', 'mate body', 'foe body', 'mate head')


def load(name):
    gs = [json.loads(l) for l in open(W + 'o1_scan-%s.jsonl' % name)]
    if name == 'live':
        gs = [g for g in gs if g['bot'] == '20850']
    return gs


def snap(g, r):
    r = min(r, g['last'])
    if str(r) in g['snaps']:
        return g['snaps'][str(r)]
    return g['snaps'][str(g['last'])]


def ledger(g, lo, hi):
    out = []
    a, b = snap(g, lo), snap(g, hi)
    for s in (0, 1):
        c = Counter()
        c['T0'], c['T1'], c['n0'], c['n1'] = a[s][1], b[s][1], a[s][0], b[s][0]
        for r, sd, role, origin, kd, L0 in g['eats']:
            if sd == s and lo < r <= hi:
                c['eat'] += 1
                c['eat_' + origin] += 1
        for d in g['deaths']:
            if d[1] == s and lo < d[0] <= hi:
                c['dead'] += d[2]
                c['deadn'] += 1
                c['d_' + d[4]] += d[2]
                c['n_' + d[4]] += 1
                c['drop'] += d[15]
                c['back'] += d[10]
                c['lost'] += d[11]
        for r, sd, L0, paid, e, ram, q, died in g['paids']:
            if sd == s and lo < r <= hi:
                c['paid'] += paid
                c['paid_ram' if ram else 'paid_other'] += paid
        for r, sd, Lb, Lp, Lc, q in g['splits']:
            if sd == s and lo < r <= hi:
                c['splits'] += 1
        c['resid'] = c['T1'] - c['T0'] - c['eat'] + c['dead'] + c['paid']
        out.append(c)
    return out


if __name__ == '__main__':
    gs = load(name)
    tot = [Counter(), Counter()]
    for g in gs:
        L = ledger(g, lo, hi)
        for s in (0, 1):
            tot[s].update(L[s])
        if pg:
            o, t = L
            print('%d %-15s %4d %-5s %-7s last %3d | us T %3d>%3d n %2d>%2d eat %3d (n%3d own%3d foe%3d) dead %3d/%2d paid %2d | them T %3d>%3d n %2d>%2d eat %3d (n%3d own%3d foe%3d) dead %3d/%2d paid %2d | resid %d %d' % (
                g['gid'], g['map'][:15], g['cells'], g['result'], g['how'], g['last'],
                o['T0'], o['T1'], o['n0'], o['n1'], o['eat'], o['eat_n'], o['eat_own'], o['eat_foe'], o['dead'], o['deadn'], o['paid'],
                t['T0'], t['T1'], t['n0'], t['n1'], t['eat'], t['eat_n'], t['eat_own'], t['eat_foe'], t['dead'], t['deadn'], t['paid'], o['resid'], t['resid']))
    n = len(gs)
    print('set', name, 'games', n, 'window', lo, hi, '(per game)')
    keys = ['T0', 'T1', 'n0', 'n1', 'eat', 'eat_n', 'eat_own', 'eat_foe', 'dead', 'deadn', 'paid', 'paid_ram', 'paid_other', 'splits', 'drop', 'back', 'lost', 'resid']
    keys += ['d_' + k for k in KINDS] + ['n_' + k for k in KINDS]
    for k in keys:
        print('%-14s %8.1f %8.1f' % (k, tot[0][k] / n, tot[1][k] / n))
