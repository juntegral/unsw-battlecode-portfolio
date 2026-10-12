"""Scratch: describe one layout from a replay header (size, walls, portals, components, starts, spawn tiles)."""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))


class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        self.edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in self.edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.portals = portals
        self.moves = []
        for y in range(h):
            for x in range(w):
                row = []
                for d in range(4):
                    dx, dy = STEP[d]
                    e = edge_id(w, h, x, y, d)
                    kind, pid = self.edges.get(e, (0, -1))
                    if kind == 2:
                        partner = [z for z in portals[pid] if z != e][0]
                        ry, px = divmod(partner, w + 1)
                        dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                    else:
                        dest = ((y + dy) % h) * w + (x + dx) % w
                    row.append((kind, dest))
                self.moves.append(row)
        self.adj = [sorted({dest for kind, dest in row if kind != 1}) for row in self.moves]


def main():
    path = sys.argv[1]
    draw = len(sys.argv) > 2
    root = replay.load(Path(path)).root()
    lines = root.text(0).splitlines()
    w, h = map(int, lines[0].split()[1:3])
    raw, tiles, starts = [], {}, []
    for l in lines:
        q = l.split()
        if not q:
            continue
        if q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
        elif q[0] == 'TILE':
            tiles[int(q[2]) * w + int(q[1])] = (int(q[3]), int(q[4]))
        elif q[0] == 'DRAGON':
            starts.append((int(q[1]), int(q[2]), int(q[3]), int(q[4])))
        elif q[0] in ('MAP', 'SYMMETRY', 'MAP_NAME'):
            print(l)
    g = Geo(w, h, raw)
    ek = Counter(k for k, p in g.edges.values())
    print('edge kinds', dict(ek), 'portal ids', len(g.portals))
    comp = [-1] * (w * h)
    sizes = []
    for s in range(w * h):
        if comp[s] >= 0:
            continue
        comp[s] = len(sizes)
        q = deque([s]); n = 0
        while q:
            c = q.popleft(); n += 1
            for kind, d in g.moves[c]:
                if kind == 0 and comp[d] < 0:
                    comp[d] = comp[s]; q.append(d)
        sizes.append(n)
    print('components without portals', len(sizes), sorted(sizes, reverse=True)[:30])
    deg = Counter(sum(1 for k, d in g.moves[c] if k != 1) for c in range(w * h))
    print('open sides per tile', dict(sorted(deg.items())))
    gaps = Counter(tiles.values())
    print('spawn gaps (min,max): tiles', sorted(gaps.items(), key=lambda z: -z[1])[:20])
    rate = sum(2.0 / (a + b) for a, b in tiles.values() if b > 0)
    print('expected spawn attempts per round', round(rate, 3), 'spawning tiles', sum(1 for a, b in tiles.values() if b > 0))
    byc = defaultdict(float)
    for c, (a, b) in tiles.items():
        if b > 0:
            byc[comp[c]] += 2.0 / (a + b)
    print('rate by component (size, rate/round):', sorted(((sizes[k], round(v, 3)) for k, v in byc.items()), reverse=True)[:20])
    pc = []
    for c in range(w * h):
        for d in range(4):
            if g.moves[c][d][0] == 2:
                pc.append((c % w, c // w, 'NESW'[d], g.moves[c][d][1] % w, g.moves[c][d][1] // w))
    print('portal sides', len(pc))
    for z in pc:
        print('   portal at', z[:3], '->', z[3:], 'comp size', sizes[comp[z[1] * w + z[0]]], '->', sizes[comp[z[4] * w + z[3]]])
    for s in starts:
        print('   start team', s[0], 'len', s[1], 'head', s[2:], 'comp size', sizes[comp[s[3] * w + s[2]]])
    if not draw:
        return
    fast = sorted({a + b for a, b in tiles.values() if b > 0})
    print('gap sums', fast)
    heads = {(s[2], s[3]): 'AB'[s[0]] for s in starts}
    order = sorted(range(len(sizes)), key=lambda i: -sizes[i])
    rank = {cid: n for n, cid in enumerate(order)}
    for y in range(h):
        row = ''
        for x in range(w):
            c = y * w + x
            a, b = tiles[c]
            ch = '.' if b == 0 else ('o' if (a + b) > 2 * fast[0] else 'O')
            if rank[comp[c]] > 0 and ch == '.':
                ch = ','
            if (x, y) in heads:
                ch = heads[(x, y)]
            east = g.moves[c][1][0]
            row += ch + ('|' if east == 1 else ':' if east == 2 else ' ')
        print(row)
        under = ''
        for x in range(w):
            c = y * w + x
            south = g.moves[c][2][0]
            under += ('-' if south == 1 else '~' if south == 2 else ' ') + ' '
        print(under)


main()
