"""late-opus quick pass from shed-sonnet/data.json (one11..one16): wait splits = split round with queen length -2 next round."""
import sys, json, os
sys.dont_write_bytecode = True
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from collections import Counter

D = json.load(open('../shed-sonnet/data.json'))
G = D['games']
print('games', len(G), sorted(Counter(g['ver'] for g in G).items()), 'wins', sum(g['win'] for g in G))


def lb(L):
    return '4-5' if L <= 5 else '6-9' if L <= 9 else '10-19' if L <= 19 else '20+'


def rb(r):
    return '0-99' if r < 100 else '100-299' if r < 300 else '300+'


tab = Counter()
runs = []
for g in G:
    T = g['turns']
    W = []
    for i in range(len(T) - 1):
        W.append(T[i]['split'] and T[i + 1]['r'] == T[i]['r'] + 1 and T[i + 1]['ql'] == T[i]['ql'] - 2)
    W.append(False)
    i = 0
    while i < len(T):
        if W[i]:
            j = i
            while W[j + 1]:
                j += 1
            runs.append((g, i, j))
            for k in range(i, j + 1):
                tab[lb(T[k]['ql']), rb(T[k]['r'])] += 1
                tab[lb(T[k]['ql']), 'all'] += 1
                tab['all', rb(T[k]['r'])] += 1
                tab['all', 'all'] += 1
            i = j + 1
        else:
            i += 1
print('%-6s %6s %8s %6s %6s' % ('L', '0-99', '100-299', '300+', 'all'))
for L in ('4-5', '6-9', '10-19', '20+', 'all'):
    print('%-6s %6d %8d %6d %6d' % (L, tab[L, '0-99'], tab[L, '100-299'], tab[L, '300+'], tab[L, 'all']))
print('runs', len(runs), 'games', len({g['id'] for g, i, j in runs}), 'len dist', sorted(Counter(j - i + 1 for g, i, j in runs).items()))
big = [(g, i, j) for g, i, j in runs if g['turns'][i]['ql'] >= 10]
print('runs from 10+:', len(big), 'games', len({g['id'] for g, i, j in big}))
print('%-8s %-5s %4s %3s %4s %4s %4s %5s %5s %5s %5s %4s %3s' % ('game', 'ver', 'r0', 'n', 'L0', 'L1', 'eq', 'lead', 'd<=5', 'd<=20', 'qdead', 'qfin', 'win'))
a = Counter()
for g, i, j in big:
    T = g['turns']
    L0, L1, r1 = T[i]['ql'], T[j]['ql'] - 2, T[j]['r']
    qd = g['qdead']
    d5 = int(qd is not None and r1 <= qd <= r1 + 5)
    d20 = int(qd is not None and r1 <= qd <= r1 + 20)
    lead = int(L0 > T[i]['eq'])
    a['n'] += 1; a['lead'] += lead; a['d5'] += d5; a['d20'] += d20; a['alive'] += int(g['qfin'] > 0); a['win'] += int(g['win']); a['lost'] += L0 - L1
    a['late'] += int(T[i]['r'] >= 300); a['late_d20'] += int(T[i]['r'] >= 300 and d20); a['lead_d20'] += lead and d20; a['lead_win'] += int(lead and g['win'])
    print('%-8d %-5s %4d %3d %4d %4d %4d %5d %5d %5d %5s %4d %3d' % (g['id'], g['ver'], T[i]['r'], j - i + 1, L0, L1, T[i]['eq'], lead, d5, d20, qd if qd is not None else '-', g['qfin'], int(g['win'])))
print(dict(a))
gb = {g['id'] for g, i, j in big}
for name, sel in (('no 10+ run', lambda g: g['id'] not in gb), ('10+ run', lambda g: g['id'] in gb)):
    gs = [g for g in G if sel(g) and any(t['r'] == 300 and t['ql'] >= 10 for t in g['turns'])]
    print(name, 'queen 10+ at r300: n', len(gs), 'alive at end', sum(1 for g in gs if g['qfin'] > 0), 'wins', sum(1 for g in gs if g['win']))
# prize
pz = Counter()
for g in G:
    t = [t for t in g['turns'] if t['r'] == 350]
    if not t:
        pz['no queen turn row at r350 (dead or ended)'] += 1
        continue
    t = t[0]
    st = 'lead' if t['ql'] > t['eq'] else 'notlead'
    pz[st] += 1
    pz[st, 'win'] += int(g['win'])
    if st == 'lead' and not g['win']:
        pz['lead-loss', 'queen died' if g['qdead'] is not None else 'alive'] += 1
        print('LEADLOSS', g['id'], g['ver'], 'q@350', t['ql'], 'e@350', t['eq'], 'qdead', g['qdead'], 'qfin', g['qfin'], 'efin', g['eqfin'], 'last', g['last'])
print(sorted(pz.items(), key=str))
