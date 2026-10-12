"""Extreme size/shape/supply maps (tag uc). Same directive/edge format as unseen/make_maps.py."""
from pathlib import Path

OUT = Path.home() / "meow-redteam/maps/un2"
OUT.mkdir(parents=True, exist_ok=True)


class Map:
    def __init__(self, name, w, h, sym="xy", limit=64):
        self.name, self.w, self.h, self.sym, self.limit = name, w, h, sym, limit
        self.tiles = [(0, 0)] * (w * h)
        self.edges = [(0, -1)] * (2 * w * h)
        self.dragons = []

    def tile(self, x, y):
        return y * self.w + x

    def mt(self, k):
        x, y = k % self.w, k // self.w
        if "y" in self.sym:
            x = self.w - 1 - x
        if "x" in self.sym:
            y = self.h - 1 - y
        return y * self.w + x

    def bed(self, x, y, lo, hi):
        k = self.tile(x, y)
        self.tiles[k] = (lo, hi)
        self.tiles[self.mt(k)] = (lo, hi)

    def starter(self, body):
        ks = [self.tile(x, y) for x, y in body]
        self.dragons.append((0, ks))
        self.dragons.append((1, [self.mt(k) for k in ks]))

    def save(self):
        occ = [k for _, b in self.dragons for k in b]
        assert len(occ) == len(set(occ)), self.name
        rows = [f"MAP {self.w} {self.h}", f"SYMMETRY {self.sym}", f"MAP_NAME {self.name}",
                f"UNIT_LIMIT {self.limit}", f"TILE_COUNT {len(self.tiles)}"]
        rows += [f"TILE {i % self.w} {i // self.w} {lo} {hi}" for i, (lo, hi) in enumerate(self.tiles)]
        rows.append(f"EDGE_COUNT {len(self.edges)}")
        n = self.w * self.h
        for k, (kind, pid) in enumerate(self.edges):
            i = k % n
            x, y = i % self.w, i // self.w
            raw = (2 * y + (k >= n)) * (self.w + 1) + x
            rows.append(f"EDGE {raw} {kind} {pid}")
        rows.append(f"DRAGON_COUNT {len(self.dragons)}")
        rows += [f"DRAGON {t} {len(b)} " + " ".join(f"{k % self.w} {k // self.w}" for k in b) for t, b in self.dragons]
        rows.append("END")
        (OUT / (self.name + ".map")).write_text("\n".join(rows) + "\n")
        print(self.name, self.w, self.h, len(self.dragons), sum(1 for t in self.tiles if t != (0, 0)))


def beds(m, mod, lo=8, hi=30):
    occ = {k for _, b in m.dragons for k in b}
    for y in range(m.h):
        for x in range(m.w):
            if (x + y) % mod == 0 and m.tile(x, y) not in occ and m.mt(m.tile(x, y)) not in occ:
                m.bed(x, y, lo, hi)


m = Map("uc_tiny7x7", 7, 7)
m.starter([(1, 0), (0, 0)])
m.starter([(1, 2), (0, 2)])
beds(m, 4)
m.save()

m = Map("uc_tiny7x9", 7, 9)
m.starter([(2, 1), (1, 1), (0, 1)])
m.starter([(2, 3), (1, 3), (0, 3)])
beds(m, 4)
m.save()

m = Map("uc_tiny9x9_2", 9, 9)
m.starter([(2, 1), (1, 1), (0, 1)])
m.starter([(2, 3), (1, 3), (0, 3)])
beds(m, 4)
m.save()

m = Map("uc_tiny9x9_6", 9, 9)
for i in range(3):
    m.starter([(1, i), (0, i)])
    m.starter([(5, i), (4, i)])
beds(m, 4)
m.save()

m = Map("uc_thin7x200", 7, 200)
m.starter([(1, 6), (1, 5), (1, 4), (1, 3)])
m.starter([(2, 16), (2, 15), (2, 14), (2, 13)])
beds(m, 7)
m.save()

m = Map("uc_thin200x7", 200, 7)
m.starter([(6, 1), (5, 1), (4, 1), (3, 1)])
m.starter([(16, 0), (15, 0), (14, 0), (13, 0)])
beds(m, 7)
m.save()

m = Map("uc_sparse3000", 60, 50)
m.starter([(6, 3), (5, 3), (4, 3), (3, 3)])
m.starter([(6, 6), (5, 6), (4, 6), (3, 6)])
m.starter([(6, 9), (5, 9), (4, 9), (3, 9)])
m.bed(12, 5, 8, 30); m.bed(30, 12, 8, 30); m.bed(20, 22, 8, 30)
m.save()

m = Map("uc_rich16", 16, 16)
m.starter([(6, 3), (5, 3), (4, 3), (3, 3)])
m.starter([(6, 5), (5, 5), (4, 5), (3, 5)])
beds(m, 1, 1, 10)
m.save()

m = Map("uc_many12", 16, 16)
for y in range(1, 7):
    m.starter([(3, y), (2, y)])
    m.starter([(10, y), (9, y)])
beds(m, 5)
m.save()

m = Map("uc_adj0", 20, 20, sym="y")
m.starter([(9, 9), (8, 9), (7, 9), (6, 9)])
m.starter([(9, 12), (8, 12), (7, 12), (6, 12)])
beds(m, 6)
m.save()

m = Map("uc_adj1", 21, 20, sym="y")
m.starter([(9, 9), (8, 9), (7, 9), (6, 9)])
m.starter([(9, 12), (8, 12), (7, 12), (6, 12)])
beds(m, 6)
m.save()
