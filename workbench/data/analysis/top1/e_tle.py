#!/usr/bin/env python3
"""For given games: every death of a dragon of 15+ with reason `noaction`, both sides, with the replay's time-out flag of
that action (tle), the free cells at the start of its turn, its rank in the team and the nearest enemy head.
Then, over all walked games: how many `noaction` deaths of dragons of 15+ each team has, and how many carry the flag.
Usage: python3 e_tle.py [game_id ...]"""
import json
import os
import sys

import e_data as D
import e_lib as E

for gid in sys.argv[1:]:
    d = json.load(open(os.path.join(E.HERE, "e_out", "w4", "%s.json" % gid)))
    DI = {k: i for i, k in enumerate(d["dcol"])}
    for S in "AB":
        for x in d["sides"][S]["deaths"]:
            if x[2] >= 15 and x[DI["reason"]] == 4:
                print("game %s %s r%d #%d L%d noaction: time-out flag %d, action kind %d, free cells %d, rank %d, enemy head %d cells, pearls %d (own %d, enemy %d)" % (
                    gid, d[S + "n"], x[0], x[1], x[2], x[DI["tle"]], x[DI["akind"]], x[DI["free"]], x[DI["rank"]], x[DI["emanh"]], x[DI["drop"]],
                    x[DI["e_t"]] + x[DI["e_l"]] + x[DI["e_q"]] + x[DI["e_o"]], x[DI["e_e"]]))

agg = {}
for r in D.rows():
    DI = {k: i for i, k in enumerate(r.d["dcol"])}
    for g in D.groups(r):
        a = agg.setdefault(g, [0, 0, 0, 0, 0])
        a[0] += 1
        for x in r.s["deaths"]:
            if x[2] >= 15 and x[DI["reason"]] == 4:
                a[1] += 1
                a[2] += x[DI["tle"]]
                a[3] += int(x[DI["rank"]] == 1)
                a[4] += int(x[DI["free"]] == 0)
print("")
print("all study games: `noaction` deaths of dragons of 15+ | with the time-out flag | of the team's longest | with no free cell")
for g in ("meow", "opp", "test4 (vs us)", "WHQ (vs us)", "forgot", "SSS", "Vibing++"):
    a = agg.get(g)
    if a:
        print("%-16s games %4d | %4d | %3d | %3d | %3d" % (g, a[0], a[1], a[2], a[3], a[4]))
