#!/usr/bin/env python3
"""Per map: how our queen dies vs how top-three queens die (cause, round, distance from spawn at death, length).

Opp elo >= 2000. Reads q/*.json.
"""
import glob
import json
import statistics
from collections import Counter, defaultdict

TOP3 = {306, 91, 264}
rows = defaultdict(lambda: defaultdict(list))
for f in glob.glob("q/*.json"):
    d = json.load(open(f))
    for s in "AB":
        o = "B" if s == "A" else "A"
        t = d["sides"][s]["team"]
        if (d["sides"][o]["elo"] or 0) < 2000:
            continue
        grp = "top3" if t in TOP3 else "meow" if t == 1119 else None
        if not grp:
            continue
        sd = d["sides"][s]
        qd = sd["qdeath"]
        if qd is None:
            rows[d["map"]][grp].append(("alive", 500, None, sd["final"]["queen"], None))
            continue
        r = qd["reason"]
        if r == "headon":
            r = "own_ram" if qd["killer"] is None else "ally_ram" if qd["killer"]["team"] == s else "rammed"
        last = qd["last"]
        rows[d["map"]][grp].append((r, qd["round"], last[15] if last else None, qd["len"], last[6] if last else None))
print("map | group | games | alive | rammed | self-inflicted (wall/self/body/own_ram/ally_ram) | noaction | median death round | median dist from spawn at death | queen len<=3 at death")
for m in sorted(rows):
    for grp in ("top3", "meow"):
        v = rows[m][grp]
        if not v:
            continue
        n = len(v)
        c = Counter(x[0] for x in v)
        selfi = sum(c[k] for k in ("wall", "self", "body", "own_ram", "ally_ram"))
        dead = [x for x in v if x[0] != "alive"]
        rounds = [x[1] for x in dead]
        homes = [x[2] for x in dead if x[2] is not None]
        small = sum(1 for x in dead if x[3] <= 3)
        print(f"{m:18s} {grp:5s} n={n:3d} alive {c['alive'] / n:.2f} rammed {c['rammed'] / n:.2f} self-inflicted {selfi / n:.2f} noaction {c['noaction'] / n:.2f} "
              f"death r{statistics.median(rounds) if rounds else 0:5.0f} home {statistics.median(homes) if homes else 0:4.0f} len<=3 {small}/{len(dead)}")
