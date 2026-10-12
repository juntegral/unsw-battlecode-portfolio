#!/usr/bin/env python3
"""Debug: what the walker's act_dirs look like, and whether board.step(head, dir) gives the first moved head.
Usage: python3 y_dbg3.py <game_id>"""
import sys

import lib
import y_lib as Y

G = {g["game_id"]: g for g in Y.load_games()}


class D(lib.Hooks):
    def __init__(self):
        self.n = 0
        self.ok = self.bad = 0
        self.exp = None

    def action(self, g, did, kind, nsteps):
        self.exp = None
        if kind == 0 and g.act_dirs:
            d0 = g.act_dirs[0]
            if self.n < 5:
                self.n += 1
                print("dirs", g.act_dirs, type(d0))
            self.exp = (did, g.board.step(g.bodies[did][0], int(d0)))

    def moved(self, g, did, head, step_index, ate):
        if self.exp and self.exp[0] == did and step_index == 1:
            if self.exp[1] == head:
                self.ok += 1
            else:
                self.bad += 1
                if self.bad < 5:
                    print("mismatch r%d #%d expected %s got %s" % (g.round, did, self.exp[1], head))


d = D()
lib.Walk(G[sys.argv[1]]["replay_path"]).run(d)
print("first step matches board.step:", d.ok, "mismatch:", d.bad)
