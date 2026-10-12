# Scratch (diag-topopen): draw the walls around a tile and give the size of the walled region it lies in (cap 48, portals shut).
# Usage: python3 to_map.py <replay path> <x> <y> [radius]
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import deque
from pathlib import Path

STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))


def main():
    path, cx, cy = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    rad = int(sys.argv[4]) if len(sys.argv) > 4 else 5
    root = replay.load(Path(path)).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    raw = [tuple(map(int, line.split()[1:4])) for line in text.splitlines() if line.split()[:1] == ['EDGE']]
    edges = canonical_edges(w, h, raw)

    def kind(x, y, d):
        return edges.get(edge_id(w, h, x % w, y % h, d), (0, -1))[0]

    seen = {(cx, cy)}
    q = deque([(cx, cy)])
    while q and len(seen) < 48:
        x, y = q.popleft()
        for d in range(4):
            if kind(x, y, d) == 0:
                t = ((x + STEP[d][0]) % w, (y + STEP[d][1]) % h)
                if t not in seen:
                    seen.add(t)
                    q.append(t)
    print('walled region of', (cx, cy), ':', len(seen), '(48 = that or more)')
    for y in range(cy - rad, cy + rad + 1):
        top = ''
        mid = ''
        for x in range(cx - rad, cx + rad + 1):
            kn = kind(x, y, 0)
            kw = kind(x, y, 3)
            top += '+' + ('--' if kn == 1 else '~~' if kn == 2 else '  ')
            mid += ('|' if kw == 1 else '~' if kw == 2 else ' ') + ('XX' if (x, y) == (cx, cy) else '..' if (x % w, y % h) in seen else '  ')
        print(top)
        print(mid + '   y=%d' % (y % h))


main()
