"""unB-opus: corridor / start-room / dead-end maps. Draw the A half as cells, B = 180 degree rotation. python3 mk.py"""
import sys, random
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'mapgen'))
from gen import Map
OUT = Path.home() / 'meow-redteam/maps/un2'
OUT.mkdir(parents=True, exist_ok=True)


class G:
    def __init__(s, w, h):
        s.w, s.h = w, h
        s.c = {}
        s.dr = []

    def rect(s, x0, y0, x1, y1, ch='.'):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                if ch == '.' and s.c.get((x, y)) == 'p':
                    continue
                s.c[(x, y)] = ch

    def path(s, pts, pearl_every=0, off=0):
        cells = []
        for (a, b), (c, d) in zip(pts, pts[1:]):
            dx, dy = (c > a) - (c < a), (d > b) - (d < b)
            x, y = a, b
            while (x, y) != (c, d):
                cells.append((x, y))
                x += dx
                y += dy
        cells.append(pts[-1])
        for i, xy in enumerate(cells):
            s.c[xy] = 'p' if pearl_every and i % pearl_every == off else s.c.get(xy, '.')
        return cells

    def write(s, name, gap=(10, 30)):
        w, h = s.w, s.h
        full = dict(s.c)
        for (x, y), ch in s.c.items():
            full[(w - 1 - x, h - 1 - y)] = ch
        m = Map(w, h, 'xy')
        for (x, y), ch in full.items():
            if ch == 'p':
                m.tiles[y * w + x] = gap
        for y in range(h):
            for x in range(w):
                k = y * w + x
                a = (x, y) in full
                if not (a and (x, (y - 1) % h) in full) or y == 0:
                    m.edges[k] = (1, -1)
                if not (a and ((x - 1) % w, y) in full) or x == 0:
                    m.edges[m.n + k] = (1, -1)
        for body in s.dr:
            m.dragons.append((0, [y * w + x for x, y in body]))
            m.dragons.append((1, [(h - 1 - y) * w + (w - 1 - x) for x, y in body]))
        (OUT / (name + '.map')).write_text(m.text(name))
        npearl = sum(1 for v in full.values() if v == 'p')
        print(name, w, h, w * h, 'floor', len(full), 'pearls', npearl)
        for y in range(h):
            print(''.join(full.get((x, y), '#') for x in range(w)))


def room(name, w, h, rw, cor, hall_x0, tr=False):
    g = G(w, h)
    ym = h // 2
    g.rect(1, ym - rw // 2, rw, ym - rw // 2 + rw - 1)
    g.path(cor)
    g.rect(hall_x0, 1, w // 2 - 1, h - 2)
    for y in range(2, h - 2, 3):
        for x in range(hall_x0 + 1, w // 2, 3):
            g.c[(x, y)] = 'p'
    g.dr = [[(2, ym), (1, ym)], [(2, ym - 1), (1, ym - 1)]]
    if tr:
        t = G(h, w)
        t.c = {(y, x): ch for (x, y), ch in g.c.items()}
        t.dr = [[(y, x) for x, y in b] for b in g.dr]
        g = t
    g.write(name)


room('ub_room3', 24, 12, 3, [(4, 6), (6, 6)], 7)
room('ub_room8u', 44, 22, 4, [(5, 11), (12, 11)], 13)
room('ub_room8o', 46, 22, 4, [(5, 11), (12, 11)], 13)
room('ub_room8t', 44, 22, 4, [(5, 11), (12, 11)], 13, True)
room('ub_room5o', 52, 20, 3, [(4, 10), (8, 10)], 9)
room('ub_sq900', 30, 30, 4, [(5, 15), (9, 15)], 10)
room('ub_room20', 40, 16, 5, [(6, 8), (9, 8), (9, 14), (9, 2), (10, 2), (15, 2)][:1] + [(9, 8), (9, 2), (15, 2), (15, 8)], 16)

rng = random.Random(7)
g = G(33, 21)
seen = {(1, 1)}
st = [(1, 1)]
g.c[(1, 1)] = '.'
while st:
    x, y = st[-1]
    nx = [(x + dx, y + dy, x + dx // 2, y + dy // 2) for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2))
          if 1 <= x + dx <= 15 and 1 <= y + dy <= 19 and (x + dx, y + dy) not in seen]
    if not nx:
        st.pop()
        continue
    a, b, c, d = rng.choice(nx)
    g.c[(a, b)] = g.c[(c, d)] = '.'
    seen.add((a, b))
    st.append((a, b))
g.c[(16, 1)] = g.c[(16, 9)] = '.'
fl = sorted(g.c)
for i, xy in enumerate(fl):
    if i % 5 == 2:
        g.c[xy] = 'p'
for xy in fl:
    if sum(1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if (xy[0] + dx, xy[1] + dy) in g.c) == 1 and xy != (1, 1):
        g.c[xy] = 'p'


def nbr(g, xy):
    return [(xy[0] + dx, xy[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if (xy[0] + dx, xy[1] + dy) in g.c]


a = (1, 1)
b = nbr(g, a)[0]
c = [n for n in nbr(g, b) if n != a][0]
d = [n for n in nbr(g, c) if n != b][0]
g.dr = [[b, a], [d, c]]
for xy in (a, b, c, d):
    g.c[xy] = '.'
g.write('ub_maze')

g = G(40, 15)
g.rect(1, 7, 19, 7)
for x in range(3, 19, 2):
    g.path([(x, 6), (x, 1)], 5, 5 if x % 4 == 1 else 3)
    g.path([(x, 8), (x, 13)], 5, 5 if x % 4 == 3 else 3)
    g.c[(x, 1)] = g.c[(x, 13)] = 'p'
g.dr = [[(2, 7), (1, 7)], [(5, 6), (5, 5)]]
for b in g.dr:
    for xy in b:
        g.c[xy] = '.'
g.write('ub_comb')

g = G(34, 17)
sp = g.path([(7, 9), (9, 9), (9, 7), (5, 7), (5, 11), (11, 11), (11, 5), (3, 5), (3, 13), (13, 13), (13, 3), (1, 3), (1, 15), (15, 15), (15, 1), (16, 1)], 4, 3)
g.rect(16, 1, 16, 15)
g.dr = [[sp[1], sp[0]], [sp[4], sp[3]]]
for b in g.dr:
    for xy in b:
        g.c[xy] = '.'
g.write('ub_spiral')

g = G(44, 9)
g.rect(1, 2, 5, 6)
g.path([(6, 4), (21, 4)], 3, 1)
g.dr = [[(4, 4), (3, 4)], [(4, 3), (3, 3)]]
g.write('ub_tworooms')

g = G(30, 16)
for y0 in (3, 7, 11):
    g.rect(1, y0, 14, y0 + 1)
g.rect(12, 3, 14, 12)
for y, dy in ((2, 0), (5, 1), (6, 0), (9, 1), (10, 0), (13, 1)):
    for x in range(2 + dy, 11, 2):
        g.c[(x, y)] = 'p'
g.dr = [[(2, 7), (1, 7)], [(2, 8), (1, 8)]]
g.write('ub_deadend')
