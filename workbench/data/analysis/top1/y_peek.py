#!/usr/bin/env python3
"""First look: how many games per set and run pass the study filter. Output: stdout."""
from collections import Counter

import y_lib as Y

games = Y.load_games()
print("rows", len(games))
c = Counter()
runs = Counter()
vs = Counter()
ends = Counter()
for g in games:
    for team, side in Y.study_sides(g):
        c[team] += 1
        if team == Y.ME:
            runs[(g["battle_id"], Y.build_of(g))] += 1
            o = g["team%sId" % Y.opp(side)]
            vs[(o, g["team%sName" % Y.opp(side)])] += 1
            ends[(g["end_type"], g["rounds"] == "500")] += 1
print("study sides per team:", dict(c))
for k, v in sorted(runs.items()):
    print("  run", k, v)
print("opponents of ours:", vs.most_common(12))
print("end types of ours:", ends.most_common())
print("columns:", list(games[0].keys()))
big = Counter()
for g in games:
    for team, side in Y.study_sides(g):
        if team == Y.ME:
            big[(g["map"], g["cells"], Y.is_big(g))] += 1
for k, v in sorted(big.items(), key=lambda kv: int(kv[0][1])):
    print("  map", k, v)
