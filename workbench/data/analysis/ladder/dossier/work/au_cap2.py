"""Scratch (diag-australia): what an even trade started by us is worth, from the stretches where our code already takes
it (59+ of ours alive), and how much of r100-299 each big layout spends below that count. Reads au_ev-*.jsonl."""
import json
from collections import defaultdict, Counter
from pathlib import Path

D = Path('data/analysis/ladder/dossier/work')
games = []
for n in range(4):
    with open(D / ('au_ev-%d.jsonl' % n)) as f:
        for line in f:
            games.append(json.loads(line))
BIG = [g for g in games if g['w'] * g['h'] > 1200]


def start_len(e):
    for p in range(0, 8):
        L0 = e['Lm'] + p
        if p == max(0, e['k'] - 1 - (L0 + 3) // 4):
            return L0
    return e['Lm']


acc = defaultdict(Counter)
share = defaultdict(Counter)
for g in BIG:
    s = {x[0]: x for x in g['snaps']}
    for b in range(4, 12):
        if b * 25 in s and (b + 1) * 25 in s:
            cap = min(s[b * 25][1][0], s[(b + 1) * 25][1][0]) >= 59
            share[g['layout']]['bins'] += 1
            share[g['layout']]['below'] += int(not cap)
            share[g['layout']]['won_' + g['result']] += 0
    for e in g['hos']:
        if not e['cross'] or not 100 <= e['r'] <= 299:
            continue
        b = e['r'] // 25
        if b * 25 not in s or (b + 1) * 25 not in s:
            continue
        cap = min(s[b * 25][1][0], s[(b + 1) * 25][1][0]) >= 59
        L0 = start_len(e)
        even = e['Lv'] < max(5, L0 + 2) and e['Lv'] >= L0 and L0 <= 4
        key = (e['ms'], 'cap' if cap else 'below', 'even target' if even else 'other')
        a = acc[key]
        a['n'] += 1
        a['mover_lost'] += L0; a['victim_lost'] += e['Lv']
        v = 'u' if e['ms'] == 't' else 't'
        a['mover_back'] += e['eat'][e['ms']]; a['victim_back'] += e['eat'][v]
        a['drop'] += e['drop']
        a['edge'] += int(e['near_m'] >= e['near_v'])
print('big layouts r100-299; even target = victim at least as long as the mover (length 2-4 at its turn start) and below our size rule max(5, length+2)')
print('mover | our count | target | meetings | mover start length | victim length | mover side net a meeting | victim side net | drops eaten by mover side | mover side not outnumbered within 5 steps')
for key in sorted(acc):
    a = acc[key]
    n = a['n']
    print('%s | %s | %s | %d | %.2f | %.2f | %.2f | %.2f | %.3f | %.3f' % (
        'we' if key[0] == 'u' else 'they', key[1], key[2], n, a['mover_lost'] / n, a['victim_lost'] / n,
        (a['mover_back'] - a['mover_lost']) / n, (a['victim_back'] - a['victim_lost']) / n, a['mover_back'] / max(1, a['drop']), a['edge'] / n))
print()
print('share of 25-round bins in r100-299 with fewer than 59 of our dragons, by layout')
for lay, c in sorted(share.items(), key=lambda z: -z[1]['below'] / z[1]['bins']):
    gs = [g for g in BIG if g['layout'] == lay]
    print('  %s: %d of %d bins (%.2f); record %d of %d' % (lay, c['below'], c['bins'], c['below'] / c['bins'],
                                                      sum(g['result'] == 'win' for g in gs), len(gs)))
# games by whether we were at the cap at r150
print()
print('big-layout games by our dragon count at r150: games, won')
c = defaultdict(Counter)
for g in BIG:
    s = {x[0]: x for x in g['snaps']}
    if 150 not in s:
        continue
    k = '59+' if s[150][1][0] >= 59 else '50-58' if s[150][1][0] >= 50 else 'under 50'
    c[(g['layout'], k)]['n'] += 1
    c[(g['layout'], k)]['won'] += int(g['result'] == 'win')
    c[('ALL', k)]['n'] += 1
    c[('ALL', k)]['won'] += int(g['result'] == 'win')
for key in sorted(c):
    print('  ', key, c[key]['n'], c[key]['won'])
