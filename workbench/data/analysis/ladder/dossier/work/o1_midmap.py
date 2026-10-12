"""Scratch (meow-main07): per map, natural pearls per 100 dragon turns in r101-200 and r201-300, ours/theirs, by set."""
import sys, json
from collections import defaultdict
W = 'data/analysis/ladder/dossier/work/'
sets = sys.argv[1:]
T = defaultdict(dict)
tot = {s: [[0, 0, 0, 0], [0, 0, 0, 0]] for s in sets}
for s in sets:
    for l in open(W + 'o1_mid-%s.jsonl' % s):
        g = json.loads(l)
        c = defaultdict(int)
        for side, w, k, v in g['C']:
            c[(side, w, k)] += v
        cell = []
        for w in (1, 2):
            a = (c[(0, w, 'pearls nat')], c[(0, w, 'turns')], c[(1, w, 'pearls nat')], c[(1, w, 'turns')])
            for i in range(4):
                tot[s][w - 1][i] += a[i]
            cell.append('%3d/%4d %3d/%4d' % a)
        T[(g['cells'], g['map'])][s] = ' | '.join(cell)
print('map (cells): per set  r101-200 ours nat/turns theirs nat/turns | r201-300 same')
for (cells, m), d in sorted(T.items()):
    print('%-16s %5d' % (m[:16], cells))
    for s in sets:
        print('   %-3s %s' % (s, d.get(s, '-')))
for s in sets:
    r = []
    for w in (0, 1):
        a = tot[s][w]
        r.append('ours %.2f theirs %.2f per 100 turns (turns %d / %d)' % (100 * a[0] / max(1, a[1]), 100 * a[2] / max(1, a[3]), a[1], a[3]))
    print(s, '| r101-200', r[0], '| r201-300', r[1])
