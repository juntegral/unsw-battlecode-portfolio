"""Scratch (diag-one1): take rate with an enemy head in ram reach, which gate was shut, and what followed.
Usage: o1_striketab.py <set[+set]> <lo> <hi> [all|big|small]"""
import sys, json
from collections import Counter
W = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
name, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
cls = sys.argv[4] if len(sys.argv) > 4 else 'all'
gs = []
for nm in name.split('+'):
    for l in open(W + 'o1_strike-%s.jsonl' % nm):
        g = json.loads(l)
        if nm == 'live' and g['bot'] != '20850':
            continue
        if cls == 'all' or (cls == 'big') == (g['cells'] > 1200):
            gs.append(g)
n = len(gs)
print('==', name, cls, 'games', n, 'rounds %d-%d' % (lo + 1, hi), 'per game')
for s in (0, 1):
    C = Counter()
    for g in gs:
        big = g['cells'] > 1200
        for r in g['rows']:
            if r['s'] != s or not (lo < r['r'] <= hi):
                continue
            L = r['L']
            tg = [t for t in r['tg'] if not t[3]] or r['tg']
            st, tL, parts, tq, z = tg[0]
            edge = r['allies'] + 1 - r['foes'] >= 1
            units = r['units'] >= (8 if big else 1)
            worth = any(t[2] >= L for t in r['tg'])
            worth1 = any(t[2] >= L - 1 for t in r['tg'])
            gate = 'open' if (edge and units and worth) else 'edge' if (not edge and worth and units) else 'parts' if (edge and units and not worth) else 'units' if (edge and worth) else 'two+'
            C['turns'] += 1
            C['turns L%d' % L] += 1
            C['turns st%d' % st] += 1
            C['gate ' + gate] += 1
            if r['ram']:
                C['ram'] += 1
                C['ram L%d' % L] += 1
                C['ram st%d' % st] += 1
                C['ram gate ' + gate] += 1
            else:
                C['after ' + r['after']] += 1
                C['noram gate %s' % gate] += 1
                if r['after'] == 'rammed':
                    C['rammed gate %s' % gate] += 1
                    C['rammed by a head that was in reach'] += r['byin']
                    C['rammed L%d' % L] += 1
                    if gate == 'parts' and worth1:
                        C['rammed, parts gate, open at length-1'] += 1
                    if gate == 'edge':
                        C['rammed edge: allies %d foes %d' % (min(r['allies'], 2), min(r['foes'], 3))] += 1
    print('-- side', 'ours' if s == 0 else 'theirs')
    for k in sorted(C):
        print('  %-44s %7.1f' % (k, C[k] / n))
    print('  take rate %.0f%%' % (100 * C['ram'] / max(1, C['turns'])), ' rammed after not ramming %.0f%%' % (100 * C['after rammed'] / max(1, C['turns'] - C['ram'])))
