#!/usr/bin/env python3
"""b_sonar4.py <game_id> <team A|B> [r1 r2] [target=queen|leader]: search the team's sonar value for a cell INDEX
that tracks a target (sub-session A2).

A team may pack a cell as one number (y * width + x, or x * height + y) instead of two 6-bit fields. For every bit
offset 0..52 and both orders this decodes a 12-bit index, and counts in how many pings (rounds r1..r2, target alive,
and at least one own dragon had the target's head in view in the last 5 rounds) the decoded cell is within 2 cells
(wrapped chebyshev) of the target's head. Target: the enemy queen (default) or the enemy's longest dragon.
Prints the best layouts. A random cell is within 2 cells of a given cell about 25 times in (width * height).
"""
import csv
import sys

import lib

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
gid, side = sys.argv[1], sys.argv[2]
r1 = int(sys.argv[3]) if len(sys.argv) > 3 else 0
r2 = int(sys.argv[4]) if len(sys.argv) > 4 else 499
target = sys.argv[5] if len(sys.argv) > 5 else "queen"
op = "B" if side == "A" else "A"


class S(lib.Hooks):
    def __init__(self):
        self.t = None
        self.lastseen = -99
        self.rows = []
        self.allrows = []

    def round_start(self, g, r):
        b = g.board
        if target == "queen":
            q = g.bodies.get(b.queen[op])
        else:
            best = None
            for d, o in g.bodies.items():
                if g.teams[d] == op and (best is None or len(o) > len(best)):
                    best = o
            q = best
        self.t = q[0] if q else None
        if q and any(g.teams[d] == side and b.cheb(o[0], q[0]) <= 3 for d, o in g.bodies.items()):
            self.lastseen = r

    def sonar(self, g, sender, value, raw):
        if g.teams.get(sender) != side or not (r1 <= g.round <= r2) or self.t is None:
            return
        self.allrows.append((g.round, value, self.t, g.round - self.lastseen))
        if g.round - self.lastseen > 5:
            return
        self.rows.append((value, self.t))


x = S()
w_ = lib.Walk(GAMES[gid]["replay_path"])
w_.run(x)
b = w_.board
W, Hh = b.w, b.h
rows = x.rows
print(f"=== SONAR4 {gid} {GAMES[gid]['map']} {W}x{Hh} team {side} ({GAMES[gid]['team%sName' % side]}), rounds {r1}-{r2}, target {target}: {len(rows)} pings in rounds where the target was known")
res = []
for o in range(0, 53):
    for bits in (11, 12, 13):
        mask = (1 << bits) - 1
        for order in ("y*w+x", "x*h+y", "x*64+y", "y*64+x"):
            hit = 0
            for v, t in rows:
                idx = (v >> o) & mask
                if order == "y*w+x":
                    c = (idx % W, idx // W)
                elif order == "x*h+y":
                    c = (idx // Hh, idx % Hh)
                elif order == "x*64+y":
                    c = (idx >> 6, idx & 63)
                else:
                    c = (idx & 63, idx >> 6)
                if c[0] < W and c[1] < Hh and b.cheb(c, t) <= 2:
                    hit += 1
            res.append((hit, o, bits, order))
res.sort(reverse=True)
for hit, o, bits, order in res[:6]:
    print(f"  {100 * hit / max(1, len(rows)):.1f}% ({hit}) of pings: index of {bits} bits at bit {o}, order {order}")
# with the best layout: share of pings near the target by how long ago the team last had it in view
if res:
    hit, o, bits, order = res[0]
    mask = (1 << bits) - 1
    from collections import defaultdict
    by = defaultdict(lambda: [0, 0])
    per = defaultdict(lambda: [0, 0])
    for r, v, t, ago in x.allrows:
        idx = (v >> o) & mask
        if order == "y*w+x":
            c = (idx % W, idx // W)
        elif order == "x*h+y":
            c = (idx // Hh, idx % Hh)
        elif order == "x*64+y":
            c = (idx >> 6, idx & 63)
        else:
            c = (idx & 63, idx >> 6)
        near = c[0] < W and c[1] < Hh and b.cheb(c, t) <= 2
        k = "0-5" if ago <= 5 else "6-20" if ago <= 20 else "21-60" if ago <= 60 else "61+ or never"
        by[k][0] += near
        by[k][1] += 1
        per[r // 10 * 10][0] += near
        per[r // 10 * 10][1] += 1
    print(f"  best layout ({bits} bits at bit {o}, {order}): share of pings with the cell within 2 of the target, by rounds since the team last had it in view: "
          + "; ".join(f"{k}: {100 * v[0] / max(1, v[1]):.1f}% of {v[1]}" for k, v in sorted(by.items())))
    print("  per 10 rounds: " + " ".join(f"r{r}:{100 * v[0] // max(1, v[1])}%/{v[1]}" for r, v in sorted(per.items())))
