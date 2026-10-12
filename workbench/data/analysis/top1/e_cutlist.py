#!/usr/bin/env python3
"""For a list of games: every leader cut from a given round on, both sides (round, parent id, length before -> head keeps
+ child gets, free cells at the head; a cut = the team's longest dragon of 8+ keeps 2-3), the leader's deaths, and the
first three feeder deaths of each side. Usage: python3 e_cutlist.py id,id,... [from_round=300]"""
import json
import os
import sys

import e_lib as E

r0 = int(sys.argv[2]) if len(sys.argv) > 2 else 300
for gid in sys.argv[1].split(","):
    d = json.load(open(os.path.join(E.HERE, "e_out", "w4", "%s.json" % gid)))
    DI = {k: i for i, k in enumerate(d["dcol"])}
    print("game %s %s %s" % (gid, d["map"], d["set"]))
    for S in "AB":
        s = d["sides"][S]
        me = d["me"] == S
        cuts = [x for x in s["splits"] if x[7] and x[3] >= 8 and x[4] <= 3 and x[0] >= r0]
        print("   %s (%s): %d leader cuts from r%d: %s" % (S, d[S + "n"], len(cuts), r0, "; ".join(
            "r%d #%d %d->%d+%d free %d" % (x[0], x[1], x[3], x[4], x[5], x[6]) for x in cuts)))
        lost = [x for x in s["deaths"] if x[DI["rank"]] == 1 and x[2] >= 12 and x[0] >= r0 - 50]
        if lost:
            print("      longest dragon (12+) died: " + "; ".join("r%d #%d L%d %s%s at (%d,%d)" % (
                x[0], x[1], x[2], ("rammed", "it rammed", "by choice", "boxed in", "own ram")[x[DI["cls"]]],
                (" by #%d L%d in %d steps" % (x[DI["kid"]], x[DI["klen"]], x[DI["ksteps"]])) if x[DI["cls"]] == 0 else "", x[DI["x"]], x[DI["y"]]) for x in lost))
        fd = [x for x in s["deaths"] if ((x[DI["cls"]] == 2 and 0 <= x[DI["tdist"]] <= 3) or (me and x[DI["reason"]] == 4 and x[DI["akind"]] == 2)) and x[0] >= 200]
        rs = sorted(x[0] for x in fd)
        st = next((rs[i] for i in range(len(rs) - 2) if rs[i + 2] - rs[i] <= 15), None)
        first = [x for x in fd if st is not None and x[0] >= st][:3]
        print("      feeding starts r%s; first feeders: %s" % (st, "; ".join("r%d #%d L%d at (%d,%d) next to #%d L%d (%d steps)" % (
            x[0], x[1], x[2], x[DI["x"]], x[DI["y"]], x[DI["tid"]], x[DI["tlen"]], x[DI["tdist"]]) for x in first)))
