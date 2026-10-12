#!/usr/bin/env python3
"""Approach episodes: an enemy head comes within 6 path-steps of a live queen. What share end with that dragon
ramming the queen, by the dragon's length when the episode began and by the attacking team?

Episode ends when the dragon dies, moves more than 9 steps away, or the queen dies. Reads q/*.json (sealed map excluded).
"""
import glob
import json
from collections import defaultdict

TOP3 = {306, 91, 264}
SEALED = {"Schooltime"}


def lc(n):
    return "2" if n <= 2 else "3" if n == 3 else "4" if n == 4 else "5-6" if n <= 6 else "7-9" if n <= 9 else "10+"


def size(d):
    c = d["w"] * d["h"]
    return "small" if c <= 700 else "medium" if c <= 1500 else "large"


tab = defaultdict(lambda: [0, 0, 0, 0])   # episodes, rammed queen, rammed by defender, min dist <= 3
for f in glob.glob("q/*.json"):
    d = json.load(open(f))
    if d["map"] in SEALED:
        continue
    for s in "AB":          # s = side whose queen is approached
        o = "B" if s == "A" else "A"
        att = d["sides"][o]["team"]
        grp = "top3" if att in TOP3 else "meow" if att == 1119 else "other"
        if grp == "top3" and (d["sides"][s]["elo"] or 0) < 2000:
            continue
        if grp == "meow" and (d["sides"][s]["elo"] or 0) < 2000:
            continue
        for ep in d["sides"][s]["episodes"]:
            for key in ((grp, size(d), lc(ep["len"])), (grp, "all", lc(ep["len"]))):
                t = tab[key]
                t[0] += 1
                t[1] += ep["outcome"] == "it_rammed" and bool(ep.get("victim_queen"))
                t[2] += ep["outcome"] in ("rammed_by_defender", "rammed_by_queen")
                t[3] += ep["min"] <= 3
print("attacker group | map size | attacker length at the start of the approach | approaches | ended by ramming the queen | attacker rammed by a defender | got within 3 steps")
for grp in ("top3", "meow", "other"):
    for sz in ("small", "medium", "large", "all"):
        for cls in ("2", "3", "4", "5-6", "7-9", "10+"):
            t = tab[(grp, sz, cls)]
            if t[0] >= 15:
                print(f"{grp:5s} {sz:6s} L{cls:4s} n={t[0]:5d}  rammed the queen {t[1] / t[0]:.3f} ({t[1]:4d})  rammed by defender {t[2] / t[0]:.3f}  within 3 steps {t[3] / t[0]:.2f}")
