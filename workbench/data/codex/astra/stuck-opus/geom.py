"""stuck-opus: static map geometry from a replay's map text: neighbour table, portal cells, dead-end cells."""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import edge_id, canonical_edges
from collections import deque, defaultdict
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))


def geometry(text):
    lines = text.splitlines()
    W, H = map(int, lines[0].split()[1:3])
    N = W * H
    bodies, teams, raw = {}, {}, []
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * W + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q and q[0] == 'EDGE':
            raw.append((int(q[1]), int(q[2]), int(q[3])))
    edges = canonical_edges(W, H, raw)
    portals = defaultdict(list)
    for e, (k, p) in edges.items():
        if k == 2:
            portals[p].append(e)
    nb = [None] * N
    pcell = set()
    nwall = 0
    for y in range(H):
        for x in range(W):
            out = []
            for d in range(4):
                e = edge_id(W, H, x, y, d)
                kind, pid = edges.get(e, (0, -1))
                if kind == 1:
                    nwall += 1
                    continue
                if kind == 2:
                    pcell.add(y * W + x)
                    partner = [z for z in portals[pid] if z != e][0]
                    prow, px = divmod(partner, W + 1)
                    py = prow // 2
                    out.append(((py - (d == 0)) % H) * W + (px - (d == 3)) % W)
                else:
                    dx, dy = STEP[d]
                    out.append(((y + dy) % H) * W + (x + dx) % W)
            nb[y * W + x] = out
    # dead-end cells: prune cells with at most one open side until none is left; depth = pruning wave (1 = the innermost tip)
    deg = [len(set(nb[c]) - {c}) for c in range(N)]
    alive = [True] * N
    dead = {}
    fr = [c for c in range(N) if deg[c] <= 1]
    wave = 1
    while fr:
        nx = []
        for c in fr:
            if not alive[c]:
                continue
            alive[c] = False
            dead[c] = wave
            for n in set(nb[c]):
                if alive[n]:
                    deg[n] -= 1
                    if deg[n] <= 1:
                        nx.append(n)
        fr = nx
        wave += 1
    def wall(x, y, d):
        return edges.get(edge_id(W, H, x, y, d), (0, -1))[0] == 1
    return dict(wall=wall, W=W, H=H, N=N, nb=nb, pcell=pcell, nwall=nwall, portals=portals, dead=dead, bodies=bodies, teams=teams)
