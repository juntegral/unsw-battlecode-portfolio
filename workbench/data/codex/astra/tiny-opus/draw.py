"""ASCII map with walls and pearl spawners: python3 -B data/codex/astra/tiny-opus/draw.py <map file>"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from o1_scan import edge_id, canonical_edges
lines = open(sys.argv[1]).read().splitlines()
W, H = map(int, lines[0].split()[1:3])
tiles = {}; raw = []; drag = []
for l in lines:
    q = l.split()
    if q and q[0] == 'TILE': tiles[(int(q[1]), int(q[2]))] = (int(q[3]), int(q[4]))
    elif q and q[0] == 'EDGE': raw.append(tuple(map(int, q[1:4])))
    elif q and q[0] == 'DRAGON': drag.append(q)
edges = canonical_edges(W, H, raw)
print([l for l in lines if not l.startswith(('TILE', 'EDGE '))][:12])
kinds = {}
for e, (k, p) in edges.items(): kinds[k] = kinds.get(k, 0) + 1
print('edge kinds', kinds, 'edges', len(edges))
# rows of edges: row 2y = horizontal edges above tile row y? probe by edge_id
heads = {}
for q in drag:
    heads[(int(q[3]), int(q[4]))] = 'AB'[int(q[1])] if q[1] in '01' else q[1]
for y in range(H):
    top = ''; mid = ''
    for x in range(W):
        up = edges.get(edge_id(W, H, x, y, 0), (0, -1))[0] if True else 0
        top += '+' + ('--' if up == 1 else '==' if up == 2 else '  ')
    for x in range(W):
        lf = edges.get(edge_id(W, H, x, y, 3), (0, -1))[0]
        t = tiles.get((x, y), (0, 0))
        c = heads.get((x, y)) or ('.' if t == (0, 0) else 'o' if t[0] <= 1 and t[1] <= 100 else 'p' if t[0] <= 1 else 'L')
        mid += ('|' if lf == 1 else ':' if lf == 2 else ' ') + c + ' '
    print(top); print(mid)
