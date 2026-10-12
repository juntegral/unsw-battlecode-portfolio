#!/usr/bin/env python3
"""For our round-500 losses with their queen alive: did we ever have her in reach / in sight, by map and by whether her death would flip the game."""
import glob
import json
from collections import defaultdict

SEALED = {"Schooltime"}
rows = defaultdict(list)
for f in glob.glob("q/*.json"):
    d = json.load(open(f))
    if d["map"] in SEALED or d["end_type"] == "wipe-out":
        continue
    for s in "AB":
        o = "B" if s == "A" else "A"
        if d["sides"][s]["team"] != 1119 or (d["sides"][o]["elo"] or 0) < 2000 or d["winner"] == s:
            continue
        me, op = d["sides"][s], d["sides"][o]
        mq, oq = me["final"]["queen"], op["final"]["queen"]
        if not oq:
            continue
        op_long, op_second = op["final"]["longest"], op["per"]["second"][-1]
        op_noq = op_second if oq == op_long else op_long
        flip = True if mq else me["final"]["longest"] > op_noq
        q = op["per"]["q"]
        reach = sum(1 for x in q if x and x[9] is not None and x[9] <= 0)
        reach_late = sum(1 for r, x in enumerate(q) if r >= 300 and x and x[9] is not None and x[9] <= 0)
        seen = sum(1 for x in q if x and x[8] > 0)
        near8 = sum(1 for x in q if x and x[4] > 0)
        rows[(d["map"], flip)].append((reach, reach_late, seen, near8, oq))
print("map | flips if she dies | games | games with >=1 reach-round | mean reach-rounds | mean reach-rounds after r300 | mean rounds seen | mean rounds one of our heads within 8 steps | her mean final length")
tot = defaultdict(lambda: [0, 0, 0])
for (m, flip), v in sorted(rows.items()):
    n = len(v)
    print(f"{m:18s} {'FLIP' if flip else 'no  '} n={n:2d} reach>=1: {sum(1 for x in v if x[0] >= 1):2d}  reach {sum(x[0] for x in v) / n:5.1f}  late reach {sum(x[1] for x in v) / n:5.1f}  "
          f"seen {sum(x[2] for x in v) / n:6.1f}  within8 {sum(x[3] for x in v) / n:6.1f}  her len {sum(x[4] for x in v) / n:5.1f}")
    tot[flip][0] += n
    tot[flip][1] += sum(1 for x in v if x[0] >= 1)
    tot[flip][2] += sum(1 for x in v if x[0] >= 5)
for flip, v in tot.items():
    print("FLIP" if flip else "no", "games", v[0], "with >=1 reach-round", v[1], "with >=5", v[2])
