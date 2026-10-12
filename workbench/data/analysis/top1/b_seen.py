#!/usr/bin/env python3
"""b_seen.py <game_id>: when was each queen inside the 7x7 view of an enemy head? (sub-session A2)

For each side's queen: the rounds (as ranges) in which at least one enemy head had her HEAD inside its 7x7 square at
round start, with the number of such enemy heads and the queen's length then; and the same for "any segment of her
body" (a long queen is seen more often than her head is). Then her length every 10 rounds.
"""
import csv
import sys

import lib

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
gid = sys.argv[1]
info = GAMES[gid]


class S(lib.Hooks):
    def __init__(self):
        self.head = {"A": {}, "B": {}}
        self.body = {"A": {}, "B": {}}
        self.qlen = {"A": {}, "B": {}}

    def round_start(self, g, r):
        b = g.board
        for s in "AB":
            q = g.bodies.get(b.queen[s])
            if q is None:
                continue
            self.qlen[s][r] = len(q)
            h = [d for d, o in g.bodies.items() if g.teams[d] != s and b.cheb(o[0], q[0]) <= 3]
            if h:
                self.head[s][r] = len(h)
            cells = list(q)
            bb = [d for d, o in g.bodies.items() if g.teams[d] != s and any(b.cheb(o[0], c) <= 3 for c in cells)]
            if bb:
                self.body[s][r] = len(bb)


def ranges(d, qlen):
    out, cur = [], None
    for r in sorted(d):
        if cur and r - cur[1] <= 1:
            cur[1] = r
            cur[2] = max(cur[2], d[r])
        else:
            cur = [r, r, d[r]]
            out.append(cur)
    return " ".join(f"{a}-{c}(x{n},L{qlen[a]})" if a != c else f"{a}(x{n},L{qlen[a]})" for a, c, n in out)


x = S()
lib.Walk(info["replay_path"]).run(x)
print(f"=== SEEN {gid} {info['map']} | A = {info['teamAName']} B = {info['teamBName']}")
for s in "AB":
    name = info["team%sName" % s]
    print(f"  queen of {s} ({name}): head in view of an enemy head in {len(x.head[s])} rounds, any segment in {len(x.body[s])} rounds, alive {len(x.qlen[s])} rounds")
    print("    head seen (rounds, max seers, her length at the start of the range):", ranges(x.head[s], x.qlen[s]))
    print("    any segment seen:", ranges(x.body[s], x.qlen[s]))
    print("    her length every 10 rounds:", " ".join(f"{r}:{x.qlen[s][r]}" for r in sorted(x.qlen[s]) if r % 10 == 0))
