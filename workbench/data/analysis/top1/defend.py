#!/usr/bin/env python3
"""The defence side of approaches: for the queen of each team (as victim), by allied heads within 6 steps when a
small (<= 4 long) enemy began its approach: share ending with the queen rammed by that enemy, with the queen dead by
any other cause before the enemy left, with the enemy rammed by a defender. Reads q/*.json, sealed map excluded.
"""
import glob
import json
from collections import defaultdict

TEAMS = {306: "Vibing++", 91: "SSS", 264: "forgot", 1119: "meow"}
SEALED = {"Schooltime"}
tab = defaultdict(lambda: [0, 0, 0, 0])
for f in glob.glob("q/*.json"):
    d = json.load(open(f))
    if d["map"] in SEALED:
        continue
    for s in "AB":
        o = "B" if s == "A" else "A"
        t = d["sides"][s]["team"]
        if t not in TEAMS or (d["sides"][o]["elo"] or 0) < 2000:
            continue
        for ep in d["sides"][s]["episodes"]:
            if ep["len"] > 4:
                continue
            a = ep.get("a6") or 0
            for key in ((TEAMS[t], "0 allies" if a == 0 else "1-2 allies" if a <= 2 else "3+ allies"), (TEAMS[t], "any")):
                x = tab[key]
                x[0] += 1
                x[1] += ep["outcome"] == "it_rammed" and bool(ep.get("victim_queen"))
                x[2] += ep["outcome"] == "queen_dead"
                x[3] += ep["outcome"] in ("rammed_by_defender", "rammed_by_queen")
print("victim queen's team | allied heads within 6 steps at the start | small-enemy approaches | queen rammed by it | queen died otherwise during it | it was rammed by a defender")
for name in TEAMS.values():
    for grp in ("0 allies", "1-2 allies", "3+ allies", "any"):
        x = tab[(name, grp)]
        if x[0]:
            print(f"{name:9s} {grp:10s} n={x[0]:5d} ({x[0] / max(1, tab[(name, 'any')][0]):.2f})  rammed by it {x[1] / x[0]:.3f}  died otherwise {x[2] / x[0]:.3f}  defender rammed it {x[3] / x[0]:.3f}")
