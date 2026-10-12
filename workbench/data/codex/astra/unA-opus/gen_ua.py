"""unA-opus: 9 small/medium portal + closed-room maps -> ~/meow-redteam/maps/un2/ua_*.map (xy = 180 degree symmetry)."""
from pathlib import Path
OUT = Path.home() / 'meow-redteam/maps/un2'
OUT.mkdir(parents=True, exist_ok=True)


class Map:
    def __init__(self, name, w, h, sym="xy", limit=64):
        self.name, self.w, self.h, self.sym, self.limit = name, w, h, sym, limit
        self.tiles = [(0, 0)] * (w * h)
        self.edges = [(0, -1)] * (2 * w * h)
        self.dragons = []
        self.pid = 0

    def tile(self, x, y): return (y % self.h) * self.w + (x % self.w)
    def edge(self, x, y, vertical=False): return (self.w * self.h if vertical else 0) + self.tile(x, y)

    def mirror(self, k, edge=False):
        n = self.w * self.h
        vertical = edge and k >= n
        x, y = (k % n) % self.w, (k % n) // self.w
        if "y" in self.sym: x = (self.w - (0 if vertical else 1) - x) % self.w
        if "x" in self.sym: y = (self.h - (1 if vertical else 0) - y) % self.h
        return (n if vertical else 0) + y * self.w + x

    def mirrored_tile(self, k):
        x, y = k % self.w, k // self.w
        return (self.h - 1 - y) * self.w + (self.w - 1 - x)

    def bed(self, x, y, lo, hi):
        k = self.tile(x, y); self.tiles[k] = (lo, hi); self.tiles[self.mirrored_tile(k)] = (lo, hi)

    def wall(self, x, y, vertical=False):
        k = self.edge(x, y, vertical); self.edges[k] = (1, -1); self.edges[self.mirror(k, True)] = (1, -1)

    def portal(self, a, b):
        self.edges[a] = self.edges[b] = (2, self.pid)
        ma, mb = self.mirror(a, True), self.mirror(b, True)
        if {ma, mb} != {a, b}:
            self.edges[ma] = self.edges[mb] = (2, self.pid + 1); self.pid += 1
        self.pid += 1

    def room(self, x0, y0, rw, rh, lo=1, hi=10, beds=True):
        for x in range(x0, x0 + rw): self.wall(x, y0); self.wall(x, y0 + rh)
        for y in range(y0, y0 + rh): self.wall(x0, y, True); self.wall(x0 + rw, y, True)
        for x in range(x0, x0 + rw):
            for y in range(y0, y0 + rh):
                if beds: self.bed(x, y, lo, hi)
                else: self.tiles[self.tile(x, y)] = (0, 0); self.tiles[self.mirrored_tile(self.tile(x, y))] = (0, 0)

    def starter(self, body):
        self.dragons.append((0, [self.tile(x, y) for x, y in body]))
        self.dragons.append((1, [self.mirrored_tile(k) for k in self.dragons[-1][1]]))

    def save(self):
        self.dragons.sort(key=lambda d: 0)
        rows = [f"MAP {self.w} {self.h}", f"SYMMETRY {self.sym}", f"MAP_NAME {self.name}", f"UNIT_LIMIT {self.limit}", f"TILE_COUNT {len(self.tiles)}"]
        rows += [f"TILE {i % self.w} {i // self.w} {lo} {hi}" for i, (lo, hi) in enumerate(self.tiles)]
        rows.append(f"EDGE_COUNT {len(self.edges)}")
        for k, (kind, pid) in enumerate(self.edges):
            n = self.w * self.h; i = k % n; x, y = i % self.w, i // self.w
            rows.append(f"EDGE {(2 * y + (k >= n)) * (self.w + 1) + x} {kind} {pid}")
        rows.append(f"DRAGON_COUNT {len(self.dragons)}")
        rows += [f"DRAGON {team} {len(body)} " + " ".join(f"{k % self.w} {k // self.w}" for k in body) for team, body in self.dragons]
        rows.append("END")
        (OUT / (self.name + ".map")).write_text("\n".join(rows) + "\n")
        npair = self.pid
        print(self.name, self.w, self.h, self.w * self.h, 'pairs', npair, 'beds', sum(1 for t in self.tiles if t != (0, 0)))


def scatter(m, mod, lo, hi, ymax=None):
    for y in range(ymax if ymax else m.h // 2):
        for x in range(m.w):
            if (x * 7 + y * 3) % mod == 0: m.bed(x, y, lo, hi)


def rooms_map(name, w, h, sizes, mod=6, start_len=3):
    """Closed pearl rooms of the given sizes in the top half; one portal each, its open end on rows near A's start."""
    m = Map(name, w, h)
    hh = h // 2
    scatter(m, mod, 5, 60)
    sy = hh - 2
    m.starter([(4 - i, sy) for i in range(start_len)])
    m.starter([(4 - i, sy - 2 if sy >= 3 else sy + 1) for i in range(2)])
    x = 7
    for i, s in enumerate(sizes):
        if x + s + 1 >= w: break
        m.room(x, 0 if s == 1 and hh < 6 else 1, s, s)
        ry = 0 if s == 1 and hh < 6 else 1
        room_edge = m.edge(x, ry, True)
        open_edge = m.edge(x + (1 if s > 1 else 0), ry + s + 1 + (i % 2), True) if ry + s + 2 + (i % 2) <= hh - 0 else m.edge(x - 2, ry, True)
        m.portal(open_edge, room_edge)
        x += s + 3
    m.save()


def box_map(name, w, h, mod=4):
    """A's start area is a closed 6x3 box with two portal exits; food is outside."""
    m = Map(name, w, h)
    hh = h // 2
    scatter(m, mod, 3, 40)
    bx, by = 2, 1
    m.room(bx, by, 6, 3, beds=False)
    m.bed(bx + 5, by, 400, 500)
    m.starter([(bx + 3 - i, by + 1) for i in range(3)])
    m.starter([(bx + 1 + i, by + 2) for i in range(2)])
    m.portal(m.edge(bx + 6, by + 1, True), m.edge(w // 2 - 2, hh - 2, True))
    m.portal(m.edge(bx + 2, by + 3), m.edge(bx + 10, by + 2))
    m.save()


def chain_map(name, w, h):
    """Start box -> pearl room 3x3 -> pearl room 3x3 -> open field, every link a portal."""
    m = Map(name, w, h)
    hh = h // 2
    scatter(m, 4, 3, 40)
    m.room(1, 1, 5, 3, beds=False)
    m.room(8, 1, 3, 3, 2, 20)
    m.room(13, 1, 3, 3, 2, 20)
    m.starter([(4 - i, 2) for i in range(3)])
    m.starter([(2 + i, 3) for i in range(2)])
    m.portal(m.edge(6, 2, True), m.edge(8, 2, True))
    m.portal(m.edge(11, 2, True), m.edge(13, 2, True))
    m.portal(m.edge(16, 2, True), m.edge(w - 6, hh - 2, True))
    m.save()


def many_map(name, w, h):
    """8 pairs (4 per half): rooms of 1, 4, 9 and one open-to-open pair landing beside a wall stub."""
    m = Map(name, w, h)
    hh = h // 2
    scatter(m, 6, 5, 60)
    m.starter([(4 - i, hh - 2) for i in range(3)])
    m.starter([(4 - i, hh - 4) for i in range(2)])
    m.starter([(2, 1), (1, 1)])
    m.room(8, 1, 1, 1); m.portal(m.edge(7, hh - 2, True), m.edge(8, 1, True))
    m.room(12, 1, 2, 2); m.portal(m.edge(11, hh - 3, True), m.edge(12, 1, True))
    m.room(17, 1, 3, 3); m.portal(m.edge(16, hh - 2, True), m.edge(17, 2, True))
    for y in range(1, 5): m.wall(26, y, True)
    m.wall(25, 1); m.wall(25, 5)
    m.portal(m.edge(23, hh - 2, True), m.edge(25, 3, True))
    m.save()


def single_map(name, w, h):
    """Two sealed halves, one portal pair on the centre wall, far (vertically) from both starts."""
    m = Map(name, w, h)
    for y in range(h): m.wall(w // 2, y, True); m.wall(0, y, True)
    for y in range(h):
        for x in range(w // 2):
            if y < 6:
                if (x + y) % 5 == 0: m.tiles[m.tile(x, y)] = (300, 500); m.tiles[m.mirrored_tile(m.tile(x, y))] = (300, 500)
            elif (x * 7 + y * 3) % 4 == 0:
                m.tiles[m.tile(x, y)] = (2, 20); m.tiles[m.mirrored_tile(m.tile(x, y))] = (2, 20)
    m.starter([(6 - i, 2) for i in range(3)])
    m.starter([(6 - i, 4) for i in range(2)])
    e = m.edge(w // 2, h // 2 + 3, True)
    m.portal(e, m.mirror(e, True))
    m.save()


rooms_map('ua_r1_200', 20, 10, [1, 1, 1])
rooms_map('ua_r4_384', 24, 16, [2, 2, 2])
rooms_map('ua_r9_600', 30, 20, [3, 3, 3])
rooms_map('ua_mix_900', 36, 25, [1, 2, 3, 3, 2])
box_map('ua_box_288', 24, 12)
box_map('ua_box_704', 32, 22)
chain_map('ua_chain_448', 28, 16)
many_map('ua_many_512', 32, 16)
single_map('ua_single_750', 30, 25)
