"""late-opus quick pass 2 from shed-sonnet/data.json: wait-split runs starting at r100+ from 10+."""
import sys, json, os
sys.dont_write_bytecode = True
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from collections import Counter

G = json.load(open('../shed-sonnet/data.json'))['games']
runs = []
for g in G:
    T = g['turns']
    W = [T[i]['split'] and T[i + 1]['r'] == T[i]['r'] + 1 and T[i + 1]['ql'] == T[i]['ql'] - 2 for i in range(len(T) - 1)] + [False]
    i = 0
    while i < len(T):
        if W[i]:
            j = i
            while W[j + 1]:
                j += 1
            runs.append((g, i, j))
            i = j + 1
        else:
            i += 1
late = [(g, i, j) for g, i, j in runs if g['turns'][i]['ql'] >= 10 and g['turns'][i]['r'] >= 100]
lg = {g['id'] for g, i, j in late}
b = Counter()
for g, i, j in late:
    T = g['turns']
    L0, L1, r1 = T[i]['ql'], T[j]['ql'] - 2, T[j]['r']
    qd = g['qdead']
    lead = int(L0 > T[i]['eq'])
    b['runs'] += 1; b['turns'] += j - i + 1; b['lost'] += L0 - L1; b['lead'] += lead
    b['d5'] += int(qd is not None and r1 <= qd <= r1 + 5); b['d20'] += int(qd is not None and r1 <= qd <= r1 + 20)
    b['lead_d20'] += int(lead and qd is not None and r1 <= qd <= r1 + 20)
    b['multi'] += int(j > i); b['multi_lost'] += (L0 - L1) if j > i else 0
    b['lead_lost_after'] += int(lead and L1 <= T[i]['eq'])
print(dict(b), 'games', len(lg), 'of', len(G))
gs = [g for g in G if g['id'] in lg]
print('games with a late 10+ run: n', len(gs), 'wins', sum(1 for g in gs if g['win']), 'queen alive at end', sum(1 for g in gs if g['qfin'] > 0),
      'length lost per game', round(b['lost'] / max(1, len(gs)), 1))
for name, sel in (('no late 10+ run', lambda g: g['id'] not in lg), ('late 10+ run', lambda g: g['id'] in lg)):
    for lead in (0, 1):
        gs = [g for g in G if sel(g) and any(t['r'] == 300 and t['ql'] >= 10 and (t['ql'] > t['eq']) == bool(lead) for t in g['turns'])]
        print(name, '| queen 10+ at r300, lead', lead, ': n', len(gs), 'alive at end', sum(1 for g in gs if g['qfin'] > 0), 'wins', sum(1 for g in gs if g['win']))
alive300 = [g for g in G if any(t['r'] == 300 for t in g['turns'])]
print('queen alive at r300:', len(alive300), 'of', len(G), '; 10+ at r300:', sum(1 for g in alive300 if any(t['r'] == 300 and t['ql'] >= 10 for t in g['turns'])))
dead_by = Counter()
for g in G:
    qd = g['qdead']
    dead_by['alive' if qd is None else '<100' if qd < 100 else '100-299' if qd < 300 else '300-349' if qd < 350 else '350+'] += 1
print('our queen death round', sorted(dead_by.items()))
