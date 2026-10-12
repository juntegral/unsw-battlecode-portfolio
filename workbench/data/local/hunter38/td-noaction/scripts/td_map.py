#!/usr/bin/env python3
"""Draw tower_defense and test its symmetry. Usage: td_map.py MAPFILE"""
import sys
W = H = 0
tiles, edges, dragons = {}, {}, []
for line in open(sys.argv[1]):
    p = line.split()
    if not p: continue
    if p[0] == 'MAP': W, H = int(p[1]), int(p[2])
    elif p[0] == 'TILE': tiles[(int(p[1]), int(p[2]))] = (int(p[3]), int(p[4]))
    elif p[0] == 'EDGE': edges[int(p[1])] = (int(p[2]), int(p[3]))
    elif p[0] == 'DRAGON': dragons.append((int(p[1]), [(int(p[3 + 2*k]), int(p[4 + 2*k])) for k in range(int(p[2]))]))
row = W + 1
# the board wraps: the file gives each tile its north and west edge only (1024 = 2*32*16), so row H is row 0 and column W is column 0
def north(x, y): return edges.get(2 * (y % H) * row + (x % W), (0, -1))[0]
def west(x, y): return edges.get((2 * (y % H) + 1) * row + (x % W), (0, -1))[0]
sym = {(400, 500): 'L', (1, 1): '*', (1, 100): 'o', (1, 500): ',', (0, 0): '.'}
occ = {}
for i, (team, cells) in enumerate(dragons):
    for k, c in enumerate(cells):
        occ[c] = ('AB'[team] if k == 0 else 'ab'[team])
print('legend: L gap 400-500, * gap 1-1, o gap 1-100, , gap 1-500, . never; A/B head a/b body; | - kelp, : = portal')
for y in range(H + 1):
    print(''.join('+' + {0: ' ', 1: '-', 2: '='}[north(x, y)] for x in range(W)) + '+')
    if y == H: break
    print(''.join({0: ' ', 1: '|', 2: ':'}[west(x, y)] + occ.get((x, y), sym.get(tiles.get((x, y), (0, 0)), '?')) for x in range(W)) + {0: ' ', 1: '|', 2: ':'}[west(W, y)])
# symmetry: 180-degree rotation and the two mirrors, tiles only then edges
def tile_ok(f): return sum(1 for c, g in tiles.items() if tiles.get(f(c)) != g)
print('tile gap mismatches: rot180', tile_ok(lambda c: (W-1-c[0], H-1-c[1])), 'mirror x', tile_ok(lambda c: (W-1-c[0], c[1])), 'mirror y', tile_ok(lambda c: (c[0], H-1-c[1])))
bad = 0
for y in range(H):
    for x in range(W):
        # rot180: north of (x,y) <-> south of (W-1-x,H-1-y) = north of (W-1-x, H-y); west of (x,y) <-> east of mirror = west of (W-x, H-1-y)
        if north(x, y) != north(W-1-x, H-y): bad += 1
        if west(x, y) != west(W-x, H-1-y): bad += 1
print('edge mismatches under rot180:', bad)
bx = by = 0
for y in range(H):
    for x in range(W):
        if north(x, y) != north(W-1-x, y): bx += 1
        if west(x, y) != west(W-x, y): bx += 1
        if north(x, y) != north(x, H-y): by += 1
        if west(x, y) != west(x, H-1-y): by += 1
print('edge mismatches under mirror x:', bx, 'mirror y:', by)
print('dragons:', dragons)
for team, cells in dragons:
    print('  team', 'AB'[team], cells, '-> rot180', [(W-1-x, H-1-y) for x, y in cells], 'mirror-x', [(W-1-x, y) for x, y in cells])
from collections import Counter
print('tile classes', Counter(tiles.values()), 'edges kinds', Counter(k for k, _ in edges.values()))
