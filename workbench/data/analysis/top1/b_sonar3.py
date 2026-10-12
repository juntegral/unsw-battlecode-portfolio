#!/usr/bin/env python3
"""b_sonar3.py <game_id> <team A|B> <xbit> <ybit> [r1 r2]: how close is the cell in the team's sonar value to the
enemy queen? (sub-session A2)

For every ping of the team in rounds r1..r2 (enemy queen alive): the wrapped chebyshev distance between the decoded
cell (6 bits at xbit, 6 bits at ybit) and (a) the enemy queen's head, (b) the own queen's head as a control,
(c) the sender's head. Prints the three histograms (0, 1, 2, 3-5, 6-10, 11+), split into rounds in which at least
one dragon of the team had her head in view during the last 5 rounds ("known") and other rounds ("not known").
Then, per round, the share of pings whose cell is within 2 cells of her head (to see when the team starts and stops
talking about her), and the same for pings that ENDED ON a named dragon if a dragon id is given as 7th argument.
"""
import csv
import sys
from collections import Counter, defaultdict

import lib

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
gid, side, xbit, ybit = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
r1 = int(sys.argv[5]) if len(sys.argv) > 5 else 0
r2 = int(sys.argv[6]) if len(sys.argv) > 6 else 499
watch = int(sys.argv[7]) if len(sys.argv) > 7 else None
op = "B" if side == "A" else "A"


def cls(d):
    return "0" if d == 0 else "1" if d == 1 else "2" if d == 2 else "3-5" if d <= 5 else "6-10" if d <= 10 else "11+"


class S(lib.Hooks):
    def __init__(self):
        self.h = defaultdict(Counter)
        self.q = self.oq = None
        self.lastseen = -99
        self.per = defaultdict(lambda: [0, 0])
        self.onw = defaultdict(lambda: [0, 0])
        self.seers = 0

    def round_start(self, g, r):
        b = g.board
        q = g.bodies.get(b.queen[op])
        oq = g.bodies.get(b.queen[side])
        self.q = q[0] if q else None
        self.oq = oq[0] if oq else None
        self.seers = 0
        if q:
            self.seers = sum(1 for d, o in g.bodies.items() if g.teams[d] == side and b.cheb(o[0], q[0]) <= 3)
            if self.seers:
                self.lastseen = r

    def sonar(self, g, sender, value, raw):
        if g.teams.get(sender) != side or not (r1 <= g.round <= r2) or self.q is None:
            return
        b = g.board
        body = g.bodies.get(sender)
        if not body:
            return
        cell = ((value >> xbit) & 63, (value >> ybit) & 63)
        known = "known" if g.round - self.lastseen <= 5 else "not known"
        dq = b.cheb(cell, self.q)
        self.h[(known, "enemy queen")][cls(dq)] += 1
        if self.oq is not None:
            self.h[(known, "own queen (control)")][cls(b.cheb(cell, self.oq))] += 1
        self.h[(known, "sender")][cls(b.cheb(cell, body[0]))] += 1
        self.per[g.round][0] += dq <= 2
        self.per[g.round][1] += 1
        if watch is not None and watch in g.bodies:
            try:
                end = lib.rp.point(raw.pointer(1))
            except Exception:
                end = None
            if end is not None and end in g.bodies[watch] and sender != watch:
                self.onw[g.round][0] += dq <= 2
                self.onw[g.round][1] += 1
        self.per[g.round].append(self.seers) if len(self.per[g.round]) == 2 else None


x = S()
lib.Walk(GAMES[gid]["replay_path"]).run(x)
print(f"=== SONAR3 {gid} {GAMES[gid]['map']} team {side} ({GAMES[gid]['team%sName' % side]}), rounds {r1}-{r2}, cell = 6 bits at {xbit} / 6 bits at {ybit}")
order = ["0", "1", "2", "3-5", "6-10", "11+"]
for k in sorted(x.h):
    tot = sum(x.h[k].values())
    print(f"  {k[0]:9s} | distance from the cell to the {k[1]:20s}: " + " ".join(f"{o}:{100 * x.h[k][o] / tot:.0f}%" for o in order) + f"  (n={tot})")
print("  per round: share of pings whose cell is within 2 cells of her head / pings / own dragons with her head in view")
line = []
for r in sorted(x.per):
    v = x.per[r]
    line.append(f"r{r}:{100 * v[0] // max(1, v[1])}%/{v[1]}/{v[2] if len(v) > 2 else 0}")
print("   " + " ".join(line))
if watch is not None:
    print(f"  rays that ended on #{watch}: per round (cell within 2 of her head / rays): " + " ".join(f"r{r}:{v[0]}/{v[1]}" for r, v in sorted(x.onw.items())))
