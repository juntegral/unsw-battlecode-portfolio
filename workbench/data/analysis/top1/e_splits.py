#!/usr/bin/env python3
"""Every split of one side of one game between two rounds, from e_out/w4/<gid>.json: round, parent, child, length
before -> parent keeps + child gets, free cells next to the parent's head at the start of its turn (-1 = not known: the
parent was born in this same round), whether the parent was the team's longest at the start of the round.
Usage: python3 e_splits.py <game_id> <A|B|me|opp> <from_round> <to_round> [min_length=8]"""
import json
import os
import sys

import e_lib as E

gid, side, r1, r2 = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
mn = int(sys.argv[5]) if len(sys.argv) > 5 else 8
d = json.load(open(os.path.join(E.HERE, "e_out", "w4", "%s.json" % gid)))
if side == "me":
    side = d["me"]
elif side == "opp":
    side = E.other(d["me"])
for x in d["sides"][side]["splits"]:
    if r1 <= x[0] <= r2 and x[3] >= mn:
        print("r%d #%d -> #%d  %d -> %d + %d  free %d%s%s" % (x[0], x[1], x[2], x[3], x[4], x[5], x[6], "  LONGEST" if x[7] else "", "  QUEEN" if x[8] else ""))
