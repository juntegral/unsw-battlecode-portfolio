#!/usr/bin/env python3
"""Self-test of e_lib.Walk: occupancy map against a full rebuild at every round start, the order of events
around deaths (does the head of a crashing dragon enter the occupied cell first?), and timing.
Usage: python3 e_test.py <game_id> [...]"""
import sys
import time
from collections import Counter

import e_lib as E

GAMES = {g["gid"]: g for g in E.load_games()}


class T(E.Hooks):
    def __init__(self):
        self.bad = 0
        self.c = Counter()
        self.noact_ping = Counter()
        self.dying = {}

    def round_start(self, g, r):
        full = {}
        dup = 0
        for d, body in g.bodies.items():
            for c in body:
                if c in full:
                    dup += 1
                full[c] = d
        if full != g.occ or dup:
            self.bad += 1
            if self.bad <= 3:
                extra = {k: v for k, v in g.occ.items() if full.get(k) != v}
                miss = {k: v for k, v in full.items() if g.occ.get(k) != v}
                print("  r%d occupancy differs: dup %d, in occ only %s, in rebuild only %s" % (r, dup, list(extra.items())[:5], list(miss.items())[:5]))

    def turn(self, g, did):
        self.c["turns"] += 1

    def action(self, g, did, kind, nsteps):
        self.c["action kind %s" % kind] += 1

    def death(self, g, did, reason, length, body, actor):
        head = body[0]
        shared = sum(1 for d, b in g.bodies.items() if d != did and head in b)
        self.c["death %s, actor is self %s, head cell also in another body %s, act kind %s, steps done %d of %d" % (
            reason, actor == did, bool(shared), g.act_kind, min(g.step_index, 9), min(g.act_steps, 9))] += 1
        if reason == "noaction":
            self.dying[did] = g.round

    def sonar(self, g, sender, value, raw):
        if sender in self.dying and self.dying[sender] == g.round:
            self.noact_ping["ping in the round of a noaction death"] += 1
            del self.dying[sender]

    def drop(self, g, cell, origin):
        self.c["drop %s" % origin[0]] += 1


for a in sys.argv[1:]:
    g = GAMES[int(a)]
    t0 = time.time()
    t = T()
    E.Walk(g["path"]).run(t)
    print(a, g["map"], g["An"], "vs", g["Bn"], "| %.1f s | occupancy mismatches at %d round starts" % (time.time() - t0, t.bad))
    for k, v in sorted(t.c.items()):
        print("   ", v, k)
    print("   ", dict(t.noact_ping), "| noaction deaths without a ping that round:", len(t.dying))
