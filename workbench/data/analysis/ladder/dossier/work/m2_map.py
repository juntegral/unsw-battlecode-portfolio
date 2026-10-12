# Scratch (diag-med20): draw a whole layout from a replay: kelp, portals (letter = pair), starts (head = team letter + id,
# body = lower case), tiles a natural pearl is born on (digit = first birth round // 10, capped 9; '*' present at round 0).
# Usage: python3 m2_map.py <replay path> [x0 x1 y0 y1]
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict
from pathlib import Path

STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))


def main():
    path = sys.argv[1]
    root = replay.load(Path(path)).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    raw, cells, n = [], {}, 0
    for line in text.splitlines():
        q = line.split()
        if q[:1] == ['EDGE']:
            raw.append(tuple(map(int, q[1:4])))
        elif q[:1] == ['DRAGON']:
            for k in range(int(q[2])):
                c = (int(q[3 + 2 * k]), int(q[4 + 2 * k]))
                cells[c] = ('AB'[int(q[1])] + str(n)) if k == 0 else 'ab'[int(q[1])] + ' '
            n += 1
    edges = canonical_edges(w, h, raw)
    pid = {}
    first = {}
    rnd, actor = 0, None
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k == 0:
            rnd, actor = ev.pointer(0).i32(0), None
        elif k == 1:
            actor = ev.pointer(0).i32(0)
        elif k == 3 and actor is None and ev.pointer(0).u32(0):
            c = replay.point(ev.pointer(0).pointer(0))
            first.setdefault(c, rnd)

    def kind(x, y, d):
        k, p = edges.get(edge_id(w, h, x % w, y % h, d), (0, -1))
        if k == 2:
            return chr(ord('A') + p % 26) if True else '~'
        return '-' if k == 1 else ' '

    x0, x1, y0, y1 = (list(map(int, sys.argv[2:6])) if len(sys.argv) > 5 else [0, w - 1, 0, h - 1])
    print('size', w, h, 'spawn tiles', len(first), 'at r0', sum(1 for v in first.values() if v == 0))
    print('    ' + ''.join('%-3d' % x for x in range(x0, x1 + 1)))
    for y in range(y0, y1 + 1):
        top, mid = '   ', '%2d ' % y
        for x in range(x0, x1 + 1):
            kn, kw = kind(x, y, 0), kind(x, y, 3)
            top += '+' + (kn * 2 if kn != ' ' else '  ')
            body = cells.get((x, y))
            if body is None:
                f = first.get((x, y))
                body = '  ' if f is None else '* ' if f == 0 else str(min(9, f // 10)) + ' '
            mid += ('|' if kw == '-' else kw) + body
        print(top)
        print(mid)


main()
