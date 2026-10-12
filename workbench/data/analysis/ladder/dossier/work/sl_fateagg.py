# Scratch (diag-split): tables from sl_fate-*.jsonl: what becomes of the child and of the parent after a split,
# by the class of the parent's state on the turn of the split. Prints only.
# Usage: python3 data/analysis/ladder/dossier/work/sl_fateagg.py
import json
from collections import defaultdict

D = 'data/analysis/ladder/dossier/work/'
acc = {'O': defaultdict(lambda: [0] * 20), 'R': defaultdict(lambda: [0] * 20)}
games = {'O': 0, 'R': 0}
for k in range(4):
    for line in open(D + 'sl_fate-%d.jsonl' % k):
        g = json.loads(line)
        games[g['tm']] += 1
        for name, v in g['fate'].items():
            q = name.split('|')
            if name.startswith('vol'):
                keys = ['V|' + q[0] + '|' + q[1]]
                if q[3] in ('N0', 'N1', 'N2'):
                    keys.append('W|' + q[0] + '|' + q[1] + '|' + ('L4' if q[2] == 'L0' else 'L5+'))
            else:
                keys = ['C|' + q[0], 'D|' + q[0] + '|' + q[1], 'B|' + q[0] + '|' + q[2], 'ALL']
            for key in keys:
                a = acc[g['tm']][key]
                for z in range(20):
                    a[z] += v[z]
print('games', games)
print('per split followed for 20 rounds: child dead within 2 / 5 / 20 rounds %, boxed in within 5 %, rammed or ramming within 5 %, pearls eaten in 20 rounds, ate at all %; then the same for the parent; last: pearls of both')
names = sorted(set(acc['O']) | set(acc['R']))
for name in names:
    line = '%-26s' % name
    for tm in 'OR':
        v = acc[tm][name]
        if v[1] < 30:
            line += ' | %s n<30' % tm
            continue
        c, p = v[1], v[10]
        line += ' | %s %6.1f/g child %2.0f %2.0f %2.0f box %2.0f ram %2.0f eat %.2f any %2.0f; parent %2.0f %2.0f %2.0f box %2.0f ram %2.0f eat %.2f any %2.0f; both eat %.2f' % (
            tm, v[0] / games[tm], 100 * v[2] / c, 100 * v[3] / c, 100 * v[4] / c, 100 * v[5] / c, 100 * v[6] / c, v[7] / c, 100 * v[8] / c,
            100 * v[11] / p, 100 * v[12] / p, 100 * v[13] / p, 100 * v[14] / p, 100 * v[15] / p, v[16] / p, 100 * v[17] / p, (v[7] + v[16]) / c)
    print(line)
