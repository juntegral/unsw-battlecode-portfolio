#!/usr/bin/env python3
"""b_sonar.py <game_id> <team A|B> [r1 r2]: does the team's sonar value carry the enemy queen's position? (sub-session A2)

Every ping carries one 64-bit value. For each ping sent by the team in rounds r1..r2 this records the value and four
candidate targets: the enemy queen's head (x, y) at the start of that round, and her head (x, y) at the last round in
which any dragon of the team had her head inside its 7x7 view ("last seen"). For every bit offset 0..58 and field
widths 6, 7 and 8 it counts how often the field equals each target coordinate, and prints the best offsets. A random
6-bit field matches a coordinate about 1 time in 64 (1.6%), so a rate of 30% or more over hundreds of pings is a
real encoding. Also prints how many different values the team sends per round (one shared value = a broadcast).
"""
import csv
import sys
from collections import Counter, defaultdict

import lib

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
gid, side = sys.argv[1], sys.argv[2]
r1 = int(sys.argv[3]) if len(sys.argv) > 3 else 0
r2 = int(sys.argv[4]) if len(sys.argv) > 4 else 499
op = "B" if side == "A" else "A"


class S(lib.Hooks):
    def __init__(self):
        self.q = None
        self.last = None
        self.lastr = None
        self.rows = []
        self.vals = defaultdict(set)
        self.seen_rounds = 0
        self.ownq = None

    def round_start(self, g, r):
        b = g.board
        q = g.bodies.get(b.queen[op])
        self.q = q[0] if q else None
        oq = g.bodies.get(b.queen[side])
        self.ownq = oq[0] if oq else None
        if q:
            if any(g.teams[d] == side and b.cheb(o[0], q[0]) <= 3 for d, o in g.bodies.items()):
                self.last, self.lastr = q[0], r
                self.seen_rounds += 1

    def sonar(self, g, sender, value, raw):
        if g.teams.get(sender) != side or not (r1 <= g.round <= r2):
            return
        self.vals[g.round].add(value)
        body = g.bodies.get(sender)
        self.rows.append((g.round, value, self.q, self.last, self.lastr, body[0] if body else None, self.ownq))


x = S()
lib.Walk(GAMES[gid]["replay_path"]).run(x)
rows = x.rows
print(f"=== SONAR {gid} {GAMES[gid]['map']} team {side} ({GAMES[gid]['team%sName' % side]}), rounds {r1}-{r2}: {len(rows)} pings; rounds in which the team had the enemy queen's head in view: {x.seen_rounds}")
nv = [len(v) for r, v in sorted(x.vals.items())]
if nv:
    print(f"  different values sent per round: mean {sum(nv) / len(nv):.1f}, max {max(nv)}; rounds with one single value: {sum(1 for n in nv if n == 1)} of {len(nv)}")
targets = {
    "queen x now": lambda row: row[2][0] if row[2] else None,
    "queen y now": lambda row: row[2][1] if row[2] else None,
    "queen x last seen": lambda row: row[3][0] if row[3] else None,
    "queen y last seen": lambda row: row[3][1] if row[3] else None,
    "sender x": lambda row: row[5][0] if row[5] else None,
    "sender y": lambda row: row[5][1] if row[5] else None,
    "own queen x": lambda row: row[6][0] if row[6] else None,
    "own queen y": lambda row: row[6][1] if row[6] else None,
    "round (low 8 bits)": lambda row: row[0] & 255,
    "round last seen (low 8 bits)": lambda row: (row[4] & 255) if row[4] is not None else None,
}
for name, fn in targets.items():
    best = []
    for w in (6, 7, 8):
        mask = (1 << w) - 1
        for o in range(0, 64 - w + 1):
            n = hit = 0
            for row in rows:
                t = fn(row)
                if t is None:
                    continue
                n += 1
                if ((row[1] >> o) & mask) == t:
                    hit += 1
            if n:
                best.append((hit / n, hit, n, o, w))
    best.sort(reverse=True)
    print(f"  {name}: best fields (match rate, hits/n, bit offset, width): " + "; ".join(f"{100 * b[0]:.0f}% {b[1]}/{b[2]} @bit{b[3]} w{b[4]}" for b in best[:3]))
