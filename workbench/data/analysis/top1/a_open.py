#!/usr/bin/env python3
"""a_open.py <game_id> [team=306] [upto=100]: opening economy per 10 rounds for both teams (sub-session A).

Per 10-round block and team: units and total length at the block start, natural pearls eaten, corpse pearls eaten,
splits, self-kills (noaction), other own deaths, mean path-free (wrapped manhattan) distance of non-queen heads from
the team's queen spawn, and natural pearls lying on the board within 10 cells (chebyshev) of that spawn.
"""
import csv
import sys
from collections import Counter

import lib

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
gid = sys.argv[1]
team = int(sys.argv[2]) if len(sys.argv) > 2 else 306
upto = int(sys.argv[3]) if len(sys.argv) > 3 else 100
info = GAMES[gid]


class Stop(Exception):
    pass


class O(lib.Hooks):
    def __init__(self):
        self.c = Counter()
        self.rows = {}
        self.spawn = {}

    def round_start(self, g, r):
        b = g.board
        if r == 0:
            for s in "AB":
                self.spawn[s] = g.bodies[b.queen[s]][0]
        if r > upto:
            raise Stop
        if r % 10 == 0:
            row = {}
            nat = [c for c, v in g.pearls.items() if v[0] == "natural"]
            for s in "AB":
                ls = [(d, body) for d, body in g.bodies.items() if g.teams[d] == s]
                others = [b.manhattan(body[0], self.spawn[s]) for d, body in ls if d != b.queen[s]]
                row[s] = (len(ls), sum(len(x[1]) for x in ls), round(sum(others) / max(1, len(others)), 1),
                          sum(1 for c in nat if b.cheb(c, self.spawn[s]) <= 10))
            row["nat"] = len(nat)
            self.rows[r] = row

    def eat(self, g, did, cell, origin):
        self.c[(g.round // 10 * 10, g.teams[did], "nat" if origin[0] == "natural" else "corpse")] += 1

    def split(self, g, parent, child, before, plen, clen):
        self.c[(g.round // 10 * 10, g.teams[parent], "split")] += 1

    def death(self, g, did, reason, length, body, actor):
        self.c[(g.round // 10 * 10, g.teams[did], "selfkill" if reason == "noaction" else "died")] += 1


o = O()
g = lib.Walk(info["replay_path"])
try:
    g.run(o)
except Stop:
    pass
names = {s: info.get("team_%s_name" % s.lower(), s) for s in "AB"}
print(f"=== OPEN {gid} {info.get('map')} | spawns {o.spawn} | {dict((k, v) for k, v in info.items() if k in ('team_a', 'team_b', 'team_a_id', 'team_b_id', 'a_name', 'b_name', 'name_a', 'name_b'))}")
print("  block | side: units total meanDistFromSpawn naturalPearlsWithin10 | ate nat/corpse, splits, selfkills, other deaths | natural pearls on board")
for r in sorted(o.rows):
    parts = []
    for s in "AB":
        u = o.rows[r][s]
        parts.append(f"{s}: {u[0]:2d}u {u[1]:3d}t dist{u[2]:5.1f} near{u[3]:3d} | ate {o.c[(r, s, 'nat')]:2d}/{o.c[(r, s, 'corpse')]:2d} sp{o.c[(r, s, 'split')]:2d} sk{o.c[(r, s, 'selfkill')]:2d} d{o.c[(r, s, 'died')]:2d}")
    print(f"  r{r:3d} | " + " || ".join(parts) + f" | board {o.rows[r]['nat']}")
