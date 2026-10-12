#!/usr/bin/env python3
"""c_tiles.py <game_id> [upto=150]: every fountain tile of the map (10+ natural pearls per 500 rounds in the pooled
supply map) in one game: which half it is in, its shape (open sides of the cell = degree; cells within 4 path steps =
ball, 41 in the open), path distance from each queen spawn, the round each team first had it in view (7x7 square of a
head) and first ate on it, natural pearls eaten on it by each team, rounds a pearl lay on it and rounds a body covered
it up to <upto>, and own / enemy deaths without a ram on the tile.
Then a summary by shape class for each half: dead end (degree 1), corridor (degree 2 and ball <= 20), other.
"""
import csv
import json
import sys
from collections import Counter, defaultdict

sys.dont_write_bytecode = True
import c_lib  # noqa: E402
from c_lib import GAMES, Hooks2, Stop, Walk2, tname  # noqa: E402

gid = sys.argv[1]
upto = int(sys.argv[2]) if len(sys.argv) > 2 else 150
info = GAMES[gid]
sup = json.load(open("c_out/supply_%s.json" % info["map"].lower().replace(" ", "_")))
HOT = {}
for key, v in sup["cells"].items():
    if v / sup["games"] >= 10:
        x, y = key.split(",")
        HOT[(int(x), int(y))] = v / sup["games"]


class T(Hooks2):
    def __init__(self):
        self.seen = {"A": {}, "B": {}}
        self.first = {"A": {}, "B": {}}
        self.eaten = {"A": Counter(), "B": Counter()}
        self.lying = Counter()
        self.body = Counter()
        self.deaths = {"A": Counter(), "B": Counter()}
        self._view = {}
        self.spawn = {}
        self.dspawn = {}

    def view(self, b, cell):
        v = self._view.get(cell)
        if v is None:
            v = self._view[cell] = tuple(c for c in HOT if b.cheb(cell, c) <= 3)
        return v

    def round_start(self, g, r):
        b = g.board
        if not self.spawn:
            for s in "AB":
                self.spawn[s] = b.starts[b.queen[s]]
                self.dspawn[s] = b.bfs(self.spawn[s], 10 ** 9)
        if r > upto:
            raise Stop
        occ = c_lib.occupied(g)
        for c in HOT:
            if c in g.pearls:
                self.lying[c] += 1
            elif c in occ:
                self.body[c] += 1
        for d, body in g.bodies.items():
            for c in self.view(b, body[0]):
                self.seen[g.teams[d]].setdefault(c, r)

    def moved(self, g, did, head, step_index, ate):
        for c in self.view(g.board, head):
            self.seen[g.teams[did]].setdefault(c, g.round)

    def eat(self, g, did, cell, origin):
        if origin[0] == "natural" and cell in HOT:
            s = g.teams[did]
            self.eaten[s][cell] += 1
            self.first[s].setdefault(cell, g.round)

    def death(self, g, did, reason, length, body, actor):
        if reason != "headon" and body[0] in HOT:
            self.deaths[g.teams[did]][body[0]] += 1


t = T()
g = Walk2(info["replay_path"])
try:
    g.run(t)
except Stop:
    pass
b = g.board
nm = {s: tname(info, s) for s in "AB"}
print(f"=== TILES {gid} {info['map']} | A = {nm['A']} B = {nm['B']} | rounds 0-{upto} | {len(HOT)} fountain tiles | queen spawns {t.spawn}")
print("  half cell | pooled rate per 500 rounds | open sides, cells within 4 steps | path distance from A spawn / B spawn | first in view A / B | first eaten A / B | natural eaten A / B | rounds a pearl lay / a body covered | non-ram deaths on it A / B")
rows = []
summ = defaultdict(Counter)
for c in sorted(HOT, key=lambda c: (t.dspawn["A"].get(c, 999) - t.dspawn["B"].get(c, 999), c)):
    da, db = t.dspawn["A"].get(c, 999), t.dspawn["B"].get(c, 999)
    half = "A" if da < db else "B" if db < da else "-"
    deg, ball = b.degree(c), b.ball(c, 4)
    shape = "dead end" if deg == 1 else "corridor" if deg == 2 and ball <= 20 else "open"
    fa, fb = t.first["A"].get(c), t.first["B"].get(c)
    print(f"  {half} ({c[0]:2d},{c[1]:2d}) | {HOT[c]:5.1f} | deg {deg} ball {ball:2d} {shape:8s} | {da:3d} / {db:3d} | seen {str(t.seen['A'].get(c, '-')):>3s} / {str(t.seen['B'].get(c, '-')):>3s} | "
          f"ate {str(fa if fa is not None else '-'):>3s} / {str(fb if fb is not None else '-'):>3s} | n {t.eaten['A'][c]:2d} / {t.eaten['B'][c]:2d} | lay {t.lying[c]:3d} body {t.body[c]:3d} | deaths {t.deaths['A'][c]} / {t.deaths['B'][c]}")
    for s in "AB":
        o = "B" if s == "A" else "A"
        if half == s:
            k = (s, shape)
            summ[k]["tiles"] += 1
            summ[k]["own_ate_tiles"] += t.eaten[s][c] > 0
            summ[k]["enemy_ate_tiles"] += t.eaten[o][c] > 0
            summ[k]["own_n"] += t.eaten[s][c]
            summ[k]["enemy_n"] += t.eaten[o][c]
            summ[k]["lying"] += t.lying[c]
            summ[k]["body"] += t.body[c]
            summ[k]["own_deaths"] += t.deaths[s][c]
            summ[k]["enemy_deaths"] += t.deaths[o][c]
print("  summary by half and shape: tiles | tiles the own team ate from / the enemy ate from | natural pearls eaten there by own / by enemy | share of tile-rounds with a pearl lying / with a body | non-ram deaths on the tile own / enemy")
for k in sorted(summ):
    v = summ[k]
    tr = max(1, v["tiles"] * (upto + 1))
    print(f"    {k[0]} ({nm[k[0]]}) half, {k[1]:8s}: {v['tiles']:3d} tiles | own ate from {v['own_ate_tiles']:3d}, enemy from {v['enemy_ate_tiles']:3d} | pearls own {v['own_n']:4d} enemy {v['enemy_n']:4d} | "
          f"lying {100 * v['lying'] / tr:3.0f}% body {100 * v['body'] / tr:3.0f}% | deaths own {v['own_deaths']} enemy {v['enemy_deaths']}")
