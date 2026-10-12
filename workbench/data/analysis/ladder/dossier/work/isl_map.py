# Scratch (diag-islands): ASCII render of a .map file. Read-only.
# Usage: python3 data/analysis/ladder/dossier/work/isl_map.py <map file>
import sys
from collections import Counter
from pathlib import Path

lines = Path(sys.argv[1]).read_text().splitlines()
W = H = 0
tiles, edges, dragons = {}, {}, []
for line in lines:
    q = line.split()
    if not q:
        continue
    if q[0] == 'MAP':
        W, H = int(q[1]), int(q[2])
    elif q[0] == 'TILE':
        tiles[(int(q[1]), int(q[2]))] = (int(q[3]), int(q[4]))
    elif q[0] == 'EDGE':
        edges[int(q[1])] = (int(q[2]), int(q[3]))
    elif q[0] == 'DRAGON':
        n = int(q[2])
        dragons.append((int(q[1]), [(int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(n)]))
print('size', W, H, 'tiles', len(tiles), 'edges', len(edges), 'dragons', len(dragons))
gaps = Counter(v for v in tiles.values())
print('gap classes (min,max): count', sorted(gaps.items()))
kinds = Counter(k for k, p in edges.values())
print('edge kinds', dict(kinds))
heads = {b[0]: 'AB'[t] for t, b in dragons}
body = {c: 'ab'[t] for t, b in dragons for c in b[1:]}
PORT = 'abcdefghijklmnopqrstuvwxyz'


def cls(g):
    if g[1] == 0:
        return '.'
    m = (g[0] + g[1]) / 2
    return '#' if m <= 15 else '+' if m <= 60 else ':'


out = []
for y in range(H):
    top, mid = '', ''
    for x in range(W):
        k, p = edges.get((2 * y) * (W + 1) + x, (0, -1))
        top += ' ' + ('-' if k == 1 else PORT[p % 26] if k == 2 else ' ')
        k, p = edges.get((2 * y + 1) * (W + 1) + x, (0, -1))
        c = heads.get((x, y)) or body.get((x, y)) or cls(tiles.get((x, y), (0, 0)))
        mid += ('|' if k == 1 else PORT[p % 26] if k == 2 else ' ') + c
    k, p = edges.get((2 * y + 1) * (W + 1) + W, (0, -1))
    mid += '|' if k == 1 else PORT[p % 26] if k == 2 else ' '
    out.append(top)
    out.append(mid)
top = ''
for x in range(W):
    k, p = edges.get((2 * H) * (W + 1) + x, (0, -1))
    top += ' ' + ('-' if k == 1 else PORT[p % 26] if k == 2 else ' ')
out.append(top)
print('\n'.join(out))
print('legend: # mean gap<=15, + <=60, : slower, . never; A/B start heads; letters on edges = portal ids')
for t, b in dragons:
    print('dragon', 'AB'[t], len(b), b[0])
