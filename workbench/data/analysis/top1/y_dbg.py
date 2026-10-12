#!/usr/bin/env python3
"""Debug: event order around deaths and splits in one game, and timing of a plain walk.
Usage: python3 y_dbg.py <game_id> [max lines]"""
import sys
import time
from collections import Counter

import lib
import y_lib as Y

G = {g["game_id"]: g for g in Y.load_games()}


class D(lib.Hooks):
    def __init__(self, limit):
        self.limit = limit
        self.n = 0
        self.reasons = Counter()
        self.kinds = Counter()
        self.last_action = None
        self.sonar_n = 0
        self.sonar_big = 0

    def action(self, g, did, kind, nsteps):
        self.kinds[kind] += 1
        self.last_action = (g.round, did, kind, nsteps)

    def death(self, g, did, reason, length, body, actor):
        self.reasons[reason] += 1
        if self.n < self.limit and g.round >= 380:
            self.n += 1
            print("r%d death #%d %s L%d actor %s current %s act_kind %s last_action %s team %s" % (
                g.round, did, reason, length, actor, g.current, g.act_kind, self.last_action, g.teams[did]))

    def split(self, g, parent, child, before, plen, clen):
        if self.n < self.limit and before >= 8:
            self.n += 1
            print("r%d split #%d -> #%d before %d parent %d child %d current %s parent head %s child head %s" % (
                g.round, parent, child, before, plen, clen, g.current, g.bodies[parent][0], g.bodies[child][0]))

    def sonar(self, g, sender, value, raw):
        self.sonar_n += 1
        if value >> 32:
            self.sonar_big += 1

    def end(self, g, rounds, winner, result):
        print("end rounds", rounds, "winner", winner)


gid = sys.argv[1]
t = time.time()
d = D(int(sys.argv[2]) if len(sys.argv) > 2 else 30)
w = lib.Walk(G[gid]["replay_path"])
w.run(d)
print("time %.2fs" % (time.time() - t), "reasons", dict(d.reasons), "action kinds", dict(d.kinds), "sonar", d.sonar_n, d.sonar_big)
print("board", w.board.w, w.board.h, w.board.name, "queens", w.board.queen)
