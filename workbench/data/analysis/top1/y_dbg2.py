#!/usr/bin/env python3
"""Debug: find the first event after which my occupancy mirror differs from lib's bodies.
Usage: python3 y_dbg2.py <game_id>"""
import sys

import lib
import y_lib as Y
import y_w1

G = {g["game_id"]: g for g in Y.load_games()}


class D(y_w1.W1):
    def __init__(self):
        super().__init__(False)
        self.bad = 0
        self.log = []

    def chk(self, g, what):
        if self.bad >= 3 or not self.ready:
            return
        ref = {}
        for d, b in g.bodies.items():
            for c in b:
                ref[c] = ref.get(c, 0) + 1
        if ref != self.occ:
            self.bad += 1
            diff = [(c, ref.get(c), self.occ.get(c)) for c in set(ref) | set(self.occ) if ref.get(c) != self.occ.get(c)]
            print("DIFF after", what, "round", g.round, diff[:6])
            for line in self.log[-6:]:
                print("    ", line)
            # resync
            self.occ = ref
            self.my = {d: __import__("collections").deque(b) for d, b in g.bodies.items()}

    def round_start(self, g, r):
        self.chk(g, "round_start-pre %d" % r)
        super().round_start(g, r)

    def moved(self, g, did, head, step_index, ate):
        self.log.append(("moved", g.round, did, head, step_index, ate, len(g.bodies[did])))
        super().moved(g, did, head, step_index, ate)

    def split(self, g, parent, child, before, plen, clen):
        self.log.append(("split", g.round, parent, child, before, plen, clen))
        super().split(g, parent, child, before, plen, clen)

    def death(self, g, did, reason, length, body, actor):
        self.log.append(("death", g.round, did, reason, length, list(body)[:4], actor, list(self.my.get(did, []))[:4]))
        super().death(g, did, reason, length, body, actor)

    def action(self, g, did, kind, nsteps):
        self.chk(g, "before action of #%d" % did)
        self.log.append(("action", g.round, did, kind, nsteps))
        super().action(g, did, kind, nsteps)


d = D()
lib.Walk(G[sys.argv[1]]["replay_path"]).run(d)
print("bad", d.bad)
