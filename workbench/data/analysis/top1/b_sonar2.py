#!/usr/bin/env python3
"""b_sonar2.py <game_id> <team A|B> <xbit> <ybit> [tbit] [r1 r2]: test a decoded layout of the team's sonar value.

Hypothesis: the value holds a cell (x = 6 bits at xbit, y = 6 bits at ybit) and, if tbit is given, a round stamp
(8 bits at tbit, the low 8 bits of a round number). For every ping of the team in rounds r1..r2 the cell is compared
with: the sender's head, the enemy queen's head now, the enemy queen's head at the stamped round, the own queen's
head now, the enemy queen's spawn, the own queen's spawn, any enemy head now, any own head now, a pearl now.
Prints how often each matches (first match in that order wins, so the rows add up to 100% with "nothing"), split by
whether the sender itself had the enemy queen in view; and how old the stamp is.
"""
import csv
import sys
from collections import Counter

import lib

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
gid, side, xbit, ybit = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
tbit = int(sys.argv[5]) if len(sys.argv) > 5 and int(sys.argv[5]) >= 0 else None
r1 = int(sys.argv[6]) if len(sys.argv) > 6 else 0
r2 = int(sys.argv[7]) if len(sys.argv) > 7 else 499
op = "B" if side == "A" else "A"


class S(lib.Hooks):
    def __init__(self):
        self.qtrack = {}
        self.c = {True: Counter(), False: Counter()}
        self.age = Counter()
        self.n = 0
        self.snap = None
        self.examples = []

    def round_start(self, g, r):
        b = g.board
        q = g.bodies.get(b.queen[op])
        oq = g.bodies.get(b.queen[side])
        self.qtrack[r] = q[0] if q else None
        self.snap = dict(q=q[0] if q else None, oq=oq[0] if oq else None,
                         en={o[0] for d, o in g.bodies.items() if g.teams[d] == op},
                         own={o[0] for d, o in g.bodies.items() if g.teams[d] == side},
                         enb={c for d, o in g.bodies.items() if g.teams[d] == op for c in o})

    def sonar(self, g, sender, value, raw):
        if g.teams.get(sender) != side or not (r1 <= g.round <= r2):
            return
        b = g.board
        body = g.bodies.get(sender)
        if not body:
            return
        cell = ((value >> xbit) & 63, (value >> ybit) & 63)
        s = self.snap
        sees = s["q"] is not None and b.cheb(body[0], s["q"]) <= 3
        stamp_cell = None
        if tbit is not None:
            t = (value >> tbit) & 255
            rr = g.round - ((g.round - t) % 256)
            if rr >= 0:
                stamp_cell = self.qtrack.get(rr)
                self.age[min(60, g.round - rr) // 10 * 10] += 1
        if cell == body[0]:
            k = "sender's head"
        elif s["q"] is not None and cell == s["q"]:
            k = "enemy queen's head now"
        elif stamp_cell is not None and cell == stamp_cell:
            k = "enemy queen's head at the stamped round"
        elif s["oq"] is not None and cell == s["oq"]:
            k = "own queen's head now"
        elif cell == b.starts[b.queen[op]]:
            k = "enemy queen's spawn"
        elif cell == b.starts[b.queen[side]]:
            k = "own queen's spawn"
        elif cell in s["en"]:
            k = "another enemy head"
        elif cell in s["enb"]:
            k = "an enemy body cell"
        elif cell in s["own"]:
            k = "another own head"
        elif cell in g.pearls:
            k = "a pearl"
        elif s["q"] is not None and b.cheb(cell, s["q"]) <= 2:
            k = "within 2 cells of the enemy queen's head"
        elif cell[0] < b.w and cell[1] < b.h:
            k = "some other cell on the board"
        else:
            k = "not a cell (off the board)"
        self.c[sees][k] += 1
        self.n += 1
        if k.startswith("enemy queen") and len(self.examples) < 6:
            self.examples.append((g.round, sender, hex(value), cell, s["q"]))


x = S()
lib.Walk(GAMES[gid]["replay_path"]).run(x)
print(f"=== SONAR2 {gid} {GAMES[gid]['map']} team {side} ({GAMES[gid]['team%sName' % side]}), rounds {r1}-{r2}, x at bit {xbit}, y at bit {ybit}, stamp at bit {tbit}: {x.n} pings")
for sees in (True, False):
    tot = sum(x.c[sees].values())
    print(f"  sender {'HAD' if sees else 'did not have'} the enemy queen's head in its view: {tot} pings: " + "; ".join(f"{k} {100 * v / max(1, tot):.0f}% ({v})" for k, v in x.c[sees].most_common()))
if tbit is not None:
    print("  age of the stamp in rounds (0 = this round ... 60 = 60 or more):", dict(sorted(x.age.items())))
print("  examples:", x.examples)
