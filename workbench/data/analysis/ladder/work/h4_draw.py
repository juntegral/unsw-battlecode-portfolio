# Own look (analyst, run 20261007-0400): draw a layout as text with its kelp, portals and the pearls on the board at one round,
# and list for every pearl tile how many tiles can be reached from it within 8 steps without passing back through a given neighbour.
# Usage: python3 data/analysis/ladder/work/h4_draw.py <battle> <game> <round>
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict
from pathlib import Path


def main():
    battle, game, want = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    folder = Path('data/online/ladder') / str(battle)
    root = replay.load(folder / ('M%d.replay' % game)).root()
    text = root.text(0)
    W, H = map(int, text.splitlines()[0].split()[1:3])
    raw = []
    bodies = dict()
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
        elif q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
    edges = canonical_edges(W, H, raw)
    present = set()
    ever = defaultdict(int)
    rnd = 0
    snap = None
    snapb = None
    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k == 'roundStart':
            rnd = p.i32(0)
            if rnd == want:
                snap = set(present)
                snapb = dict((z, list(bb)) for z, bb in bodies.items())
        elif k == 'tileChange':
            c = replay.point(p.pointer(0))
            if p.u32(0):
                present.add(c)
                ever[c] += 1
            else:
                present.discard(c)
        elif k == 'dragonUpdate':
            i = p.i32(0)
            h = replay.point(p.pointer(0))
            tail = replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != h:
                b.appendleft(h)
            while len(b) > 1 and b[-1] != tail:
                b.pop()
        elif k == 'dragonSplit':
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
        elif k == 'dragonDeath':
            bodies.pop(p.i32(0))
    heads = dict()
    for z, bb in snapb.items():
        for n, c in enumerate(bb):
            heads[c] = str(z % 10) if n == 0 else '+'
    print('size', W, H, 'round', want, ' o = pearl now, . = tile that spawned a pearl at some time, digit = head, + = body, | and - = kelp, P = portal edge')
    for y in range(H):
        top = ''
        mid = ''
        for x in range(W):
            kn = edges.get(edge_id(W, H, x, y, 0), (0, -1))[0]
            kw = edges.get(edge_id(W, H, x, y, 3), (0, -1))[0]
            top += '+' + ('--' if kn == 1 else 'PP' if kn == 2 else '  ')
            c = (x, y)
            ch = heads.get(c, 'o' if c in snap else '.' if c in ever else ' ')
            mid += ('|' if kw == 1 else 'P' if kw == 2 else ' ') + ch + ' '
        print(top)
        print(mid + '  y=%d' % y)
    print('spawn counts of the busiest tiles', sorted(((v, c) for c, v in ever.items()), reverse=True)[:16])


main()
