#!/usr/bin/env python3
"""Kill rate per approach by attacker length, for each of the three top teams separately (all sizes, sealed map excluded),
and how far the attacker was from the queen at the start of the fatal round (from q2 tracks). Reads q/*.json, q2/*.json."""
import glob
import json
from collections import Counter, defaultdict

TEAMS = {306: "Vibing++", 91: "SSS", 264: "forgot", 1119: "meow"}
SEALED = {"Schooltime"}


def lc(n):
    return "L2-3" if n <= 3 else "L4" if n == 4 else "L5-9" if n <= 9 else "L10+"


tab = defaultdict(lambda: [0, 0])
maps = {}
for f in glob.glob("q/*.json"):
    d = json.load(open(f))
    maps[d["game_id"]] = d
    if d["map"] in SEALED:
        continue
    for s in "AB":
        o = "B" if s == "A" else "A"
        att = d["sides"][o]["team"]
        if att not in TEAMS or (d["sides"][s]["elo"] or 0) < 2000:
            continue
        for ep in d["sides"][s]["episodes"]:
            t = tab[(TEAMS[att], lc(ep["len"]))]
            t[0] += 1
            t[1] += ep["outcome"] == "it_rammed" and bool(ep.get("victim_queen"))
for name in TEAMS.values():
    print(f"{name:9s} " + " | ".join(f"{c}: {tab[(name, c)][1]}/{tab[(name, c)][0]} = {tab[(name, c)][1] / max(1, tab[(name, c)][0]):.3f}"
                                    for c in ("L2-3", "L4", "L5-9", "L10+")))

print("\nqueen kills by the top three: path distance killer -> queen at the START of the fatal round, by killer length")
dist = defaultdict(Counter)
for f in glob.glob("q2/*.json"):
    d2 = json.load(open(f))
    d = maps.get(d2["game_id"])
    if not d or d["map"] in SEALED:
        continue
    for k in d2["kills"]:
        if not k["queen"]:
            continue
        killer_side = "A" if k["victim_team"] == "B" else "B"
        if d["sides"][killer_side]["team"] not in (306, 91, 264):
            continue
        t = k["track"].get("1")
        if t is None:
            dist[lc(k["klen"])]["born that round"] += 1
        else:
            dd = t[0]
            dist[lc(k["klen"])]["1-2" if 0 <= dd <= 2 else "3" if dd == 3 else "4-6" if 0 <= dd <= 6 else "7+"] += 1
for c in ("L2-3", "L4", "L5-9", "L10+"):
    n = sum(dist[c].values())
    print(f"  {c:5s} n={n:3d} " + " ".join(f"{k}: {v / n:.2f}" for k, v in sorted(dist[c].items())))
