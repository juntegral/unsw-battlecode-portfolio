#!/usr/bin/env python3
"""b_chance4.py <team_id> [max_round=100]: independent recount of the "local head count" rule (sub-session A2).

b_chance3.py found that before round 100 forgot's 2-3-long dragons ram a queen in view mostly when they are not
outnumbered within 4 path steps. This script recounts the same turns (q3v2 in-view chances, attacker 2-3 long,
round < max_round, 2000+ opponents, no Schooltime) with its own code and five different ways of counting heads
around the attacker at the start of its turn:
  path3 / path4 / path5: heads within 3 / 4 / 5 path steps (kelp respected, bodies ignored)
  view: heads inside the attacker's 7x7 square
  cheb2: heads inside the 5x5 square
For each it prints taken / all by the difference (other own heads) - (enemy heads, the queen included), and the two
numbers that matter: taken when the difference is >= 0 and when it is < 0. It also prints the same split with the
attacker itself counted on the own side (difference >= 1 instead of >= 0 is then the same test).
"""
import csv
import json
import os
import sys
from collections import defaultdict

import lib

HERE = os.path.dirname(os.path.abspath(__file__))
tid = sys.argv[1]
maxr = int(sys.argv[2]) if len(sys.argv) > 2 else 100
games = {g["game_id"]: g for g in csv.DictReader(open(os.path.join(HERE, "games.csv")))}
todo = {}
for gid, g in games.items():
    if g["map"] == "Schooltime":
        continue
    side = "A" if g["teamAId"] == tid else "B" if g["teamBId"] == tid else None
    if side is None:
        continue
    op = "B" if side == "A" else "A"
    try:
        if float(g["team%sElo" % op]) < 2000:
            continue
    except ValueError:
        continue
    p = os.path.join(HERE, "q3v2", gid + ".json")
    if not os.path.exists(p):
        continue
    ch = {(c[0], c[2]): c[5] for c in json.load(open(p))["chances"] if c[1] == side and c[9] and c[0] < maxr and c[3] <= 3}
    if ch:
        todo[gid] = (side, ch)


class Stop(Exception):
    pass


MODES = ("path3", "path4", "path5", "view", "cheb2")
tab = {m: defaultdict(lambda: [0, 0]) for m in MODES}


class H(lib.Hooks):
    def __init__(self, side, ch):
        self.side, self.ch = side, ch
        self.last = max(k[0] for k in ch)

    def round_start(self, g, r):
        if r > self.last:
            raise Stop

    def action(self, g, did, kind, nsteps):
        taken = self.ch.get((g.round, did))
        if taken is None:
            return
        b = g.board
        s = self.side
        head = g.bodies[did][0]
        d5 = b.bfs(head, 5)
        own = [o[0] for i, o in g.bodies.items() if g.teams[i] == s and i != did]
        foe = [o[0] for i, o in g.bodies.items() if g.teams[i] != s]
        for m in MODES:
            if m.startswith("path"):
                k = int(m[4:])
                a = sum(1 for c in own if d5.get(c, 99) <= k)
                e = sum(1 for c in foe if d5.get(c, 99) <= k)
            else:
                k = 3 if m == "view" else 2
                a = sum(1 for c in own if b.cheb(c, head) <= k)
                e = sum(1 for c in foe if b.cheb(c, head) <= k)
            diff = max(-3, min(2, a - e))
            tab[m][diff][0] += taken
            tab[m][diff][1] += 1


n = 0
for gid, (side, ch) in sorted(todo.items()):
    try:
        lib.Walk(games[gid]["replay_path"]).run(H(side, ch))
    except Stop:
        pass
    n += 1
tot = sum(v[1] for v in tab["path4"].values())
print(f"team {tid}: rounds 0-{maxr - 1}, attackers 2-3 long: {tot} in-view chances in {n} games")
for m in MODES:
    t = tab[m]
    ge = [sum(t[d][i] for d in t if d >= 0) for i in (0, 1)]
    lt = [sum(t[d][i] for d in t if d < 0) for i in (0, 1)]
    print(f"  {m:6s}: other own heads minus enemy heads (queen included): " + " | ".join(f"{d}: {t[d][0]}/{t[d][1]}" for d in sorted(t))
          + f"  ||  not outnumbered: {ge[0]}/{ge[1]}   outnumbered: {lt[0]}/{lt[1]}")
