# Scratch (diag-feeding): does length protect our queen? Deaths of our queen per 100 rounds after round 300 by her length,
# by whether their queen is alive, and by how many of ours are alive. Same for our longest non-queen. Reads fd_scan-*.jsonl.
import json
from collections import Counter
from pathlib import Path

G = []
for k in range(4):
    G += [json.loads(l) for l in Path('data/analysis/ladder/dossier/work/fd_scan-%d.jsonl' % k).open()]
for lo in (200, 300):
    expo, dead = Counter(), Counter()
    for g in G:
        s = g['series']
        last = g['last_round']
        for r in range(lo + 1, last + 1):
            a = s[r]
            if a[3] == 0:
                continue
            L = a[3]
            lb = 'L2-4' if L <= 4 else 'L5-9' if L <= 9 else 'L10-19' if L <= 19 else 'L20+'
            foe = 'their queen dead' if a[8] == 0 else 'their queen alive'
            nb = 'n<=10' if a[0] <= 10 else 'n11-30' if a[0] <= 30 else 'n31+'
            big = 'cells>600' if g['cells'] > 600 else 'cells<=600'
            nxt = s[r + 1][3] if r + 1 <= last else g['final'][3]
            died = int(nxt == 0)
            # a game that ends by our elimination in this round also counts as her death; a win by eliminating them does not
            for key in ((lb, foe, big), (foe, big)):
                expo[key] += 1
                dead[key] += died
    print('== our queen, rounds after', lo, '==')
    for key in sorted(expo, key=lambda k: (len(k), k)):
        if expo[key] >= 100:
            print('  ', key, 'queen-rounds', expo[key], 'deaths', dead[key], 'per 100 rounds %.2f' % (100.0 * dead[key] / expo[key]))
