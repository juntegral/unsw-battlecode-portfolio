#!/usr/bin/env python3
"""Candidate 3z, part 4: small dragons near their own longest dragon, every team: natural pearls per 100
dragon-rounds inside (9 cells from the longest at round start) against outside. Reads y_out/w3. Output: y_out/c3d.txt
Also: how our games end by map class and whether they reach the switch round (where 3z can act at all).
"""
import json
import os
from collections import Counter

import y_lib as Y

OUTF = open(Y.out_path("c3d.txt"), "w")


def pr(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUTF.write(s + "\n")


games = {g["game_id"]: g for g in Y.load_games()}
RECS = []
for f in os.listdir(os.path.join(Y.OUT, "w3")):
    if not f.endswith(".json"):
        continue
    d = json.load(open(os.path.join(Y.OUT, "w3", f)))
    g = games[d["gid"]]
    for team, side in Y.study_sides(g):
        o = Y.opp(side)
        RECS.append(dict(d=d, g=g, side=side, group="meow" if team == Y.ME else Y.TOP[team], team=team,
                         build=Y.build_of(g) if team == Y.ME else "", big=Y.is_big(g)))
        if team == Y.ME:
            RECS.append(dict(d=d, g=g, side=o, group="opp", team=g["team%sId" % o], build="", big=Y.is_big(g)))

GROUPS = [("meow live", lambda r: r["group"] == "meow" and r["build"] == "live"),
          ("meow test", lambda r: r["group"] == "meow" and r["build"] == "test"),
          ("opponents", lambda r: r["group"] == "opp"),
          ("test4 (vs us)", lambda r: r["group"] == "opp" and r["team"] == Y.T4),
          ("WHQ (vs us)", lambda r: r["group"] == "opp" and r["team"] == Y.WHQ),
          ("forgot", lambda r: r["group"] == "forgot"),
          ("SSS", lambda r: r["group"] == "SSS"),
          ("Vibing++", lambda r: r["group"] == "Vibing++")]

pr("== Small dragons (2-4): natural pearls per 100 dragon-rounds inside / outside 9 cells of their own longest dragon; share of their dragon-rounds inside")
for cls, lab, phases in ((False, "small maps", [(200, 299), (300, 399), (400, 499)]), (True, "big maps", [(100, 149), (150, 299), (300, 399), (400, 499)])):
    pr(" %s: rounds %s" % (lab, " | ".join("%d-%d" % p for p in phases)))
    for gname, pred in GROUPS:
        rs = [r for r in RECS if pred(r) and r["big"] == cls]
        if not rs:
            continue
        cells = []
        for lo, hi in phases:
            a = [0] * 6
            for r in rs:
                dr = r["d"]["dr"][r["side"]]
                for b in range(lo // 25, hi // 25 + 1):
                    v = dr.get(str(b))
                    if v:
                        for i in range(6):
                            a[i] += v[i]
            if a[0] < 500 or a[1] < 500:
                cells.append("-")
                continue
            cells.append("%.2f / %.2f (%.0f%% inside)" % (100.0 * a[3] / a[0], 100.0 * a[4] / a[1], 100.0 * a[0] / (a[0] + a[1] + a[2])))
        pr("   %-14s %s" % (gname, " | ".join(cells)))

pr("\n== Where 3z can act: our 401 games by map class, how they end, and whether they reach the switch round")
c = Counter()
for g in games.values():
    side = Y.side_of(g, Y.ME)
    if side is None or not any(t == Y.ME for t, s in Y.study_sides(g)):
        continue
    big = Y.is_big(g)
    sw = 150 if big else 300
    rounds = int(g["rounds"])
    won = g["winner"] == side
    c[(big, "reaches the switch" if rounds > sw else "over before the switch", g["end_type"], won)] += 1
for k in sorted(c):
    pr("   %-12s %-24s %-12s won=%s : %d" % ("big maps" if k[0] else "small maps", k[1], k[2], k[3], c[k]))
OUTF.close()
