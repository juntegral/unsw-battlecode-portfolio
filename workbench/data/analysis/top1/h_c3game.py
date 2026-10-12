#!/usr/bin/env python3
"""Per-game view of the candidate-3 count: for given game ids, the share of "free pearl next to the head" turns on
which a dragon of 2-4 ate it, per side, in 50-round blocks.  Usage: python3 h_c3game.py <gid> [<gid> ...]
(walks the replay; same turn definition as h_c3.py part A)."""
import csv
import sys
from collections import defaultdict

import lib


class H(lib.Hooks):
    def __init__(self):
        self.tab = defaultdict(lambda: [0, 0])
        self.pend = None

    def close(self):
        p = self.pend
        self.pend = None
        if p:
            side, blk, cands, first = p
            self.tab[(side, blk)][0] += 1
            self.tab[(side, blk)][1] += int(first in cands)

    def round_start(self, g, r):
        self.close()

    def action(self, g, did, kind, nsteps):
        self.close()
        b = g.board
        s = g.teams[did]
        if did == b.queen[s] or kind != 0:
            return
        body = g.bodies[did]
        if len(body) > 4:
            return
        head = body[0]
        occupied = set()
        for d2, other in g.bodies.items():
            occupied.update(other)
            if d2 != did and g.teams[d2] != s and b.cheb(other[0], head) <= 3:
                return
        cands = [c for c in b.nb(head) if c is not None and c not in occupied and c in g.pearls
                 and any(m is not None and m != head and m not in occupied for m in b.nb(c))]
        if cands:
            self.pend = (s, g.round // 50, cands, b.step(head, g.act_dirs[0]) if g.act_dirs else None)

    def end(self, g, rounds, winner, result):
        self.close()


rows = {r["game_id"]: r for r in csv.DictReader(open("games.csv"))}
for gid in sys.argv[1:]:
    r = rows[gid]
    h = H()
    lib.Walk(r["replay_path"]).run(h)
    print(f"\n{gid} {r['map']} ({r['cells']} cells): A = {r['teamAName']} | B = {r['teamBName']} | winner {r['winner']} | {r['end_type']} | run {r['battle_id']}")
    for s in "AB":
        print(f"   side {s}: " + "  ".join(f"r{50 * k}-{50 * k + 49}: {100 * h.tab[(s, k)][1] / h.tab[(s, k)][0]:.0f}% of {h.tab[(s, k)][0]}"
                                           for k in range(10) if h.tab[(s, k)][0]))
